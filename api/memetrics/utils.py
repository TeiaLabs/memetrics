from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from tauth.schemas import Creator

from .settings import Settings

settings = Settings()


class DB:
    client = MongoClient(settings.MEME_MONGODB_URI)

    @classmethod
    def get(cls, db_name: Optional[str] = None, suffix: Optional[str] = None) -> Database:
        if not db_name:
            db_name = settings.MEME_MONGODB_DBNAME
        if suffix:
            db_name = f"{db_name}-{suffix}"
        return cls.client[db_name]

    @classmethod
    def get_client(cls, url: Optional[str] = None) -> MongoClient:
        if url:
            return MongoClient(url)
        return cls.client


def get_root_dir(path: str) -> Optional[str]:
    """
    Get the root folder name from a path-like string.

    >>> get_root_dir("/foo/bar/baz")
    "foo"
    """
    without_surrounding_slashes = path.strip("/")
    breadcrumbs = without_surrounding_slashes.split("/")
    root_folder = breadcrumbs[0]
    if not root_folder:
        return None
    return root_folder
