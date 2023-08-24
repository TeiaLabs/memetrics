from fastapi import APIRouter, BackgroundTasks, Body, Request
from fastapi import status as s
from memetrics_utils import GeneratedFields

from . import controllers
from .schemas import EventIn

router = APIRouter()
examples = [
    {
        "action": "requested",
        "actor": {"id": "123", "email": "user@mail.com"},
        "app": "vscode.extension.OSFDigital.wingman",
        "extra": {"suggestion_id": "123"},
        "type": "code.completion",
        "_id": "64e7c43b9192c0f134769e23"
    },
]


@router.post("/events", status_code=s.HTTP_201_CREATED)
async def create_one(
    request: Request,
    background_tasks: BackgroundTasks,
    body: EventIn = Body(examples=examples),
) -> GeneratedFields:
    # TODO: switch_db
    return controllers.create_one(background_tasks, body, request.state.creator)
