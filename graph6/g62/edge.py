from .tree import TreeStore
from .utils import make_stable_id, as_ids


class Edges(TreeStore):
    """Edges is an extension of the TreeStore class, applying additional methods
    to `Edges.make_edge` and `TreeStore.store_edge` a ThinEdge type.
    """

    def add_edge(self, unit_pair, direction, data=None, edge=None):
        """Add a new "edge" given a pair of ids, direction and other properties

            add_edge(unit_pair=(1,2,), direction=1, data={},)

        Return the newly create ThinEdge
        """
        # store the edge entity, returing a uuid
        temp_edge = self.make_edge(unit_pair, direction, data, edge=edge)
        self.store_edge(temp_edge, direction)
        return temp_edge

    def make_edge(self, unit_pair, direction, data, edge=None):
        #A transparent edge applies all values to a new key value dict
        #location in 'edge_data' without manifesting a real edge in

        # _id = self.make_id
        # ids = tuple(_id(x) for x in unit_pair)
        ids = as_ids(*unit_pair)
        return ThinEdge(self, ids, unit=unit_pair, meta=data, edge=edge)
        #, _spawn_index=self._spawn_index)

    def make_id(self, unit):
        return make_stable_id(unit)
        # return lambda x:x


class ThinEdge(object):
    """A temporary edge unit, used during creation. It doesn't live very long
    and should be designed to throw-away.
    """

    def __init__(self, parent, ab_id, edge_id=None, meta=None, edge=None, **kw):
        """A ThinEdge is a meta-data container of all the information for the
        _real_ (optional) given `edge`.
        The `parent` is the Connection with all data reference
        `ab_id` is a tuple if entity `a` and `b` nodes for this edge. The
        `edge_id` should be the unique identifier matching the ID within the
        parent references

        Provide additional edge data through the `meta`. If meta is `None`, an
        empty object will be applied.

        Any additional keyword arguments are applied to the `__dict__` of this
        class - such as `unit`.

        """
        self.parent = parent
        self.edge_id = edge_id
        # tuple of ids ('a', 'b')
        self.ab_id = ab_id
        # Return meta and edge through self.get_store()
        self.meta = meta or {}
        # May be a real class wrapper.
        self.edge = edge
        # mutate this edge with any additional attributes
        # - bound for `TreeStore.store_edge`
        self.__dict__.update(kw)

    def get_id(self):
        """Return this edge id through either `self.edge_id` or generating
        a new one using the existing node ids

        A new id is both node ids merged with an underscore `_`

        Return a `str` of the ID.
        """
        _id = lambda x: '_'.join(map(str, x))# f"e_{id(x)}" #f'e_{self._spawn_index}'
        return self.edge_id or _id(self.get_node_ids())

    def get_node_ids(self):
        """Return the tuple of node IDS.
        """
        return self.ab_id

    @property
    def first(self):
        """Return the first node id
        """
        return self.get_node_ids()[0]

    @property
    def last(self):
        """Return the last node id
        """
        return self.get_node_ids()[-1]

    def get_store(self):
        # return self
        return self.meta, self.edge

    def get_entities(self):
        """Return a tuple of node reference (data objects) for each node id
        within the ab_id tuple.
        """
        refs = self.parent.datas['nodes_references']
        return tuple(refs[x] for x in self.get_node_ids())

    def __repr__(self):
        """A clean representation of this class

            >>> g.connect('a','b'[0]
            <ThinEdge "a_b" ('a', 'b')>
        """
        entities = self.get_entities()
        # entities = self.ab_id
        return f'<{self.__class__.__name__} "{self.get_id()}" {entities}>'
