from typing import Any, Self

from bson import ObjectId
from fastapi import Depends, FastAPI, Header, Request
from pydantic import BaseModel
from tauth.schemas import Creator

from .schemas import Actor, Event, EventData


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

    def into_event(
        self,
        action: str,
        type: str,
        extra: dict[str, Any] | None = None,
        actor: Actor | None = None,
    ) -> Event:
        event_data = self.into_event_data(
            action=action, actor=actor, extra=extra, type=type
        )

        return Event(
            created_by=self.creator,
            data=event_data,
            _id=self.id,
            parent_id=self.parent_id,
        )

    def into_event_data(
        self,
        action: str,
        type: str,
        extra: dict[str, Any] | None = None,
        actor: Actor | None = None,
    ) -> EventData:
        if actor is None:
            actor = Actor(
                email=self.creator.user_email,
                ip=self.creator.user_ip,
                extra={
                    "origin": "created from tauth creator",
                    "token_name": self.creator.token_name,
                    "client_name": self.creator.client_name,
                },
            )

        if extra is None:
            extra = {}

        return EventData(
            action=action,
            actor=actor,
            app=self.app,
            extra=extra,
            type=type,
        )


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
