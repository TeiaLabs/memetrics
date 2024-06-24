import os
from datetime import datetime

import dotenv
from pymongo import MongoClient
from rich import print

dotenv.load_dotenv()
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db = client[os.environ["MEME_MONGODB_DBNAME"]]

filters = {
    "created_at": {
        "$gte": datetime.fromisoformat("2024-05-01T00:00:00Z"),
        "$lt": datetime.fromisoformat("2024-06-01T00:00:00Z"),
    },
    # "created_by.token_name": "athena.prod",
    "data.app": "/teialabs/athena/api",
    "data.action": "post",
    "data.type": "/ask",
    "data.user.extra": {
        "$elemMatch": {
            "name": "organization_name",
            "value": {"$in": ["osf", "OSF Digital", "osfdigital"]},
        }
    },
}
collection = db["events"]
print(f"Deleting {collection.count_documents(filters)} events.")
input("Press Enter to continue: ")
print(collection.delete_many(filters))

# filters = {
#     "date": {"$lt": datetime.fromisoformat("2024-02-01T00:00:00Z")},
#     "app": "/teialabs/athena/api",
# }
# collection = db["events_per_user"]
# print(f"Deleting {collection.count_documents(filters)} events_per_user.")
# print(collection.delete_many(filters))
