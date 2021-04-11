A Terminal defines a _throughput_ for the given device, as a Power or Data event
port. This entity help solve the circuit loop and _in game_ presented terminals
for a hardware device.

A Terminal acts as an IN or OUT, Power or Data entity. Every connection within a Circuit should manifest through a chain of terminals, connected with logical _wires_. For Power events, the Terminal should pattern an IN OUT attachment through all
units within the circuit. If terminals match polarity (e.g IN <> IN), the wire heats up. This is solved within the circuit power event chain.


```py
class AThing(Unit):
    power_in = Terminal(type=Power, polarity=IN, volts=4, amps=1)
    power_out = Terminal(type=Power, polarity=OUT)
```
