from g4.nodes.mixins import NodesMixin


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

