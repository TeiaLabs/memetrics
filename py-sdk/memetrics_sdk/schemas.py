from datetime import datetime
from typing import TypedDict

from bson import ObjectId as BsonObjectId
from pydantic import BaseModel, EmailStr, Field


class Creator(BaseModel):
    client_name: str
    token_name: str
    user_email: EmailStr
    user_ip: str = "127.0.0.1"


class PyObjectId(BsonObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (cls, BsonObjectId, str)) or not BsonObjectId.is_valid(v):
            raise TypeError("Invalid ObjectId.")
        return str(v)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(
            type="string",
            examples=["5eb7cf5a86d9755df3a6c593", "5eb7cfb05e32e07750a1756a"],
        )


class GeneratedFields(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime
    created_by: Creator

    class Config:
        allow_mutation = False
        json_encoders = {PyObjectId: str}


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
