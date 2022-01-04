from .edge import Edges
from .pins import Pins
from .enums import FORWARD
from .node import LiveNode, ExitNode, LiveEdge
from .iter_tools import pairwise

from pprint import pprint


class NodeMixin(object):

    def get_node_class(self):
        return Node


class Edge(NodeMixin, LiveEdge):
    pass


class Node(LiveNode):
    edge_class = Edge
    # def get_edge_class(self):
    #     return Edge


class Connections(NodeMixin, Edges, Pins):
    """An entity to hold and spawn edges."""
    # node_class = Node

    def connect(self, *units, direction=FORWARD, data=None, edge=None):
        edges = bridge_pairs(self.add_edge, *units,
                             direction=direction, data=data, edge=edge)
        self.pin_ends(edges, direction)
        return edges

    def pp(self):
        pprint(vars(self))

    def node(self, *a, **kw):
        return self.get_node_class()(self, *a, **kw)

    def get_start_node(self, direction=FORWARD):
        return ExitNode(self, 'start', direction)

    def __call__(self, *a, **kw):
        return self.node(*a, **kw)



def bridge_pairs(func, *units, **kw):
    edges = ()
    # func = func or func.add_edge
    for unit_pair in pairwise(units):
        new_edge = func(unit_pair, **kw)
        edges += (new_edge, )
    return edges
