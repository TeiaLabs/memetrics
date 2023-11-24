from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request, BackgroundTasks, Header
from memetrics.events.models import EventsPerUser

from . import controllers

router = APIRouter(tags=["eggregator"])


@router.get("/eggregations/count-by-user")
async def read_many(
    background_tasks: BackgroundTasks,
    request: Request,
    action: Optional[str] = Query(None),
    app: str = Query(None),
    app_startswith: Optional[str] = Query(None, alias="app:startswith"),
    date_gte: str = Query("2021-01-01", alias="date:gte"),
    date_lt: str = Query("2024-01-01", alias="date:lt"),
    groupby: Literal["day", "month", "quarter", "year"] = Query("day", alias="$groupby"),
    limit: int = Query(10, ge=1, lt=100000, alias="$limit"),
    offset: int = Query(0, ge=0, alias="$offset"),
    sort: str = Query("-date,-count,+app", alias="$sort"),
    type: Optional[str] = Query(None),
    user_email: Optional[list[str]] = Query(None),
    show_events_ref: Literal["none", "default", "always"] = Header("default", alias="x-show-event-refs"),
) -> list[EventsPerUser]:
    if show_events_ref == "always":
        raise HTTPException(422, "Returning event-refs when groupby!=day is not supported yet.")
    if app and app_startswith:
        raise HTTPException(422, "Cannot use both `app` and `app:startswith`.")
    def parse_sort(sort: str) -> list[tuple[str, int]]:
        return [(field_order[1:], -1 if field_order[0] == "-" else 1) for field_order in sort.split(",")]

    sort_tuples = parse_sort(sort)

    items = controllers.read_many(
        background_tasks=background_tasks,
        creator=request.state.creator,
        app=app,
        action=action,
        app_startswith=app_startswith,
        date_gte=date_gte,
        date_lt=date_lt,
        groupby=groupby,
        limit=limit,
        offset=offset,
        sort=sort_tuples,
        type=type,
        user_email=user_email,
        extra_projection={"events": 0} if show_events_ref == "none" else {},
    )
    return items
