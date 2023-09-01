from datetime import datetime
from typing import Any, Literal, TypedDict

from bson import ObjectId
from pydantic import BaseModel, Field
from tauth.schemas import Creator


class Attribute(BaseModel):
    name: str
    type: Literal["string", "integer"] = "string"
    value: str


class User(TypedDict, total=False):
    email: str
    extra: list[Attribute]
    id: str


class EventData(BaseModel):
    action: str
    app: str
    app_version: str
    extra: dict[str, Any] = Field(default_factory=dict)
    type: str  # location in app/feature name
    user: User

    class Config:
        examples = {
            "Minimal": {
                "value": {
                    "action": "verb.specifying.what.the.user.did",
                    "app": "/org/namespace/app-name",
                    "type": "location.where.event.was.triggered.in.app",
                    "user": {"email": "user@org.com"},
                }
            },
            "VSCode wingman: request completion": {
                "value": {
                    "action": "request",
                    "app": "/osf/vscode-extension/OSFDigital.wingman",
                    "extra": {
                        "suggestion_id": "123",
                        "extension_version": "1.2.1",
                        "vscode_version": "1.2.3",
                    },
                    "type": "code.completion",
                    "user": {
                        "extra": [
                            {"name": "auth0-id", "value": "123"},
                        ],
                        "id": "123",
                    },
                },
            },
            "Chat-athena: copy code": {
                "value": {
                    "action": "copy",
                    "app": "/osf/web/chat-wingman",
                    "extra": {"message_id": "123", "user_agent": "firefox-116"},
                    "type": "chat.thread.message.code-block",
                    "user": {
                        "email": "user@org.com",
                        "extra": [
                            {"name": "azure_id", "value": "123"},
                            {"name": "ip", "value": "200.0.0.42"},
                        ],
                    },
                },
            },
        }


class Event(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Creator
    data: EventData
    id: str = Field(
        default_factory=lambda: str(ObjectId()), alias="_id"
    )  # TODO: don't cast to str
    schema_version: int = Field(default=1)


class GeneratedFields(BaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime
    created_by: Creator


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
