from g4.edges.edge import Edges
from g4.pins import Pins
from g4.enums import FORWARD
from g4.nodes.node import Node, ExitNode
from g4.iter_tools import pairwise


class Connections(Edges, Pins):
    """An entity to hold and spawn edges.
    """

    # def __init__(self):
    #     print('Setup Connections')
    #     # self.trees = defaultdict(lambda: defaultdict(set))
    #     # self.datas = defaultdict(lambda: defaultdict(set))
    #     # self.pins = defaultdict(lambda: defaultdict(set))
    #     super().__init__()
    #     # self._spawn_index = 0

    def connect(self, *units, direction=FORWARD, data=None, edge=None):
        edges = ()
        for unit_pair in pairwise(units):
            new_edge = self.add_edge(unit_pair, direction, data=data, edge=edge)
            edges += (new_edge, )
        self.pin_ends(edges, direction)
        return edges

    def pp(self):
        pp(vars(self))

    def node(self, *a, **kw):
        return Node(self, *a, **kw)

    def get_start_node(self, direction=FORWARD):
        return ExitNode(self, 'start', direction)

    def __call__(self, *a, **kw):
        return self.node(*a, **kw)
