import os
from datetime import datetime
from typing import Iterable, TypeVar

import dotenv
import tqdm
from pymongo import MongoClient

from memetrics.events.models import EventsPerUser
from memetrics.events.schemas import Event

dotenv.load_dotenv()
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


dotenv.load_dotenv()
BATCH_SIZE = 4096
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]
# db_local = MongoClient()["nei"]
date_filter = {"$lt": datetime.fromisoformat("2023-11-10T00:00:00Z")}
filters = {"created_at": date_filter, "data.app": "/teialabs/athena/api"}
# db["events_per_user"].delete_many({"date": date_filter})

count = db["events"].count_documents(filters)
cursor = db["events"].find(filters)
batched_cursor = batchify_iter(cursor, BATCH_SIZE)
for obj_batch in tqdm.tqdm(batched_cursor, total=count // BATCH_SIZE + 1):
    obj_batch = [Event(**obj) for obj in obj_batch]
    EventsPerUser.bulk_increment_from_events(obj_batch, db)
client.close()
