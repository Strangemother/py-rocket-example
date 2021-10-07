

class ClassID(object):
    """Apply one method get_id() to return self.uuid or the class name
    if UUID is none.
    """
    uuid = None
    _owner_id = None

    def get_id(self):
        _a = str(self._owner_id or '')
        _b = str(self.uuid or self.__class__.__name__)
        return '.'.join((_a, _b, str(id(_b))))

    def set_owner(self, owner):
        self._owner_id = owner.get_id() if hasattr(owner, 'get_id') else id(owner)


    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.get_id()}">'


class Event(ClassID):
    origin = None
    _data = None

    def __init__(self, origin, data):
        self.uuid = id(self)
        _origin = origin
        if isinstance(origin, str) is False:
            _origin = origin.get_id()
        self.origin = _origin
        self._data = data

    def get(self, k):
        return (self._data or {}).get(k)
