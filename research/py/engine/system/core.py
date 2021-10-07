"""Core functionality for the engine such as DataNetwork, Power and other base elements
"""

from engine import api

signals = api.signals
pipes = api.pipes


from enum import Enum, auto

class Level(Enum):
    """Flag the type of entity for control layers

        CRITICAL
        SUB_SYSTEM
    """
    # There is nothing below CORE, being the _fundamental_ components
    # of an engine, such as power plugs and cables.
    CORE = auto()
    # Critical functions must exist for the ship to function such as life support
    CRITICAL = auto()


class DataNetwork(api.OnOffSwitch):
    """The backbone of all communication through the AFS
    """
    sys_level = Level.CORE
    requires = ('power',)
    sys_type = ('network', )

    async def bind_power_requirement(self, power):
        """The Power module has been picked and in the process of _plugging in_.
        Perform any necessary operations and return a success boolean.

        This isn't in-game, and handles data connections prior to game logic
        actuation.
        This doesn't _turn on_ the device - but moreso _plugs it into_ the socket
        """
        print(f'bind_power_requirement {self.name} to', power.name)

        """In this example we verify the power given matches the internal
        power requirement. By direction 'ours' we perform a test in favour
        of the given power matching our potentials.

        """
        vv = await power.match_many(self.power_requirement(), direction='ours')
        return len(vv) == 2
        # return True

    def power_requirement(self):
        """return the values expected for the power for this instance
        such as a Power(Electric). When being _plugged in_, it should be compatible
        with the target
        """
        return( Power(
                    _name='eric',
                    type=Power.ELECTRIC,
                    watts_per_hour=self.get_watts_per_hour,
                ),  Power(
                _name='derek',
                type=Power.ELECTRIC,
                watts_per_hour=self.get_watts_per_hour() * 2,
            ),)

    async def state_complete(self):
        print(f"\nDevice Complete: {self.name} - ok to attach device.")
        await signals.emit(f'{self.name}.ready')

    async def attach_device_to(self, other):
        print(self.name, 'attach_device_to', other)
        ok = await other.attach_device(self)
        return ok

    async def switch_on(self):
        print('Draw power from device')
        pipes

    def get_watts_per_hour(self):
        """Called by the power unit when required, return a value representing
        watts per hour load of the power.
        """
        return 1.77


class Power(api.OnOffSwitch):
    """Everything needs power, therefore the API has _plugs_ and power input
    for each unit.
    """
    ELECTRIC = 'electric'

    # API Base vars.
    type = ELECTRIC
    sys_type = ('power', )

    # logic based vars
    #
    # Default watts per hour for a power module.
    watts_per_hour = 0
    # Plug-in device slots for power conduits.
    device_slots = 16

    async def app_load(self):
        """API base for internal application management.
        Apply the 'attached' devices board. or alternatively the sync 'mount()'
        method
        """
        print(">> ", self.name, 'App Load')
        self.attached_devices = {}

    async def match_many(self, items, direction='theirs'):
        """Given many items to check, return a list of appliable given
        the internal configuration.
        """
        print(' ', self.name, 'match_many', items)
        res = ()
        for item in items:
            if await self.match(item, direction=direction) is True:
                print('  Accepted', item.name)
                res += (item,)
            else:
                print(f'  Unacceptable (other){item.name} for (self){self.name}')
        return res

    async def match(self, potentional, direction='theirs'):
        """Match the given item to _self_. For variable elements, ensure the
        _other_ item is potentially acceptable, such as watts: the

            potential.watts > self.watts
            True
        The potential is a match as it can accept the internal configuration.

        if the direction is "ours", not the default "theirs", the match direction
        is flipped
        """

        is_type = self.get_type() == potentional.get_type()

        wa = maybe_resolve(potentional.get_watts_per_hour())
        wb = maybe_resolve(self.get_watts_per_hour())

        is_watts_per_hour = (wa <= wb) # ours
        if direction == 'theirs':
            is_watts_per_hour = (wa >= wb)

        print(f"  is_watts_per_hour {potentional.name}(other)={wa}"
              f" >= {self.name}(self)={wb}")

        return is_type and is_watts_per_hour

    def get_type(self):
        return self.type

    def get_watts_per_hour(self):
        """Called by the power unit when required, return a value representing
        watts per hour load of the power.
        """
        return self.watts_per_hour

    async def attach_device(self, pluggable):
        """Called by the in-game logic when required.
        Literally plug in the device to begin power transfer - but not
        necessarily turn the device _on_.

        Return boolean for success
        """
        print(">> Clunk! let's plug-in that socket <> plug; ", self.name, 'plugin', pluggable.name)
        if len(self.attached_devices) >= self.device_slots:
            print('Power socket says no holes left.')
            return False

        pipe = await self.build_pipe(pluggable)
        if pipe:
            print(self.name, 'Attaching Device', pluggable.name)
            self.attached_devices[pluggable.name] = pipe
            return True

        print('build_pipe did not occur')
        return False

    async def build_pipe(self, other):
        """Build an API Pipe to the other entity; allowing communication
        outside the game profile.
        """
        print('? Build pipe from', self.name, 'to', other)
        pipe = api.Pipe()
        res = await pipe.connect(self, other)
        return res

    async def draw_power(self):

import inspect

def maybe_resolve(value):
    """If the given value is a method or function, call and return the value
    else return the value.
    """
    if inspect.isfunction(value) or inspect.ismethod(value):
        # print('Resolving', value.__name__)
        return value()
    return value
