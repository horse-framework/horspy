import threading
import socket
import unique_generator

from datetime import timedelta
from typing import List
from known_content_types import KnownContentTypes
from message_type import MessageType
from protocol_reader import ProtocolReader
from protocol_writer import ProtocolWriter
from twino_headers import TwinoHeaders
from twino_message import TwinoMessage, MessageHeader
from twino_result import TwinoResult


class TwinoClient:
    """ Twino Client object """

    auto_reconnect: bool = True
    """ If true, reconnects automatically when disconnected """

    reconnect_delay: timedelta = timedelta(milliseconds=1500)
    """
    When auto_reconnect is true, client reconnects when disconnected.
    That value is the delay before reconnect attempt.
    """

    id: str = None
    """
    Unique client id for MQ server.
    If server has another active client with same id, it will generate new id for the client.    
    """

    name: str = "noname"
    """ Client name """

    type: str = "notype"
    """ Client type """

    token: str = None
    """ Client token for server authentication and authorization """

    headers: List[MessageHeader] = []
    """ Handshake message headers """

    __socket: socket = None
    __read_thread: threading.Thread
    __heartbeat_timer: threading.Timer

    def __init__(self):
        self.id = unique_generator.create()

    def connect(self, host: str) -> bool:
        """Connects to a twino messaging queue host"""
        try:
            self.disconnect()
            resolved = self.__resolve_host(host)
            self.__socket = socket.create_connection((resolved[0], resolved[1]))
            hs = self.__handshake()
            if not hs:
                return False

            self.__read_thread = threading.Thread(target=self.__read)
            self.__read_thread.start()

            if not self.__heartbeat_timer:
                self.__heartbeat_timer = threading.Timer(5, self.__heartbeat)
                self.__heartbeat_timer.start()

            return True

        except:
            return False

    def __handshake(self) -> bool:
        """
        Sends TMQP handshake message and reads handshake response.
        :returns true if handshake is successful
        """

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

    def __read_certain(self, length: int) -> bytearray:
        """
        Reads a certaion amount of bytes
        """

        left = length
        buf = bytearray(length)
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
        """ Resolves host, protocol and port from full endpoint string """

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
        """ Reads messages from socket while connected """

        reader = ProtocolReader()
        while True:
            try:
                message = reader.read(self.__socket)

                if message.type == MessageType.Terminate:
                    self.disconnect()

                elif message.type == MessageType.Ping:
                    self.__pong()

                elif message.type == MessageType.Pong:
                    pass

                elif message.type == MessageType.Server:
                    if message.content_type == KnownContentTypes.ACCEPTED:
                        self.id = message.target
                    continue

                elif message.type == MessageType.QueueMessage:
                    pass

                elif message.type == MessageType.DirectMessage:
                    pass

                elif message.type == MessageType.Acknowledge:
                    pass

                elif message.type == MessageType.Response:
                    pass

                # if message.type == MessageType.Event:
                #    pass

            except:
                self.__read_thread = None

    def __pong(self):
        """ Sends pong message as ping response """

        pass

    def __heartbeat(self):
        pass

    def send(self, msg: TwinoMessage, additional_headers: List[MessageHeader] = None) -> bool:
        """ Sends a raw message to server. Returns true if all data sent over network. """

        try:
            writer = ProtocolWriter()
            bytes = writer.write(msg, additional_headers)
            self.__socket.sendall(bytes.getbuffer())
            return True
        except:
            self.disconnect()
            return False

    async def send_get_ack(self, msg: TwinoMessage, additional_headers: List[MessageHeader] = None) -> TwinoResult:
        """ Sends a message and waits for acknowledge """

        pass

    async def request(self, msg: TwinoMessage, additional_headers: List[MessageHeader] = None) -> TwinoResult:
        pass

    async def send_direct(self, target: str, content_type: int, message: str, wait_ack: bool, headers=[]):
        """ Sends a direct message to a client """
        pass

    def push_queue(self, channel: str, queue: int, message: str, wait_ack: bool, headers=[]):
        pass

    def publish_router(self, router: str, content_type: int, message: str, wait_ack: bool, headers=[]):
        pass

    def ack(self, message: TwinoMessage):
        pass

    def negative_ack(self, message: TwinoMessage):
        pass

    def response(self, request_msg: TwinoMessage, response_content: str, headers=[]):
        pass
