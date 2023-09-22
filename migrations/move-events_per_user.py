import os

import dotenv
import tqdm
from pymongo import MongoClient

from memetrics.events.models import EventsPerUser
from memetrics.events.schemas import Event

dotenv.load_dotenv()
BATCH_SIZE = 1024
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]
db_local = MongoClient()["egg"]
obj_batch = []
filters = {"date": {"$gte": "2024-01-01"}}
db["events_per_user"].delete_many(filters)
count = db_local["events_per_user"].count_documents(filters)
for obj in tqdm.tqdm(db_local["events_per_user"].find(filters).batch_size(BATCH_SIZE), total=count):
    obj_batch.append(obj)
    if len(obj_batch) == BATCH_SIZE:
        db["events_per_user"].insert_many(obj_batch)
        obj_batch = []
if obj_batch:
    db["events_per_user"].insert_many(obj_batch)
    obj_batch = []
