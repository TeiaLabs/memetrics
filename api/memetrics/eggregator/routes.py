from typing import Literal

from fastapi import APIRouter, Request, Query
from pymongo.cursor import Cursor

from memetrics.events.models import EventsPerUser

router = APIRouter()


@router.get("/metrics/count-by-user")
async def read_many(
    request: Request,
    groupby: Literal["day", "month", "quarter", "year"] = Query("day", alias="$groupby"),
    limit: int = Query(1000, ge=1, lt=100000, alias="$limit"),
    offset: int = Query(0, ge=0, alias="$offset"),
    sort: str = Query(..., alias="$sort"),
    action: str = Query(),
    app_startswith: str = Query(..., alias="app:startswith"),
    date_gte: str = Query(..., alias="date:gte"),
    date_lt: str = Query(..., alias="date:lt"),
    type: str = Query(),
    user_email: list[str] = Query(..., alias="user_email"),
) -> list[EventsPerUser]:
    sort = request.query_params.get("sort", "date,-count")  # TODO
    if groupby != "day":
        raise NotImplementedError("Needs aggregation.")
    query = {
        "action": action,
        "app": {"$regex": f"^{app_startswith}"},
        "date": {"$gte": date_gte, "$lt": date_lt},
        "type": type,
        "user_email": {"$in": user_email}
    }

    def paginate(cursor: Cursor) -> Cursor:
        return cursor.sort(sort).skip(offset).limit(limit)

    return []
