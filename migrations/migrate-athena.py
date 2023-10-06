import json
import os
from datetime import datetime

import dotenv
from tqdm import tqdm
from pymongo import MongoClient
from memetrics.events.schemas import Attribute, Creator, Event, EventData, User

dotenv.load_dotenv()
BATCH_SIZE = 2048
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]
collection = db["events"]
app = "/teialabs/athena/api"


def load_jsonl(filepath):
    with open(filepath, "r") as f:
        for line in f:
            yield json.loads(line)


def count_file_lines(filepath):
    with open(filepath, "rb") as f:
        return sum(1 for _ in f)


file = "osfdigital.thread.jsonl"
data = load_jsonl(file)
num_lines = count_file_lines(file)

batch = []
_type = "/ask"
_action = "post"
_version = "1.0.0"

mapping = json.load(open("athena-user_id-to-email.json", "r"))

def lookup_email(user_id):
    if user_id in mapping:
        return mapping[user_id]
    tqdm.write(f"Unknown user_id: {user_id}")
    return "unknown@unknown.osf"


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
                        Attribute(name="organization_name", type="string", value="osfdigital"),
                    ],
                ),
            ),
        )
        batch.append(memetrics_event.bson())
        if len(batch) == BATCH_SIZE:
            r = collection.insert_many(documents=batch)
            batch = []

if batch:
    r = collection.insert_many(documents=batch)
    batch = []
