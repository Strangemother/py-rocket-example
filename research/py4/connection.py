from collections import defaultdict
from base import Base, HostSingleton
from sockets import SocketMixin


class Connection(Base):
    """ A connection binds two entities together though a bi-directional
    event signal-like handling.
    """

    # count of devices expected for this connection. By default 2
    device_count = 2

    def __init__(self, *devices):
        """Store the many devices to prepare a connection. A device should
        have a `socket` to asset during compatiblity tests.
        """
        self.devices = devices

    def is_compatible(self):
        """Test if the given devices are compatible for a connection.

        This does not check wiring or throughput - moreso if the endpoints can
        literally _plug in_.

        Return boolean.
        """
        if self.assert_device_count() is False:
            return False

        a, b = self.devices
        return a.socket.opposite_of(b.socket)

    def assert_device_count(self):
        return len(self.devices) == self.device_count

    def __repr__(self):
        return f'<{self.name}: {self.devices}>'

    def set_device_state(self, device, key, value):
        """
            con.get_device(self).state_manager.enabled = True
            con.set_device_state(self, 'enabled', True)
            self.state_manager.enabled = True
            self.state_manager['enabled'] = True
            self.state_manager.set_state('enabled', True)
        """
        #device = self.get_device(device)
        device.state_manager.set_state(key, value)



class ConnectionManager(HostSingleton):
    """Manage many connections in a queryable list like.
    """
    def __init__(self, **kwargs):
        self.items = defaultdict(tuple)
        self.uuids = defaultdict(dict)
        self.__dict__.update(kwargs)

    def get_names(self, a, b):
        return [f'{a.name}-{b.name}', f'{b.name}-{a.name}']

    def get(self, entity, name=None):
        uuid = id(entity)

        if uuid in self.uuids:
            if name is None:
                # return all
                return tuple(self.uuids[uuid].values())

            # return list of 1 for the connect name
            return (self.uuids[uuid][name],)
        # not a uuid entity.
        return ()

    def add(self, a, b, name='default'):
        """Add a connection to the connection manager from the given _a_ to _b_.
        If B is None, the A is assumed a Connection type and managed thusly.

        If A And B are defined, a new connection is made.
        The connection binds vis ID to the lists and a new connection>new
        event emits from the host.
        """
        connection = a
        names = self.get_names(a,b)

        if b is not None:
            connection = Connection(a,b)

        for subname in names:
            self.items[subname] += (connection, )

        self.uuids[id(a)][name] = connection

        self.host.emit_signal('connection', 'new', connection)
        return connection

    def exists(self, a, b=None):

        if b is None:
            return id(a) in self.uuids

        keys = self.items.keys()
        for name in self.get_names(a,b):
            if name in keys: return True
        return False

    def remove(self, a, b):

        for name in self.get_names(a,b):
            if (name in self.items) is False:
                continue

            for connection_pair in self.items[name]:
                (x.remove_connection(self) for x in connection_pair)

            self.items.pop(name)


class ConnectionManagerMixin(HostSingleton):
    _connections = None

    @property
    def connections(self):
        if self._connections is None:
            self._connections = self.get_connection_manager()
        return self._connections

    def get_connection_manager(self):
        return self.host.get_connection_manager()


class Connectable(ConnectionManagerMixin, SocketMixin):
    """A Mixin to identify and apply functions to a device. If it's
    _connectable_, it may signal to another connectable through a bound
    connection.

    Binding entities to a connection ensures the two units communicate through
    an externally managed singular channel. Connection Taps may alter the
    cleanliness of the two utils - similar to a wire.
    """

    def connect_to(self, other):
        """Connect this item to the other item through a connection.

        Example connecting lamp (self) to other (wall_socket) through a PlugUK
        socket. If the connection is allowed, generate a new Connection and
        store to the _other_.
        """
        if self.can_connect_to(other):
            return self.perform_connection(other)
        raise Exception(f'Cannot connect to other "{other}"')

    def perform_connection(self, other):
        """Connect the two devices
        """
        if self.is_connected():
            self.disconnect()

        print(self, 'perform connection to', other)
        return self.connections.add(self, other)

    def disconnect(self, other=None):
        """remove the Connection of self to _other_ if it exists.
        If the given other is None, disconnect all connections
        """
        self.connections.remove(self, other)

    def is_connected(self, other=None):
        """Assert if this device is connected to another device through a
        Connection. If the given `other` is None, _any_ connection is tested
        for existence.
        """
        return self.connections.exists(self, other)

    def can_connect_to(self, other):
        """Test if this unit it compatible with the _other_ device through the
        socket connection. Return boolean, True for _yes_ and False for _no_.
        """
        return Connection(self, other).is_compatible()
