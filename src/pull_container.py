import asyncio
from datetime import datetime
from enum import Enum
from typing import List, Callable

from twino_message import TwinoMessage


class PullProcess(Enum):
    """ Pull request statuses"""

    Receiving = 0
    """ Still receiving messages from server """

    Unacceptable = 1
    """ Server respond unacceptable request """

    Unauthorized = 2
    """ Unauthorized process """

    Empty = 3
    """ Queue is empty """

    Completed = 4
    """ All messages are received, process completed. """

    Timeout = 5
    """ Message receive operation timed out. """

    NetworkError = 6
    """ Disconnected from server while receiving messages """


class PullContainer:
    """ Response container of pull request """

    request_id: str
    """ Pull request message id """

    received_count: int
    """ Received message count """

    request_count: int
    """ Requested message count """

    status: PullProcess
    """ Pull request status """

    last_received: datetime
    """ The date last message received """

    messages: List[TwinoMessage]
    """ Received messages """

    future: asyncio.Future

    each_msg_func: Callable[[int, TwinoMessage], None]