

import power, pluggable
from plug import MalePlug


class FemalePlate(power.PowerEmitter):
    """A Female Plate acts similar to the socket of a plug<>socket pair,
    accepting a MalePlug type of connection.

        light = Light()
        plugs = FemalePlate()
        plugs.add(light)
        light.on()
        light.pb() # '67%'
    """
    socket_count = 20
    _powers = ()
    def __init__(self, **kw):
        super().__init__()
        self.sockets = ()

    def add(self, *pluggable):
        """Add one or more items in 'connect' fashion.
        """
        for item in pluggable:
            ok = self.connect(item)
            if ok is False:
                print('Fail connect for',item)

    def socket_match(self, other):
        if isinstance(other, MalePlug):
            return True

    def connect(self, pluggable):
        if len(self.sockets) >= self.socket_count:
            return False
        # MalePlug.connect_to
        if self.socket_match(pluggable) is False:
            print('Given plug', pluggable, 'does not match female socket')
            return False

        is_connected = pluggable.plug.connect_to(self)
        if is_connected:
            self.sockets += (pluggable.plug,)
        print(f'connected {pluggable} to {self} == {is_connected}')
        return is_connected

    def get_extra(self):
        return f" {self.extra}" if self.extra else f" {self._powers}"


class Light(pluggable.PowerReceiver):

    def created(self):
        print('new light', self.watts)

    def brightness(self):
        """Return a 0-1 percent of light given the total expected
        to available watts
        """
        return self.available_power / self.watts

    def pb(self):
        """Return string percent of brightness
        """
        b = self.brightness()
        return f"{b*100:.1f}%"
