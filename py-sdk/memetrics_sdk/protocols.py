from typing import Any, Protocol


class Client(Protocol):
    def insert_one(self, document: dict[str, Any], db_name: str = "memetrics") -> str:
        ...
