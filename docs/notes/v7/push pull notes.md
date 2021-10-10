Power and data events are the same thing. A data event is a power event with a minute voltage or amp. A Terminal for any node receives Power or Data to optionally emit the same (or less) power, or some data.

A unit can communicate through its OUT terminals. In the theory a Terminal may PULL events, or PUSH events. Some terminals may be universal (e.g a USB is both) and the unit can act accordingly. Events in and out occur from a parent Circuit. A Terminal isn't immediately aware of siblings - mearly the events given from a circuit.

Logically a cicuit is a Dictionary and event manager. Upon a child (Unit) event the Circuit evaulates the event possibility. If a circuit is _off_ the event does nothing _past_ the switch.


# Circuit

A small event graph managing connected units and events through Terminals.
Every unit connects to a circuit and may receive Power or Data events. The Circuit ensures events distribute to the correct unit clients, with altered event signal information.

Each event step alters the _power_ and _signal_ of the event. The circuit passes the event to the next sibling within the tree connected children until the event progagates to the original entity, or is destroyed through the loop by unit intervention.

---

Following an event, a Unit emits a Power or Data in OUT state, such as `Power(volts=12, amps=3)`. The circuit dispatches the event to the next sibling and waits for a change.

---

## Logical

A circuit can manfiest as a table of units with power calculations.


# Age

Every unit has an age. Older age degraged functionality, specific to its max norms.

e.g:

+ Unit life cycle is 10k hours


## Power

The event of power draws inspiration from standard electronics.

The power event must cycle through the entire circuit before the _power draw_ can occur for all units. Upon a new power event the circuit will only push the event if all units are correctly attached. The 'is circuit closed' variable is determined before the event occurs.

If all unit _functionality_ is enabled, and all terminals are connected the power state is send to the closed loop. Each unit should manage the power event and return a _change_ for the circuit to continue.


---

In this case, the state of 'switching' acts as a state manager. An attached unit sends an enablement event (off or on for example) and the circuit records the updated loop state. If the circuit is okay to dispatch events, each unit will recombobulate the information to spec.

+ Switches. Given their default _off on_ state, if off the power events do not emit.
    To ensure a device unit _has power_ within a switched circuit, is should _hotwire_ another terminal output.


# Resistor

A resistor removes a portion of energy, returning a smaller subset, such as 90% the original with a max. A List of resistors in series simply computes the power through a range of percentiles.

# Capacitor

A capacitor receives power events over a give period, to emit power signals after a certain charge occurs. This is a little tricker regarding as the power should contain power phase and frequency. Dealing with time this asks for a timer.

Therefore to cheat we can use a sinoidal wave to compute peaks for a discharge rate. The test event contains a 'sine wave' or hertz of change. The capacitor can compute the _expected_ power event for each cycle rather than a real event. Power update events will change this at later intervals.

To deal with _emission_ of the OUT event, during the _test_event_ phase, the returned event includes an altered phase change of which is stepped into phase upon the next iteration.

The siblings receive a power event with the new wave and may optionally normalise the input (default) or refuse the event (e.g. a "lower power conversion")

https://mechatrofice.com/circuits/charging-capacitor-derivation

1. Somehow return a sigma function of charge over time
2. emit an altered event

---

Normally a capacitor emits out events with a cycle fast enough to use, therefore in _game life_ this shouldn't be a factor. Therefore upon each iteration of the Circuit siblings, the power frequency is tested to _be within a range_.

```py

class Capacitor(Unit):
    def on_positive_event(self, event:Power):
        if event.test_event:
            event.
            event.give_to(self.negative)
            return

        # do something with power.

    def on_negative_event(self, event:Power):
        """Do nothing. Power should not come into the negative terminal.
        """
        pass

    positive = Terminal(type=Power, on_positive_event)
    negative = Terminal(type=Power, on_negative_event)

```

# Wire

Connects A to B with minor resistance.

# Fuse

A Fuse has no polarity. Allow an event in, and send it to the OUT without change.
If the power is greater than the limit - pop, sending an _enabled=False_ to the parent circuit. This should OPEN the closed circuit and kill the loop.


# Battery

A Battery has two Terminals, PULL and PUSH. Upon connection the battery emits a `continuous` Power event. energy must travel within a closed loop, therefore the circuit should ensure the circuit is _closed_ before all "series" connected elements accept the power.

The circuit receives the Power type event


# USB

Four
