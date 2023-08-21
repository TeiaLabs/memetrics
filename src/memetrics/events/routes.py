from fastapi import APIRouter, BackgroundTasks, Request, Body
from fastapi import status as s

from . import controllers
from .schemas import EventData, GeneratedFields

router = APIRouter()
examples = [
    {
        "type": "user-action",
        "app": "vscode.wingman.code-completion",
        "subject": "user",
        "action": "accepted",
        "object": "suggestion",
        "extra": {"suggestion_id": "123"},
    },
    {
        "type": "user-action",
        "app": "vscode.wingman.datasources",
        "subject": "user",
        "action": "requested",
        "object": "indexing",
        "extra": {"indexing_id": "123"},
    },
]


@router.post("/events", status_code=s.HTTP_201_CREATED)
async def create_one(
    request: Request,
    background_tasks: BackgroundTasks,
    body: EventData = Body(examples=examples),
) -> GeneratedFields:
    # TODO: switch_db
    return controllers.create_one(background_tasks, body, request.state.creator)
