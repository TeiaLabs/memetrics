from fastapi import BackgroundTasks
from memetrics_utils import Event, EventData, GeneratedFields
from tauth.schemas import Creator

from ..utils import DB
from .schemas import EventIn


def create_one(
    background_tasks: BackgroundTasks, body: EventIn, created_by: Creator
) -> GeneratedFields:
    db = DB.get()

    event_id = body.id
    obj = Event(
        created_by=created_by,
        data=EventData.construct(**body.dict(exclude={"id"})),
        _id=event_id,
    )
    background_tasks.add_task(db["events"].insert_one, obj.dict())
    return GeneratedFields(**obj.dict(by_alias=True))
