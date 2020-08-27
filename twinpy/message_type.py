from enum import Enum


class MessageType(Enum):
    """ Message types """

    Other = 0x00
    """ Unknown message, may be peer to peer """

    Terminate = 0x08
    """ Connection close request """

    Ping = 0x09
    """ Ping message from server """

    Pong = 0x0A
    """ Pong message to server """

    Server = 0x10
    """ A message to directly server. Server should deal with it directly. """

    QueueMessage = 0x11
    """ A message to a channel """

    DirectMessage = 0x12
    """ Direct message, by Id, @type or @name """

    Acknowledge = 0x13
    """ A acknowledge message, points to a message received before. """

    Response = 0x14
    """ A response message, point to a message received before. """

    QueuePullRequest = 0x15
    """ Used for requesting to pull messages from the queue """

    Event = 0x16
    """ Notifies events if it's from server to client. Subscribes or ubsubscribes events if it's from client to server. """

    Router = 0x17
    """ Message is routed to a custom exchange in server """
