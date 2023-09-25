"""
Compare concrete aggregation with real-time aggregation.

In the collection "events" we have documents such as this:
{
  "_id": {"$oid": "6510fefb30f289bbc50c34db"},
  "created_at": {"$date": "2023-09-22T10:14:09Z"},
  "data": {
    "action": "request",
    "app": "/osf/allai_code/vscode/OSFDigital.allai",
    "type": "chat",
    "user": {"email": "user.name@osf.digital"}
  },
}

In "events_per_user" we have a trigger to aggregate the above into this:
{
  "_id": {"$oid": "6511008c81ec376e593583d0"},
  "action": "request",
  "app": "/osf/allai_code/vscode/OSFDigital.allai",
  "date": {"$date": "2023-09-22T00:00:00Z"},
  "type": "chat",
  "user_email": "user.name@osf.digital",
  "count": 22,
  "events": [
    {
      "event_id": {"$oid": "6510fefb30f289bbc50c34db"},
      "event_creation": {"$date": "2023-09-22T10:14:09Z"}
    },
    ...x22
}

The script will use a mongo aggregation to compare the number
of events in the "events" collection with the events_per_user.count.
"""
import os
from datetime import datetime

import dotenv
from pymongo import MongoClient
from tqdm import tqdm

dotenv.load_dotenv()
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]

pipeline = [
    {
        "$match": {
            "created_at": {
                "$gte": datetime.fromisoformat("2023-09-15"),
            },
        },
    },
    {
        "$group": {
            "_id": {
                "action": "$data.action",
                "app": "$data.app",
                "type": "$data.type",
                "user_email":"$data.user.email",
                "date": {
                    "$dateTrunc": {
                        "date": "$created_at",
                        "unit": "day",
                    },
                },
            },
            "count": {"$sum": 1},
        }
    },
    {"$sort": {"created_at": 1}},
]
agg = db["events"].aggregate(pipeline)
num_docs_in_agg = db["events"].aggregate(pipeline + [{"$count": "total"}]).next()["total"]
for doc in tqdm(agg, total=num_docs_in_agg):
    egg = db["events_per_user"].find_one({
        "action": doc["_id"]["action"],
        "app": doc["_id"]["app"],
        "type": doc["_id"]["type"],
        "user_email": doc["_id"]["user_email"],
        "date": doc["_id"]["date"],
    })
    if not egg:
        print("No egg for", doc)
        continue
    tqdm.write(str(egg["date"]))
    if egg["count"] != doc["count"]:
        print("Mismatch:", doc["count"], egg["count"], doc["_id"])
