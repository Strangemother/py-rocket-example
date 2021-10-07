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
        print(f'! {self} brightness: {percent*100}%')


class LampManual(object):
    plug = Plug()
    led = LED()
    switch = Tap('switch', connect=plug, enabled=False)
    fuse = Fuse('fuse', connect=plug)
    plug_wire = Feed('plug_wire', a=plug, b=led)

    async def setup(self):
        # Connections and _base pipe_ mutations
        await self.fuse.connect()
        await self.plug_wire.connect()

        self.switch.key='switch'
        self.switch.say='>> switch {enabled}'
        await self.switch.connect()


class Wire(Feed):
    async def perform(self, event):
        print('... wire feed', event)
        return event


class ToggleSwitch(Tap):
    enabled = False
    key = 'switch'
    say = '>> switch {enabled}'

    def toggle(self):
        self.enabled = not self.enabled
        print(f'{self} toggle = {self.enabled}')


class Lamp(CallAutoConnect):
    plug = Plug()
    led = LED()
    switch = ToggleSwitch(connect=plug)
    fuse = Fuse(connect=plug)
    plug_wire = Wire(a=plug, b=led)

    # parts.CallAutoConnect
    auto_connect = (plug, led, fuse, plug_wire, switch,)

    async def setup(self):
        await super().setup()
        await self.build_powerchains()

    async def build_powerchains(self):
        """Create connections for power push conditions.
        from plug to led

        This builds a condition Ensuring each entity in a chain is _enabled_.

        On true, call led, "on_power_event(powerEvent)"

        """
        print('build powerchain')
        mem = self.plug.get_memory()
        import pdb; pdb.set_trace()  # breakpoint f70b5fbd //

