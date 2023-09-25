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
app = "/osf/allai_code/vscode/OSFDigital.allai"


def load_jsonl(filepath):
    with open(filepath, "r") as f:
        for line in f:
            yield json.loads(line)


def count_file_lines(filepath):
    with open(filepath, "rb") as f:
        return sum(1 for _ in f)


data = load_jsonl("dump_cosmos_3_client.jsonl")
num_lines = count_file_lines("dump_cosmos_3_client.jsonl")

mapping = {
    "client:chat.requested": {
        "type": "chat",
        "action": "request",
    },
    "client:completion.displayed": {
        "type": "completion",
        "action": "display",
    },
    "client:chat.displayed": {
        "type": "chat",
        "action": "display",
    },
    "client:explanation.requested": {
        "type": "explanation",
        "action": "request",
    },
    "client:docstring.requested": {
        "type": "docstring",
        "action": "request",
    },
    "client:completion.requested": {
        "type": "completion",
        "action": "request",
    },
    "client:completion.accepted": {
        "type": "completion",
        "action": "accept",
    },
    "client:docstring.displayed": {
        "type": "docstring",
        "action": "display",
    },
    "client:unit_tests.requested": {
        "type": "unit_tests",
        "action": "request",
    },
    "client:unit_tests.displayed": {
        "type": "unit_tests",
        "action": "display",
    },
    "client:explanation.displayed": {
        "type": "explanation",
        "action": "display",
    },
    "client:bug_fix.requested": {
        "type": "bug_fix",
        "action": "request",
    },
    "client:optimization.displayed": {
        "type": "optimization",
        "action": "display",
    },
    "client:optimization.requested": {
        "type": "optimization",
        "action": "request",
    },
    "client:chat.failed": {
        "type": "chat",
        "action": "fail",
    },
    "client:optimization.failed": {
        "type": "optimization",
        "action": "fail",
    },
    "client:completion.failed": {
        "type": "completion",
        "action": "fail",
    },
}

batch = []
for event in tqdm(data, total=num_lines):
    creator = Creator(
        client_name="/teialabs",
        token_name="nei.workstation",
        user_email=event["user_email"],
    )

    type_action = mapping[event["event"]]
    event_creation_date = datetime.fromtimestamp(event["ts"])

    extra = []
    if event.get("vsc_version"):
        extra.append(
            Attribute(name="vsc_version", type="string", value=event["vsc_version"])
        )
    if event.get("string_length"):
        extra.append(
            Attribute(
                name="string_length", type="integer", value=event["string_length"]
            )
        )
    if event.get("tokens_length"):
        extra.append(
            Attribute(
                name="tokens_length", type="integer", value=event["tokens_length"]
            )
        )
    if event.get("event_id"):
        extra.append(Attribute(name="event_id", type="string", value=event["event_id"]))

    memetrics_event = Event(
        created_by=creator,
        created_at=event_creation_date,
        data=EventData(
            action=type_action["action"],
            app=app,
            app_version=event["ext_version"],
            extra=extra,
            type=type_action["type"],
            user=User(
                email=event["user_email"],
                extra=[
                    Attribute(name="user_ip", type="string", value=event["user_ip"]),
                    Attribute(name="id", type="string", value=event["user_id"]),
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
