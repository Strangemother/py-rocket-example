from .enums import *
from .node import NodeBase, NodesMixin
# from .nodes.mixins import NodesMixin
# from .live.node import LiveNode


class LiveEdge(NodesMixin):
    """A 'live edge' represents an existing connection of two nodes within the
    graph. Usually this node yields from iteration calls of edges and should be
    the starting point for overrides.

    This is purposefully not called an "Edge" - leaving scope for easier
    abstraction. Take a look at `connect.Edge` for a real-world implementation:

        class Edge(LiveEdge):
            node_class  = MyNode

        class Graph(Connections):
            edge_class = Edge
    """

    def __init__(self, parent, uuid, direction, index=-1):
        self.parent = parent
        self.uuid = uuid
        self.direction = direction
        self.index = index

    def get_parent_data(self, key=None):
        if key:
            return self.parent.datas[key]
        return self.parent.datas

    def get_data(self):
        return self.get_parent_data('edge_data')[self.uuid]

    def get_edge_class(self):
        return self.__class__ #LiveEdge

    # def get_node_class(self):
    #     return Node

    def __repr__(self):
        is_valid = self.get_nodes()
        # is_valid = 'Valid' if self.is_valid() else 'Not Valid'
        return f'<{self.__class__.__name__} {self.direction} "{self.uuid}" {is_valid}>'

    def get_next_nodes(self, direction=None):
        """Return a list of nodes in the forward direction across the
        edge connections. This doesn't _call_ the edge.
        """
        di = self.direction if direction is None else direction
        return tuple(x.get_nodes(di)[-1] for x in self.get_edges())

    def __eq__(self, other):
        """
            g('B', direction=-1).edges[0] ==  g('A').edges[0]
            True
        """
        if isinstance(other, self.__class__):
            return self.uuid == other.uuid
        return super().__eq__(other)

    @property
    def data(self):
        return self.get_data()

    @property
    def a(self):
        return self.get_nodes()[0]

    @property
    def b(self):
        return self.get_nodes()[-1]


class LiveNode(NodeBase):
    edge_class = None
    node_class = None

    def __init__(self, parent, name=None, direction=FORWARD, tree_name='trees', uuid=None):
        self.parent = parent
        self.name = name
        self.direction = direction
        self.tree_name = tree_name
        self.uuid = uuid

    def __repr__(self):
        ref = self.get_reference()
        cn = self.__class__.__name__
        return f'<{cn} "{self.get_uuid()}" {ref}>'

    def get_edge_class(self):
        return self.edge_class # LiveEdge

    def get_node_class(self):
        return self.node_class or self.__class__

    def get_uuid(self):
        return self.uuid or self.parent.make_id(self.name)

    def __repr__(self):
        is_valid = 'Valid' if self.is_valid() else 'Not Valid'
        cn = self.__class__.__name__
        return f'<{cn} "{self.uuid or self.name}" {is_valid}>'


class ExitNode(LiveNode, NodesMixin):
    """An exit node represents a connection to the graph from a _null point_
    containing all the _start_ or _end_ references of the graph.
    For each linear entry, the first and last items are bound to their respective
    "Pin".
    """
    # g.node(uuid='start', tree_name='pins').get_entry()
    node_class = None

    def __init__(self, parent, name, direction, tree_name='pins'):
        null_name = None
        super().__init__(parent, null_name, direction, tree_name, name)

    def get_edges(self):
        """Override NodeBase.get_edges() to return a tuple of flat edges for
        all internal nodes through `NodesMixin.get_nodes` - rather than a
        tuple of edges for a single nodes' edge list."""
        return tuple(y for x in self.get_nodes() for y in x.get_edges())

    def get_node_class(self):
        return self.node_class or self.parent.get_node_class() or self.__class__

    def get_connection(self):
        """Override the `NodeBase.get_connection()` function to return this units
        tree data through `NodeBase.get_entry()`, rather than the parents
        edge_connections
        """
        return self.get_entry()

    def get_entry(self):
        """Return the _current_ tree entry using the internal `get_uuid()`.
        This will be the sub data for the node item, by default a set of
        edge ids.

            >>> self.get_entry()
            {'3_4', '3_5'}

        Synonymous to:

            self.parent.trees[direction][uuid]

        To gather a tuple of resolved edge entities, consider `self.get_edges()`
        """
        return self.get_tree()[self.get_uuid()]
