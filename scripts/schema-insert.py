"""
"employee_id": 4043,
"user_email": "sarah.zingelmann@osf.digital",
"basic_role": "Graphic Designer",
"country": "Germany",
"date_of_joining": 1371254400000,
"department": "Fullstack Commerce DACH",
"division": "Commerce B2B",
"experience": "Senior 1",
"dateMonth": 1719792000000,
"chat": 3.0,
"chrome": 0.0,
"code": 0.0,
"jira": 0.0,
"total_events": 3.0,
"working_days": 6,
"last_day": "2024-07-08",
"logged_hours": 4.0,
"logged_days": 1.0,
"working_days_employee": 5.0,
"average daily usage": 0.6,
"status": "Inactive user"
"""

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import dotenv
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator
from pymongo import ASCENDING, DESCENDING, MongoClient
from rich import print
from tqdm import tqdm

dotenv.load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")


class EmployeeMonthlyStatus(BaseModel):
    # keys
    employee_id: int
    employee_email: EmailStr = Field(alias="user_email")
    # dates
    date_of_joining: datetime
    date_month: datetime = Field(alias="dateMonth")
    # metadata
    basic_role: str
    country: str
    department: str
    division: str
    experience: str
    # apps
    chat: int
    chrome: int
    code: int
    jira: int
    # counts
    total_events: int
    working_days: int
    last_day: str
    logged_hours: float
    logged_days: float
    working_days_employee: float
    average_daily_usage: float | None = Field(alias="average daily usage")
    # computations
    status: (
        Literal[
            "No AI Used", "Inactive user", "Casual user", "Active user", "Power user"
        ]
        | None
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("experience", mode="before")
    def check_experience(cls, value, values):
        if value == 0.0:
            return ""
        return value


indices = [
    [("upn", 1), ("date_month", -1)],
    [("date_month", -1)],
]


def read_args():
    args = argparse.ArgumentParser(
        description="Insert data from a JSONL file into MongoDB."
    )
    args.add_argument(
        "-p", "--path", type=Path, help="Path to the JSONL file to insert."
    )
    args.add_argument("--db", type=str, required=True)
    args.add_argument(
        "-X", "--execute", action="store_true", help="Execute the script."
    )
    args.add_argument("--create-indexes", action="store_true")
    return args.parse_args()


def read_jsonl(jsonl_path: Path):
    print("Reading JSONL file...")
    with open(jsonl_path, "r") as file:
        for line in file:
            yield json.loads(line)


def read_json(json_path: Path) -> list[dict]:
    with open(json_path, "r") as file:
        jsonified = json.load(file)
        print(f"Read {len(jsonified)} documents.")
        return jsonified


def insert_from_jsonl(args):
    if not args.execute:
        print("Dry run. No data will be inserted.")
    client = MongoClient(MONGODB_URI)
    db = client[args.db]
    collection = db[EmployeeMonthlyStatus.__name__]
    insertions = []
    func = read_jsonl if args.path.suffix == ".jsonl" else read_json
    for document in tqdm(func(args.path)):
        try:
            obj = EmployeeMonthlyStatus(**document)
        except ValidationError as e:
            print(f"Error: {e}")
            print(document)
            continue
        insertions.append(obj.model_dump())
    if insertions:
        collection.insert_many(insertions)
    print(f"Inserted {len(insertions)} documents.")
    client.close()


def create_indices(args):
    client = MongoClient(MONGODB_URI)
    db = client[args.db]
    collection = db[EmployeeMonthlyStatus.__name__]
    for index in indices:
        index_spec = [
            (field[0], ASCENDING if field[1] == 1 else DESCENDING) for field in index
        ]
        index_result = collection.create_index(index_spec)
        print(f"Created index: {index_result}")
    client.close()


def main():
    args = read_args()
    create_indices(args)
    insert_from_jsonl(args)


if __name__ == "__main__":
    main()
