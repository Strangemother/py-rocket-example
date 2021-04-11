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

    def __init__(self, start_terminal, end_terminal):
        # self.circuit = circuit

        self.start_terminal = start_terminal
        self.end_terminal = end_terminal
        self.path = []
        self.next_terminals = ()

    def clone(self, origin=None):
        """a shallow copy with a unique path
        """
        nc = self.__class__(self.start_terminal, self.end_terminal)
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

        names = ', '.join(x.uuid() for x in next_terminals)
        self.path.append(terminal)

        if terminal == self.end_terminal:
            # The loop is complete as per the route spec.
            if on_complete:
                on_complete(self.clone())
            return

        if len(next_terminals) == 0:
            circuit.looptest_incomplete(self)

        should_clone = len(next_terminals) > 1

        for i, term in enumerate(next_terminals):
            entity = self.clone() if should_clone else self

            if term == entity.start_terminal:
                print('Hit start term', entity.path)
                continue

            entity.emit(circuit, term, on_complete)




class Circuit(object):

    def __init__(self):
        self.graph = defaultdict(set)
        self.terminals = {}

    def connect(self, a, b):
        print('connect', a, b)
        self.graph[a.uuid()].add(b.uuid())

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
        lt.emit(self, on_complete=self.looptest_complete)

    def looptest_complete(self, looptest_event):
        p = ' - '.join(x.uuid() for x in looptest_event.path)
        print('Complete\n  ', p, '\n')

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

c = Circuit()

# c2 = Circuit()
# a2 = Unit(label='a2')
# b2 = Unit(label='#')
# d2 = Unit(label='d2')

# c2.connect(b.t_out, a2.t_in)
# c2.connect(a2.t_out, d2.t_in)
# c2.connect(d2.t_out, b.t_in)

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

c.connect(e.t_out, f.t_in) # e fork to f (and earlier A)
c.connect(f.t_out, g.t_in)

c.connect(g.t_out, h.t_in) # H Does not close.
c.connect(g.t_out, i.t_in)
c.connect(i.t_out, j.t_in) # J Does not close.

c.connect(i.t_out, a.t_in) # Close a..g>i>a

pprint(c.graph)
c.looptest(a.t_out, a.t_in)

