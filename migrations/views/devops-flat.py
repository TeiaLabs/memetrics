"""

"""

import os
from pathlib import Path

import dotenv
from pymongo import MongoClient
from rich import print

dotenv.load_dotenv()


FLATTENED_MEMES_VIEW = [
    {
        "$addFields": {
            "data.extra": {
                "$arrayToObject": {
                    "$map": {
                        "input": "$data.extra",
                        "as": "item",
                        "in": {"k": "$$item.name", "v": "$$item.value"},
                    }
                }
            },
            "data.user.extra": {
                "$arrayToObject": {
                    "$map": {
                        "input": "$data.user.extra",
                        "as": "item",
                        "in": {"k": "$$item.name", "v": "$$item.value"},
                    }
                }
            },
        }
    },
    {
        "$project": {
            "action": "$data.action",
            "app_version": "$data.app_version",
            "app": "$data.app",
            "created_at": 1,
            "extra_created-at": "empty",
            "extra_issue-number": "$data.extra.issue_number",
            "extra_repo-name": "$data.extra.repo_name",
            "extra_repo-owner": "$data.extra.repo_owner",
            "extra_user-login": "$data.user.extra.user_login",
            "type": "$data.type",
            "user-email": "$data.user.email",
        }
    },
]
MEMES_MATCH = {
    "$match": {
        "data.app": {
            "$in": [
                # "/teialabs/devopsai/gitlab",
                # "/teialabs/devopsai/bitbucket",
                # "/teia/devopsai/github",
                "/teialabs/devopsai/github",
            ]
        },
    }
}


def main(dry_run: bool, view_name: str, delete: bool, limit: int):
    client = MongoClient(os.environ["MEME_MONGODB_URI"])
    db = client[os.environ["MEME_MONGODB_DBNAME"]]
    if dry_run:
        cursor = db["events"].aggregate([MEMES_MATCH, *FLATTENED_MEMES_VIEW])
        try:
            for i, doc in zip(range(limit), cursor):
                print(i)
                print(doc)
        except KeyboardInterrupt:
            pass
    else:
        if delete:
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
    parser.add_argument("-l", "--limit", type=int, default=1)
    parser.add_argument("-d", "--delete", action="store_true")
    parser.add_argument("-n", "--name")
    args = parser.parse_args()
    if not args.name:
        args.name = Path(__file__).stem
    main(
        dry_run=not args.execute,
        view_name=args.name,
        delete=args.delete,
        limit=args.limit,
    )
