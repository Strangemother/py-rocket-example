from base import Base, HOST
from connection import Connectable, ConnectionManager
from state import StateManagerMixin, get_state_manager
from collections import defaultdict



class BaseSystem(Base):
    """Base manager for the system API. This is not game exposed - moreso
    being a background host for all core game utilities, such as the raw
    connections and breadboard.
    """

    def __init__(self):
        self.bound = defaultdict(list)
        # self.items = []

    def bake(self):
        """Apply this base system as the HOST system, enabling all other
        units to utilise as the host.
        """
        HOST['system'] = self

    def bind(self, other):
        """Apply the given connectable item to the _bound_ list within this
        entity, ensuring signals occur without a connection.
        """
        # self.items.append(other)
        self.bound[other.name].append(other)

    def get_connection_manager(self):
        return ConnectionManager(system=self)

    def get_state_manager(self, owner):
        """Given the owner of the state instance, return a manager for the
        instance. If no manager exists a new one is created.
        """
        # _id = id(owner)
        return get_state_manager(owner)

    def emit_signal(self, *keys, **kwargs):
        print('Emit signal', keys)
