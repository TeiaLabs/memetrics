from typing import Literal, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
)
from fastapi import status as s

from . import controllers
from .helpers import help_user_edge_cases
from .schemas import EventData, GeneratedFields, PatchEventData, Event, PatchEventExtra
from ..utils import PyObjectId, parse_sort

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


@router.patch(
    "/events/{identifier}",
    status_code=s.HTTP_200_OK,
    responses={404: {}, 304: {}, 422: {}, 204: {}},  # TODO
)
async def update_one(
    request: Request,
    response: Response,
    identifier: PyObjectId,
    body: list[PatchEventExtra] = Body(examples=PatchEventExtra.Config.examples),
    return_preference: Literal["representation", "minimal"] = Header(
        "minimal", alias="X-Return-Preference"
    ),
) -> Event | None:
    """
    200: modified and returned representation
    204: modified
    304: not modified
    404: not found
    """
    if len(body) != 1:
        raise HTTPException(
            status_code=s.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "msg": "Only one patch operation is allowed.",
                "type": "NotImplementedError",
            },
        )
    success = controllers.update_one(identifier, body[0], request.state.creator)
    if not success:
        response.status_code = s.HTTP_304_NOT_MODIFIED
        return
    if return_preference == "representation":
        return controllers.read_one(identifier)
    response.status_code = s.HTTP_204_NO_CONTENT


@router.get("/events", status_code=s.HTTP_200_OK)
async def read_many(
    action: Optional[str] = Query(None, alias="data.action"),
    app: Optional[str] = Query(None, alias="data.app"),
    identifier: Optional[PyObjectId] = Query(None, alias="_id"),
    type: Optional[str] = Query(None, alias="data.type"),
    user_email: Optional[list[str]] = Query(None, alias="user.email"),
    extra_name: Optional[str] = Query(None, alias="data.extra.name"),
    extra_value: Optional[str] = Query(None, alias="data.extra.value"),
    sorting: Optional[str] = Query(
        None,
        alias="$sort",
        examples={
            "-created_at": {},
            "+data.app,+data.type,+data.action": {},
        },
    ),
    limit: int = Query(10, ge=1, lt=100000, alias="$limit"),
    offset: int = Query(0, ge=0, alias="$offset"),
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
    if sorting:
        sort_tuples = parse_sort(sorting)
    else:
        sort_tuples = [("$natural", 1)]
    return controllers.read_many(
        **filters, limit=limit, offset=offset, sort=sort_tuples
    )
