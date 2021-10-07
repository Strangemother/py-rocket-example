"""
A Circuit Keeps devices in a closed loop chains and distributes power events
on a predicable clock.
"""

class Power(object):

    def get_uuid(self):
        return id(self)

    def __init__(self, owner, origin_terminal=None, test=False, closed=False):
        self.owner = owner

        self.origin = origin_terminal
        # Flag test attributes.
        self.test = test

        # terminal stop if the event flow reaches the owner.
        self.closed = closed
        self.prepare()

    def prepare(self):
        pass


class LoopTest(Power):

    """A ID of the current terminal.
    """
    current_terminal = None

    def prepare(self):
        self.current_terminal = self.current_terminal or self.origin.get_id()
        self.path = [self.current_terminal]

    def step_to_next(self, circuit):
        next_t_ids = self.get_next(circuit)
        r = tuple(circuit.terminals_parent_ref[x] for x in tuple(next_t_ids))
        print('LoopTest requested, step_to_next', next_t_ids, r)
        self.step_to(next_t_ids, circuit)

    def get_next(self, circuit):
        """Return a list of sibling terminals within the given circuit using
        the internal position pointer, relative from the last step.
        """
        # given the current terminal, fetch the next from the circuit graph
        return circuit.graph.get(self.current_terminal)

    def step_to(self, ids, circuit=None):
        if ids is None:
            print('No more steps', self.path)
            return

        ids = tuple(ids)
        if len(ids) == 1:
            # no clone required
            term_id = ids[0]
            if term_id == self.path[0]:
                print('Hit Self!')
                return

            print('Step to', term_id)
            self.path.append(term_id)
            self.current_terminal = term_id
            bus.emit(self)

    def passthrough(self, *terminals):
        """The event was given to a terminal, which passed _through_ the
        device to the given expected output terminal.
        """
        ids = tuple(x.get_id() for x in terminals)
        print('passthrough', ids)
        import pdb; pdb.set_trace()  # breakpoint 49d7c24e //

        return self.step_to(ids, None)

class Identity(object):
    """An entity to apply to a circuit.
    """
    # Provide a unique name for this device.
    name = None

    def static_id(self):
        return self.name or self.__class__.__name__

    def get_uuid(self):
        return id(self)

    def get_id(self):
        return f"{self.static_id()}_{self.get_uuid()}"


class PowerLoop(object):
    """Tools to manage the power loop suite
    """
    def send_test_signal(self, terminal):
        """Emit a test event from a circuit source unit through the given terminal
        expecting the signal to arrive here.
        """
        unit = terminal.parent
        event = LoopTest(unit, terminal, test=True, closed=True)
        event.step_to_next(self)
        #bus.emit(event)


class Terminal(Identity):
    """A connectable entity for units within circuits.
    """

    # Automatically set during bake.
    label = 'no label'
    parent = None

    def emit(self, event):
        event.origin = self
        print('Emit event from', self, event)
        bus.emit(event)

    def __str__(self):
        return f'<Terminal "{self.label}"({self.get_id()})>'

    def looptest_event(self, event):
        print('Terminal looptest_event', self)
        return self.parent.looptest_event(event, self)

class Unit(Identity):

    def __init__(self):
        self.circuits = []
        self.bake()

    def on_circuit_append(self, circuit):
        self.circuits.append(circuit)

    def bake(self):
        """Set the local attributes for API work
        """
        ts = ()

        for name in dir(self):
            e = getattr(self, name)
            if isinstance(e, Terminal):
                ts += (e, )
                e.label = name
                e.parent = self

        self.terminals = ts

    def __str__(self):
        return f'<Unit "{self.get_id()}">'


class LED(Unit):

    terminal_in = Terminal()
    terminal_out = Terminal()

    def looptest_event(self, event, terminal):
        print('LED Looptest event', event)
        t = [self.terminal_out, self.terminal_in]
        t.remove(terminal)
        event.passthrough(*t)
        # t[0].emit(event)


class Battery(Unit):

    terminal_in = Terminal()
    terminal_out = Terminal()

    def on_circuit_append(self, circuit):
        super().on_circuit_append(circuit)
        print('Battery::on_circuit_append emit Power')
        self.terminal_out.emit(Power(self, test=True))


class StandardKnuckle(object):
    """Acts like a connecting two terminals without a wire.
    """

from collections import defaultdict

class EventMachine(object):
    """A singleton for all circuits to event emit through.
    """

    def __init__(self):
        self.graph = defaultdict(set)
        self.circuits = {}

    def emit(self, event):
        """Given an event from a terminal, send to the correct circuit.

        A power event may emit to multiple circuits.
        """
        unit_id = event.owner.get_id()
        print('EventMachine::emit heard event for', unit_id)
        circuits = self.graph.get(unit_id, None)
        if circuits is None:
            print('Event for no circuit?', unit_id)
            return


        for circuit_name in circuits:
            self.circuits[circuit_name].device_event(event)


    def add_owner(self, device, circuit):
        """Append a map of the device to the circuit for later access for
        incoming events
        """
        cid = circuit.get_id()
        self.circuits[cid] = circuit
        self.graph[device.get_id()].add(cid)


bus = EventMachine()

class Circuit(Identity, PowerLoop):

    def __init__(self):
        # Keep all devices bound to the circuit. This is not required
        # for loop closure
        self.devices = {}
        self.terminals = {}
        # A graph of node terminal connections.
        self.graph = defaultdict(set)
        self.graph_rev = defaultdict(set)
        self.terminals_parent_ref = {}
        # A KV of wire connections between two units.
        # A missing wire denotes a _soldered_ connection (no intermediate)
        self.wires = {}

    def append(self, *devices):
        """May occur clean for debugging.
        """
        for device in devices:
            did = device.get_id()
            if did not in self.devices:
                print('New device to circuit', device)
            self.devices[did] = device
            bus.add_owner(device, self)
            device.on_circuit_append(self)

    def device_event(self, event):
        """An event from a device, given by the bus from a terminal emit()
        """
        name = f'{type(event).__name__}_event'.lower()
        return getattr(self, name)(event)

    def power_event(self, event):
        """Power event collect through a device event"""
        print('Circuit received power_event', event.get_uuid())

    def looptest_event(self, event):
        """The input looptest started from a given device. Perform the
        loop test or fail the event.
        """
        # Begin the signal stepping to identify a closed loop.
        t_id = event.current_terminal
        owner_name = self.terminals_parent_ref[t_id]
        print('looptest_event', self.terminals[t_id], owner_name)

        terminal = self.terminals[t_id]
        device = self.devices[owner_name]
        terminal.looptest_event(event)
        # device.looptest_event(event)
        # The result should be nothing - as a continuation may occur later
        next_t_ids = event.get_next(self)
        print('circuit LoopTest requested; next:', next_t_ids)
        event.step_to(next_t_ids, self)

    def connect(self, ta, tb, through=None, append=True):
        """Bind two terminals through a wire.
        """
        print('Connecting Terminals', ta, tb)
        if append:
            self.append(ta.parent, tb.parent)

        ta_id = ta.get_id()
        tb_id = tb.get_id()

        if through is not None:
            ab_id = f'{ta_id}_{tb_id}'
            self.wires[ab_id] = through


        self.terminals_parent_ref[ta_id] = ta.parent.get_id()
        self.terminals_parent_ref[tb_id] = tb.parent.get_id()

        self.terminals[ta_id] = ta
        self.terminals[tb_id] = tb

        # Build graph connection
        self.graph[ta_id].add(tb_id)
        self.graph_rev[tb_id].add(ta_id)

    def default_connection(self):
        """Return a default connection for the graph to bind two terminals.
        """
        return StandardKnuckle()


def main():
    c = Circuit()
    b = Battery()
    l = LED()
    # c.append(b)
    # c.append(l)

    c.connect(b.terminal_out, l.terminal_in)
    c.connect(l.terminal_out, b.terminal_in)
    print('\nEmit:')
    c.send_test_signal(b.terminal_out)
    return c


if __name__ == '__main__':
    c = main()
