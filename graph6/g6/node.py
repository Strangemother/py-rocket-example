from .enums import *
from .base import NodeBase, NodesMixin
# from .nodes.mixins import NodesMixin
# from .live.node import LiveNode


class LiveEdge(NodesMixin):

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
# class LiveNode(NodeBase):
    edge_class = None

    def __repr__(self):
        ref = self.get_reference()
        cn = self.__class__.__name__
        return f'<{cn} "{self.get_uuid()}" {ref}>'

    def get_edge_class(self):
        return self.edge_class # LiveEdge

    # class Node(LiveNode):

    def get_node_class(self):
        return self.__class__

    def __init__(self, parent, name=None, direction=FORWARD, tree_name='trees', uuid=None):
        self.parent = parent
        self.name = name
        self.direction = direction
        self.tree_name = tree_name
        self.uuid = uuid

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

    def __init__(self, parent, name, direction, tree_name='pins'):
        null_name = None
        super().__init__(parent, null_name, direction, tree_name, name)

    def get_edges(self):
        """Override NodeBase.get_edges() to return a list of flat edges per node,
        rather than a list of edges for a entry list of edge ids.
        """
        r= ()
        for n in self.get_nodes():
            r += n.get_edges()
        return r

    def get_connection(self):
        return self.get_entry()
