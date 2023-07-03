from fastapi import FastAPI

from .events import routes as events_routes

def create_app():
    app = FastAPI()
    return app
