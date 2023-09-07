from datetime import date
from bson import ObjectId
from pymongo.database import Database


class EventsPerUser:
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
        obj = cls(**event.data.dict(by_alias=True))
        filters = {
            "action": obj.action,
            "app": obj.app,
            "type": obj.type,
            "user_email": obj.user_email,
            "date": obj.date,
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
