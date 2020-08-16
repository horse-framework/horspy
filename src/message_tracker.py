import asyncio
import threading
import time
from datetime import timedelta, datetime
from typing import List

from tracking_message import TrackingMessage
from twino_message import TwinoMessage

class MessageTracker:
    """ Tracks all messages """

    __items: List[TrackingMessage] = []
    __tracker_thread: threading.Thread
    __running: bool = False
    __lock = asyncio.Lock()

    def run(self):
        """ Runs message tracker """
        self.__running = True
        self.__items.clear()
        self.__tracker_thread = threading.Thread(target=self.__elapse)
        self.__tracker_thread.start()
        pass

    def destroy(self):
        """ Stops message tracker background processes and releases all resources """
        self.__running = False
        self.__items.clear()
        self.__tracker_thread = None
        pass

    def track(self, msg: TwinoMessage, timeout: timedelta):
        """ Tracks a message """
        item = TrackingMessage(msg)
        item.expiration = datetime.utcnow() + timeout

        with self.__lock:
            self.__items.append(item)

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
        while self.__running:
            time.sleep(1.0)
            now = datetime.utcnow()
            with self.__lock:
                for i in self.__items:
                    if i.completed:
                        self.__items.remove(i)
                    elif i.expiration < now:
                        i.expired()
                        self.__items.remove(i)
