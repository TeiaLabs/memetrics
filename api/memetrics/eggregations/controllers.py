from typing import Any, Literal, Optional

from pymongo.database import Database

from ..utils import DB


def read_many(
    action: Optional[str],
    app_startswith: Optional[str],
    date_gte: str,
    date_lt: str,
    groupby: Literal["day", "month", "quarter", "year"],
    limit: int,
    offset: int,
    sort: list[tuple[str, int]],
    type: Optional[str],
    user_email: Optional[list[str]],
):
    db = DB.get()
    filters: dict[str, Any] = {}
    if action is not None:
        filters["action"] = action
    if app_startswith is not None:
        filters["app"] = {"$regex": f"^{app_startswith}"}
    if date_gte is not None:
        from datetime import datetime
        filters["date"] = {"$gte": datetime.fromisoformat(date_gte)}
    if date_lt is not None:
        filters["date"] |= {"$lt": datetime.fromisoformat(date_lt)}
    if type is not None:
        filters["type"] = type
    if user_email is not None:
        filters["user_email"] = {"$in": user_email}

    if groupby == "day":
        ret = db["events_per_user"].find(filters, {"_id": 0})
        return ret.limit(limit).skip(offset).sort(sort)
    else:
        ret = aggregate_events_per_user(
            db, filters, groupby, limit, offset, sort=sort
        )

    return ret


def aggregate_events_per_user(
    db: Database,
    filters: dict,
    date_granularity: Literal["day", "month", "quarter", "year"],
    limit: int,
    offset: int,
    sort: list[tuple[str, int]],
):
    groupby = {
        "$group": {
            "_id": {
                "user_email": "$user_email",
                "action": "$action",
                "app": "$app",
                "date": {
                    "$dateTrunc": {
                        "date": "$date",
                        "unit": date_granularity,
                    },
                },
                "type": "$type",
            },
            "count": {"$sum": "$count"},
        }
    }

    match = {"$match": filters}
    project = {
        "$project": {
            "_id": 0,
            "user_email": "$_id.user_email",
            "action": "$_id.action",
            "app": "$_id.app",
            "date": "$_id.date",
            "type": "$_id.type",
            "count": 1,
        }
    }
    sort_stage = {"$sort": dict(sort)}
    limit_stage = {"$limit": limit}
    skip = {"$skip": offset}

    pipeline = [match, groupby, project, sort_stage, limit_stage, skip]

    ret = db["events_per_user"].aggregate(pipeline)
    return ret
