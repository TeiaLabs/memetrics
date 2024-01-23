from fastapi import FastAPI
from memetrics_schemas import Event
from redb.core.instance import MongoConfig, RedB
from starlette.middleware.cors import CORSMiddleware
from tauth.dependencies import security

from .events.models import EventsPerUser
from .settings import Settings
from .utils import DB


def init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_redb():
    """
    Initialize REDB because TAUTH needs it.

    TODO: get rid of this dependency.
    """
    sets = Settings()
    RedB.setup(
        backend="mongo",
        config=MongoConfig(
            database_uri=sets.MEME_MONGODB_URI,
            default_database=sets.MEME_MONGODB_DBNAME,
        ),
    )


def init_mongodb():
    db = DB.get()
    db["events"].create_indexes(Event.Config.indices)
    db["events_per_user"].create_indexes(EventsPerUser.Config.indices)


def init_dependencies(app):
    security.init_app(app)
    init_cors(app)
    init_redb()
    # init_mongodb()
