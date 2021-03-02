# Plugs and Feeds

A 'lamp' has three components.

+ LED
+ switch
+ Plug

The led feeds data from the plug through the Lamp component. The
switch will _tap_ into the feed from the plug, changing the Feed rate or value.

A Feed may _Transmit_ any information streamed from A to B, The digesting
components accept the input as required; notably _power_ or _data_.

    Lamp:
        led = LED
        switch = ToggleSwitch
        plug = PlugUK

        setup():
            feed = plug.feed(led)
            switch.tap(feed)

The plug connects to an external _receiver_ - a socket - enabling a feed from
plug "socket" to "plug". The data feed should emit change conditions, altering
the plugs _current state_.


    lamp = Lamp()
    socket = WallSocket(on=True) # Enabled auto feed
    feed = connect(lamp.plug, socket.port[0])
    feed.enabled == True

Given the socket is _enabled_ the feed is established from A to B. The "lamp plug"
is expecting input and should manage its internal state, in turn sending
the feed to the "led".

A _thing_ or a sub-component of a device will expect a feed of changes, reading
the feeds for continued changes, or settings internal states for continued feed
emission. In this case, a simple LED has no wiring. A more complex LED may have
literal pin-contacts. Something the API will provide:

```py
class LED:
    positive_pin = Pin('A')
    negative_pin = Pin('B')

class Lamp:
    setup():
        pfeed = plug.positive.feed(led.positive_pin)
        nfeed = plug.negative.feed(led.negative_pin)
```

## Feed

A Feed class represents a connection of two entities. The two connected entities
have no hard coded binding, and "messages" emit through the feed will connect
to the chosen output "receivers". Disabling the feed (or with no feed existing),
two units will not interact.

On each side of a Feed, the given units expect feeding. The receiver "on_feed",
propagates the event from through its internals. Potentially another feed.

---

Here we identify the lamp _plug_ connects to the _led_. The plug will emit
events, given to the `lamp.led.on_feed(event)`.

```py
feed = Feed(plug, led)
# same as
feed = plug.feed(led)
```

Notably an incorrect setup would not feed correctly. Synonymous to wiring a plug
backward.

    feed = Feed(led, plug) # led into the plug.

There when the plug emits an event, forward feeds won't exist. In this case, the
API may help -

```py
class Feed:
    init(a, b):
        if b.is_female and a.is_male:
            # switch
            a,b = b,a
        print(f'Plugging {a} into {b}')

feed = Feed(led, plug) # led into the plug.
```

But this may not be the _wanted_ configuration, for allowing
_advanced_ setup with "poor wiring" is an alternative option

```py
class Feed:
    def __init__(a, b):
        assert self.opposite_of(a, b)

    def opposite_of(self, a, b):
        """Test to ensure the b entity is the same as this"""
        is_same_type = a.socket_type == b.socket_type
        b_is_wire = b.socket_type == SOCKET_TYPE.WIRE
        # A and B are a wire.
        if is_same_type and b_is_wire: return True
        print(self,' is same as', b, '==', is_same_type)
        return (not is_same_type)
```


The receiver should manage input events manually

```py
class LED:

    max_power = Energy(volts=12, amps=3)
    broken = False

    def on_feed(self, event):
        if self.broken: return
        # data from an input pipe. Let's hope it's Energy < max.
        wire_power:Energy = event.get_energy(as_int=True) # Volt/Amp/Watts
        self.set_power(wire_power)

    def set_power(self, energy:Energy):
        if wire_power > max_power:
            self.explode()
        self.set_brightness(energy)

    def explode(self):
        print('pop!')
        self.brightness = 0
        self.broken = True

    def set_brightness(self, energy):
        percent = energy / max_power
        self.brightness = percent
        # Emit to renderer / state machine.
```

Therefore a Plug may emit data events nominally, when content is incoming

```py
class Plug:
    enabled = True

    def on_feed(self, event):
        if self.enabled:
            self.send_feeds(event)


class WallSocket:
    port = (
        Socket(), Socket(),
        )


class Socket:

    def on(self):
        event = Energy(volts=12, amps=1)
        self.emit_feed(event)


socket = WallSocket()
feed = Feed(socket.port[0], lamp.plug)
socket.on() # -> event:Energy -> lamp.plug.on_feed(event)
```
