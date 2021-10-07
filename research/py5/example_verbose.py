
class OldLED(FeedEmit):

    max_power = Energy(volts=12, amps=3)
    broken = False

    async def on_feed(self, event):
        if self.broken: return
        # data from an input pipe. Let's hope it's Energy < max.
        wire_power = event.get_energy(as_int=True) # Volt/Amp/Watts
        self.set_power(wire_power)

    def set_power(self, energy:Energy):
        if energy > self.max_power:
            self.explode()
        self.set_brightness(energy)

    def explode(self):
        print('pop!')
        self.brightness = 0
        self.broken = True

    def set_brightness(self, energy):
        percent = int(energy) / int(self.max_power)
        self.brightness = percent
        # Emit to renderer / state machine.
        print('brightness', self.brightness)


class LampA(object):
    plug = Plug()
    led = LED()

    async def setup(self):
        # Connections and _base pipe_ mutations

        tap = Tap(uuid='fuse')
        plug_wire = Feed('plug_wire')

        # Bind the 'fuse' to the 'plug'['emit']
        await tap.connect(self.plug)
        # Capture plug emits to the led through this 'wire'
        await plug_wire.connect(self.plug, self.led)

        self.feed_plug_wire = plug_wire
        self.tap_fuse = tap

