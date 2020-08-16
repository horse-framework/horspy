import threading
from datetime import datetime
from typing import List

from twino_message import TwinoMessage


class TrackingMessage:
    message: TwinoMessage
    expiration: datetime
    completed: bool
    is_ack: bool


class MessageTracker:
    """ Tracks all messages """

    __items: List[TrackingMessage] = []
    __tracker_thread: threading.Thread

    def run(self):
        """ Runs message tracker """
        pass

    def destroy(self):
        """ Stops message tracker background processes and releases all resources """
        pass

    def track(self, msg: TwinoMessage):
        """ Tracks a message """
        pass

    def forget(self, msg: TwinoMessage):
        """ Forgets a message """
        pass

    def mark_all_expired(self):
        """ Marks all messages as expired. Used when client is disconnected. """
        pass

    def process_ack(self, ack: TwinoMessage):
        """ Process acknowledge message, does process if message is tracked """
        pass

    def process_response(self, response: TwinoMessage):
        """ Process response message, does process if message is tracked """
        pass

    def __elapse(self):
        """ Checks tracking messages if they are expired """
        pass
