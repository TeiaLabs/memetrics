from datetime import date, datetime, time

from bson import ObjectId
from pydantic import BaseModel
from pymongo.database import Database


class EventsPerUser(BaseModel):
    _id: ObjectId
    # event
    action: str  # send-message
    app: str  # /osf/vscode-extension/OSFDigital.wingman
    type: str  # sidebar.chat
    user_email: str
    # aggregation
    count: int
    date: date  # 2020-01-01

    @classmethod
    def increment_from_event(cls, event, db: Database):
        filters = {
            "action": event.data.action,
            "app": event.data.app,
            "type": event.data.type,
            "user_email": event.data.user["email"],
            "date": datetime.combine(event.created_at.date(), time.min),
        }
        res = db["events_per_user"].find_one_and_update(
            filter=filters,
            update={"$inc": {"count": 1}},
            upsert=True,
        )


class EventsPerApp:
    _id: ObjectId
    # event
    action: str
    app: str
    type: str
    # aggregation
    count: int
    date: date
