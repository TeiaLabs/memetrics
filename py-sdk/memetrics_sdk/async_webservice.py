import asyncio
import os
import time
from collections import defaultdict
from threading import Lock, Thread
from typing import Optional, cast

import httpx
from memetrics.events.schemas import GeneratedFields

from .schemas import EventData, TAuthHeaders


class AsyncWebserviceClient:
    def __init__(
        self,
        timeout: float = 0.5,
        url: str = os.environ.get("MEMETRICS_URL"),
        api_key: str = os.environ.get("TEIA_API_KEY"),
    ):
        if url is None:
            raise ValueError("URL not defined.")

        if api_key is None:
            raise ValueError("API Key not defined.")

        self.api_key = api_key
        self.url = url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        self.timeout = timeout
        self.lock = Lock()
        self.is_active = False
        self.events: list[tuple[EventData, Optional[TAuthHeaders]]] = []
        self.http_client = httpx.AsyncClient(base_url=self.url, headers=self.headers)

    def __create_thread(self):
        return Thread(target=self.__wait_for_events, args=(self.timeout,))

    def __wait_for_events(self, timeout: float):
        time.sleep(timeout)

        # Critical section
        self.lock.acquire()

        # Create copy of current events and clear global list
        local_events = []
        for event in self.events:
            local_events.append(event)
        self.events.clear()

        # End of critical session
        self.lock.release()

        event_batches = defaultdict(list)
        for event, headers in local_events:
            key = get_dict_key(headers)
            event_batches[key].append((event, headers))

        relative_url = "/events"
        coros = []
        for batch in event_batches.values():
            patch_body = [{"op": "add", "value": e[0].dict()} for e in batch]

            coros.append(
                self.http_client.post(
                    relative_url,
                    headers=cast(dict[str, str], batch[0][1]),
                    json=patch_body,
                )
            )

        future = asyncio.gather(*coros)
        try:
            asyncio.get_running_loop()
            asyncio.ensure_future(future)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(future)

        self.is_active = False

    def delayed_insert_one(
        self, document: EventData, headers: Optional[TAuthHeaders] = None
    ) -> None:
        # Critical section
        self.lock.acquire()

        self.events.append((document, headers))

        # End of critical session
        self.lock.release()

        if not self.is_active:
            self.is_active = True
            self.__create_thread().run()

    async def insert_one(
        self,
        document: EventData,
        headers: Optional[TAuthHeaders] = None,
    ) -> GeneratedFields:
        relative_url = "/events"
        result = await self.http_client.post(
            relative_url,
            headers=cast(dict[str, str], headers),
            json=document,
        )
        return GeneratedFields(**result.json())

    def __del__(self):
        future = self.http_client.aclose()
        try:
            asyncio.get_running_loop()
            asyncio.ensure_future(future)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(future)


def get_dict_key(d: dict[str, str] | None) -> str:
    if d is None:
        return ""
    return "-".join(v for v in d.values())
