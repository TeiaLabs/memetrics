from fastapi import BackgroundTasks
from tauth.schemas import Creator

from .. import utils
from ..utils import DB
from .schemas import Event, EventData, GeneratedFields, PatchEventData


def create_one(
    background_tasks: BackgroundTasks, body: EventData, created_by: Creator
) -> GeneratedFields:
    db = DB.get(suffix=utils.get_root_dir(created_by.client_name))
    obj = Event(
        created_by=created_by,
        data=body,
    )
    background_tasks.add_task(db["events"].insert_one, obj.dict())
    return GeneratedFields(**obj.dict(by_alias=True))


def create_many(
    background_tasks: BackgroundTasks,
    body: list[PatchEventData],
    created_by: Creator,
) -> list[GeneratedFields]:
    fields = []
    objs = []
    for event_data in body:
        obj = Event(
            created_by=created_by,
            data=event_data.value,
        )
        objs.append(obj.dict())
        fields.append(
            GeneratedFields(
                _id=obj.id,
                created_at=obj.created_at,
                created_by=created_by,
            )
        )

    db = DB.get(suffix=utils.get_root_dir(created_by.client_name))
    background_tasks.add_task(db["events"].insert_many, objs)

    return fields
