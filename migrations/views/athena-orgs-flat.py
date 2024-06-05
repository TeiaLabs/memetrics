"""
{
    "_id": ObjectId("651ffdfea131a60f49e3aab8"),
    "created_at": datetime.datetime(2023, 3, 6, 16, 42, 35, 468000),
    "created_by": {
        "client_name": "/teialabs",
        "token_name": "nei.workstation",
        "user_email": "nurcin.ayazoglu@osf.digital",
        "user_ip": "127.0.0.1",
    },
    "data": {
        "action": "post",
        "app": "/teialabs/athena/api",
        "app_version": "1.0.0",
        "extra": [
            {
                "name": "_id",
                "type": "string",
                "value": "d78bf9492ea80f262ed1c910bf04d47d64469e0ba5fe669d138c6161b9ed0ba8",
            },
            {"name": "app_id", "type": "string", "value": "teia_chat_wingman_prod"},
            {"name": "channel_id", "type": "string", "value": "single"},
            {"name": "team_id", "type": "string", "value": "single"},
            {
                "name": "messages.id",
                "type": "string",
                "value": "640617fbbb835e6aa1a280d0",
            },
        ],
        "type": "/ask",
        "user": {
            "email": "nurcin.ayazoglu@osf.digital",
            "extra": [
                {"name": "organization_name", "type": "string", "value": "osfdigital"}
            ],
        },
    },
    "schema_version": 1,
}
# "data.user.extra.value": { $nin: ["", "psgequity", "teialabs", "teia", "osf", "OSF Digital"] }
"""

import os

import dotenv
from pymongo import MongoClient

dotenv.load_dotenv()


FLATTENED_MEMES_VIEW = [
    {
        "$set": {
            "data.extra": {
                "$filter": {
                    "input": "$data.extra",
                    "cond": {"$eq": ["$$this.name", "app_id"]},
                }
            },
        }
    },
    {"$unwind": "$data.extra"},
    {"$unwind": "$data.user.extra"},
    {
        "$project": {
            "created_at": 1,
            "action": "$data.action",
            "app": "$data.app",
            "app_version": "$data.app_version",
            "extra-name": "$data.extra.name",
            "extra-type": "$data.extra.type",
            "extra-value": "$data.extra.value",
            "organization_name": "$data.user.extra.value",
            "type": "$data.type",
            "user-email": "$data.user.email",
        }
    },
]
MEMES_MATCH = {
    "$match": {
        "data.app": "/teialabs/athena/api",
    }
}


def main(dry_run: bool, view_name: str, delete: bool):
    client = MongoClient(os.environ["MEME_MONGODB_URI"])
    db = client[os.environ["MEME_MONGODB_DBNAME"]]
    if dry_run:
        cursor = db["events"].aggregate([MEMES_MATCH, *FLATTENED_MEMES_VIEW])
        for doc in cursor:
            print(doc)
        print("Finished inspecting.")
    else:
        if delete:
            print(db.drop_collection(view_name))
        res = db.create_collection(
            view_name,
            viewOn="events",
            pipeline=[MEMES_MATCH, *FLATTENED_MEMES_VIEW],
        )
        print(res)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--execute", action="store_true")
    parser.add_argument("-d", "--delete", action="store_true")
    parser.add_argument("-n", "--name")
    args = parser.parse_args()
    main(dry_run=not args.execute, view_name=args.name, delete=args.delete)
