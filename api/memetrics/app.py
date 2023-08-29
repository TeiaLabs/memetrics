from fastapi import FastAPI

from . import dependencies
from .events import routes as events_routes


def create_app():
    app = FastAPI()
    # never change the order of these two lines
    dependencies.init_dependencies(app)
    app.include_router(events_routes.router)

    @app.get("/", status_code=200)
    def _():
        return {"status": "ok"}

    return app
