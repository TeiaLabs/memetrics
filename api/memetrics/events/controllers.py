from fastapi import BackgroundTasks
from tauth.schemas import Creator

from .. import utils
from ..utils import DB
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
    dict_objs = []
    objs = []
    for event_data in body:
        obj = Event(
            created_by=created_by,
            data=event_data.value,
        )
        objs.append(obj)
        dict_objs.append(obj.dict())
        fields.append(
            GeneratedFields(
                _id=obj.id,
                created_at=obj.created_at,
                created_by=obj.created_by,
            )
        )
    db = DB.get()
    res = db["events"].insert_many(dict_objs)
    EventsPerUser.bulk_increment_from_events(objs, db)
    return fields


def read_many(**filters) -> list[Event]:
    filters = {k: v for k, v in filters.items() if v is not None}
    db = DB.get()
    cursor = db["events"].find(filters)
    return list(cursor.limit(10))
