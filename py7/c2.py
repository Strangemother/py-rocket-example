"""A simplfied version of the circuit, to product closed loop paths.
"""

class LoopTest(object):

    current_terminal = None
    start_terminal = None
    end_terminal = None
    step_count = 0
    path = None
    origin = None

    def __init__(self, start_terminal, end_terminal):
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
        nc.path = self.path[:]
        nc.origin = origin
        return nc

    def get_next_step(self, circuit):
        """Move the internal step to the next record in the list.
        """
        current = self.current_terminal or self.start_terminal
        _next = circuit.graph.get(current.uuid(), ())
        _next_terms = circuit.get_attached(current.uuid())

        print('Looptest::', current ,' get_next_step =', _next_terms)
        return _next_terms + self.next_terminals

    def step_to(self, terminal):
        """Given a new Terminal, append the current step (terminal) into the
        path and _move_ to the given terminal.

        Return a new list of _out_ ports from new unit
        """
        self.step_count += 1
        self.path.append(self.current_terminal)

        if terminal == self.end_terminal:
            print('Looptest step_to end_terminal', terminal)
            return ()

        self.current_terminal = terminal
        internal_out_terminals = terminal.looptest_in(self)
        self.next_terminals = internal_out_terminals

        return internal_out_terminals


from collections import defaultdict


class Circuit(object):

    def __init__(self):
        self.graph = defaultdict(set)
        self.terminals = {}

    def connect(self, a, b):
        print('connect', a, b)
        self.graph[a.uuid()].add(b.uuid())

        self.terminals[a.uuid()] = a
        self.terminals[b.uuid()] = b

    def get_attached(self, uuid):
        _next = self.graph.get(uuid, ())
        return tuple(self.terminals[x] for x in _next)

    def get_next_step(self, event):
        """Move the internal step to the next record in the list.
        """
        current = event.current_terminal or event.start_terminal
        _next = self.graph.get(current.uuid(), ())
        _next_terms = self.get_attached(current.uuid())

        print('Circuit::', current ,' get_next_step =', _next_terms)
        return _next_terms # + self.next_terminals

    def looptest(self, start_a, end_b):
        ev = LoopTest(start_a, end_b)

        open_loop = True
        count = 0

        _next = self.get_next_step(ev)
        terminals = _next # tuple(self.terminals[x] for x in _next)

        while open_loop:

            print('Circuit next terminals', terminals)

            if len(terminals) == 0:
                print('No more steps.', ev)
                open_loop = False
                break

            new_terminals = ()

            for i, terminal in enumerate(terminals):
            #     # we don't clone the first
                new_ev = ev
                if bool(i):
                    # clone into new
                    new_ev = ev.clone()
                    new_ev.origin = ev

                new_terminals += new_ev.step_to(terminal)

            print('Next will be', new_terminals)
            terminals = new_terminals
            open_loop = count < 10
            count += 1


class Terminal(object):
    """
    """
    parent = None
    label = None

    def __init__(self, parent, label=None):
        self.label = label
        self.parent = parent

    def looptest_in(self, looptest_event):
        return self.parent.looptest_in(self, looptest_event)

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

    def looptest_in(self, terminal, looptest_event):
        """Return zero or more terminals.
        """
        print('Unit::looptest_in', self.label, terminal)
        return (self.t_out,)


a = Unit(label='a')
b = Unit(label='b')
d = Unit(label='d')
e = Unit(label='e')

c = Circuit()

c2 = Circuit()
a2 = Unit(label='a2')
# b2 = Unit(label='#')
d2 = Unit(label='d2')

c2.connect(b.t_out, a2.t_in)
c2.connect(a2.t_out, d2.t_in)
c2.connect(d2.t_out, b.t_in)

c.connect(a.t_out, b.t_in)
c.connect(b.t_out, d.t_in)
c.connect(d.t_out, e.t_in)
c.connect(e.t_out, a.t_in)

c.looptest(b.t_out, b.t_in)

