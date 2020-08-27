import io
from typing import List, Optional
from message_type import MessageType


class MessageHeader:
    """ Key value pair item for message headers """

    key: str
    value: str

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


class TwinoMessage:
    """ Message object for Twino Messaging Queue Server """

    first_acquirer: bool = False
    """ If true, only one consumer receives the message """

    high_priority: bool = False
    """ If true, message will be sent as high priority message """

    pending_response: bool = False
    """ If true, message must be respond by consumer. That information will be sent to consumer. """

    pending_acknowledge: bool = False
    """ If true, message must be acknowledged by consumer. That information will be sent to consumer. """

    ttl: int = 16
    """ Message time to live value for TMQP between clients and server nodes. Default value is 16 """

    content_type: int = 0
    """ Message content type. For queue messages, it's queue id. """

    type: MessageType
    """ Message type """

    # region Message Id

    __message_id_length: int = 0
    __message_id: str = None

    @property
    def message_id_len(self) -> int:
        return self.__message_id_length

    @property
    def message_id(self) -> str:
        return self.__message_id

    @message_id.setter
    def message_id(self, var: str):
        self.__message_id = var
        if var == None:
            self.__message_id_length = 0
        else:
            self.__message_id_length = len(var)

    # endregion

    # region Source

    __source_length: int = 0
    __source: str = None

    @property
    def source_len(self) -> int:
        return self.__source_length

    @property
    def source(self) -> str:
        return self.__source

    @source.setter
    def source(self, var: str):
        self.__source = var
        if var == None:
            self.__source_length = 0
        else:
            self.__source_length = len(var)

    # endregion

    # region Target

    __target_length: int = 0
    __target: str = None

    @property
    def target_len(self) -> int:
        return self.__target_length

    @property
    def target(self) -> str:
        return self.__target

    @target.setter
    def target(self, var: str):
        self.__target = var
        if var == None:
            self.__target_length = 0
        else:
            self.__target_length = len(var)

    # endregion

    # region Headers

    has_header: bool = False
    __headers: List[MessageHeader] = []

    def add_header(self, key: str, value: str):
        """ Adds new header key value pair. If key exists, value will be overwritten """
        lower = key.lower()
        found = next((e for e in self.__headers if e.key.lower() == lower), None)

        if found == None:
            header = MessageHeader(key, value)
            self.__headers.append(header)
        else:
            found.value = value

        self.has_header = True

    def get_header(self, key: str) -> Optional[str]:
        """ Finds header value by key, if key isn't exist returns None """
        lower = key.lower()
        found = next((e for e in self.__headers if e.key.lower() == lower), None)
        if found == None:
            return None
        return found.value

    def remove_header(self, key: str):
        """ Removes header by key, If key isn't exist does nothing """
        lower = key.lower()
        found = next((e for e in self.__headers if e.key.lower() == lower), None)
        if found != None:
            self.__headers.remove(found)

        if len(self.__headers) == 0:
            self.has_header = False
        else:
            self.has_header = True

    def get_headers(self) -> List[MessageHeader]:
        """ DO NOT add or remove to list """
        return self.__headers

    # endregion

    # region Content

    __length: int = 0
    __content: io.BytesIO = None

    @property
    def length(self) -> int:
        return self.__length

    def reset_content_stream(self):
        self.__content = io.BytesIO()
        self.__length = 0

    def get_content_stream(self) -> io.BytesIO:
        """ DO NOT write to stream """

        return self.__content

    def get_content(self) -> Optional[str]:
        """ Gets message content """

        if self.__content == None:
            return None

        self.__content.seek(0)
        bytes_str = self.__content.read()
        string_content = bytes_str.decode('UTF-8')

        return string_content

    def set_content(self, content: str):
        """ Sets message content """

        if not content:
            self.__content = io.BytesIO()
            self.__length = 0
            return

        if self.__content is None:
            self.__content = io.BytesIO()

        self.__content.write(content.encode('UTF-8'))
        self.__length = self.__content.getbuffer().nbytes

    def recalculate_length(self):
        self.__length = self.__content.getbuffer().nbytes

    # endregion
