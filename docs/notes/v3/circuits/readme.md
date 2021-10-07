An attempt to rethink and build _tapped pipes and wires_ for ingame components,
focusing on simplicity.

Using Async and a clean mizin style build, each )unit_ can append and connect
to an existing interface of _wires_. A simple class like `Connection` handles
the _wire_ communication for two units. This allows extended coupling of communicative componets.

A main problem arises through the _switched_ connection of a complex object.
If a linear list of units is connected with a _switch_ in the center, all units after the switch should work when the switch is _on_.

When enabling a switch, the bridged state should allow the flow of _events_.


Each unit should have a power terminal set, applied to a _switchboard_ of _pipes_.
The switchboard manifests as a Graph, connecting nodes through events. Applying a nodes terminals enables data flow from the graph.

When a unit is _turned on_ it may _request power_ from the connected units. This is done through the event graph - by sending an event and reading siblings. A unit may read the sibling unit data, accepting info as events.

```py

class Unit:
    def on_connect(self, other):
        if other.is_powered():
            power = Power(volts=12, amps=1)
            other.request_power_draw(self, power=power)
```


Every unit is applied to a Circuit, allowing the bound closed flow of electrons, simulating the electronic breadboard. The circuit identifies as a mini graph of "units" through "connection" edges. Upon an event change the circuit may react to events such as "off" and disable flow to other units.

When a unit event occurs, the Circuit manager distributes the events to the correct siblings. Direct handling of a cicuit by the developer is not required, with graph bridging occuring automatically through terminals.

