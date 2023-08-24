from typing import Any, Literal

from .atlas import AtlasClient
from .webservice import WebserviceClient


class Memetrics:
    """
    Instantiate client.

    Client factory.
    """

    def __new__(cls, backend: Literal["atlas", "webservice"]):
        if backend == "atlas":
            return AtlasClient()
        elif backend == "webservice":
            return WebserviceClient()
        else:
            raise ValueError("backend must be lambda or microservice")

