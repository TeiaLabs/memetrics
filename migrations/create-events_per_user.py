import os
from datetime import datetime

import dotenv
import tqdm
from pymongo import MongoClient

from memetrics.events.models import EventsPerUser
from memetrics.events.schemas import Event

dotenv.load_dotenv()
BATCH_SIZE = 4096
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]
db_local = MongoClient()["egg"]
obj_batch = []
filters = {"created_at": {"$gte": datetime.fromisoformat("2024-07-01")}}
count = db["events"].count_documents(filters)
for obj in tqdm.tqdm(db["events"].find(filters).batch_size(BATCH_SIZE), total=count):
    obj_batch.append(obj)
    if len(obj_batch) == BATCH_SIZE:
        obj_batch = [Event(**obj) for obj in obj_batch]
        EventsPerUser.bulk_increment_from_events(obj_batch, db_local)
        obj_batch = []
if obj_batch:
    obj_batch = [Event(**obj) for obj in obj_batch]
    EventsPerUser.bulk_increment_from_events(obj_batch, db_local)
    obj_batch = []
client.close()
