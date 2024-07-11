from datetime import datetime
from typing import Any, TypedDict

from pydantic import BaseModel, Field
from tauth.schemas import Creator

TAuthHeaders = TypedDict(
    "AuthHeaders",
    {"Authorization": str, "X-User-Email": str, "X-User-ID": str, "X-User-IP": str},
    total=False,
)


EventsPerUSer = TypedDict(
    "EventsPerUser",
    {
        "_id": str,
        "action": str,
        "app": str,
        "type": str,
        "user_email": str,
        "count": int,
        "date": str,
        "events": list,
    },
)

EventData = TypedDict(
    "EventData",
    {
        "action": str,
        "app": str,
        "app_version": str,
        "extra": list,
        "type": str,
        "user": dict,
    },
)


class GeneratedFields(BaseModel):
    id: Any = Field(..., alias="_id")
    created_at: datetime
    created_by: Creator

    class Config:
        allow_mutation = False
        json_encoders = {Any: str}
