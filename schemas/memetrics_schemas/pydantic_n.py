from typing import Literal


def version_less_than_3_12() -> bool:
    import platform

    return float(".".join(platform.python_version().split(".")[:2])) < 3.12


if version_less_than_3_12():
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

from pydantic import BaseModel, EmailStr


class Creator(BaseModel):
    client_name: str
    token_name: str
    user_email: EmailStr
    user_ip: str = "127.0.0.1"


class Attribute(BaseModel):
    name: str
    type: Literal["string", "integer", "float", "dict", "list"]
    value: str | int | float | dict | list


class User(TypedDict, total=False):
    email: str
    extra: list[Attribute]
    id: str


class PatchEventExtra(BaseModel):
    op: Literal["add"]
    path: Literal["/data/extra"]
    value: list[Attribute]

    class Config:
        examples = {
            "Add another attribute.": {
                "value": [
                    {
                        "op": "add",
                        "path": "/data/extra",
                        "value": [
                            {
                                "name": "special-id",
                                "type": "string",
                                "value": "789",
                            }
                        ],
                    },
                ]
            }
        }
