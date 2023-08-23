import os
from typing import Any, Literal

import httpx


class LambdaClient:
    def __init__(self):
        self.api_key = os.environ["MONGODB_API_KEY"]
        self.cluster_name = os.environ["MONGODB_CLUSTER"]
        self.url = os.environ["MONGODB_URL"]
        self.headers = {
            "Content-Type": "application/json",
            "Access-Control-Request-Headers": "*",
            "api-key": self.api_key,
        }

    def insert_one(self, document: dict[str, Any], db_name: str = "memetrics") -> str:
        url = f"{self.url}/insertOne"
        payload = {
            "collection": "events",
            "database": db_name,
            "dataSource": self.cluster_name,
            "document": document,
        }
        with httpx.Client() as client:
            res = client.post(url, headers=self.headers, json=payload)
        res_json = res.json()
        return res_json["insertedId"]


class Memetrics:
    """
    Allow user to interact with the Memetrics API.

    backend: lambda or microservice.
    """

    def __init__(self, backend: Literal["lambda", "microservice"]):
        self.backend = backend
        if self.backend == "lambda":
            self.client = LambdaClient()
        elif self.backend == "microservice":
            raise NotImplementedError("Microservice backend not implemented yet.")
        else:
            raise ValueError("backend must be lambda or microservice")

    # def track(self, )
