from typing import Optional
from datetime import date, datetime, time
from pydantic import BaseModel
from pymongo.database import Database

from .schemas import Event
from ..utils import PyObjectId

class SourceRefs(BaseModel):
    event_id: PyObjectId
    event_creation: datetime


class EventsPerUser(BaseModel):
    _id: PyObjectId
    # event
    action: str  # send-message
    app: str  # /osf/vscode-extension/OSFDigital.wingman
    type: str  # sidebar.chat
    user_email: str
    # aggregation
    count: int
    date: date | str  # 2020-01-01
    events: Optional[list[SourceRefs]] = None

    @classmethod
    def increment_from_event(cls, event: Event, db: Database):
        filters = {
            "action": event.data.action,
            "app": event.data.app,
            "type": event.data.type,
            "user_email": event.data.user.get("email"),
            "date": datetime.combine(event.created_at.date(), time.min),
        }
        res = db["events_per_user"].find_one_and_update(
            filter=filters,
            update={
                "$inc": {"count": 1},
                "$push": {
                    "events": {"event_id": event.id, "event_creation": event.created_at}
                },
            },
            upsert=True,
        )


class EventsPerApp:
    _id: PyObjectId
    # event
    action: str
    app: str
    type: str
    # aggregation
    count: int
    date: date
