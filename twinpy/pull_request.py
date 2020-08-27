from enum import Enum
from typing import List

from twino_message import MessageHeader


class MessageOrder(Enum):
    """ Message consuming order """

    Default = 0
    """ Does not send any order information. Uses default """

    FIFO = 1
    """ Requests messages with first in first out order (as queue) """

    LIFO = 2
    """ Requests messages with last in first out order (as stack) """

class ClearDecision(Enum):
    """ After all messages received with pull operation. Clearing left messages in queue option """

    No = 0
    """ Do nothing. Do not delete any message. """

    AllMessages = 1
    """ Clear all messages in queue """

    PriorityMessages = 2
    """ Clear high priority messages in queue """

    Messages = 3
    """ Clear default priority messages in queue """


class PullRequest:
    """ Pull request form """

    channel: str
    """ Channel name """

    queue_id: int
    """ Queue Id """

    count: int
    """ Maximum message count wanted received """

    clear_after: ClearDecision
    """ After all messages are received, clearing left messages in queue option """

    order: MessageOrder
    """ Consuming order """

    get_counts: bool
    """
    If true each message will have two headers
    "Priority-Messages" and "Messages" includes left messages in queue
    """

    request_headers: List[MessageHeader]
    """ Additinal headers for pull request message """
