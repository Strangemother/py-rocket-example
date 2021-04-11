The Power event path is pre-computed by the circuit through prelimary setup and change
events given by connected units. This simplifies the instant like connection of energy.

+ A Power event emits from a unit
+ The circuit passes this events to CLOSED loop siblings
+ The Power event changes per iteration


## Unit Connection

A Units connects to a circuit through its Terminals



## Power Event flow

?How do you enable a persistent event flow?
?Path of least resistence?

The user should instigate a 'circuit' connection of a unit. By connecting a battery to a Light through the interface, a circuit maps the two units. The circuit manages the IO of each unit, emiting signals given the event power cycle.


# Sim Test (Pre check)

The power flow must be pre-tested before the unit works. This occurs when the unit is attached to a Circuit.
In the real work this emits as an immediate flow of electrons through the path of least resistance. To simulate this the Circuit emits a "Fuzz" power event. The attached unit should accept this and dispatch across the expected output.

This should flag as a test or _low voltage_ to ensure the unit does not react:


```py
class USB:
    """A example USB with 4 pins. The Terminal type is expected to _hint_ the
    circuit, but may not be required.
    """


    def on_positive_event(self, event:Power):
        if event.test_event:
            event.give_to(self.negative)
            return

        # do something with power.

    def on_negative_event(self, event:Power):
        """Do nothing. Power should not come into the negative terminal.
        """
        pass

    positive = Terminal(type=Power, on_positive_event)
    negative = Terminal(type=Power, on_negative_event)
    data_1 = Terminal(type=Data)
    data_2 = Terminal(type=Data)
```

---

This ensures the engine can initially map the power distribution before usage.



A


# Examples

Fuse example:

```py
class Fuse:
    """A Fuse has two connections with no direction.
    """
    def send_to_other(self, origin:Terminal, event:Power):
        """Send the power event though to the other terminal, as long as it's
        within the limits.
        """

        others = self.get_terminals().remove(origin) # list
        event.give_to(others)

    one = Terminal(on_event=send_to_other, with_origin_terminal=True)
    two = Terminal(on_event=send_to_other, with_origin_terminal=True)
    # Setup terminals definitions
    #

class Battery:
    """A Standard battery emits power and recieves events from itself to
    enable the event.

    Using the standard circuit flow direction, not the electron flow direction.
    """
    def positive_in(self, event:Power):
        """No power should by pushed into the battery positive terminal.
        Call upon the internally api "heat discharge", converting the amount
        of power into melting.
        """
        self.heat_discharge(event)

    def negative_in(self, event:Power):
        """Given the power emits from _this_ terminal sibling, accept the event,
        allowing the power to flow.
        """

        if event.origin == self.positive:
            event.accept()



    positive = Terminal(on_event=positive_in)
    negative = Terminal(on_event=negative_in)

```
