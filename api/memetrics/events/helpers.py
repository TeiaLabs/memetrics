from tauth.schemas import Creator

from .schemas import Attribute, EventData


def help_user_edge_cases(body: EventData, creator: Creator) -> EventData:
    if not body.user.get("email"):
        body.user["email"] = creator.user_email

    extra = body.user.setdefault("extra", [])

    extra.append(
        Attribute(
            name="ip_address",
            type="string",
            value=creator.user_ip,
        )
    )
    return body
