from tauth.dependencies import security
from redb.core.instance import RedB, MongoConfig

from .settings import Settings


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


def init_dependencies(app):
    security.init_app(app)
    init_redb()
