import asyncio
import threading
import time
from datetime import timedelta, datetime
from typing import List

from tracking_message import TrackingMessage
from horse_message import HorseMessage


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
        self.__tracker_thread = threading.Thread(target=self.__trigger_elapse)
        self.__tracker_thread.start()

    def destroy(self) -> None:
        """ Stops message tracker background processes and releases all resources """
        self.__running = False
        self.__items.clear()
        self.__tracker_thread = None

    async def track(self, msg: HorseMessage, timeout: timedelta) -> TrackingMessage:
        """ Tracks a message """
        item = TrackingMessage(msg)
        item.expiration = datetime.utcnow() + timeout

        async with self.__lock:
            self.__items.append(item)

        return item

    async def forget(self, msg: HorseMessage) -> None:
        """ Forgets a message """
        found = await self.__find(msg.message_id)
        if found is None:
            return

        async with self.__lock:
            self.__items.remove(found)

    async def mark_all_expired(self) -> None:
        """ Marks all messages as expired. Used when client is disconnected. """
        async with self.__lock:
            for i in self.__items:
                i.expired()
            self.__items.clear()

    async def process(self, response: HorseMessage) -> None:
        """ Process response or acknowledge message, does process if message is tracked """
        tracking = await self.__find(response.message_id)
        if tracking is None:
            return

        tracking.received(response)
        async with self.__lock:
            self.__items.remove(tracking)

    async def __find(self, msg_id: str) -> TrackingMessage:
        """ Finds tracking message by message id """
        async with self.__lock:
            print(len(self.__items))
            for i in self.__items:
                if i.message.message_id == msg_id:
                    return i
        return None

    def __trigger_elapse(self):
        asyncio.run(self.__elapse())

    async def __elapse(self):
        """ Checks tracking messages if they are expired """
        while self.__running:
            time.sleep(1.0)
            now = datetime.utcnow()
            # with (yield from self.__lock):
            async with self.__lock:
                for i in self.__items:
                    if i.completed:
                        self.__items.remove(i)
                    elif i.expiration < now:
                        i.expired()
                        self.__items.remove(i)
