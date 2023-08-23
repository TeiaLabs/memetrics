from fastapi import APIRouter, BackgroundTasks, Request, Body
from fastapi import status as s

from . import controllers
from .schemas import EventData, GeneratedFields

router = APIRouter()
examples = [
    {
        "action": "requested",
        "actor": {"id": "123", "email": "user@mail.com"},
        "app": "vscode.extension.OSFDigital.wingman",
        "extra": {"suggestion_id": "123"},
        "type": "code.completion",
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
