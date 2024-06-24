"""
    {
  "_id": {
    "$oid": "65118cb4cd998199e67f79b0"
  },
  "created_at": {
    "$date": "2023-09-25T13:35:48.362Z"
  },
  "created_by": {
    "client_name": "/osf/wingman",
    "token_name": "auth0-jwt",
    "user_email": "olha.vatamaniuk@osf.digital",
    "user_ip": "109.229.29.158"
  },
  "data": {
    "action": "request",
    "app": "/osf/allai/vscode/OSFDigital.allai",
    "app_version": "2.3.1",
    "extra": [
      {
        "name": "event_id",
        "type": "string",
        "value": "ae2a835f-344a-4c55-b320-60c05550893e"
      },
      {
        "name": "context",
        "type": "string",
        "value": "DEFAULT"
      },
      {
        "name": "language",
        "type": "string",
        "value": "javascript"
      },
      {
        "name": "vscode_version",
        "type": "string",
        "value": "1.82.2"
      }
    ],
    "type": "unit_tests",
    "user": {
      "email": "olha.vatamaniuk@osf.digital",
      "extra": [
        {
          "name": "ip_address",
          "type": "string",
          "value": "109.229.29.158"
        }
      ]
    }
  },
  "schema_version": 1
}
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
                    "cond": {"$eq": ["$$this.name", "vscode_version"]},
                }
            },
        }
    },
    {"$unwind": "$data.extra"},
    {
        "$project": {
            "created_at": 1,
            "action": "$data.action",
            "app": "$data.app",
            "app_version": "$data.app_version",
            "extra-name": "$data.extra.name",
            "extra-type": "$data.extra.type",
            "extra-value": "$data.extra.value",
            "type": "$data.type",
            "user-email": "$data.user.email",
        }
    },
]
MEMES_MATCH = {
    "$match": {
        "data.app": {
            "$in": [
                "/osf/allai/vscode/OSFDigital.allai",
                "/osf/allai_code/vscode/OSFDigital.allai",
            ]
        },
        "$nor": [
            {"data.type": "completion", "data.action": "request"},
            {"data.type": "completion", "data.action": "display"},
            {"data.type": "chat", "data.action": "request"},
            {"data.type": "chat", "data.action": "fail"},
            {"data.type": "docstring", "data.action": "request"},
            {"data.type": "explanation", "data.action": "request"},
            {"data.type": "unit_tests", "data.action": "request"},
        ],
    }
}


def main(dry_run: bool, view_name: str):
    client = MongoClient(os.environ["MEME_MONGODB_URI"])
    db = client[os.environ["MEME_MONGODB_DBNAME"]]
    if dry_run:
        cursor = db["events"].aggregate([MEMES_MATCH, *FLATTENED_MEMES_VIEW])
        for doc in cursor:
            print(doc)
    else:
        db.drop_collection(view_name)
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
    parser.add_argument("-n", "--name")
    args = parser.parse_args()
    main(dry_run=not args.execute, view_name=args.name)
