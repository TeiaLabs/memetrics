from typing import Any, Literal, Optional

from fastapi import APIRouter, Request, Query
from pymongo.cursor import Cursor

from memetrics.events.models import EventsPerUser

router = APIRouter(tags=["eggregator"])


@router.get("/eggregations/count-by-user")
async def read_many(
    request: Request,
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
    if groupby != "day":
        raise NotImplementedError("Needs aggregation.")
    query: dict[str, Any] = {"$gte": date_gte, "$lt": date_lt}
    if action:
        query["action"] = action
    if app_startswith:
        query["app"] = {"$regex": f"^{app_startswith}"}
    if type:
        query["type"] = type
    if user_email:
        query["user_email"] = {"$in": user_email}

    def parse_sort(sort: str) -> list[tuple[str, int]]:
        return [(field_order[:1], -1 if field_order[0] == "-" else 1) for field_order in sort.split(",")]
    sort = parse_sort(sort)
    def paginate(cursor: Cursor) -> Cursor:
        return cursor.sort(sort).skip(offset).limit(limit)

    return []
