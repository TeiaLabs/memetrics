from typing import Self

from bson import ObjectId
from fastapi import Depends, FastAPI, Header, Request
from pydantic import BaseModel
from tauth.schemas import Creator


class PreBuiltEvent(BaseModel):
    app: str
    creator: Creator
    id: str
    parent_id: str | None

    def get_child(self) -> Self:
        return PreBuiltEvent(
            app=self.app,
            creator=self.creator,
            id=str(ObjectId()),
            parent_id=self.id,
        )

    def as_header(self) -> dict[str, str]:
        return {"X-Event-ID": self.id}


def event_handler(app: FastAPI, app_name: str) -> None:
    app.router.dependencies.append(Depends(event_builder(app_name)))


def event_builder(app_name: str):
    def get_event(
        request: Request,
        event_id: str | None = Header(None, alias="X-Event-ID"),
    ):
        return PreBuiltEvent(
            app=app_name,
            creator=request.state.creator,
            id=str(ObjectId()),
            parent_id=event_id,
        )

    return get_event
