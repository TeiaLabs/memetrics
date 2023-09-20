import os

import dotenv
import tqdm
from pymongo import MongoClient

from memetrics.events.models import EventsPerUser
from memetrics.events.schemas import Event

dotenv.load_dotenv()
BATCH_SIZE = 512
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]
db_local = MongoClient()["egg"]
obj_batch = []
filters = {}
db["events_per_user"].delete_many(filters)
count = db_local["events_per_user"].count_documents(filters)
for obj in tqdm.tqdm(db_local["events_per_user"].find(filters).batch_size(BATCH_SIZE), total=count):
    obj_batch.append(obj)
    tqdm.tqdm.write(obj["user_email"])
    if len(obj_batch) == BATCH_SIZE:
        tqdm.tqdm.write(repr(db["events_per_user"].insert_many(obj_batch)))
        obj_batch = []
if obj_batch:
    tqdm.tqdm.write(repr(db["events_per_user"].insert_many(obj_batch)))
    obj_batch = []
