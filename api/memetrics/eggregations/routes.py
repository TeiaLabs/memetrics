from typing import Any, Literal, Optional

from fastapi import APIRouter, Request, Query
from pymongo.cursor import Cursor

from memetrics.events.models import EventsPerUser
from . import controllers

router = APIRouter(tags=["eggregator"])


@router.get("/eggregations/count-by-user")
async def read_many(
    action: Optional[str] = Query(None),
    app_startswith: Optional[str] = Query(None, alias="app:startswith"),
    date_gte: str = Query("2021-01-01", alias="date:gte"),
    date_lt: str = Query("2024-01-01", alias="date:lt"),
    groupby: Literal["day", "month", "quarter", "year"] = Query("day", alias="$groupby"),
    limit: int = Query(10, ge=1, lt=100000, alias="$limit"),
    offset: int = Query(0, ge=0, alias="$offset"),
    sort: str = Query("-date,-count,+app", alias="$sort"),
    type: Optional[str] = Query(None),
    user_email: Optional[list[str]] = Query(None),
) -> list[EventsPerUser]:

    def parse_sort(sort: str) -> list[tuple[str, int]]:
        return [(field_order[1:], -1 if field_order[0] == "-" else 1) for field_order in sort.split(",")]

    sort_tuples = parse_sort(sort)

    cursor = controllers.read_many(
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
    )
    items = list(cursor)
    return items
