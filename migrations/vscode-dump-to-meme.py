"""
'upn', 'vsc_version', 'ext_version', 'create_at', 'eventType', 'eventUuid', 'languageId', 'completionLength', 'completionTokensCount', 'source'
mihaela.andonoaei@osf.digital, 1.80.0, 2.1.0, 2023-07-24 09:09:03, wingman_chat.sent, 7c724402-04ec-4be1-9eca-84dacafdf8db, javascript, 0, 0, Cosmos 1

->

{
    "created_at": {"$date": "2023-09-27T17:07:07.533Z"},
    "created_by": {
      "client_name": "/osf/wingman",
      "token_name": "auth0-jwt",
      "user_email": "glenda.paiva@osf.digital",
      "user_ip": "177.37.249.228"
    },
    "data": {
      "action": "request",
      "app": "/osf/allai/vscode/OSFDigital.allai",
      "app_version": "2.4.0",
      "extra": [
        {"name": "event_id", "value": "56221b8e-4be4-4553-b5ed-d711d68e08dc"},
        {"name": "context", "value": "DEFAULT"},
        {"name": "language", "value": "javascript"},
        {"name": "vscode_version", "value": "1.82.2"}
      ],
      "type": "bug_fix",
      "user": {
        "email": "glenda.paiva@osf.digital",
        "extra": [
          {"name": "ip_address", "value": "177.37.249.228"}
        ]
      }
    },
  }

"""

import math
import os
from datetime import datetime
from typing import Iterable, TypeVar

import dotenv
import pandas as pd
from pymongo import MongoClient
from rich import print
from tqdm import tqdm

from memetrics.events.schemas import Attribute, Creator, Event, EventData, User

APP = "/osf/allai/vscode/OSFDigital.allai"
dotenv.load_dotenv()
BATCH_SIZE = 4096
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]

T = TypeVar("T")


def batchify_iter(
    it: Iterable[T],
    batch_size: int,
) -> Iterable[list[T]]:
    batch = []
    for item in it:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def assemble_event(row) -> Event:
    creator = Creator(
        client_name="/teialabs",
        token_name="nei.workstation",
        user_email=row["upn"],
    )
    _type, _action = row["eventType"].split(".")
    if _action.endswith("ed"):
        _action = _action[:-2]
    elif _action == "sent":
        _action = "request"
    if _type == "wingman_chat":
        _type = "chat"
    extra = [
        {
            "name": "prompt_tokens_count",
            "type": "integer",
            "value": (
                -1
                if math.isnan(row["promptTokensCount"])
                else int(row["promptTokensCount"])
            ),
        },
        {
            "name": "suffix_tokens_count",
            "type": "integer",
            "value": (
                -1
                if math.isnan(row["suffixTokensCount"])
                else int(row["suffixTokensCount"])
            ),
        },
        {
            "name": "time_to_generate",
            "type": "integer",
            "value": (
                -1 if math.isnan(row["timeToGenerate"]) else int(row["timeToGenerate"])
            ),
        },
        {
            "name": "event_id",
            "type": "string",
            "value": row["eventUuid"],
        },
        {
            "name": "language",
            "type": "string",
            "value": row["languageId"],
        },
        {
            "name": "vscode_version",
            "type": "string",
            "value": row["vsc_version"],
        },
        {
            "name": "source",
            "type": "string",
            "value": row["source"],
        },
        {
            "name": "completion_length",
            "type": "integer",
            "value": int(row["completionLength"]),
        },
        {
            "name": "completion_tokens_count",
            "type": "integer",
            "value": int(row["completionTokensCount"]),
        },
        {
            "name": "suggestion_length",
            "type": "integer",
            "value": (
                -1
                if math.isnan(row["suggestionLength"])
                else int(row["suggestionLength"])
            ),
        },
    ]
    # remove -1 values
    extra = [e for e in extra if e["value"] != -1]
    data = EventData(
        action=_action,
        app=APP,
        app_version=row["ext_version"],
        extra=extra,  # type: ignore
        type=_type,
        user=User(email=row["upn"]),
    )
    created_at = datetime.fromisoformat(row["create_at"])
    event = Event(
        created_by=creator,  # type: ignore
        created_at=created_at,
        data=data,
        schema_version=0,
    )
    return event


def main():
    df = pd.read_csv("../reports/2024.06.19_code-legacy.csv", sep=";")
    df["create_at"] = pd.to_datetime(df["create_at"]).dt.strftime(
        r"%Y-%m-%dT%H:%M:%S.%fZ"
    )
    events = [
        assemble_event(row).bson() for _, row in tqdm(df.iterrows(), total=len(df))
    ]
    for obj_batch in tqdm(
        batchify_iter(events, BATCH_SIZE), total=len(events) // BATCH_SIZE + 1
    ):
        tqdm.write(str(len(db["events"].insert_many(obj_batch).inserted_ids)))


main()
