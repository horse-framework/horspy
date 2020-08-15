import threading
from typing import List

import numpy as np
import socket
import io

import unique_generator
from known_content_types import KnownContentTypes
from message_type import MessageType
from protocol_reader import ProtocolReader
from protocol_writer import ProtocolWriter
from twino_headers import TwinoHeaders
from twino_message import TwinoMessage, MessageHeader


class TwinoClient:
    """ Twino Client object """

    auto_reconnect: bool = True
    reconnect_delay: int = 1000

    id: str = None
    name: str = None
    type: str = None
    token: str = None
    headers: List[MessageHeader] = []

    __socket: socket = None
    __read_thread: threading.Thread

    def __init__(self):
        self.id = unique_generator.create()

    def connect(self, host: str) -> bool:
        """Connects to a twino messaging queue host"""
        #    try:
        if 1 == 1:
            self.disconnect()
            resolved = self.__resolve_host(host)
            self.__socket = socket.create_connection((resolved[0], resolved[1]))
            hs = self.__handshake()
            if not hs:
                return False

            self.__read_thread = threading.Thread(target=self.__read)
            self.__read_thread.start()
            return True

    #    except e:
    #        return False

    def __handshake(self) -> bool:
        self.__socket.sendall("TMQP/2.0".encode('UTF-8'))

        # create handshake message properties
        content = 'CONNECT /\r\n'
        if self.id:
            content += TwinoHeaders.create_line(TwinoHeaders.CLIENT_ID, self.id)
        if self.name:
            content += TwinoHeaders.create_line(TwinoHeaders.CLIENT_NAME, self.name)
        if self.type:
            content += TwinoHeaders.create_line(TwinoHeaders.CLIENT_TYPE, self.type)
        if self.token:
            content += TwinoHeaders.create_line(TwinoHeaders.CLIENT_TOKEN, self.token)

        if self.headers:
            for h in self.headers:
                content += TwinoHeaders.create_line(h.key, h.value)

        msg = TwinoMessage()
        msg.type = MessageType.Server
        msg.content_type = KnownContentTypes.HELLO
        msg.set_content(content)
        sent = self.send(msg)
        if not sent:
            return False

        hr_result = self.__read_certain(8)
        if hr_result is None:
            return False

        hs_response = hr_result.decode('UTF-8')
        return hs_response == "TMQP/2.0"

    def __read_certain(self, bytes: int) -> bytearray:
        left = bytes
        buf = bytearray(bytes)
        view = memoryview(buf)
        while left:
            read_count = self.__socket.recv_into(view, left)
            if read_count == 0:
                return None

            view = view[read_count:]  # slicing views is cheap
            left -= read_count

        return buf

    def disconnect(self):
        """ Disconnects from twino messaging queue server """

        if self.__socket is not None:
            self.__socket.close()

    def __resolve_host(self, host: str) -> (str, int, bool):

        sp_protocol = host.split('://')
        sp_host = sp_protocol[0]
        if len(sp_protocol) > 1:
            sp_host = sp_protocol[1]

        sport = sp_host.split(':')
        hostname = sport[0]

        port = 2622
        if len(sport) > 1:
            port_str = sport[1]
            if port_str.endswith('/'):
                port_str = port_str[0:len(port_str) - 1]

            port = int(port_str)

        ssl = False
        if len(sp_protocol) > 1:
            proto = sp_protocol[0].lower().strip()
            if proto == 'tmqs':
                ssl = True

        return (hostname, port, ssl)

    def __read(self):
        while True:
            try:
                reader = ProtocolReader()
                message = reader.read(self.__socket)
                if message.length > 0:
                    print(message.get_content())
            except:
                self.__read_thread = None

    def send(self, msg: TwinoMessage, additionalHeaders: List[MessageHeader] = None) -> bool:
        try:
            writer = ProtocolWriter()
            bytes = writer.write(msg, additionalHeaders)
            self.__socket.sendall(bytes.getbuffer())
            return True
        except:
            self.disconnect()
            return False

    def send_direct(self, target: str, contentType: np.short, message: str, waitAcknowledge: bool, headers=[]):
        """ Sends a direct message to a client """
        pass

    def push_queue(self, channel: str, queue: np.short, message: str, waitAcknowledge: bool, headers=[]):
        pass

    def publish_router(self, router: str, contentType: np.short, message: str, waitAcknowledge: bool, headers=[]):
        pass

    def ack(self, message: TwinoMessage):
        pass

    def negative_ack(self, message: TwinoMessage):
        pass

    def response(self, requestMessage: TwinoMessage, responseContent: str, headers=[]):
        pass
