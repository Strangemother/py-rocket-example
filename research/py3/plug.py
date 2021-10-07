
class MalePlug:
    auto_draw_power = False
    other = None

    def __init__(self, owner, **config):
        """Assign a Male Plug to a Pluggable item, something that
        requires 'draw_power'
        """
        self.owner = owner
        self.config = config
        self.__dict__.update(config)
        print('New plug for', owner)

    def connect_to(self, other):
        """Connect this plug (and its attached owner) to the given _other_
        entity.
        Store the _other_ until draw_power is required.
        """
        # Connect this plug into the other device. Likely a socket.
        self.other = other
        print('Connect plug', self.owner, 'to', self.other)
        if self.auto_draw_power:
            print('auto_draw_power', other)
        return True

    def draw_power(self, watts):
        """Ask the _other_ connected entity for the requested power value.
        Apply the value to self.watts and call begin_draw_power on
        the other item, providing self.

        The internal _watt_ request is applied to the event ticker. Later the
        other entity calls `set_given_power`, proving the value of available
        watts.
        The given watts may not match the draw power
        """
        # append pull of watts from other side.
        self.watts = watts
        if self.other is None:
            print(f'{self} for {self.owner} cannot turn on - no "other" entity to draw power')
            return
        print('Draw Power', self.owner, self.other, watts)
        self.other.begin_draw_power(self)

    def undraw_power(self):
        """Apply 0 as the self.watts and call stop_draw_power  on the other
        item.
        """
        # append pull of watts from other side.
        print('UnDraw Power', self.owner, self.other, self.watts)
        self.watts = 0
        self.other.stop_draw_power(self)

    def set_given_power(self, watts):
        """The socket 'other' adapted the available power. Assign
        to the owner.
        """
        self.available_power = watts
        self.owner.set_given_power(watts)

    def __repr__(self):
        return f'<{self.__class__.__name__} {id(self)} of {self.owner}>'
