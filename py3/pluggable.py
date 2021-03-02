from plug import MalePlug


class PlugWattsMixin(object):
    def get_watts(self):
        return self._watts

    def set_watts(self, v):
        if self._watts != v:
            print(f'Change watts {self} == {v}')
        self._watts = v
        self.draw_power(self._watts)

    watts = property(get_watts, set_watts)


class ChangePowerMixin(object):
    """A single function handler for "set_given_power", called by a
    socketable _other_ for the input power.
    If the value != self.available_power, "change_power" signals a change.
    """
    def set_given_power(self, watts):
        """The socket 'other' adapted the available power. Assign
        to the owner.
        """
        if watts != self.available_power:
            self.change_power(self.available_power, watts)

    def change_power(self, old_value, new_value):
        """The power value has changed from "old" to "new".
        Set the current "available_power" with the new value.
        """
        print(f'{self} has power from', self.available_power, 'to', new_value)
        self.available_power = new_value


class Pluggable(object):
    """The entity has a literal plug to connect into a socket. Consider
    a single power lead; with A (Pluggable) MakePlug, and B (Socket) FemalePlate

    The self.plug should be connected to the _other_ item. on() and off() call
    the plug draw_power() and undraw_power(), with the expected watts
    The self.plug will likely yield a call upon the self[set_given_power]
    hopefully receiving the same watts input as requested through draw_power.

    psuedo code:

        light = Light(Pluggable, watts=10)
        light.plug.connect_to(female)
        light.on()
        light.pb()
        "67%"
        light.off()
    """
    # plug = Plug()
    _watts = 3
    _on = False
    extra = None
    plug_class = None # MalePlug
    plug_config = None # {}

    def __init__(self):
        self.make_plug()

    def make_plug(self):
        self.plug = self.get_plug_class()(self, **self.get_plug_config())

    def get_plug_class(self):
        return self.plug_class or MalePlug

    def get_plug_config(self):
        return self.plug_config or {}

    def on(self):
        print(f'Turn on {self}')
        self._on = True
        self.draw_power(self._watts)

    def off(self):
        print(f'Turn off {self}')
        self._on = False
        self.plug.undraw_power()

    def is_on(self):
        return self._on

    def is_off(self):
        return not self._on

    def draw_power(self, val):
        """Pull the given value from the self.plug, initating a chain casacade
        of dependencies through the event tick.
        """
        return self.plug.draw_power(val)

    def get_extra(self):
        return f" {self.extra}" if self.extra else f" {self._watts} watts"

    def __repr__(self):
        return f'<{self.__class__.__name__} {id(self)}{self.get_extra()} on:{self._on}>'


class PowerReceiver(Pluggable, ChangePowerMixin, PlugWattsMixin):
    """An entity with a plug, and the handlers to manage the power change
    """
    def __init__(self, **kw):
        self.__dict__.update(**kw)
        super().__init__()
        self.available_power = .002 #background noise
        self.created()

    def created(self):
        pass

    def change_power(self,old_value, new_value):
        """The socket 'other' adapted the available power. Assign
        to the owner.
        """
        self.extra = f'{self._watts}W (act.) {new_value}W'
        super().change_power(old_value, new_value)
