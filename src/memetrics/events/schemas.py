from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field
from tauth.schemas import Creator


class EventData(BaseModel):
    type: str  # code-completion.requested
    app: str  # vscode.extension.wingman
    subject: str  # user
    action: str  # accepted
    object: str  # suggestion
    extra: dict[str, str]  # {"suggestion_id": "123"}


class Event(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Creator
    data: EventData
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")  # TODO: don't cast to str


class GeneratedFields(BaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime
    created_by: Creator
