from result_code import ResultCode
from horse_message import HorseMessage


class HorseResult:
    """ Horse Messaging Queue Operation Result """

    code: ResultCode
    """ Result code """

    reason: str
    """
    Reason is usually used for unsuccessful results
    """

    message: HorseMessage
    """
    Raw message of the operation
    """
