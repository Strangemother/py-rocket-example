from parts import *
# from afeed import FeedEmit, Feed, Tap, Event, DropEvent

class Plug(FeedEmit):

    event_class = PoweredEvent
    amps = 2.2
    volts = 6
    power = dict(watts=-1, volts=volts, amps=amps)

    def get_poweredevent_power(self):
        print('Returning plug conf')
        return self.power

    async def on(self):
        self.power.update(volts=self.volts, amps=self.amps)
        return await super().on()

    async def off(self):
        self.power.update(volts=.2, amps=.001)
        return await super().off()


class Fuse(MaxEnergyExplode, Tap):

    max_power = Energy(volts=12, amps=1)

    async def tap(self, event):
        ok = await self.on_feed(event)
        if ok is False: raise DropEvent(self)
        return await super().tap(event)


class LED(MaxEnergyExplode, FeedEmit):
    max_power = Energy(volts=12, amps=1)

    def explode(self):
        super().explode()
        self.brightness = 0

    async def on_feed_powered(self, event):
        power = event.get_energy()
        # power = event.get_energy(as_int=True)
        await self.set_brightness(power)

    async def set_brightness(self, energy):
        percent = int(energy) / int(self.max_power)
        self.brightness = percent
        # Emit to renderer / state machine.
        print('! brightness', self.brightness)


class Lamp(object):
    plug = Plug()
    led = LED()
    fuse = Fuse('fuse', connect=plug)
    plug_wire = Feed('plug_wire', a=plug, b=led)

    async def setup(self):
        # Connections and _base pipe_ mutations
        await self.fuse.connect()
        await self.plug_wire.connect()
