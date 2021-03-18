import asyncio
from datetime import datetime

from horse_message import HorseMessage


class TrackingMessage:
    """ Tracks a message till a response is received or expires """

    expiration: datetime

    __completed: bool
    __message: HorseMessage
    __is_ack: bool
    __future: asyncio.Future

    @property
    def completed(self):
        return self.__completed

    @property
    def message(self):
        return self.__message

    @property
    def is_ack(self):
        return self.__is_ack

    @property
    def future(self):
        return self.__future

    def __init__(self, msg: HorseMessage):
        self.__message = msg
        self.__is_ack = msg.pending_acknowledge
        self.__completed = False
        loop = asyncio.get_event_loop()
        self.__future = loop.create_future()  # asyncio.Future()

    def expired(self):
        """ Marks future as response is expired """

        if self.__completed:
            return

        try:
            self.__completed = True
            self.__future.set_result(None)
        except:
            pass

    def received(self, msg: HorseMessage):
        """ Marks future as response is received and sends response message to awaiter """

        if self.__completed:
            return

        try:
            self.__completed = True
            self.__future.set_result(msg)
        except:
            pass
