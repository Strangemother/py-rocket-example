
from base import HostSingleton


# A Live list of states, full of StateDict types.
STATE_MACHINES = {}

UNDEFINED = '__undefined__'


def get_state_manager(_id):
    """Given the owner of the state instance, return a manager for the
    instance. If no manager exists a new one is created.
    """
    # _id = id(owner)
    if _id in STATE_MACHINES:
        return STATE_MACHINES[_id]

    STATE_MACHINES[_id] = sd = StateDict(_id)
    return sd


class StateDict(HostSingleton):
    """A StateDict keeps a persistent cache and dispach place for device states.
    All entities may maintain a state dict with each key reactive to change
    on listeners.

    For a change a single will emit through the singleton host.
    """

    def __init__(self, owner, init_data=None):
        # super().__init__()
        # self.data = {}
        self.owner = owner
        self.data = init_data or {}

    def set_state(self, key, value):
        previous = UNDEFINED
        try:
            previous = self.data[key]
        except KeyError:
            pass

        self.data[key] = value
        print('State', self, key, value)
        self.emit_state(key, previous, value)

    def emit_state(self, key, previous, value):

        self.host.emit_signal('state', 'change',
            state=self,
            key=key, old=previous, new=value)

        name = f"on_state_change"
        method = getattr(self.owner, name, None)
        if method:
            method(key, previous, value)
        else:
            print(f'Entity does noy have function "{self.owner}" : {name}')

    def __repr__(self):
        keys = tuple(self.data.keys())
        return f'<{self.__class__.__name__} {self.owner} {keys}>'


class StateManagerMixin(HostSingleton):
    _state = None

    @property
    def state_manager(self):
        if self._state is None:
            self._state = self.get_state_manager()
        return self._state

    def get_state_manager(self):
        """
        return the state manager for this device, or generate a new one
        through the singleton host.
        """
        return self.host.get_state_manager(self)
