from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

from .settings import Settings

settings = Settings()


class DB:
    client = MongoClient(settings.MEME_MONGODB_URI)

    @classmethod
    def get(cls, db_name: Optional[str] = None) -> Database:
        if db_name:
            return cls.client[db_name]
        return cls.client[settings.MEME_MONGODB_DBNAME]

    @classmethod
    def get_client(cls, url: Optional[str] = None) -> MongoClient:
        if url:
            return MongoClient(url)
        return cls.client


def create_timeseries_collection(db_name: str, collection_name: str):
    DB.get(db_name).create_collection(
        collection_name,
        timeseries={
            "timeField": "created_at",
            "metaField": "data",
            "granularity": "seconds",
        },
    )
