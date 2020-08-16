import io
from socket import socket

from message_type import MessageType
from twino_message import TwinoMessage


class ProtocolReader:
    """
    Reads twino message frame from socket
    """

    def read(self, sock: socket) -> TwinoMessage:
        """
        Reads a twino message from socket.
        :returns None if frame is corrupted or connection is lost while reading
        """

        # magic num 8: protocol frame must have at least 8 bytes
        frame_bytes = self.__read_certain(sock, 8)
        if frame_bytes is None:
            return None

        msg = TwinoMessage()
        message_len = self.__read_frame(frame_bytes, sock, msg)

        if msg.has_header:
            self.__read_headers(sock, msg)

        if message_len > 0:
            self.__read_content(sock, message_len, msg)

        return msg

    def __read_frame(self, array: bytearray, sock: socket, msg: TwinoMessage) -> int:
        """ Reads frame data """

        first = array[0]
        second = array[1]

        if first >= 128:
            msg.first_acquirer = True
            first -= 128

        if first >= 64:
            msg.high_priority = True
            first -= 64

        msg.type = first

        if second >= 32 and msg.type != MessageType.Ping and msg.type != MessageType.Pong:
            msg.has_header = True
            second -= 32

        msg.ttl = second
        id_len = array[2]
        source_len = array[3]
        target_len = array[4]

        size_bytes = [array[5], array[6]]
        msg.content_type = int.from_bytes(size_bytes, byteorder='little', signed=False)

        message_len = 0
        # length is unsigned in 16
        if array[7] == 253:
            short_len = self.__read_certain(sock, 2)
            message_len = int.from_bytes(short_len, byteorder='little', signed=False)

        # length is unsigned int 32
        elif array[7] == 254:
            int_len = self.__read_certain(sock, 4)
            message_len = int.from_bytes(int_len, byteorder='little', signed=False)

        # length is unsigned int 64
        elif array[7] == 255:
            long_len = self.__read_certain(sock, 8)
            message_len = int.from_bytes(long_len, byteorder='little', signed=False)

        # length is byte
        else:
            message_len = array[7]

        if id_len > 0:
            id_bytes = self.__read_certain(sock, id_len)
            msg.message_id = id_bytes.decode('UTF-8')

        if source_len > 0:
            source_bytes = self.__read_certain(sock, source_len)
            msg.source = source_bytes.decode('UTF-8')

        if target_len > 0:
            target_bytes = self.__read_certain(sock, target_len)
            msg.target = target_bytes.decode('UTF-8')

        return message_len

    def __read_headers(self, sock: socket, msg: TwinoMessage):
        """ Reads message headers """

        # read unsigned int 16 for headers length
        header_bytes = self.__read_certain(sock, 2)
        header_length = int.from_bytes(header_bytes, byteorder='little', signed=False)

        buffer = self.__read_certain(sock, header_length)
        header_str: str = buffer.decode('UTF-8')

        # split header data with CR LF, split per line with : and get key value pair
        lines = header_str.split('\r\n')
        for line in lines:
            if len(line) < 2:
                continue
            index = line.index(':')
            if index < 1:
                continue
            key = line[:index].strip()
            value = line[index + 1:].strip()
            msg.add_header(key, value)

    def __read_content(self, sock: socket, length: int, msg: TwinoMessage):
        """ Reads message content """

        msg.reset_content_stream()
        content = msg.get_content_stream()

        left = length
        buf = bytearray(255)

        while left > 0:
            read_count = len(buf)
            if left < read_count:
                read_count = left

            read_done = sock.recv_into(buf, read_count)
            if read_done == 0:
                raise IOError()

            left -= read_done
            if read_done == len(buf):
                content.write(buf)
            else:
                writebuf = buf[:read_done]
                content.write(writebuf)

        msg.recalculate_length()

    def __read_certain(self, sock: socket, length: int) -> bytearray:
        """
        Reads certain amount of bytes from socket.
        If available amount is less than required, blocks the thread.
        """

        left = length
        buf = bytearray(length)
        view = memoryview(buf)
        while left:
            read_count = sock.recv_into(view, left)

            # if disconnected
            if read_count == 0:
                return None

            view = view[read_count:]  # slicing views is cheap
            left -= read_count

        return buf
