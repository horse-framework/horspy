from enum import Enum


class KnownContentTypes(Enum):
    """
    Known content types are usually used for Server type messages.
    """

    HELLO = 101
    """ 101 """

    OK = 200
    """ 200 """

    ACCEPTED = 202
    """ 202 """

    BAD_REQUEST = 400
    """ 400 """
