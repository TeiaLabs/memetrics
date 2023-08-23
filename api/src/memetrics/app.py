from fastapi import FastAPI

from .events import routes as events_routes
from . import dependencies


def create_app():
    app = FastAPI()
    # never change the order of these two lines
    dependencies.init_dependencies(app)
    app.include_router(events_routes.router)
    return app
