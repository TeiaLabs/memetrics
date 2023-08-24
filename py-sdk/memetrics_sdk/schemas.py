from typing import TypedDict


TAuthHeaders = TypedDict(
    "AuthHeaders",
    {"Authorization": str, "X-User-Email": str, "X-User-ID": str, "X-User-IP": str},
    total=False,
)
