"""The _root_ components to help build a graph of connections.

To build a custom solution, the Connections (graphing abstract) should yield
the custom node. The custom node may also yield a custom edge.

Abstracting to your own solution is quick:

    from g6.live import LiveEdge, LiveNode
    from g6.connect import Connections

    class NodeClassMixin(object):
        def get_node_class(self):
            return Node

    class Edge(NodeClassMixin, LiveEdge):
        pass

    class Node(LiveNode):
        edge_class = Edge

    class Graph(NodeClassMixin, Connections):
        pass


Finally - connect your _nodes_. In this library a _node_ doesn't really exist,
pushing any entity becomes a reference:

    >>> g = Graph()
    >>> g.connect(1,2,3,4,5)
    (
        <ThinEdge "1_2" (1, 2)>,
        <ThinEdge "2_3" (2, 3)>,
        <ThinEdge "3_4" (3, 4)>,
        <ThinEdge "4_5" (4, 5)>
    )

The numericals `1` through `5` are valid _node_ types - calling upon the _graph_
returns a fresh `Node` wrapper we made earlier:
    >>> g(3)
    <Node "3" Valid>

with some neat functions:

    >>> g(3).edges
    (
        <Edge 1 "3_4" (<Node "3" Valid>, <Node "4" Valid>)>,
    )
    >>> g(3).next_nodes
    (<Node "4" Valid>,)
"""
from .edge import Edges
from .pins import Pins
from .enums import FORWARD
from .live import LiveNode, ExitNode, LiveEdge
from .iter_tools import bridge_pairs

from pprint import pprint



def clean_dict_dict(entity):
    r = {}
    for k,v in entity.items():
        r[k] = {x:dict(y) for x,y in v.items()}
    return r



class NodeClassMixin(object):
    """This mixin supplies the `get_node_class() -> Node` function.
    Applied as a function so it may reference the `Node` class from the module
    globals after instanstiation. """

    def get_node_class(self):
        return Node


class Edge(NodeClassMixin, LiveEdge):
    """An `Edge` represents a connect between two _nodes_ within the graph.

    A single _Edge_ extends the default `LiveEdge` with a reference to the `Node`
    through the `get_node_class() -> Node` method
    """
    pass


class Node(LiveNode):
    """A single _Node_ extends the default `LiveNode` to wrap the entities
    when walking the graph.  Note this class has a reference to the yielding `Edge`:

        class MyNode(LiveNode):
            edge_class = Edge

    Alternatively implement a method:

        class MyNode(LiveNode):
            def get_edge_class(self):
                return Edge
    """
    edge_class = Edge


class Connections(NodeClassMixin, Edges, Pins):
    """An entity to hold and spawn edges."""
    # node_class = Node

    def connect(self, *units, direction=FORWARD, data=None, edge=None):
        """

        Call upon the bridge_pairs function, passing `self.add_edge` as the pair
        calling function. Then pin nodes 0 and -1 using `pin_ends` passing all
        newly created edges.

        All units as a iterable n+1 are pair split and all other attributes
        pass directly to the caller function. `A` and `D` are pinned as exit
        nodes:

            g.connect('ABCD', direction=1, foo='bar')
            A => B | B => C | C => D

        Return a tuple of ThinEdge types
        """
        edges = bridge_pairs(self.add_edge, *units,
                             direction=direction, data=data, edge=edge)
        self.pin_ends(edges, direction)
        return edges

    def pp(self):
        """Print a clean version of the internal data structure by recasting
        all _defaultdict_ to `dict` types before pretty print.
        Return None
        """
        pprint(self.get_data())

    def get_data(self, clean=True):
        """Return the internal data-structures responsible for the graph,
        connections and assicated objects. If `clean` is True the internal
        (defaultdict defaultdict set) is cast as a dict dict set.
        If `clean` is False return the unaltered data-structures
        """
        d = vars(self)
        return clean_dict_dict(d) if clean else d

    def node(self, *a, **kw):
        """A convenience method to call upon a new `Node(graph, name **)` from
        the internal setup.
        The new node `parent` is this Connections instance. All other argument
        and keyword arguments pass directly to the node:

            graph.node('Foo') == Node(graph, 'Foo')
        """
        return self.get_node_class()(self, *a, **kw)

    def get_start_node(self, direction=FORWARD):
        """Yield a "Start node"; a node item at the _start_ of a chain.
        Return an ExitNode type with a 'start' identifier.
        """
        return ExitNode(self, 'start', direction)

    def __call__(self, *a, **kw):
        """A wrapper to the `self.node` method, allowing the call of a graph
        to yield an internal node:

            g = Connections()
            g.connect(*'ABC')
            g('A') == g.node('A') == Node(g, 'A')
        """
        return self.node(*a, **kw)

