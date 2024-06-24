import os
from datetime import datetime
from typing import Iterable, TypeVar

import dotenv
import tqdm
from pymongo import MongoClient
from tap import Tap

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


class Args(Tap):
    batch: int = 4096
    col: str = "events"


args = Args().parse_args()
dotenv.load_dotenv()

BATCH_SIZE = args.batch
COLLECTION = args.col
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]
db_local = MongoClient()["memetrics"]
filters = {
    "created_at": {
        "$gte": datetime.fromisoformat("2024-05-01T00:00:00Z"),
        "$lt": datetime.fromisoformat("2024-06-01T00:00:00Z"),
    }
}

count = db_local[COLLECTION].count_documents(filters)
cursor = db_local[COLLECTION].find(filters)
for obj_batch in tqdm.tqdm(
    batchify_iter(cursor, BATCH_SIZE), total=count // BATCH_SIZE + 1
):
    db[COLLECTION].insert_many(obj_batch)

client.close()
