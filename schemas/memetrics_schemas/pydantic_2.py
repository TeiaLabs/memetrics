from datetime import datetime
from typing import Any, Literal

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from .object_id import PyObjectId
from .pydantic_n import Attribute, Creator, User


class PartialAttribute(BaseModel):
    type: Literal["string", "integer", "float", "dict", "list"]
    value: str | int | float | dict | list

    model_config = ConfigDict(
        json_schema_extra={
            "examples": {
                "string": {"value": {"type": "string", "value": "some string"}},
                "integer": {"value": {"type": "integer", "value": 42}},
                "float": {"value": {"type": "float", "value": 42.0}},
                "dict": {"value": {"type": "dict", "value": {"key": "value"}}},
                "list": {"value": {"type": "list", "value": ["item"]}},
            }
        }
    )


class EventData(BaseModel):
    action: str
    app: str
    app_version: str
    extra: list[Attribute] = Field(default_factory=list)
    type: str  # location in app/feature name
    user: User = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": {
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
                            {
                                "name": "vscode-version",
                                "type": "string",
                                "value": "1.2.3",
                            },
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
                            {
                                "name": "user-agent",
                                "type": "string",
                                "value": "firefox-116",
                            },
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
        }
    )


class Event(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Creator
    data: EventData
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    schema_version: int = Field(default=1)

    @field_validator("id")
    @classmethod
    def id_must_by_objectid(cls, v, _):
        """Make sure _id is instance of PyObjectId."""
        if isinstance(v, str):
            return PyObjectId(v)
        return v

    @field_serializer("id", when_used="json")
    def serialize_id(self, value: PyObjectId) -> str:
        return {"$oid": str(value)}

    def bson(self) -> dict[str, Any]:
        obj = self.model_dump(by_alias=True)
        obj["_id"] = ObjectId(obj["_id"])
        return obj

    model_config = ConfigDict(populate_by_name=True)


class GeneratedFields(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime
    created_by: Creator

    @field_serializer("id", when_used="json")
    def serialize_id(self, value: PyObjectId) -> str:
        return str(value)

    model_config = ConfigDict(frozen=True)


class PatchEventData(BaseModel):
    op: Literal["add"]
    value: EventData

    model_config = ConfigDict(
        json_schema_extra={
            "examples": {
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
        }
    )
