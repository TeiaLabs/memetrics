from fastapi import APIRouter, BackgroundTasks, Body, Request
from fastapi import status as s

from . import controllers
from .schemas import EventData, GeneratedFields, PatchEventData

router = APIRouter()

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
    body: EventData = Body(examples=EventData.Config.examples),
) -> GeneratedFields:
    return controllers.create_one(background_tasks, body, request.state.creator)


@router.patch("/events", status_code=s.HTTP_201_CREATED)
async def create_many(
    request: Request,
    background_tasks: BackgroundTasks,
    body: list[PatchEventData] = Body(examples=patch_examples),
) -> list[GeneratedFields]:
    return controllers.create_many(background_tasks, body, request.state.creator)
