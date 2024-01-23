from .object_id import PyObjectId
from .pydantic_n import *

try:
    from .pydantic_1 import (
        Event,
        EventData,
        GeneratedFields,
        PartialAttribute,
        PatchEventData,
    )
except:
    from .pydantic_2 import (
        Event,
        EventData,
        GeneratedFields,
        PartialAttribute,
        PatchEventData,
    )
