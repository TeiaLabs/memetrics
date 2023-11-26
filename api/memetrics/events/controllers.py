from typing import Sequence

from fastapi import BackgroundTasks
from pymongo import ReadPreference
from tauth.schemas import Creator

from ..utils import DB, PyObjectId
from .models import EventsPerApp, EventsPerUser
from .schemas import Event, EventData, GeneratedFields, PatchEventData


def create_one(
    background_tasks: BackgroundTasks, body: EventData, created_by: Creator
) -> GeneratedFields:
    db = DB.get()
    obj = Event(
        created_by=created_by,
        data=body,
    )
    background_tasks.add_task(db["events"].insert_one, obj.bson())
    background_tasks.add_task(EventsPerUser.increment_from_event, obj, db)
    return GeneratedFields(**obj.dict(by_alias=True))


def create_many(
    background_tasks: BackgroundTasks,
    body: list[PatchEventData],
    created_by: Creator,
) -> list[GeneratedFields]:
    fields = []
    bson_list = []
    objs = []
    for patch_event_data in body:
        obj = Event(
            created_by=created_by,
            data=patch_event_data.value,
        )
        objs.append(obj)
        bson_list.append(obj.bson())
        fields.append(
            GeneratedFields(
                _id=obj.id,
                created_at=obj.created_at,
                created_by=obj.created_by,
            )
        )
    db = DB.get()
    res = db["events"].insert_many(bson_list)
    EventsPerUser.bulk_increment_from_events(objs, db)
    return fields


def read_many(sort: Sequence[tuple[str, int]], limit: int, offset: int, **filters) -> list[Event]:
    filters = {k: v for k, v in filters.items() if v is not None}
    if "_id" in filters:
        filters["_id"] = PyObjectId(filters["_id"])
    db = DB.get()
    col = db.get_collection(
        "events", read_preference=ReadPreference.SECONDARY_PREFERRED
    )
    cursor = col.find(filters)
    return list(cursor.sort(sort).skip(offset).limit(limit))
