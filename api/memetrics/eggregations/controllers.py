from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import BackgroundTasks
from pymongo.database import Database
from memetrics.events.controllers import create_one
from memetrics.events.schemas import EventData
from tauth.schemas import Creator

from ..settings import Settings
from ..utils import DB

sets = Settings()
# meme_creator = Creator(client_name=sets.CLIENT_NAME, token_name=sets.TOKEN_NAME, user_email=.user_email)

def read_many(
    background_tasks: BackgroundTasks,
    creator: Creator,
    app_startswith: Optional[str],
    date_gte: str,
    date_lt: str,
    groupby: Literal["day", "month", "quarter", "year"],
    limit: int,
    offset: int,
    sort: list[tuple[str, int]],
    user_email: Optional[list[str]],
    **kwargs,
):
    db = DB.get()
    filters: dict[str, Any] = {k: v for k, v in kwargs.items() if v is not None}
    if app_startswith is not None:
        filters["app"] = {"$regex": f"^{app_startswith}"}
    if date_gte is not None:
        filters["date"] = {"$gte": datetime.fromisoformat(date_gte)}
    if date_lt is not None:
        filters["date"] |= {"$lt": datetime.fromisoformat(date_lt)}
    if user_email is not None:
        filters["user_email"] = {"$in": user_email}

    if groupby == "day":
        ret = db["events_per_user"].find(filters, {"_id": 0})
        ret = ret.limit(limit).skip(offset).sort(sort)
    else:
        ret = aggregate_events_per_user(
            db, filters, groupby, limit, offset, sort=sort
        )
    event = EventData(**{})
    # create_one(background_tasks, event, )
    return list(ret)


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
