import sys
# sys.path.append('F:/godot/python-rocket-software/graph2')

# from graph import pairwise
from collections import defaultdict
from itertools import tee
from pprint import pprint as pp


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)



UP = 3
FORWARD = 1
REVERSE = -FORWARD
DOWN = -UP


START = '_start_'

class Pins(object):

    def __init__(self):
        print('Setup Pins')
        super().__init__()
        self.pins = defaultdict(lambda: defaultdict(set))

    def pin_ends(self, edges, direction):
        first_first_id = edges[0].first
        last_last_id = edges[-1].last

        v = self.quick_pin(direction, start=first_first_id, end=last_last_id)
        vr = self.quick_pin(-direction, start=last_last_id, end=first_first_id)
        return {direction:v, -direction: vr}

    def quick_pin(self, direction, **kw):
        """
            _pins = (
                ('start', first_first_id,),
                ('end', last_last_id,),
            )

            self.pin_direction(direction, _pins)
        """
        return self.pin_direction(direction, kw.items())

    def pin_direction(self, _direction, _pins):
        """
            # pins_dir = self.pins[-direction]
            _pins = (
                ('start', last_last_id,),
                ('end', first_first_id,),
            )

            pins_dir = self.pins[direction]
            pins_dir['start'].add(first_first_id)
            pins_dir['end'].add(last_last_id)

            pins_dir = self.pins[-direction]
            pins_dir['start'].add(last_last_id)
            pins_dir['end'].add(first_first_id)
        """
        pins_dir = self.pins[_direction]
        for name, node_id in _pins:
            # self.pins[direction]['start'].add(node_id)
            pins_dir[name].add(node_id)


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


class NodeBase(object):

    def __init__(self, parent, node_id, direction, tree_name='trees'):
        self.parent = parent
        self.node_id = node_id
        self.direction = direction
        self.tree_name = tree_name

    def get_entry(self):
        return self.get_tree()[self.get_uuid()]

    def get_edges(self, direction=None):
        edge_ids = self.get_entry()
        di = direction or self.direction
        return tuple(self.spawn_edge_instance(self.parent, x, di, i) for i, x in enumerate(edge_ids))

    def spawn_edge_instance(self, parent, edge_id, direction, index=-1):
        """Return an edge, given the parent and edge id. If an edge instance
        was given during creation, return the 'edge_unit' from the parent data.

        The edge instance exists isolated of this (wrapper) unit. If a custom
        class does not exist, A new instance of "LiveEdge" is returned.


            g.connect(*'AP', edge=CustomEdge)
            g('A').edges
            (
                <LiveEdge 1 "44735656_36296048" (<LiveNode "#" A>, <LiveNode "#" B>)>,
                <__main__.CustomEdge object at 0x0000000002AA9CF8>
            )

            g.datas['edge_units']['44735656_36252896']
            <class '__main__.CustomEdge'>

        Deleting the edge does not delete the connection (just the wrapper)

            >>> del g.datas['edge_units']['44735656_36252896']

            >>> g('A').edges
            (
                <LiveEdge 1 "44735656_36296048" (<LiveNode "#" A>, <LiveNode "#" B>)>,
                <LiveEdge 1 "44735656_36252896" (<LiveNode "#" A>, <LiveNode "#" P>)>
            )
        """
        # CustomEdge
        _Class = self.parent.datas['edge_units'].get(edge_id, None)
        is_factory = getattr(_Class, 'factory', False) is True
        kw = dict(parent=parent, uuid=edge_id, direction=direction, index=index)

        if _Class is None:
            _Class = LiveEdge

        # if is_factory or callable(_Class):
        if is_factory:
            if not callable(_Class):
                _Class = _Class.__class__

            # return _Class.__class__(**kw)

        if callable(_Class):
            return _Class(**kw)

        if hasattr(_Class, 'update'):
            # Is a dict type, and has an update function.
            _Class.update(**kw)

        return _Class


    def get_next_nodes(self, direction=None):
        """Return a list of nodes in the forward direction across the
        edge connections. This doesn't _call_ the edge.
        """
        di = self.direction if direction is None else direction
        return tuple(x.get_nodes(di)[-1] for x in self.get_edges())

    def is_valid(self):
        return self.get_uuid() in self.get_tree()

    def get_uuid(self):
        return self.node_id

    def get_tree(self):
        return getattr(self.parent,self.tree_name)[self.direction]

    def get_refs(self):
        return self.parent.datas['nodes_references']

    def get_reference(self):
        return self.get_refs()[self.get_uuid()]

    def __setattr__(self, k, v):
        if k == 'data':
            self.get_refs()[self.get_uuid()] = v
            return
        return super().__setattr__(k,v)

    @property
    def data(self):
        return self.get_reference()

    @data.setter
    def set_data(self,v):
        self.get_refs()[self.get_uuid()] = v
        # return self.get_reference()

    @property
    def edges(self):
        return self.get_edges()

    @property
    def next_nodes(self):
        return self.get_next_nodes()


class LiveNode(NodeBase):

    def __repr__(self):
        ref = self.get_reference()
        cn = self.__class__.__name__
        return f'<{cn} "{self.get_uuid()}" {ref}>'


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


class NodesMixin(object):

    def get_parent_data(self, key=None):
        if key:
            return self.parent.datas[key]
        return self.parent.datas

    def get_connection(self):
        return self.get_parent_data('edge_connections')[self.uuid]

    def get_nodes(self, direction=None):
        di = self.direction if direction is None else direction
        return tuple(LiveNode(self.parent, x, di) for x in self.get_connection())
        # return tuple(LiveNode(self.parent, refs[x], di) for x in self.get_connection())

    @property
    def nodes(self):
        return self.get_nodes()


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


class CustomEdge(object):
    factory=False

    def __init__(self, parent, uuid, direction):
        print('New Custom Edge')
        self.parent = parent
        self.uuid = uuid
        self.direction = direction

    def update(self, parent, uuid, direction):
        print(f'{self.__class__.__name__} update')


def main():
    example()


def example():
    es = Connections()
    es.connect(*'ABCDE')
    es.connect(*'CAB')
    v=es.connect(*'HORSE')
    g=es
    # pp(vars(es))
    print(v)

    # Getting pinned first nodes.
    # g.node(uuid='start', tree_name='pins').get_entry()
    # Or a key node.
    c=g.node('A').get_edges()
    e=ExitNode(g, 'start', 1)
    print(c)

    a={'foo': 2}
    b={'red': 3}
    g.connect(a,b, data={'egg': 'butter'})
    assert g.node(a).edges[0].data['egg'] == 'butter'

    ab_rev = g('B', direction=-1).edges[0] ==  g('A').edges[0]
    assert ab_rev == True

    def mycaller(*a, **kw):
        print('mycaller', a, kw)
        return "sausages"

    es.connect(*'AP', edge=mycaller)

    es.connect(*'QS', edge=CustomEdge(es, 1, 1))
    es.connect(*'RS', edge=CustomEdge)#(es, 1, 1))


    es.connect(*'DT', edge={})


if __name__ == '__main__':
    main()
