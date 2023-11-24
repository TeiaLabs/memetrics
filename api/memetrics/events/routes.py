from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Query, Request
from fastapi import status as s

from . import controllers
from .helpers import help_user_edge_cases
from .schemas import EventData, GeneratedFields, PatchEventData, Event
from ..utils import PyObjectId

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


@router.get("/events", status_code=s.HTTP_200_OK)
async def read_many(
    action: Optional[str] = Query(None),
    app: Optional[str] = Query(None),
    identifier: Optional[PyObjectId] = Query(None, alias="_id"),
    type: Optional[str] = Query(None),
    user_email: Optional[list[str]] = Query(None, alias="user.email"),
    extra_name: Optional[str] = Query(None, alias="extra.name"),
    extra_value: Optional[str] = Query(None, alias="extra.value"),
) -> list[Event]:
    if (extra_name and not extra_value) or (not extra_name and extra_value):
        raise HTTPException(
            status_code=s.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="extra.name and extra.value must be used together.",
        )
    filters = {
        "_id": identifier,
        "data.action": action,
        "data.app": app,
        "data.extra.name": extra_name,
        "data.extra.value": extra_value,
        "data.type": type,
        "data.user.email": user_email,
    }
    return controllers.read_many(**filters)
