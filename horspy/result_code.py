from enum import Enum


class ResultCode(Enum):

    Ok = 0
    """ Operation succeeded """

    Failed = 1
    """ Unknown failed response """

    NoContent = 204
    """ Request successfull but response has no content """

    BadRequest = 400
    """ Request is not recognized or verified by the server """

    Unauthorized = 401
    """ Access denied for the operation """

    PaymentRequired = 402
    Forbidden = 403

    NotFound = 404
    """ Target could not be found """

    MethodNotAllowed = 405

    Unacceptable = 406
    """ Request is not acceptable. Eg, queue status does not support the operation """

    RequestTimeout = 408
    Conflict = 409
    Gone = 410
    LengthRequired = 411
    PreconditionFailed = 412
    RequestEntityTooLarge = 413
    RequestUriTooLong = 414
    UnsupportedMediaType = 415
    RequestedRangeNotSatisfiable = 416
    ExpectationFailed = 417
    MisdirectedRequest = 421
    UnprocessableEntity = 422
    Locked = 423
    FailedDependency = 424
    UpgradeRequired = 426
    PreconditionRequired = 428
    TooManyRequests = 429
    RequestHeaderFieldsTooLarge = 431
    UnavailableForLegalReasons = 451
    Duplicate = 481
    LimitExceeded = 482
    InternalServerError = 500
    NotImplemented = 501
    BadGateway = 502
    Busy = 503
    GatewayTimeout = 504
    HttpVersionNotSupported = 505
    VariantAlsoNegotiates = 506
    InsufficientStorage = 507
    LoopDetected = 508
    NotExtended = 510
    NetworkAuthenticationRequired = 511

    SendError = 581
    """ Message could not be sent to the server """
