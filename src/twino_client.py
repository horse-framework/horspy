import threading
import socket
import unique_generator

from datetime import timedelta, datetime
from typing import List
from known_content_types import KnownContentTypes
from message_tracker import MessageTracker
from message_type import MessageType
from protocol_reader import ProtocolReader
from protocol_writer import ProtocolWriter
from twino_headers import TwinoHeaders
from twino_message import TwinoMessage, MessageHeader
from twino_result import TwinoResult


class TwinoClient:
    """ Twino Client object """

    # region Properties

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

    ping_interval: timedelta = timedelta(seconds=5)
    """ PING interval """

    smart_heartbeat: bool = True
    """ If true, PING is sent only on idle mode. If there is active traffic, it's skipped. """

    __socket: socket = None
    __is_ssl: bool = False
    __read_thread: threading.Thread
    __heartbeat_timer: threading.Timer = None
    __last_ping: datetime = datetime.utcnow()
    __last_receive: datetime = datetime.utcnow()
    __pong_pending: bool = False
    __pong_deadline: datetime
    __tracker: MessageTracker

    __ping_bytes = b'\x89\xff\x00\x00\x00\x00\x00\x00'
    __pong_bytes = b'\x8a\xff\x00\x00\x00\x00\x00\x00'

    # endregion

    # region Connection

    def __init__(self):
        self.id = unique_generator.create()
        self.__tracker = MessageTracker()
        self.__tracker.run()

    def destroy(self):
        """ Destroys client, stops all background processes and releases all resources """
        self.__tracker.destroy()
        self.disconnect()

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

    def connect(self, host: str) -> bool:
        """Connects to a twino messaging queue host"""
        try:
            self.disconnect()
            resolved = self.__resolve_host(host)
            self.__is_ssl = resolved[2]
            self.__socket = socket.create_connection((resolved[0], resolved[1]))

            # todo: ssl integration
            if self.__is_ssl:
                pass

            hs = self.__handshake()
            if not hs:
                return False

            self.__init_connection()
            self.__read_thread = threading.Thread(target=self.__read)
            self.__read_thread.start()

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
        self.__pong_pending = False

        if self.__heartbeat_timer != None:
            self.__heartbeat_timer.cancel()
            self.__heartbeat_timer = None

        if self.__socket is not None:
            try:
                self.__socket.shutdown(0)
                self.__socket.close()
                self.__socket = None
            except:
                self.__socket = None

    def __pong(self):
        """ Sends pong message as ping response """
        try:
            self.__socket.sendall(self.__pong_bytes)
        except:
            self.disconnect()

    def __heartbeat(self):
        """ Checks client activity and sends PING if required """

        # we are on next heartbeat and previous pending pong still not received
        # connection will be reset
        if self.__pong_pending:
            self.disconnect()
            return

        now = datetime.utcnow()
        diff: timedelta
        if self.smart_heartbeat:
            if self.__last_receive > self.__last_ping:
                diff = now - self.__last_receive
            else:
                diff = now - self.__last_ping
        else:
            diff = now - self.__last_ping

        if diff > self.ping_interval:
            self.__pong_pending = True
            self.__last_ping = datetime.utcnow()
            try:
                self.__socket.sendall(self.__ping_bytes)
            except:
                self.disconnect()
                return

        self.__heartbeat_timer = threading.Timer(self.ping_interval.total_seconds(), self.__heartbeat)
        self.__heartbeat_timer.start()

    def __init_connection(self):
        """ Initializes connection management objects """
        self.__last_ping = datetime.utcnow()
        self.__last_receive = datetime.utcnow()
        self.__pong_pending = False

        if not self.__heartbeat_timer:
            self.__heartbeat_timer = threading.Timer(self.ping_interval.total_seconds(), self.__heartbeat)
            self.__heartbeat_timer.start()

    # endregion

    # region Read

    def __read(self):
        """ Reads messages from socket while connected """

        reader = ProtocolReader()
        while True:
            try:
                message = reader.read(self.__socket)
                if message is None:
                    self.disconnect()
                    return

                self.__last_receive = datetime.utcnow()

                if message.type == MessageType.Terminate.value:
                    self.disconnect()

                elif message.type == MessageType.Ping.value:
                    self.__pong()

                elif message.type == MessageType.Pong.value:
                    self.__pong_pending = False

                elif message.type == MessageType.Server.value:
                    if message.content_type == KnownContentTypes.ACCEPTED:
                        self.id = message.target

                elif message.type == MessageType.QueueMessage.value:
                    # todo: queue message
                    pass

                elif message.type == MessageType.DirectMessage.value:
                    # todo: direct message
                    pass

                elif message.type == MessageType.Acknowledge.value:
                    # todo: acknowledge
                    pass

                elif message.type == MessageType.Response.value:
                    # todo: response
                    pass

                # if message.type == MessageType.Event.value:
                #    pass

            except:
                self.__read_thread = None

    # endregion

    # region Send

    def send(self, msg: TwinoMessage, additional_headers: List[MessageHeader] = None) -> bool:
        """ Sends a raw message to server. Returns true if all data sent over network. """

        try:
            writer = ProtocolWriter()
            if msg.source_len == 0:
                msg.source = self.id

            bytes = writer.write(msg, additional_headers)
            self.__socket.sendall(bytes.getbuffer())
            return True
        except:
            self.disconnect()
            return False

    async def send_get_ack(self, msg: TwinoMessage, additional_headers: List[MessageHeader] = None) -> TwinoResult:
        """ Sends a message and waits for acknowledge """
        # todo: send_get_ack
        pass

    async def request(self, msg: TwinoMessage, additional_headers: List[MessageHeader] = None) -> TwinoResult:
        # todo: request
        pass

    async def send_direct(self, target: str, content_type: int, message: str, wait_ack: bool, headers=[]):
        """ Sends a direct message to a client """
        # todo: send_direct
        pass

    def push_queue(self, channel: str, queue: int, message: str, wait_ack: bool, headers=[]):
        # todo: push_queue
        pass

    def publish_router(self, router: str, content_type: int, message: str, wait_ack: bool, headers=[]):
        # todo: publish_router
        pass

    def ack(self, message: TwinoMessage):
        # todo: ack
        pass

    def negative_ack(self, message: TwinoMessage):
        # todo: negative_ack
        pass

    def response(self, request_msg: TwinoMessage, response_content: str, headers=[]):
        # todo: response
        pass

    # endregion
