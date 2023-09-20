from datetime import datetime
from typing import Any, Literal, TypedDict

from bson import ObjectId
from pydantic import BaseModel, Field, validator
from pymongo import IndexModel
from tauth.schemas import Creator

from ..utils import PyObjectId


class Attribute(BaseModel):
    name: str
    type: Literal["string", "integer", "float", "dict", "list"]
    value: str | int | float | dict | list


class User(TypedDict, total=False):
    email: str
    extra: list[Attribute]
    id: str


class EventData(BaseModel):
    action: str
    app: str
    app_version: str
    extra: list[Attribute] = Field(default_factory=list)
    type: str  # location in app/feature name
    user: User = Field(default_factory=dict)

    class Config:
        examples = {
            "Minimal": {
                "value": {
                    "action": "verb.specifying.what.the.user.did",
                    "app": "/org/namespace/app-name",
                    "app_version": "1.2.3",
                    "type": "location.where.event.was.triggered.in.app",
                    "user": {"email": "user@org.com"},
                }
            },
            "VSCode wingman: request completion": {
                "value": {
                    "action": "request",
                    "app": "/osf/allai/vscode/OSFDigital.wingman",
                    "app_version": "1.2.3",
                    "extra": [
                        {"name": "completion-id", "type": "string", "value": "123"},
                        {"name": "vscode-version", "type": "string", "value": "1.2.3"},
                    ],
                    "type": "code.completion",
                },
                "user": {"extra": [{"name": "ip", "value": "200.0.0.42"}]},
            },
            "Chat-athena: copy code": {
                "value": {
                    "action": "copy",
                    "app": "/osf/web/chat-wingman",
                    "app_version": "1.2.3",
                    "extra": [
                        {"name": "message-id", "type": "string", "value": "123"},
                        {"name": "user-agent", "type": "string", "value": "firefox-116"},
                    ],
                    "type": "chat.thread.message.code-block",
                    "user": {
                        "email": "user@org.com",
                        "extra": [
                            {"name": "azure_id", "type": "string", "value": "123"},
                            {"name": "ip", "type": "string", "value": "200.0.0.42"},
                        ],
                    },
                },
            },
        }


class Event(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Creator
    data: EventData
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    schema_version: int = Field(default=1)

    @validator("id", always=True)
    def id_must_by_objectid(cls, v):
        """Make sure _id is instance of PyObjectId."""
        if isinstance(v, str):
            return PyObjectId(v)
        return v

    def bson(self) -> dict[str, Any]:
        obj = self.dict(by_alias=True)
        obj["_id"] = ObjectId(obj["_id"])
        return obj

    class Config:
        allow_population_by_field_name = True
        json_encoders = {PyObjectId: lambda x: {"$oid": str(x)}}
        indices = [
            IndexModel([("created_at", -1)]),
            IndexModel([("data.type", 1)]),
            IndexModel([("data.app", 1), ("data.type", 1), ("data.action", 1)]),
        ]


class GeneratedFields(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime
    created_by: Creator

    class Config:
        allow_mutation = False
        json_encoders = {PyObjectId: str}


class PatchEventData(BaseModel):
    op: Literal["add"]
    value: EventData

    class Config:
        examples = {
            "Add a single resource.": {
                "value": [
                    [
                        {
                            "op": "add",
                            "value": {
                                "action": "verb.specifying.what.the.user.did",
                                "app": "/org/namespace/app-name",
                                "type": "location.where.event.was.triggered.in.app",
                                "user": {"email": "user@org.com"},
                            },
                        },
                    ]
                ]
            }
        }
