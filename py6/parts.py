from feed import FeedEmit, Feed
from tap import Tap
from base import Event

from exceptions import DropEvent
import asyncio


class Energy(object):
    """
        What are Amps, Volts, and Watts?

        Amps: Amperes, commonly known as amps, measure the flow of electricity as
            an electric current. Specifically, they measure the amount of electrons
            that flow past a certain point per second. A common analogy used to describe
            how amps work is a garden hose.  Amps can be compared to the volume
            of water flowing through the hose. The more gallons of water flowing
            through the hose per minute, the stronger the current. Or, as the
            number of electrons flowing past a certain point per second increases, so do the amps.

        Volts: How do we make those amps flow? Voltage. In sticking with the garden
            hose analogy, voltage is similar to the water pressure in the hose.
            The pressure, or force, is what causes the water to flow. Volts are a
            measure of how much force each electron is under, which is called
            "potential.” Potential is what causes electricity to flow. The difference
            between volts and amps is that amps measure the volume of electrons
            flowing while volts measure the pressure causing them to flow.

        Watts: Amps and volts combine to create watts, a measurement of the amount
            of energy being released. In the case of the garden hose, this would
            be the amount of water flowing. The higher the wattage, which we now
            know is the combination of electrical potential and flow, the more
            power and output we'll see. For example, the more wattage a microwave
            has to offer, the faster it will cook your food.
    """
    def __init__(self, watts=None, volts=None, amps=None):
        self.watts = watts
        self.volts = volts
        self.amps = amps

    def as_float(self):
        return self.get_watts()

    def get_watts(self):
        # Watts = Amps x Volts
        # 10 Amps x 120 Volts = 1200 Watts
        # 5 Amps x 240 Volts = 1200 Watts
        return self.amps * self.volts

    def get_amps(self):
        # Amps = Watts / Volts
        #     4160 Watts / 208 Volts = 20 Amps
        #     3600 Watts / 240 Volts = 15 Amps
        return self.watts / self.volts

    def get_volts(self):
        # Volts = Watts / Amps
        #     2400 Watts / 20 Amps = 120 Volts
        #     2400 Watts / 10 Amps = 240 Volts
        return self.watts / self.amps

    def __gt__(self, other):
        _int = other
        if isinstance(other, self.__class__):
            _int = int(other)
        return int(self) > _int

    def __lt__(self, other):
        return int(self) < other

    def __int__(self):
        return round(self.as_float())


class CallAutoConnect(object):

    auto_connect = None

    async def setup(self):
        await self.do_auto_connects()

    async def do_auto_connects(self):
        connects = self.auto_connect or ()
        for item in connects:
            await item.connect(owner=self)


class PoweredEvent(Event):

    def __init__(self, origin, data):
        super().__init__(origin, data)
        self.power = self.load_power_conf(origin, key='power')

    def load_power_conf(self, origin, key, default=None):
        e_conf = default or dict(watts=-1, volts=6, amps=3)
        e_conf = self.load_parent_conf(origin, key, e_conf)
        return Energy(**e_conf)

    def load_parent_conf(self, origin, key, default=None):
        res = default
        name = f'get_{self.__class__.__name__}_{key}'.lower()
        if hasattr(origin, name):
            res = getattr(origin, name)()
        return res

    def get_energy(self, as_int=False):
        if as_int:
            return self.power.as_float()
        return self.power


class MaxEnergyExplode(object):

    max_power = Energy(volts=12, amps=3)
    broken = False

    async def on_feed(self, event):
        if self.broken:
            # print(self, 'is broken')
            return self.explode()
        # data from an input pipe. Let's hope it's Energy < max.
        ok = self.test_wire_power(event)
        if ok:
            return await self.on_feed_powered(event)
        return ok

    async def on_feed_powered(self, event):
        print('power feed')
        return True

    def test_wire_power(self, event):
        print('test_wire_power')
        energy = event.get_energy(as_int=True) # Volt/Amp/Watts
        if energy > self.max_power:
            self.explode()
            return False
        return True

    def explode(self):
        s = f'\n{self}pop!'
        if self.broken:
            s = f'{self} Bizzzfizz ... futz futz'
        print(s)
        self.broken = True
        return False

