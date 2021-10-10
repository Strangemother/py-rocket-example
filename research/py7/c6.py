"""A simplfied version of the circuit, to product closed loop paths.

Version 4 pushes the event chain tracking to the loopTest class, forking within
debices as required.

    >>> v=c.view_looptest(b.t_out, e.t_out)
    Initiate circuit looptest from <Terminal "b.t_out">
    Complete
       b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out
     step_count: 5
     clone_count: 9
     unit_count: 2
     wire_count: 2


    [<LoopTest 36665384 "b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out">]


    >>> v=c.view_looptest(b.t_out, i.t_in)
    Initiate circuit looptest from <Terminal "b.t_out">
    hit self
       b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - a.t_in - || - a.t_out - ... - b.t_in - || - b.t_out
     step_count: 8
     clone_count: 17
     unit_count: 4
     wire_count: 4


    Incomplete
       b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - f.t_in - || - f.t_out - ... - g.t_in - || - g.t_out - ... - h.t_in - || - h.t_out
     step_count: 11
     clone_count: 21
     unit_count: 5
     wire_count: 5


    Complete
       b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - f.t_in - || - f.t_out - ... - g.t_in - || - g.t_out - ... - i.t_in
     step_count: 10
     clone_count: 19
     unit_count: 4
     wire_count: 5


    [<LoopTest 36665328 "b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - f.t_in - || - f.t_out - ... - g.t_in - || - g.t_out - ... - i.t_in">]



    >>> v=c.view_looptest(b.t_out, b.t_in)
    Initiate circuit looptest from <Terminal "b.t_out">
    Complete
       b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - a.t_in - || - a.t_out - ... - b.t_in
     step_count: 8
     clone_count: 15
     unit_count: 3
     wire_count: 4


    Incomplete
       b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - f.t_in - || - f.t_out - ... - g.t_in - || - g.t_out - ... - h.t_in - || - h.t_out
     step_count: 11
     clone_count: 21
     unit_count: 5
     wire_count: 5


    Complete
       b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - f.t_in - || - f.t_out - ... - g.t_in - || - g.t_out - ... - i.t_in - || - i.t_out - ... - a.t_in - || - a.t_out - ... - b.t_in
     step_count: 14
     clone_count: 27
     unit_count: 6
     wire_count: 7


    Incomplete
       b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - f.t_in - || - f.t_out - ... - g.t_in - || - g.t_out - ... - i.t_in - || - i.t_out - ... - j.t_in - || - j.t_out
     step_count: 13
     clone_count: 25
     unit_count: 6
     wire_count: 6


    [<LoopTest 36665384 "b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - a.t_in - || - a.t_out - ... - b.t_in">,
     <LoopTest 36665384 "b.t_out - ... - d.t_in - || - d.t_out - ... - e.t_in - || - e.t_out - ... - f.t_in - || - f.t_out - ... - g.t_in - || - g.t_out - ... - i.t_in - || - i.t_out - ... - a.t_in - || - a.t_out - ... - b.t_in">]
    >>> v=c.view_looptest(g.t_out, b.t_in)
    Initiate circuit looptest from <Terminal "g.t_out">
    Incomplete
       g.t_out - ... - h.t_in - || - h.t_out
     step_count: 3
     clone_count: 5
     unit_count: 1
     wire_count: 1


    Complete
       g.t_out - ... - i.t_in - || - i.t_out - ... - a.t_in - || - a.t_out - ... - b.t_in
     step_count: 6
     clone_count: 11
     unit_count: 2
     wire_count: 3


    Incomplete
       g.t_out - ... - i.t_in - || - i.t_out - ... - j.t_in - || - j.t_out
     step_count: 5
     clone_count: 9
     unit_count: 2
     wire_count: 2


    [<LoopTest 36665328 "g.t_out - ... - i.t_in - || - i.t_out - ... - a.t_in - || - a.t_out - ... - b.t_in">]
"""

from collections import defaultdict
from pprint import pprint
pp = pprint

class LoopTest(object):

    current_terminal = None
    start_terminal = None
    end_terminal = None
    step_count = 0
    clone_count = 0
    unit_count = 0
    wire_count = 0

    path = None
    origin = None
    # circuit = None
    visits = None


    def __init__(self, start_terminal, end_terminal, origin_id=None):
        # self.circuit = circuit
        self.origin_id = origin_id or id(self)
        self.unique_id = id(self)
        self.start_terminal = start_terminal
        self.end_terminal = end_terminal
        self.visits = defaultdict(int)
        self.path = []

    def clone(self, origin=None):
        """a shallow copy with a unique path
        """
        nc = self.__class__(self.start_terminal, self.end_terminal, self.origin_id)
        nc.current_terminal = self.current_terminal
        nc.step_count = self.step_count
        nc.clone_count = self.clone_count + 1
        nc.wire_count = self.wire_count
        nc.unit_count = self.unit_count
        nc.visits = self.visits.copy()

        nc.path = self.path.copy()
        nc.origin = origin
        return nc

    def pp(self, label=None):
        p = ' - '.join(x.uuid() for x in self.path)
        print(f'{label}\n  ', p, '\n',
            f'step_count: {self.step_count}\n',
            f'clone_count: {self.clone_count}\n',
            f'unit_count: {self.unit_count}\n',
            f'wire_count: {self.wire_count}\n',
            '\n')

    def __str__(self):
        p = ' - '.join(x.uuid() for x in self.path)
        return p

    def __repr__(self):
        return f'<LoopTest {self.origin_id} "{self.__str__()}">'

    def emit(self, circuit, terminal=None):
        """Send the looptest through the cicuit.
        """

        entity = self.clone() # if should_clone else self

        if entity.step_count > 100:
            print('Entity death')
            return

        if sum(entity.visits.values()) > len(entity.visits.keys()):
            entity.pp('Revisit step death')
            print('\n')
            return

        if entity.unit_count > len(circuit.terminals):
            """We've hit all the nodes once, or resiviting a node again.
            """
            entity.pp('Exhausted death')
            print('\n')
            return

        # c3.looptest(_b.t_out, _l3.t_in)
        if terminal is not None and (terminal == self.start_terminal):
            entity.path.append(terminal)
            return circuit.looptest_loopback(entity)

        terminal = terminal or self.start_terminal
        # Get all next points, if more than 1, clone and send.
        circuit_attached = circuit.get_next_terminals(self, terminal)

        entity.path.append(terminal)
        entity.visits[terminal.uuid()] += 1
        entity.step_count += 1
        # Fetch terminal (internal) attached
        terminal_attached = terminal.looptest_in(self)

        next_terminals = circuit_attached + terminal_attached

        if terminal == entity.end_terminal:
            # The loop is complete as per the route spec.
            return circuit.looptest_complete(entity)

        if len(next_terminals) == 0:
            circuit.looptest_incomplete(entity)

        self.emit_to_circuit_many(entity, circuit, terminal, circuit_attached)
        self.emit_to_circuit_many(entity, circuit, terminal, terminal_attached,
            increment='unit', label='||')

        return

        # # Gather other circuit loops.
        # other_circuit_terminals = circuit_manager.get_circuit_terminals(terminal, circuit)

        # if len(other_circuit_terminals) > 0:
        #     print("\n   Circuit Step from", circuit.label,
        #         terminal, 'to', other_circuit_terminals, '\n')

    def emit_to_circuit_many(self, entity, circuit, terminal, many_terminals,
            increment='wire', label='...'):

        for i, term in enumerate(many_terminals):
            _entity = entity.clone()
            _entity.path.append(Label(label))
            setattr(_entity, f'{increment}_count',getattr(_entity, f'{increment}_count')+1)
            _entity.emit_terminal_connection(circuit, terminal, term)#, on_complete=on_complete)

    def emit_terminal_connection(self, circuit, from_terminal, to_terminal, entity=None):
        entity = entity or self
        entity.emit(circuit, to_terminal)


class Label(object):
    def __init__(self, label):
        self.label = label

    def uuid(self):
        return self.label


class CircuitManager(object):
    """Maintain a list of all circuits for cross referencing of
    terminals during looptests.
    """
    circuits = None

    def __init__(self):
        self.circuits = {}
        self.connections = defaultdict(set)

    def add(self, circuit):
        print('new circuit', circuit.label)
        self.circuits[circuit.label] = circuit

    def add_terminal_connection(self, circuit, a, b):
        self.connections[a.uuid()].add( (circuit.label, b.uuid()) )

    def get_circuit_terminals(self, terminal, ignore):
        r = self.connections.get(terminal.uuid(), None)
        if r is None:
            return ()

        # print('CircuitManager.get_circuit_terminals', terminal)
        result = ()
        ignore_label = ignore.label

        for circuit_label, term_uuid in r:
            if circuit_label == ignore_label:
                continue
            c = self.circuits.get(circuit_label)
            #others = c.get_graph_attached(terminal)
            #if len(others) > 0:
            result += ((c, term_uuid,),)

        return result


circuit_manager = CircuitManager()

class Circuit(object):

    label = None

    def __init__(self, label=None):
        self.label = label

        self.graph = defaultdict(set)
        self.terminals = {}
        self.looptests = defaultdict(lambda: defaultdict(set))
        self.incomplete_looptests = defaultdict(lambda: defaultdict(set))
        circuit_manager.add(self)

    def connect(self, a, b):
        print('connect', a, b)
        self.graph[a.uuid()].add(b.uuid())
        circuit_manager.add_terminal_connection(self, a,b)
        self.terminals[a.uuid()] = a
        self.terminals[b.uuid()] = b

    def get_graph_attached(self, uuid):
        _next = self.graph.get(uuid, ())
        return tuple(self.terminals[x] for x in _next)

    def linear_looptest(self, start_a, end_b):
        """The Cicuit emits a looptest and _forgets_ about it, until the
        event returns back to the cicuit - to be resubmitted.
        """
        print('Initiate circuit looptest from', start_a)
        lt = LoopTest(start_a, end_b)
        lt.emit(self)#, on_complete=self.looptest_complete)
        return lt.origin_id
        # self.looptests[lt.unique_id] = {}

    def get_looptests(self, looptest_id):
        return list(self.looptests[looptest_id].values())

    def looptest_loopback(self, looptest_event):
        looptest_event.pp('hit self')

    def view_looptest(self, a, b):
        lid = self.linear_looptest(a,b)
        tests = self.get_looptests(lid)
        self.pop_looptests(lid)
        pp(tests)
        return tests

    def pop_looptests(self, looptest_id):
        self.looptests.pop(looptest_id)

    def looptest_complete(self, looptest_event):
        p = ' - '.join(x.uuid() for x in looptest_event.path)
        print('Complete\n  ', p, '\n',
            f'step_count: {looptest_event.step_count}\n',
            f'clone_count: {looptest_event.clone_count}\n',
            f'unit_count: {looptest_event.unit_count}\n',
            f'wire_count: {looptest_event.wire_count}\n',
            '\n')
        self.looptests[looptest_event.origin_id][looptest_event.unique_id] = looptest_event


    def looptest_incomplete(self, looptest_event):
        p = ' - '.join(x.uuid() for x in looptest_event.path)
        print('Incomplete\n  ', p, '\n',
            f'step_count: {looptest_event.step_count}\n',
            f'clone_count: {looptest_event.clone_count}\n',
            f'unit_count: {looptest_event.unit_count}\n',
            f'wire_count: {looptest_event.wire_count}\n',
            '\n')
        self.incomplete_looptests[looptest_event.origin_id][looptest_event.unique_id] = looptest_event

    def get_next_terminals(self, event, terminal):
        terminals = self.get_graph_attached(terminal.uuid())
        return terminals


class Terminal(object):
    """
    """
    parent = None
    label = None

    def __init__(self, parent, label=None):
        self.label = label
        self.parent = parent

    def looptest_in(self, looptest_event):
        r = self.parent.terminal_looptest_in(self, looptest_event)
        # print(f'  Terminal {self} looptest_in to', r)
        return r

    def uuid(self):
        return f'{self.parent.label}.{self.label}'

    def __str__(self):
        return f'<Terminal "{self.parent.label}.{self.label}">'

    def __repr__(self):
        return f'<Terminal "{self.parent.label}.{self.label}">'

'''
# https://www.autodesk.com/products/eagle/blog/3-rules-humble-circuit-place-world-electronics/
# https://www.omnicalculator.com/physics/ideal-transformer#how-does-a-transformer-work

Rule 1 – Electricity will always want to flow from a higher voltage to a lower voltage.
Rule 2 – Electricity always has work that needs to be done.
Rule 3 – Electricity always needs a path to travel on.

the minute you take any of that work out of your circuit, the electricity
goes crazy and runs around its path at full speed without anything holding
it back. If you let this happen for an extended period of time, then you’ll
find yourself with a damaged power supply, a drained battery, or maybe
something even worse, like a fire!
'''

class Diode(object):
    """
    A diode is a two-terminal electronic component that conducts current
    primarily in one direction (asymmetric conductance); it has low
    (ideally zero) resistance in one direction, and high (ideally infinite)
    resistance in the other.
    """

    def setup_terminals(self):
        self.t_in = Terminal(self, label='t_in')
        self.t_out = Terminal(self, label='t_out')

    def terminal_looptest_in(self, terminal_in, looptest_event):
        """Return zero or more terminals.
        """
        # print('    Unit.looptest_in', self.label, terminal_in.label)
        port_map = {
            't_in': (self.t_out,),
        }

        return port_map.get(terminal_in.label, ())


class Resistor(object):
    """
    A resistor is a passive two-terminal electrical component that implements
    electrical resistance as a circuit element. In electronic circuits,
    resistors are used to reduce current flow, adjust signal levels, to
    divide voltages, bias active elements, and terminate transmission lines,
    among other uses. High-power resistors that can dissipate many watts of
    electrical power as heat, may be used as part of motor controls, in power
    distribution systems, or as test loads for generators. Fixed resistors
    have resistances that only change slightly with temperature, time or
    operating voltage. Variable resistors can be used to adjust circuit
    elements (such as a volume control or a lamp dimmer), or as sensing
    devices for heat, light, humidity, force, or chemical activity.
    """

class Unit(Diode):

    def __init__(self, label=None):
        self.label = label or id(self)
        self.setup_terminals()


a = Unit(label='a')
b = Unit(label='b')
d = Unit(label='d')
e = Unit(label='e')

c = Circuit(label='c')

c2 = Circuit(label='c2')
a2 = Unit(label='a2')
b2 = Unit(label='#')
d2 = Unit(label='d2')

c2.connect(b.t_out, a2.t_in)
c2.connect(a2.t_out, d2.t_in)
c2.connect(d2.t_out, b.t_in)

c.connect(a.t_out, b.t_in)
c.connect(b.t_out, d.t_in)
c.connect(d.t_out, e.t_in)
c.connect(e.t_out, a.t_in) # e fork to a (and later F)

f = Unit(label='f')
g = Unit(label='g')
h = Unit(label='h')
i = Unit(label='i')
j = Unit(label='j')

# complete:
#     a b d e a
#     a b d e a f g i a

# incomplete:
#     a b d e a f g h
#     a b d e a f g i j

"""
Complete
   a.t_out - b.t_in - b.t_out - d.t_in - d.t_out - e.t_in - e.t_out - a.t_in

   a.t_out - b.t_in - b.t_out - d.t_in - d.t_out - e.t_in - e.t_out - f.t_in - f.t_out
   - g.t_in - g.t_out - i.t_in - i.t_out - a.t_in

Incomplete
   a.t_out - b.t_in - b.t_out - d.t_in - d.t_out - e.t_in - e.t_out - f.t_in - f.t_out
   - g.t_in - g.t_out - h.t_in - h.t_out

   a.t_out - b.t_in - b.t_out - d.t_in - d.t_out - e.t_in - e.t_out - f.t_in - f.t_out
   - g.t_in - g.t_out - i.t_in - i.t_out - j.t_in - j.t_out
"""

c.connect(e.t_out, f.t_in) # e fork to f (and earlier A)
c.connect(f.t_out, g.t_in)

c.connect(g.t_out, h.t_in) # H Does not close.
c.connect(g.t_out, i.t_in)
c.connect(i.t_out, j.t_in) # J Does not close.

c.connect(i.t_out, a.t_in) # Close a..g>i>a

pprint(c.graph)
#c.linear_looptest(a.t_out, a.t_in)
# print(c.looptests)
print('Complete')
pprint(c.looptests)
print('incomplete')
pprint(c.incomplete_looptests)



_b = Unit(label='battery')
_l = Unit(label='led')
_l2 = Unit(label='led2')
_l3 = Unit(label='led3')
_l4 = Unit(label='led4')
_s = Unit(label='switch')

c3 = Circuit(label='c3')

c3.connect(_b.t_out, _s.t_in)
c3.connect(_s.t_out, _l.t_in)
c3.connect(_s.t_out, _l2.t_in)
c3.connect(_l2.t_out, _b.t_in)
c3.connect(_l.t_out, _b.t_in)

c3.connect(_b.t_out, _l3.t_in)
c3.connect(_l3.t_out, _l4.t_in)
c3.connect(_l4.t_out, _b.t_in)


print('Mini loop test:\n')

pprint(c3.graph)
tests = c3.view_looptest(_b.t_out, _b.t_in)

# c3.linear_looptest(_l3.t_out, _l3.t_in)
"""
Complete
   battery.t_out -
   ... - switch.t_in - || - switch.t_out -
   ... - led.t_in - || - led.t_out - ... - battery.t_in
"""
