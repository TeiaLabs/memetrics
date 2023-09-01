from fastapi import APIRouter, BackgroundTasks, Body, Request
from fastapi import status as s

from . import controllers
from .schemas import EventData, GeneratedFields, PatchEventData

router = APIRouter()
examples = [
    {
        "action": "request",
        "app": "/osf/vscode/extension/OSFDigital.wingman",
        "extra": {
            "suggestion_id": "123",
            "extension_version": "1.2.1",
            "vscode_version": "1.2.3",
        },
        "type": "code.completion",
        "user": {
            "id": {
                "name": "email",
                "value": "user@org.com"
            },
            "extra": [
                {
                    "name": "auth0-id",
                    "value": "123",
                },
            ],
        },
    },
    {
        "action": "copy",
        "app": "/osf/web/chat-wingman",
        "extra": {"message_id": "123", "user_agent": "firefox-116"},
        "type": "chat.thread.message.code-block",
        "user": {
            "email": "user@org.com",
            "ip": "200.0.0.42",
            "extra": {"azure_id": "123"},
        },
    },
]

patch_examples = [
    [
        {
            "op": "add",
            "value": {
                "action": "request.ctrl+enter",
                "actor": {
                    "email": "user@org.com",
                    "ip": "200.0.0.42",
                    "extras": {"auth0_id": "123"},
                },
                "app": "vscode.extension.OSFDigital.wingman",
                "extra": {"text_completion_id": "123", "vscode_version": "1.0.1"},
                "type": "code.completion",
            },
        },
        {
            "op": "add",
            "value": {
                "action": "copy.code-block",
                "actor": {
                    "email": "user@org.com",
                    "ip": "200.0.0.42",
                    "extra": {"azure_id": "123"},
                },
                "app": "web.osf.chat-wingman",
                "extra": {"message_id": "123", "user_agent": "firefox-116"},
                "type": "chat.thread",
            },
        },
    ]
]


@router.post("/events", status_code=s.HTTP_201_CREATED)
async def create_one(
    request: Request,
    background_tasks: BackgroundTasks,
    body: EventData = Body(examples=examples),
) -> GeneratedFields:
    return controllers.create_one(background_tasks, body, request.state.creator)


@router.patch("/events", status_code=s.HTTP_201_CREATED)
async def create_many(
    request: Request,
    background_tasks: BackgroundTasks,
    body: list[PatchEventData] = Body(examples=patch_examples),
) -> list[GeneratedFields]:
    return controllers.create_many(background_tasks, body, request.state.creator)
