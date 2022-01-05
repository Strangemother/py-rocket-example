
from collections import defaultdict


class TreeStore(object):
    inverse = True

    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self):
        """Setup the storage points for the internal data-sets. Naturally
        called through `TreeStore.__init__()`.

        `trees` and `datas` store the direction edge graphs and any object
        references for the relevant key.

        By default each storage is a defaultdict yielding a defaultdict,
        storing sets.

            trees = {
                direction: {
                    node_id_1: {edge_id, edge_id_1,}
                    node_id_2: {edge_id_1,}
                }
            }

        `datas` has the same layout:

            datas = {
                'edge_connections': {'A_B': ('A', 'B')},
                'edge_data': {'A_B': {}},
                'nodes_references': {'A': 'A', 'B': 'B'}
            }

        build from example:

            g = Connections()
            g.connect(*'AB')

        Return None
        """
        self.trees = defaultdict(lambda: defaultdict(set))
        self.datas = defaultdict(lambda: defaultdict(set))

    def store_edge(self, temp_edge, direction):
        """Store the values within the given temp_edge unit as a single edge,
        The given instance isn't stored, rather the content is extracted from
        the methods.

            unit_pair = ('a', 'b',)
            ids = tuple(id(x) for x in unit_pair)
            meta = { 'foo': 'bar' }
            thin_edge = ThinEdge(self, ids, unit=unit_pair, meta=meta, edge=None)

            store_edge(temp_edge, FORWARD)

        A temp edge should contain:

            temp_edge:
                get_id()        return the edge id
                get_node_ids()  return the node pair
                unit            the node references (a pair) to store as data,
                                using the node ids
                get_store()     (meta data, edge) to store. The 'edge'
                                may be an instance of a callable Edge type.

        All stacked within the TempEdge for convenience.

        1. Store edge_connections with `node_ids`
        2. store nodes_references for each id and unit
        3. Add tree references for the given `direction`
        4. store any extra `edge_data`, `edge_units`

        """
        edge_id = temp_edge.get_id()
        node_ids = temp_edge.get_node_ids()

        # store data and this unit reference.
        self.datas['edge_connections'][edge_id] = node_ids

        for _id, unit in zip(node_ids, temp_edge.unit):
            self.datas['nodes_references'][_id] = unit

        self.tree_add_both(direction, node_ids, edge_id)

        meta_data, class_unit = temp_edge.get_store()
        if meta_data is not None:
            ## Any additional content for the edge. Unpacked here
            ## if the target unit is a complex class type.
            self.datas['edge_data'][edge_id] = meta_data

        if class_unit is not None:
            self.datas['edge_units'][edge_id] = class_unit

        return temp_edge

    def tree_add_both(self, direction, node_ids, edge_id):
        """Bind the two nodes through the edge in the given direction using the
        function `self.tree_add(direction, unit_id, edge_id)`

            tree_add_both(1, ('node_id_a', 'node_id_b'), 'edge_id')

        If `self.inverse` is `True`, the _opposite_ direction is applied to the
        tree, creating the inverse (mirror) of the given connection

            B <= A => B

        If inverse is False, only the given direction is applied. This method
        is synonymous to:

            TreeStore.trees[direction][a_id].add(edge_id)
            TreeStore.trees[-direction][b_id].add(edge_id)

        Return None.
        """
        dirs = (direction, -direction) if self.inverse else (direction, )

        for _dir, _id in zip(dirs, node_ids):
            self.tree_add(_dir, _id, edge_id)

    def tree_add(self, direction, unit_id, edge_id):
        """Add the given edge_id to the set within the _direction_ for the unit_id

        The direction defines the uppermost graph start, naturally being `1` and
        inverse `-1`. Within a single direction tree, the `unit_id` has a set
        of `edge_id`.

            self.trees[1]['node_id'] = set(edge_id)

        Bind an ID to an edge in two opposite connections - synonymous to:

            self.tree_add(direction, a_id, edge_id)
            self.tree_add(-direction, b_id, edge_id)
        """
        return self.trees[direction][unit_id].add(edge_id)
