from g4.tree import TreeStore


class Edges(TreeStore):

    def add_edge(self, unit_pair, direction, data=None, edge=None):
        # store the edge entity, returing a uuid
        temp_edge = self.make_edge(unit_pair, direction, data, edge=edge)
        self.store_edge(temp_edge, direction)
        return temp_edge

    def make_edge(self, unit_pair, direction, data, edge=None):
        #A transparent edge applies all values to a new key value dict
        #location in 'edge_data' without manifesting a real edge in
        _id = self.make_id
        ids = tuple(_id(x) for x in unit_pair)

        return ThinEdge(self, ids, unit=unit_pair, meta=data, edge=edge)#, _spawn_index=self._spawn_index)

    def make_id(self, unit):
        return self.make_stable_id(unit)
        # return lambda x:x

    def make_stable_id(self, unit):

        lx = lambda x:x

        v ={
            type(0): lx,
            type(''): lx,
            type({}): id,
            type(True): lx,
        }

        return v.get(type(unit), hash)(unit)


class ThinEdge(object):
    """A temporary edge unit, used during creation if an original edge is not
    given.
    """
    def __init__(self, parent, ab_id, edge_id=None, meta=None, edge=None, **kw):
        self.parent = parent
        self.edge_id = edge_id
        self.ab_id = ab_id
        self.meta = meta or {}
        self.edge = edge
        self.__dict__.update(kw)

    def get_id(self):
        _id = lambda x: '_'.join(map(str, x))# f"e_{id(x)}" #f'e_{self._spawn_index}'
        return self.edge_id or _id(self.get_node_ids())

    def get_node_ids(self):
        return self.ab_id

    @property
    def first(self):
        return self.get_node_ids()[0]

    @property
    def last(self):
        return self.get_node_ids()[-1]

    def get_store(self):
        # return self
        return self.meta, self.edge

    def get_entities(self):
        refs = self.parent.datas['nodes_references']
        return tuple(refs[x] for x in self.get_node_ids())

    def __repr__(self):

        entities = self.get_entities()
        # entities = self.ab_id
        return f'<{self.__class__.__name__} "{self.get_id()}" {entities}>'
