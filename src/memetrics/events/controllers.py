from fastapi import BackgroundTasks
from tauth.schemas import Creator

from .schemas import EventData
from ..utils import DB


def create_one(
    background_tasks: BackgroundTasks, body: EventData, created_by: Creator
):
    db = DB.get()
    obj = EventData(
        created_by=created_by,
        data=body,
    )
    background_tasks.add_task(db["events"].insert_one, obj.dict())
    return {"_id": obj.id}
