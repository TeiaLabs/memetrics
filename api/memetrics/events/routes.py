from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Body, Query, Request
from fastapi import status as s

from . import controllers
from .helpers import help_user_edge_cases
from .schemas import EventData, GeneratedFields, PatchEventData, Event

router = APIRouter(tags=["events"])


@router.post("/events", status_code=s.HTTP_201_CREATED)
async def create_one(
    request: Request,
    background_tasks: BackgroundTasks,
    body: EventData = Body(examples=EventData.Config.examples),
) -> GeneratedFields:
    body = help_user_edge_cases(body, request.state.creator)
    return controllers.create_one(background_tasks, body, request.state.creator)


@router.patch("/events", status_code=s.HTTP_207_MULTI_STATUS)
async def create_many(
    request: Request,
    background_tasks: BackgroundTasks,
    body: list[PatchEventData] = Body(examples=PatchEventData.Config.examples),
) -> list[GeneratedFields]:
    return controllers.create_many(background_tasks, body, request.state.creator)
