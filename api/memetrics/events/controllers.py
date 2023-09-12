from fastapi import BackgroundTasks
from tauth.schemas import Creator

from .. import utils
from ..utils import DB
from .schemas import Event, EventData, GeneratedFields, PatchEventData
from .models import EventsPerUser, EventsPerApp


def create_one(
    background_tasks: BackgroundTasks, body: EventData, created_by: Creator
) -> GeneratedFields:
    db = DB.get(suffix=utils.get_root_dir(created_by.client_name))
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
    for obj in objs:
        EventsPerUser.increment_from_event(obj, db)
    return fields
