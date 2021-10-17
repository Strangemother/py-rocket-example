"""

The 'node-inator' takes a special "device" node and a "wire" edge.

Each device is an item with an IN/OUT terinal node attached (directionally)
"""
from pprint import pprint as pp
import operator as op
from collections import defaultdict

from g3 import Connections


class Unit(object):

    pin_in = None
    pin_out = None

    def __init__(self, name='U'):
        self.name = name
        self.pin_in = {'i': 1, 'ref': self.name}
        self.pin_out = {'i': 0, 'ref': self.name}

    def give_event(self, event):
        print(self.name, 'has event', event)
        return self

    def __repr__(self):
        name = self.__class__.__name__
        return f'<{name} {self.name}>'


def gen_units(*names):
    units = {}
    for name in names:
        units[name] = Unit(name)
    return units


class U(object):
    def __init__(self, *a, **kw):
        self.__dict__.update(*a, **kw)


def connect_pins():
    c.connect(u.a.pin_out, u.b.pin_in, data={ 'length': 3 })
    c.connect(u.a.pin_out, u.aa.pin_in,  data={ 'length': 1 })
    c.connect(u.aa.pin_out, u.ab.pin_in)
    c.connect(u.ab.pin_out, u.ac.pin_in)
    c.connect(u.ac.pin_out, u.a.pin_in)

    c.connect(u.b.pin_out, u.c.pin_in)
    c.connect(u.c.pin_out, u.a.pin_in)


class Event():
    current_nodes = None
    current_units = None


def gen_ev():
    return Event()


def run_step(_node, event=None):
    event = event or gen_ev()

    """
    When iterating nodes, we could simply resolve the end_nodes
    of a node, however this omits the Edge usage, and any _meta_ passthrough
    (a wire resistance) may be ignored.
        _unit = set(get_node_unit(x) for x in _node.next_nodes)
    """
    _units = ()
    for e in _node.edges:
        pin_node = get_node_unit(e.b)
        _units += ( pin_node, )

    print('Nodes ', _units)
    # The event should be split at this point, enuring the event
    ev = gen_ev()
    for u in _units:
        u.give_event(ev)

    return event


def get_node_unit(node):
    ref = node.data['ref']
    return units[ref]


def get_units_from_node_edges(node):
    _units = ()
    _nodes = ()
    edges = node.edges
    for e in edges:
        _nodes += (e.b,)
        pin_node_unit = get_node_unit(e.b)
        _units += ( pin_node_unit, )

    return edges, _units, _nodes


def gather_edges(nodes):
    r, u, n = (), (), ()
    for node in nodes:
        edges, _units, _nodes = get_units_from_node_edges(node)
        r += edges
        u += _units
        n += _nodes
    return r, u, n


class PowerUnit(object):
    start_node = None
    end_node = None

    # Every _forward_ step yields +1 from the start node
    step_index = -1
    next_nodes = None

    def start(self):
        # self.start_node = c(u.a.pin_out)
        # self.end_node = c(u.a.pin_in)
        edges, _units, _nodes = get_units_from_node_edges(self.start_node)
        print('edges')
        pp(edges)

        print('_units')
        pp(_units)

        print('_nodes')
        # get all next.
        pp(_nodes)

        # For each unit, ensure a unique path.
        # edge_tracker[]
        #
        # When the event forks, each unit generates a new ID "from"
        # As an event passes through a unit, it can be checked within its
        # history; If the node has previously been visited; step the an unused
        # edge or cancel
        ev = gen_ev()

        for u in _units:
            u.give_event(ev)

        self.step_index += 1
        self.next_nodes = _nodes

    def step_continue(self):
        print('next_nodes', self.next_nodes)
        edges, units, nodes = gather_edges(self.next_nodes)
        print('edges', edges, units, nodes)

units = gen_units('a', 'aa', 'ab', 'ac', 'b', 'c')
u = U(**units)

c = Connections()
#c.connect(f_a, f_b, f_c)

mem = defaultdict(int)
# Step each edge
#  for each split, store a reference
#  position of the event. The references
#  position may be the node name _stepped into_.
#
#  If a node name already exists, the
#  event should pass theough the n+1 edge
#  of the previously walked position from
#  that node.
#  IF all esges are walked, return nothing.

#  each edge, and the
edge_tracker = defaultdict(set)


connect_pins()

pu = PowerUnit()
pu.start_node = c(u.a.pin_out) #c.get_start_node()
pu.end_node = c(u.a.pin_in) #c.get_start_node()

v = pu.start()
v = pu.step_continue()

print(v)
# c.pp()
# cv = compute_node(c(f_a))
# print(cv)
# cv = compute_ids(cv if len(cv) > 0 else (c.get_start_node().get_uuid(),))

# get_node - > run [func(value) op g(func).data]
# store result in g(func).data
# get each next node
#
# get_node - > run [func(value) op g(func).data]
# store result in g(func).data
# get each next node
#
# get_node ...

