import json
import os
from datetime import UTC, datetime

import dotenv
from pydantic import EmailStr
from pymongo import MongoClient
from pymongo.database import Database
from tqdm import tqdm

from memetrics.events.schemas import Attribute, Creator, Event, EventData, User

dotenv.load_dotenv()
BATCH_SIZE = 4096
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]
collection = db["events"]
app = "/teialabs/athena/api"

ATHENA_DB_NAME = os.environ["ATHENA_MONGODB_NAME"]
data = client[ATHENA_DB_NAME]["thread"].find()
num_lines = client[ATHENA_DB_NAME]["thread"].count_documents({})

batch = []
_type = "/ask"
_action = "post"
_version = "0.0.0"

start_date = datetime(2024, 5, 1, tzinfo=UTC)
end_date = datetime(2024, 6, 1, tzinfo=UTC)


def assemble_user_email_map(db: Database):
    """Create user ID to email mapping."""
    objs = db["user"].find()
    data = {}
    for obj in objs:
        employee_id = obj["_id"]
        email = obj["email"]
        data[employee_id] = email
    return data


mapping: dict[str, EmailStr] = assemble_user_email_map(client[ATHENA_DB_NAME])


def lookup_email(user_id):
    if user_id in mapping:
        return mapping[user_id]
    tqdm.write(f"Unknown user_id: {user_id}")
    return "unknown@unknown.osf"


counter = 0
for thread in tqdm(data, total=num_lines):
    creator = Creator(
        client_name="/teialabs",
        token_name="nei.workstation",
        user_email=lookup_email(thread["creator_id"]),
    )
    extra = [
        {
            "name": "_id",
            "type": "string",
            "value": thread["_id"],
        },
        {
            "name": "app_id",
            "type": "string",
            "value": thread["app_id"],
        },
        {
            "name": "channel_id",
            "type": "string",
            "value": thread["channel_id"],
        },
        {
            "name": "team_id",
            "type": "string",
            "value": thread["team_id"],
        },
    ]
    for msg in thread["messages"]:
        if msg["type"] != "query":
            continue
        if isinstance(msg["created_at"], str):
            msg["created_at"] = datetime.fromisoformat(msg["created_at"])
        if not msg["created_at"].tzinfo:
            msg["created_at"] = msg["created_at"].replace(tzinfo=UTC)
        if msg["created_at"] <= start_date or msg["created_at"] >= end_date:
            continue
        extra_ = extra + [
            {
                "name": "messages.id",
                "type": "string",
                "value": msg["_id"],
            },
        ]
        memetrics_event = Event(
            created_by=creator,
            created_at=msg["created_at"],
            data=EventData(
                action=_action,
                app=app,
                app_version=_version,
                extra=extra_,
                type=_type,
                user=User(
                    email=lookup_email(msg["user_id"]),
                    extra=[
                        Attribute(
                            name="organization_name",
                            type="string",
                            value=ATHENA_DB_NAME,
                        ),
                    ],
                ),
            ),
        )
        batch.append(memetrics_event.bson())
        if len(batch) == BATCH_SIZE:
            r = collection.insert_many(documents=batch)
            counter += len(batch)
            batch = []

if batch:
    r = collection.insert_many(documents=batch)
    counter += len(batch)
    batch = []

print(f"Inserted {counter} events.")
