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

    def emit(self, circuit, terminal=None):
        """Send the looptest through the cicuit.
        """
        start = terminal or self.start_terminal
        self.path.append(start)

        if start == self.end_terminal:
            print('Break at end', start)

        next_terminals = circuit.get_next_terminals(self, start)

        out = ()

        if len(next_terminals) == 0:
            print('No where to go\n', self.path)
            return

        for t in next_terminals:
            if t == self.start_terminal:
                print('Looped back to end', t)
                continue
            self.emit(circuit, t)


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
        print('Initiate circuit looptest')
        lt = LoopTest(start_a, end_b)
        lt.emit(self)

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
        print(f'  Terminal {self} looptest_in to', r)
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
        # print('    Unit::looptest_in', self.label, terminal)
        return (self.t_out,)


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

c.connect(e.t_out, f.t_in) # e fork to f (and earlier A)
c.connect(f.t_out, g.t_in)

c.connect(g.t_out, h.t_in) # H Does not close.
c.connect(g.t_out, i.t_in)
c.connect(i.t_out, j.t_in) # J Does not close.

c.connect(i.t_out, a.t_in) # Close a..g>i>a

pprint(c.graph)
c.looptest(a.t_out, a.t_in)

