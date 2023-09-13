from typing import TypedDict


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
