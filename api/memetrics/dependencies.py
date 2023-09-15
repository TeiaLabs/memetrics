from tauth.dependencies import security
from redb.core.instance import RedB, MongoConfig
from pymongo import IndexModel

from .settings import Settings
from .utils import DB
from .events.schemas import Event
from .events.models import EventsPerUser


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
            default_database=sets.MEME_MONGODB_DBNAME
        )
    )


def init_mongodb():
    db = DB.get()
    db["events"].create_indexes(Event.Config.indices)
    db["events_per_user"].create_indexes(EventsPerUser.Config.indices)


def init_dependencies(app):
    security.init_app(app)
    init_redb()
    init_mongodb()
