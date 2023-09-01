from memetrics_sdk.client import Memetrics
from memetrics_sdk.webservice import EventData

client = Memetrics("webservice")
body = EventData(
    action="send",
    app="/web/osf/chat-wingman",
    extra={
        "message_id": "123",
        "user_agent": "firefox-116",
    },
    type="chat.thread.message",
    user={
        "email": "user@mail.com",
        "extra": {"azure-id": "123"},
    },
)
client.insert_one(body)
