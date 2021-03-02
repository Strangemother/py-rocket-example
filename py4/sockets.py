from base import Base

class SOCKET_TYPE:
    # A wire as in a single bi-directional
    WIRE = '__WIRE__' #0
    MALE = '__MALE__' #1
    FEMALE = '__FEMALE__' #2


class Socket(Base, SOCKET_TYPE):
    """ A Male Female type connection for a two way bound socket through a
    connection. The connectable will connect through a socket type, and its
    sex. For example a UK Plug socket as MALE and FEMALE 3PIN.
    """
    socket_type = SOCKET_TYPE.WIRE
    owner = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def opposite_of(self, other):
        """Test to ensure the other entity is the same as this
        """
        is_same_type = self.socket_type == other.socket_type
        other_is_wire = other.socket_type == SOCKET_TYPE.WIRE
        # A and B are a wire.
        if is_same_type and other_is_wire:
            return True
        print(self,' is same as', other, '==', is_same_type)
        return (not is_same_type)


class Watts(object):
    """The content throughput for the mapped pins. When applied, the
    calculated _pull_ and _push_ of the "content", in this case electricity.
    """


class Feed(object):
    """The conceptual "pin" throughput on the feedpin - or a connection tip
    of two entities and the pin map.

    The "enable" starts the flow. Each side of a connection (its socket) has a
    pinmap with a list of feed entities.
    """
    _enabled = False
    name = None

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def enable(self):
        self._enabled = True
        return self._enabled


class FeedPin(object):
    _feeds = None

    @property
    def feeds(self):
        if self._feeds is None:
            self._feeds = self.get_feeds()
        return self._feeds


    def get_feeds(self):
        return (Feed(name='pin'),)

    def enable(self):
        """Enable the pin and feeds within, allowing the data stream to occur.
        """
        print('Enable ping feed', self, self.owner, self.owner.socket_type)
        for feed in self.feeds:
            feed.enable()


class ThreePin(FeedPin):
    """The pin map class defines the feeds for the socket type.
    A three pin map class and its associated throughput class of Watts
    define the standard plug type Ground, Live, Neutral.
    """

    def __init__(self, owner, **kw):
        self.owner = owner
        self.__dict__.update(kw)

    throughput_class = Watts

    def get_feeds(self):
        return (
            Feed(name='ground'),
            Feed(name='neutral'),
            Feed(name='live'),
            )




class PinMapMixin(object):
    _pin_map = None
    pin_map_class = FeedPin

    @property
    def pin_map(self):
        if self._pin_map is None:
            self._pin_map = self.pin_map_class(owner=self)
        return self._pin_map


class PlugUK(Socket, PinMapMixin):
    """A UK Plug socket complete with 3 pins

    socket_type
    """
    pin_map_class = ThreePin

    def enable_flow(self):
        """
        Start the flow for one side of the bound connection.
        """
        print('\nEnable plug.', self, 'type', self.socket_type, self.owner)
        cons = self.owner.connections.get(self.owner)
        print(cons)
        self.pin_map.enable()
        # for con in cons:


    def disable_flow(self):
        """
        Start the flow for one side of the bound connection.
        """
        print('disable plug.', self)


class SocketMixin(object):
    """An entity may have a socket, such as plug FEMALE. Apply the socket
    or a socket_class

        class Light(Connectable)
            socket_class = Socket
    """
    _socket = None
    socket_type = None
    socket_class = Socket

    @property
    def socket(self):
        if self._socket is None:
            self._socket = self.make_socket(self.socket_type)
        return self._socket

    def make_socket(self, socket_type):
        """Generate and return a new socket of the given type.
        """
        return self.socket_class(owner=self, socket_type=socket_type)

