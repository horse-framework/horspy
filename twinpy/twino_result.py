from result_code import ResultCode
from twino_message import TwinoMessage


class TwinoResult:
    """ Twino Messaging Queue Operation Result """

    code: ResultCode
    """ Result code """

    reason: str
    """
    Reason is usually used for unsuccessful results
    """

    message: TwinoMessage
    """
    Raw message of the operation
    """
