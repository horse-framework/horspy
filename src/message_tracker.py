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

    def run(self) -> None:
        """ Runs message tracker """
        self.__running = True
        self.__items.clear()
        self.__tracker_thread = threading.Thread(target=self.__elapse)
        self.__tracker_thread.start()

    def destroy(self) -> None:
        """ Stops message tracker background processes and releases all resources """
        self.__running = False
        self.__items.clear()
        self.__tracker_thread = None

    def track(self, msg: TwinoMessage, timeout: timedelta) -> asyncio.Future:
        """ Tracks a message """
        item = TrackingMessage(msg)
        item.expiration = datetime.utcnow() + timeout

        with self.__lock:
            self.__items.append(item)

        return item.future

    def forget(self, msg: TwinoMessage) -> None:
        """ Forgets a message """
        found = self.__find(msg.message_id)
        if found is None:
            return

        with self.__lock:
            self.__items.remove(found)

    def mark_all_expired(self) -> None:
        """ Marks all messages as expired. Used when client is disconnected. """
        with self.__lock:
            for i in self.__items:
                i.expired()
            self.__items.clear()

    def process(self, response: TwinoMessage) -> None:
        """ Process response or acknowledge message, does process if message is tracked """
        tracking = self.__find(response.message_id)
        if tracking is None:
            return

        tracking.received(response)
        with self.__lock:
            self.__items.remove(tracking)

    def __find(self, msg_id: str) -> TrackingMessage:
        """ Finds tracking message by message id """
        with self.__lock:
            for i in self.__items:
                if i.message.message_id == msg_id:
                    return i
        return None

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
