from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel
from pymongo import operations as pymongo_operations
from pymongo.database import Database

from ..utils import PyObjectId
from .schemas import Event


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
    date: date  # 2020-01-01
    events: Optional[list[SourceRefs]] = None  # events are discarded in aggregations

    class Config:
        indices = [
            ("action", 1),
            ("date", -1),
            ("user_email", 1),
            [("app", 1), ("type", 1), ("action", 1)],
        ]

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

    @classmethod
    def bulk_increment_from_events(cls, events: list[Event], db: Database):
        """
        SAFETY: write operations (e.g. update) will block operations until committed
        to journal as per configuration on the client (fsync = True) which will ensure
        the order of execution of different operations.
        Note that write operations are atomic by default at the document level as per documentation
        https://www.mongodb.com/docs/manual/core/write-operations-atomicity/.
        """
        operations = []
        for event in events:
            filters = {
                "action": event.data.action,
                "app": event.data.app,
                "type": event.data.type,
                "user_email": event.data.user.get("email"),
                "date": datetime.combine(event.created_at.date(), time.min),
            }
            update = {
                "$inc": {"count": 1},
                "$push": {
                    "events": {
                        "event_id": event.id,
                        "event_creation": event.created_at,
                    }
                },
            }
            operations.append(
                pymongo_operations.UpdateOne(
                    filter=filters,
                    update=update,
                    upsert=True,
                )
            )

        _ = db["events_per_user"].bulk_write(operations, ordered=False)


class EventsPerApp:
    _id: PyObjectId
    # event
    action: str
    app: str
    type: str
    # aggregation
    count: int
    date: date
