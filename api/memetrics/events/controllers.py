from typing import Sequence

from bson import ObjectId as BsonObjectId
from fastapi import BackgroundTasks, HTTPException
from fastapi import status as s
from memetrics_schemas import (
    Creator,
    Event,
    EventData,
    GeneratedFields,
    PartialAttribute,
    PatchEventData,
    PatchEventExtra,
    PyObjectId,
)
from pymongo import ReadPreference

from ..utils import DB
from .models import EventsPerUser


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


def read_many(
    sort: Sequence[tuple[str, int]], limit: int, offset: int, **filters
) -> list[Event]:
    filters = {k: v for k, v in filters.items() if v is not None}
    if "_id" in filters:
        filters["_id"] = BsonObjectId(filters["_id"])
    db = DB.get()
    col = db.get_collection(
        "events", read_preference=ReadPreference.SECONDARY_PREFERRED
    )
    cursor = col.find(filters)
    return list(cursor.sort(sort).skip(offset).limit(limit))


def read_one(identifier: PyObjectId) -> Event:
    db = DB.get()
    col = db.get_collection(
        "events", read_preference=ReadPreference.SECONDARY_PREFERRED
    )
    obj = col.find_one({"_id": BsonObjectId(identifier)})
    if not obj:
        raise HTTPException(
            status_code=s.HTTP_404_NOT_FOUND,
            detail={
                "msg": f"Event with ID '{identifier}' not found.",
                "route": read_one.__name__,
            },
        )
    return Event(**obj)


def replace_one(
    identifier: PyObjectId, name: str, body: PartialAttribute, created_by: Creator
) -> tuple[bool, bool]:
    db = DB.get()
    filters = {
        "_id": BsonObjectId(identifier),
        "created_by.client_name": created_by.client_name,
        "created_by.token_name": created_by.token_name,
        "created_by.user_email": created_by.user_email,
    }
    res = db["events"].update_one(
        filters,
        {
            "$set": {
                f"data.extra.$[elem]": body.dict() | {"name": name},
            },
        },
        array_filters=[{"elem.name": name}],
    )
    found = res.matched_count == 1
    if not found:
        raise HTTPException(
            status_code=s.HTTP_404_NOT_FOUND,
            detail=f"Event with ID '{identifier}' not found for user '{created_by}'.",
        )
    overwritten = res.modified_count == 1
    created = False
    if not overwritten:
        res = db["events"].update_one(
            filters,
            {
                "$addToSet": {
                    "data.extra": body.dict() | {"name": name},
                },
            },
        )
        created = res.modified_count == 1
    return overwritten, created


def update_one(
    identifier: PyObjectId, body: PatchEventExtra, created_by: Creator
) -> bool:
    db = DB.get()
    res = db["events"].update_one(
        {
            "_id": BsonObjectId(identifier),
            "created_by.user_email": created_by.user_email,
        },
        {
            "$addToSet": {
                "data.extra": {
                    "$each": body.dict()["value"],
                },
            },
        },
    )
    found = res.matched_count == 1
    if not found:
        raise HTTPException(
            status_code=s.HTTP_404_NOT_FOUND,
            detail=f"Event with ID '{identifier}' not found for user '{created_by.user_email}'.",
        )
    updated = res.modified_count == 1
    return updated
