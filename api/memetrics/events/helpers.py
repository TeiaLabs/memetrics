from tauth.schemas import Creator

from .schemas import EventData, Attribute


def help_user_edge_cases(body: EventData, creator: Creator) -> EventData:
    if not body.user.get("email"):
        body.user["email"] = creator.user_email
        body.user["extra"] = [
            Attribute(
                name="ip_address",
                type="string",
                value=creator.user_ip,
            )
        ]
    return body
