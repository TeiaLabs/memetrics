"""
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

import json
import os
from datetime import datetime
from typing import Iterable, TypeVar

import dotenv
from pymongo import MongoClient
from rich import print
from tqdm import tqdm

from memetrics.events.schemas import (
    Attribute,
    Creator,
    Event,
    EventData,
    PyObjectId,
    User,
)

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


def read_json(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def main():
    objs = read_json("../reports/2024.06.17_memetrics-events.json")
    objs = [
        item
        for item in tqdm(objs)
        if datetime.fromisoformat(item["created_at"]) >= datetime(2023, 10, 1)
        and datetime.fromisoformat(item["created_at"]) < datetime(2023, 12, 1)
    ]
    events = []
    for obj_batch in tqdm(
        batchify_iter(objs, BATCH_SIZE), total=len(objs) // BATCH_SIZE + 1
    ):
        ids = db["events"].find(
            {"_id": {"$in": [PyObjectId(item["_id"]) for item in obj_batch]}},
            {"_id": 1},
        )
        id_set = {str(item["_id"]) for item in ids}
        events.extend(Event(**item) for item in obj_batch if item["_id"] not in id_set)
    for obj_batch in tqdm(
        batchify_iter(events, BATCH_SIZE), total=len(events) // BATCH_SIZE + 1
    ):
        result = db.events.insert_many([obj.bson() for obj in obj_batch])
        tqdm.write(f"Inserted {len(result.inserted_ids)} @ {datetime.now()}")


main()
