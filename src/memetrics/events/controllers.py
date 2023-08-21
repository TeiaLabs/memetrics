from fastapi import BackgroundTasks
from tauth.schemas import Creator

from .schemas import Event, EventData, GeneratedFields
from ..utils import DB


def create_one(
    background_tasks: BackgroundTasks, body: EventData, created_by: Creator
) -> GeneratedFields:
    db = DB.get()
    obj = Event(
        created_by=created_by,
        data=body,
    )
    background_tasks.add_task(db["events"].insert_one, obj.dict())
    return GeneratedFields(**obj.dict(by_alias=True))
