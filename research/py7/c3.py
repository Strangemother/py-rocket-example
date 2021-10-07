"""A simplfied version of the circuit, to product closed loop paths.
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

    def get_next_step(self, event):
        """Move the internal step to the next record in the list.
        """
        current = event.current_terminal or event.start_terminal
        _next = self.graph.get(current.uuid(), ())
        _next_terms = self.get_graph_attached(current.uuid())

        print('Circuit::', current ,' get_next_step =', _next_terms)
        return _next_terms # + self.next_terminals

    def looptest(self, start_a, end_b):
        ev = LoopTest(start_a, end_b)

        open_loop = True
        count = 0

        step_ids = (start_a.uuid(),)
        hidden_terminal_map = defaultdict(set)
        path = []#defaultdict(list)
        paths = ()

        end_uuid = end_b.uuid()

        while open_loop:
            # Get next terminals from the graph.
            # These terminals are attached to other terminals within
            # the Unit.
            next_steps = ()

            for step_int, step_id in enumerate(step_ids):
                path.append(step_id)
                input_terminals = self.get_graph_attached(step_id)
                out_ids = tuple(x.uuid() for x in input_terminals)

                if len(input_terminals) > 1:
                    print(f'--  Device output fork "{step_id}" to', out_ids)
                    clone_path = path[:]
                    #clone_path.append(step_id)
                    clone_path.append('%')
                    paths += (clone_path,)

                for i, terminal in enumerate(input_terminals):
                    uuid = terminal.uuid()
                    if uuid == end_uuid:
                        print('  ! Finish loop at end:', terminal, '\n')
                        clone_path = path.copy()
                        clone_path.append(uuid)
                        clone_path.append('|')

                        paths += (clone_path,)
                        continue
                    if i> 0:
                        clone_path = path.copy()
                        # clone_path.append(uuid)
                        clone_path.append('--')
                        paths += (clone_path,)

                    print('  step_id', step_int, i, step_id, '=>', uuid)
                    internal_out_terminals = terminal.looptest_in(self)
                    ids = tuple(x.uuid() for x in internal_out_terminals)

                    if len(internal_out_terminals) == 0:
                        print('  - Crash at ', uuid, '- no outports')
                    else:
                        print('  + step into ', len(ids),' terminals of', uuid, ': ', ids)
                        path.append(uuid)
                    next_steps += ids
                    hidden_terminal_map[terminal.uuid()].add(*ids)

            #print('next steps', next_steps)
            open_loop = len(next_steps) > 0
            # new_step_ids = ()
            # for ns in next_steps:
            #     if ns == end_b:
            #         print('Kill loop')
            #         continue
            #     new_step_ids += (ns,)
            # step_ids = new_step_ids
            step_ids = next_steps

        pprint(hidden_terminal_map)
        for p in paths:
            print(p)



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

