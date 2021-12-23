
from collections import defaultdict


class TreeStore(object):
    inverse = True

    def __init__(self):
        super().__init__()
        print('Setup TreeStore')
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
        # create IDS, optionally store key to node
        # Not storing should yield a standard key 2 key connection
        # Don't store for less memory refs.

        edge_id = temp_edge.get_id()
        node_ids = temp_edge.get_node_ids()
        # a_id, b_id = temp_edge.get_node_ids()
        # store data and this unit reference.
        self.datas['edge_connections'][edge_id] = node_ids

        for _id, unit in zip(node_ids, temp_edge.unit):
            self.datas['nodes_references'][_id] = unit

        self.tree_add_both(direction, node_ids, edge_id)

        d, c = temp_edge.get_store()
        if d is not None:
            ## Any additional content for the edge. Unpacked here
            ## if the target unit is a complex class type.
            self.datas['edge_data'][edge_id] = d

        if c is not None:
            self.datas['edge_units'][edge_id] = c

        return temp_edge

    def tree_add_both(self, direction, node_ids, edge_id):
        # trees[direction][a_id].add(edge_id)
        # trees[-direction][b_id].add(edge_id)

        dirs = (direction, )

        if self.inverse:
            dirs = (direction, -direction)

        for _dir, _id in zip(dirs, node_ids):
            # self.tree_add(direction, a_id, edge_id)
            # self.tree_add(-direction, b_id, edge_id)
            self.tree_add(_dir, _id, edge_id)

    def tree_add(self, direction, unit_id, edge_id):
        trees = self.trees
        return trees[direction][unit_id].add(edge_id)
