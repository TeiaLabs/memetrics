import os
from typing import Iterable, TypeVar

import dotenv
import tqdm
from pymongo import MongoClient

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
BATCH_SIZE = 1024
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]
db_local = MongoClient()["egg"]
filters = {"date": {"$gte": "2024-01-01"}}
db["events_per_user"].delete_many(filters)

count = db_local["events_per_user"].count_documents(filters)
cursor = db_local["events_per_user"].find(filters)
for obj_batch in tqdm.tqdm(batchify_iter(cursor, BATCH_SIZE), total=count // BATCH_SIZE + 1):
    db["events_per_user"].insert_many(obj_batch)

client.close()
