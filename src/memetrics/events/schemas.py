from datetime import datetime

from pydantic import BaseModel, Field
from tauth.schemas import Creator


class EventData(BaseModel):
    app: str  # wingman.code-completion
    subject: str  # user
    action: str  # accepted
    object: str  # suggestion
    extra: dict[str, str]  # {"suggestion_id": "123"}


class Event(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Creator
    data: EventData
    id: str = Field(..., alias="_id")
    type: str  # user-action


class Identifier(BaseModel):
    id: str = Field(..., alias="_id")
