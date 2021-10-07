


class PowerUnit:
    """An entity to _push_ power though a terminal, expecting a circuit loop
    to resolve back to this unit through the power event chain.
    """

    def on_attach(self, circuit):
        """The power unit is attached to the given circuit.
        Generally a power unit emits power, therefore a Power event may be
        dispatched to the circuit immediately.

        A Power unit may have a _switch_, and may not be enabled when attached.
        This should be solved through a previous test event and circuit mapping,
        ensuring all terminals connect in a closed loop.
        """

class PoweredDevice:

    def on_power(self, event):
        """A new power event
        """
        if self.enabled is False:
            # Do nothing, I'm broken.
            return

        # example some setup
        self.is_powered = self.first_power_up(event)

        return self.on_power_change(event)

    def on_power_change(self, event):
        """The existing power chain is updating to new values
        Adapt the component, such as exploding on too much power
        """

    def on_power_loss(self, event):
        """The power to this device is gone. turn off the unit of which emits
        a signal to the circuit
        """
        # Consider: implement charge down delay

        # The event contains volts=0, amps=0, resulting in zero light.
        self.on_power_change(event)


class LED(PoweredDevice):
    """A simple example of a powered device, using energy.
    """
    power_in = Terminal(type=Power, polarity=IN)
    power_out = Terminal(type=Power, polarity=OUT)

    volts = 3
    amps = .200
    max_power = volts * amps

    def on_power_change(self, event):
        self.change_brightness(event.volts, event.amps)

    def change_brightness(self, volts, amps):
        if volts * amps > self.max_power:
            return self.explode()

        # Percent of light.
        self.brightness = self.max_power / volts * amps

    def explode(self):
        """The LED explodes into a smelly dark smudge. Inform the interface
        and flag the circuit.
        """
        self.enabled = False
        print('POP!')


class Wire:

    current_lifetime = hours(10_000) #age
    max_lifetime = hours(1_000_000)
    heat = celcius(22) #room temp
    enabled = True
    limit_amps = 10
    limit_volts = 200

    def transmit_degrade(self, event):
        """A power or data event in to result out with alterations given the
        state of the wire. If the wire is not enabled (e.g _burnt out_),
        transmission will not occur.
        """
        _volts = min(event.volts, self.limit_volts)
        _amps = min(event.amps, self.limit_amps)

        self.heat *= (event.volts - _volts) * (event.amps - _amps)# some max discharge

        event.volts = _volts
        event.amps = _amps

        if heat > 100:
            self.burnout()
            event.flag_stop(self)

        return event

    def burnout(self):
        self.enabled = False
        print('Ftttzzz....')

class Circuit:
    """A Circuit manages connections through Terminals and distributes Power
    events with computiation through Wire (edges)

    To connect 2 or more items, a Circuit should manage the graph connections
    between siblings.
    """
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.terminals = {}
        self.wires = {}
        self.connections = defaultdict(set)

    def connect_terminals(self, terminal_a, terminal_b, wire=None):
        """Connect two terminals through a Wire. If the Wire is None, a
        default Wire is created.

        Each terminal exists on a PoweredDevice. This circuit should close LOOP
        allowing the complete circuit to power
        """
        wire = wire or self.default_wire(terminal_a, terminal_b)
        self.wires[id(wire)] = wire

        self.terminals[id(terminal_a)] = terminal_a
        self.terminals[id(terminal_b)] = terminal_b

        self.through[id(terminal_a) + id(terminal_b)] = id(wire)

        self.connections[id(terminal_a)].add(id(terminal_b))

    def default_wire(self, a=None, b=None):
        """Create a new wire optionally using the two terminal ends.
        """
        return Wire(limit_volts=200, limit_amps=10) # cheap wire
