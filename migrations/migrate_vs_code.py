#%%
import json
from typing import Type
import pandas as pd
from badger_api import Settings
from redb.core.base import BaseDocument
from redb.core.instance import RedB, MongoConfig

from memetrics.events.schemas import Creator, Event, EventData, User, Attribute
from memetrics_sdk.client import WebserviceClient

from redb.core import Document

RedB.setup(
    backend="mongo",
    config=MongoConfig(
    # database_uri=None, # SET this !!
    default_database="memetrics-dev"
))


def load_jsonl(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield json.loads(line)

data = load_jsonl("/home/jonatas/repos/memetrics/migrations/dump_cosmos_2_client.jsonl")

# out
#%%

# client = WebserviceClient()
#%%
app = "/osf/allai_code/vscode/OSFDigital.allai"

"""
['client:chat.requested'
 'client:completion.displayed'
 'client:chat.displayed'
 'client:explanation.requested'
 'client:docstring.requested'
 'client:completion.requested'
 'client:completion.accepted'
 'client:docstring.displayed'
 'client:unit_tests.requested'
 'client:unit_tests.displayed'
 'client:explanation.displayed'
 'client:bug_fix.requested'
 'client:optimization.displayed'
 'client:optimization.requested'
 'client:chat.failed'
 'client:optimization.failed'
 'client:completion.failed']
"""

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

#%%

from tqdm import tqdm
from datetime import datetime

class EventsDAO(Document, Event):
    @classmethod
    def collection_name(cls: type[BaseDocument]) -> str:
        return "events"

client = EventsDAO._get_driver_collection(EventsDAO)

batch_size = 2048
batch = []

for event in tqdm(data):

    creator = Creator(
        client_name='/teialabs/melt',
        token_name="jonatas.workstation",
        user_email=event["user_email"],
    )

    type_action = mapping[event["event"]]
    event_creation_date = datetime.fromtimestamp(event["ts"])

    extra = []
    if event.get("vsc_version"):
        extra.append(Attribute(name="vsc_version", type="string", value=event["vsc_version"]))
    if event.get("string_length"):
        extra.append(Attribute(name="string_length", type="integer", value=event["string_length"]))
    if event.get("tokens_length"):
        extra.append(Attribute(name="tokens_length", type="integer", value=event["tokens_length"]))
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
                # ip=event["user_ip"],
                extra=[
                    Attribute(name="user_ip", type="string", value=event["user_ip"]),
                    Attribute(name="id", type="string", value=event["user_id"])
                ]
            ),
        )
    )
    batch.append(memetrics_event.bson())

    if len(batch) == batch_size:

        r = client.insert_many(documents=batch)
        tqdm.write(f"{r}")
        batch = []

# Insert any remaining events in the last batch
if batch:
    r = client.insert_many(documents=batch)
    tqdm.write(f"{r}")

# %%
