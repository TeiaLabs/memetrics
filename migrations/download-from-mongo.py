"""
Download all objects from a MongoDB collection to a JSON file.

$ python script.py backup --db memetrics --col events --dir ./backup-and-restore
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

import dotenv
import tqdm
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection

dotenv.load_dotenv()
FILTERS = {
    "data.app": "/osf/allai/vscode/OSFDigital.allai",
    "$nor": [{"data.type": "completion"}, {"data.action": "accept"}]
}

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("--db", help="MongoDB database.")
    backup_parser.add_argument("--col", help="MongoDB collection.")
    backup_parser.add_argument("--dir", help="JSON directory path.", type=Path, default="./backup-and-restore")
    backup_parser.add_argument("--limit", help="Limit number of documents to download.", type=int)
    return parser.parse_args()


def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, cls=CustomJSONEncoder)


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def main(
    cmd: Literal["backup", "restore"],
    db: str,
    col: str,
    dir: Path,
    clear: bool,
    limit: int,
):
    client = MongoClient(os.environ["MONGODB_URI"])
    collection = client[db][col]
    file_path = dir / f"{db}.{col}.json"
    if cmd == "backup":
        cursor = collection.find(FILTERS)
        if limit:
            cursor = cursor.limit(limit)
            total = limit
        # else:
        #     print("Counting documents...")
        #     total = collection.count_documents(FILTERS)
        print("Downloading documents...")
        documents = [doc for doc in tqdm.tqdm(cursor)]
        print(f"Downloaded {len(documents)} documents.")
        if file_path.is_file():
            print(f"Renaming '{file_path}' to avoid overwriting it.")
            created_at = datetime.fromtimestamp(file_path.stat().st_ctime).strftime(r"%Y-%m-%d")
            file_path.rename(file_path.with_suffix(f".{created_at}.json"))
        save_json(documents, file_path)
        print(f"Saved them to {file_path}.")


if __name__ == "__main__":
    args = get_args()
    main(args.command, args.db, args.col, args.dir, getattr(args, "clear", False), getattr(args, "limit", 0))
