import uuid


def create():
    """ Creates new unique string """
    u = uuid.uuid4()
    return str(u)
