from typing import Optional, Literal
from pymongo.database import Database

from ..utils import DB


def read_many(
    user_email: list[str],
    action: Optional[str] = (None),
    app_startswith: Optional[str] = None,
    date_gte: str = None,
    date_lt: str = None,
    groupby: Literal["day", "month", "quarter", "year"] = "day",
    limit: int = 10,
    offset: int = 0,
    sort: tuple = ("date", -1),
    type: Optional[str] = None,
):
    db = DB.get()

    filters = {"user_email": {"$in": user_email}}
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
    groupby: Literal["month", "year"],
    limit: int = 10,
    offset: int = 0,
    sort: list[tuple] = [("date", -1)],
):

    base_group_by = {
        "$group": {
            "_id": {
                "user_email": "$user_email",
                "action": "$action",
                "app": "$app",
                "date": "$date",
                "type": "$type",
            },
            "count": {"$sum": "$count"},
        }
    }

    if groupby == "month":
        groupby_stage = {
            **base_group_by,
            "$group": {
                **base_group_by["$group"],
                "_id": {
                    **base_group_by["$group"]["_id"],
                    "date": {"$dateToString": {"format": "%Y-%m", "date": "$date"}},
                },
            },
        }

    elif groupby == "year":
        groupby_stage = {
            **base_group_by,
            "$group": {
                **base_group_by["$group"],
                "_id": {
                    **base_group_by["$group"]["_id"],
                    "date": {"$dateToString": {"format": "%Y-", "date": "$date"}},
                },
            },
        }

    match = {"$match": filters}
    groupby = groupby_stage
    # keep all fields and make sure date is compatbiel with "date"
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

    sort = {"$sort": dict(sort)}
    limit = {"$limit": limit}
    skip = {"$skip": offset}

    pipeline = [match, groupby, project, sort, limit, skip]

    ret = db["events_per_user"].aggregate(pipeline)
    return ret
