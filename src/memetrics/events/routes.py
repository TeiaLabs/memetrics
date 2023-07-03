from fastapi import APIRouter, BackgroundTasks, Request
from fastapi import status as s

from . import controllers
from .schemas import EventData, Identifier

router = APIRouter()


@router.post("/events", status_code=s.HTTP_201_CREATED)
async def create_one(
    request: Request,
    background_tasks: BackgroundTasks,
    body: EventData,
) -> Identifier:
    # TODO: switch_db
    return controllers.create_one(background_tasks, body, request.state.creator)
