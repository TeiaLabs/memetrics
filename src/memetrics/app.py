from fastapi import FastAPI

from .events import routes as events_routes
from . import dependencies

def create_app():
    app = FastAPI()
    app.include_router(events_routes.router)
    dependencies.init_dependencies(app)
    return app
