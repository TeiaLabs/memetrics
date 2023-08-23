from datetime import datetime
from typing import Any, Required, TypedDict

from bson import ObjectId
from pydantic import BaseModel, Field
from tauth.schemas import Creator


class Actor(TypedDict, total=False):
    email: Required[str]
    extra: dict[str, Any]
    ip: str


class EventData(BaseModel):
    action: str
    actor: Actor
    app: str
    extra: dict[str, Any] = Field(default_factory=dict)
    type: str


class Event(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Creator
    data: EventData
    id: str = Field(
        default_factory=lambda: str(ObjectId()), alias="_id"
    )  # TODO: don't cast to str


class GeneratedFields(BaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime
    created_by: Creator
