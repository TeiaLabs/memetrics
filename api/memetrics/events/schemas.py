from bson import ObjectId
from memetrics_utils import EventData
from pydantic import Field


class EventIn(EventData):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
