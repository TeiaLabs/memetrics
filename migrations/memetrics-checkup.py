import os

import dotenv
from pymongo import MongoClient
from rich import print

dotenv.load_dotenv()
client = MongoClient(os.environ["MEME_MONGODB_URI"])
db_meme = client[os.environ["MEME_MONGODB_DBNAME"]]
client = MongoClient(os.environ["ATHENA_MONGODB_URI"])
db_athena = client[os.environ["ATHENA_MONGODB_DBNAME"]]

AGG_MEME = [
    {
        "$match": {
            "data.app": "/teialabs/athena/api",
            "data.type": "/ask",
            "data.action": "post",
            # "created_by.user_email": {"$ne": "user@teialabs.com"},
            "created_by.user_email": "yulia.stefanets@osf.digital",
        }
    },
    {
        "$addFields": {
            "month": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}}
        }
    },
    # {
    #     "$match": {
    #         "month": "2024-05",
    #     }
    # },
    {
        "$group": {
            "_id": {
                "email": "$created_by.user_email",
                "month": "$month",
                "organization_name": {
                    "$arrayElemAt": [
                        {
                            "$filter": {
                                "input": "$data.user.extra",
                                "as": "extra",
                                "cond": {"$eq": ["$$extra.name", "organization_name"]},
                            }
                        },
                        0,
                    ]
                },
            },
            "num_messages": {"$sum": 1},
        }
    },
    {
        "$project": {
            "_id": 0,
            "email": "$_id.email",
            "date": "$_id.month",
            "num_messages": "$num_messages",
            "organization_name": "$_id.organization_name.value",
        }
    },
    {"$match": {"organization_name": "osf"}},
    {"$sort": {"date": 1}},
]


AGG_ATHENA = [
    {
        "$lookup": {
            "from": "user",
            "localField": "creator_id",
            "foreignField": "_id",
            "as": "thread_users",
        }
    },
    {"$unwind": "$thread_users"},
    {
        "$match": {
            # "thread_users.email": {"$not": {"$eq": "user@teialabs.com"}},
            "thread_users.email": "yulia.stefanets@osf.digital",
        }
    },
    {"$unwind": "$messages"},
    {
        "$match": {
            "messages.type": "query",
            # "messages.created_at": {
            #     "$gte": "2024-05-01",
            #     "$lt": "2024-06-01",
            # },
        }
    },
    {
        "$group": {
            "_id": {
                "user_id": "$thread_users._id",
                "date": {
                    "$dateToString": {
                        "format": "%Y-%m",
                        "date": {"$toDate": "$messages.created_at"},
                    }
                },
            },
            "creator_email": {"$first": "$thread_users.email"},
            "number_of_messages": {"$sum": 1},
        }
    },
    {"$sort": {"date": 1}},
    {
        "$project": {
            "_id": 0,
            "email": "$creator_email",
            "date": "$_id.date",
            "num_messages": "$number_of_messages",
            "organization_name": "osf",
        }
    },
]

print("Fetching data...")
meme_cursor = db_meme["events"].aggregate(AGG_MEME)
athena_cursor = db_athena["thread"].aggregate(AGG_ATHENA)

# obj example  {
#     "email": "yan.braga@osf.digital",
#     "date": "2024-05",
#     "num_messages": 429,
#     "organization_name": "osf"
#   }

# assemble a dict with the email and date tuple as key
meme_dict = {}
for obj in meme_cursor:
    meme_dict[(obj["email"], obj["date"])] = obj["num_messages"]
athena_dict = {}
for obj in athena_cursor:
    athena_dict[(obj["email"], obj["date"])] = obj["num_messages"]

# print the two dicts
for key in meme_dict:
    print(key, meme_dict[key], athena_dict[key])
