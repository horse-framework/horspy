from typing import List, Callable

from twino_message import TwinoMessage


class Subscription:
    """
    Queue and direct message subscription
    """

    direct: bool
    """ True, if subscription is for direct messages """

    channel: str
    """ Channel name """

    content_type: int
    """ Content Type for direct messages and Queue Id for queue messages """

    actions: List[Callable[[TwinoMessage], None]] = []
    """ Action that will be called when a message is received to specified queue or direct """
