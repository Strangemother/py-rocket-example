from g4.enums import *
# from .nodes.base import NodeBase
from g4.nodes.mixins import NodesMixin
from g4.nodes.live import LiveNode


class Node(LiveNode):

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


class ExitNode(Node, NodesMixin):
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
