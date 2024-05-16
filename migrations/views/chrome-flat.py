"""

"""

import os

import dotenv
from pymongo import MongoClient

dotenv.load_dotenv()


FLATTENED_MEMES_VIEW = [
    {
        "$project": {
            "created_at": 1,
            "action": "$data.action",
            "app": "$data.app",
            "app_version": "$data.app_version",
            "type": "$data.type",
            "user-email": "$data.user.email",
        }
    },
]
MEMES_MATCH = {
    "$match": {
        "data.app": "/osf/allai_chrome/OSFDigital.allai",
    }
}


def main(dry_run: bool, view_name: str):
    client = MongoClient(os.environ["MEME_MONGODB_URI"])
    db = client[os.environ["MEME_MONGODB_DBNAME"]]
    if dry_run:
        cursor = db["events"].aggregate([MEMES_MATCH, *FLATTENED_MEMES_VIEW])
        for doc in cursor:
            print(doc)
        print("Finished inspecting.")
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
    # -n athena-flat -x
    main(dry_run=not args.execute, view_name=args.name)
