#%%
import json


def load_jsonl(filepath):
    events = []
    with open(filepath, 'r') as f:
        for line in f:
            events.append(json.loads(line))
    return events

data = load_jsonl("/home/jonatas/repos/memetrics/migrations/wingman_export.jsonl")
# %%
import pandas as pd
# %%

df = pd.DataFrame(data)
# %%
df.columns

# %%
#%%


print(df.event.unique())

# out
#%%
from memetrics.events.schemas import Creator, Event, EventData, User, Attribute
from memetrics_sdk.client import WebserviceClient

client = WebserviceClient()
#%%
app = "/osf/allai_code/vscode/OSFDigital.allai"

mapping = {
    "client:completion.accepted": {
        "type": "code.completion",
        "action": "accept",
    },
    "client:chat.requested": {
        "type": "chat.message",
        "action": "request",
    },
    "client:explanation.displayed": {
        "type": "code.explanation",
        "action": "display",
    },
    "client:bug_fix.requested": {
        "type": "code.bug_fix",
        "action": "request",
    },
    "client:unit_tests.displayed": {
        'type': 'code.unit_tests',
        'action': 'display',
    },
    "client:docstring.displayed": {
        "type": "code.docstring",
        "action":  "display",
    }
}
from tqdm import tqdm
from datetime import datetime

batch_size = 128
batch = []

for event in tqdm(data):
    creator = Creator(
        client_name="",
        token_name="",
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
    batch.append(memetrics_event.data)

    if len(batch) == batch_size:
        r = client.insert_many(documents=batch)
        tqdm.write(f"{r}")
        batch = []

# Insert any remaining events in the last batch
if batch:
    r = client.insert_many(documents=batch)
    tqdm.write(f"{r}")

# %%
