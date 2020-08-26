import io
from typing import List

from twino_message import TwinoMessage, MessageHeader


class ProtocolWriter:
    """
    Writes twino message into a bytes stream
    """

    def write(self, msg: TwinoMessage, additional_headers: List[MessageHeader] = None) -> io.BytesIO:
        """
        Writes twino message into byte stream
        :param msg: message itself
        :param additional_headers: additional headers
        :return: returs byte stream with 0 seek position
        """

        buffer = io.BytesIO()

        # calculate first byte with first acquirer, high priority and type properties
        first = int(msg.type.value)
        if msg.first_acquirer:
            first += 128
        if msg.high_priority:
            first += 64

        # calculate second byte with response, acknowledge and header properties
        second = msg.ttl
        if second > 31:
            second = 31
        if msg.pending_response:
            second += 128
        if msg.pending_acknowledge:
            second += 64
        if msg.has_header or (additional_headers is not None and len(additional_headers) > 0):
            second += 32

        # write protocol properties and lengths
        buffer.write(bytes([first, second, msg.message_id_len, msg.source_len, msg.target_len]))

        # write content type
        buffer.write(msg.content_type.to_bytes(2, 'little', signed=False))

        # write message length
        if msg.length < 253:
            buffer.write(bytes([msg.length]))
        elif msg.length <= 65535:
            buffer.write(msg.length.to_bytes(2, 'little', signed=False))
        elif msg.length <= 4294967295:
            buffer.write(msg.length.to_bytes(4, 'little', signed=False))
        else:
            buffer.write(msg.length.to_bytes(8, 'little', signed=False))

        # write message id, source and target
        if msg.message_id_len > 0:
            buffer.write(msg.message_id.encode('UTF-8'))
        if msg.source_len > 0:
            buffer.write(msg.source.encode('UTF-8'))
        if msg.target_len > 0:
            buffer.write(msg.target.encode('UTF-8'))

        # write headers
        headers = msg.get_headers()
        header_count = len(headers)
        if not additional_headers is None:
            header_count += len(additional_headers)

        if header_count > 0:
            header_stream = io.StringIO()

            for header in headers:
                header_stream.write(header.key + ":" + header.value + "\r\n")

            if not additional_headers is None:
                for header in additional_headers:
                    header_stream.write(header.key + ":" + header.value + "\r\n")

            header_str = header_stream.read()
            header_bytes = header_str.encode('UTF-8')
            header_length = len(header_bytes)

            buffer.write(header_length.to_bytes(2, 'little', signed=False))
            buffer.write(header_bytes)

        # write content
        if msg.length > 0:
            buffer.write(msg.get_content_stream().getbuffer())

        buffer.seek(0)
        return buffer
