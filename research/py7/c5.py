"""A simplfied version of the circuit, to product closed loop paths.

Version 4 pushes the event chain tracking to the loopTest class, forking within
debices as required.
"""

from collections import defaultdict
from pprint import pprint


class LoopTest(object):

    current_terminal = None
    start_terminal = None
    end_terminal = None
    step_count = 0
    path = None
    origin = None
    # circuit = None

    def __init__(self, start_terminal, end_terminal, origin_id=None):
        # self.circuit = circuit
        self.origin_id = origin_id or id(self)
        self.unique_id = id(self)
        self.start_terminal = start_terminal
        self.end_terminal = end_terminal
        self.path = []

    def clone(self, origin=None):
        """a shallow copy with a unique path
        """
        nc = self.__class__(self.start_terminal, self.end_terminal, self.origin_id)
        nc.current_terminal = self.current_terminal
        nc.step_count = self.step_count
        nc.path = self.path.copy()
        nc.origin = origin
        return nc

    def emit(self, circuit, terminal=None, on_complete=None):
        """Send the looptest through the cicuit.
        """
        terminal = terminal or self.start_terminal
        # Get all next points, if more than 1, clone and send.
        circuit_attached = circuit.get_next_terminals(self, terminal)
        # Fetch terminal (internal) attached

        terminal_attached = terminal.looptest_in(self)
        next_terminals = circuit_attached + terminal_attached

        entity = self.clone()# if should_clone else self
        entity.path.append(terminal)

        if terminal == entity.end_terminal:
            # The loop is complete as per the route spec.
            # clone = self.clone()
            # clone.path.append(terminal)
            circuit.looptest_complete(entity)
            # if on_complete:
            #     on_complete(clone)
            return

        if len(next_terminals) == 0:
            circuit.looptest_incomplete(entity)

        self.emit_to_circuit_many(entity, circuit, terminal, circuit_attached)

        # for i, term in enumerate(circuit_attached):
        #     _entity = entity.clone()
        #     _entity.path.append(Label('...'))
        #     _entity.emit_terminal_connection(circuit, terminal, term)#, on_complete=on_complete)

        self.emit_to_circuit_many(entity, circuit, terminal, terminal_attached, label='||')

        # Gather other circuit loops.
        other_circuit_terminals = circuit_manager.get_circuit_terminals(terminal, circuit)

        if len(other_circuit_terminals) > 0:
            print("\n   Circuit Step from", circuit.label,
                terminal, 'to', other_circuit_terminals, '\n')

            #import pdb; pdb.set_trace()  # breakpoint a8a5413d //

            # for other_circuit, other_terminal_uuid in other_circuit_terminals:
            #     #other_terminal = other_circuit.terminals.get(other_terminal_uuid)
            #     print('Emiting to', other_circuit.label)
            #     import pdb; pdb.set_trace()  # breakpoint 2cab086b //
            #     entity.emit(other_circuit, terminal)
            # self.emit_to_circuit_many(entity, other_circuit, terminal, (other_terminal,),)

        # for i, term in enumerate(terminal_attached):
        #     _entity = entity.clone()
        #     _entity.path.append(Label('||'))

        #     if term == _entity.start_terminal:
        #         print('Hit start term', _entity.path)
        #         return

        #     _entity.emit_terminal_connection(circuit, terminal, term)#, on_complete=on_complete)

    def emit_to_circuit_many(self, entity, circuit, terminal, many_terminals, label='...'):
        for i, term in enumerate(many_terminals):
            _entity = entity.clone()
            _entity.path.append(Label(label))
            _entity.emit_terminal_connection(circuit, terminal, term)#, on_complete=on_complete)

    def emit_terminal_connection(self, circuit, from_terminal, to_terminal, on_complete=None, entity=None):
        entity = entity or self
        entity.emit(circuit, to_terminal, on_complete)


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
        self.looptests = {}
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

    def looptest(self, start_a, end_b):
        """The Cicuit emits a looptest and _forgets_ about it, until the
        event returns back to the cicuit - to be resubmitted.
        """
        print('Initiate circuit looptest from', start_a)
        lt = LoopTest(start_a, end_b)
        lt.emit(self)#, on_complete=self.looptest_complete)
        # self.looptests[lt.unique_id] = {}

    def looptest_complete(self, looptest_event):
        p = ' - '.join(x.uuid() for x in looptest_event.path)
        print('Complete\n  ', p, '\n')
        self.looptests[looptest_event.unique_id] = looptest_event


    def looptest_incomplete(self, looptest_event):
        p = ' - '.join(x.uuid() for x in looptest_event.path)
        print('Incomplete\n  ', p)

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


class Unit(object):

    def __init__(self, label=None):
        self.label = label or id(self)
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
c.looptest(a.t_out, a.t_in)
print(c.looptests)



_b = Unit(label='battery')
_l = Unit(label='led')
_s = Unit(label='switch')

c3 = Circuit(label='c3')

c3.connect(_b.t_out, _s.t_in)
c3.connect(_s.t_out, _l.t_in)
c3.connect(_l.t_out, _b.t_in)

print('Mini loop test:\n')

pprint(c3.graph)
c3.looptest(_b.t_out, _b.t_in)
print(c3.looptests)
"""
Complete
   battery.t_out -
   ... - switch.t_in - || - switch.t_out -
   ... - led.t_in - || - led.t_out - ... - battery.t_in
"""
