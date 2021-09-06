from collections import UserDict
from pprint import pprint as pp
from itertools import chain
from collections import Counter
from collections import defaultdict

from collections import UserList
from collections import ChainMap
from itertools import tee
import random

from nodes import *
from edges import *
import walker
import chains
import render


class IDMethod(object):
    """A node applied to the graph may be anything, such as a int, str, dict, or
    function etc..

    The ID should be predicable across sessions.
    When applying an item to the tree, the ID references siblings.

    If the ID is none, the given node value is used. This is very usable, but
    not great for storing long-values or secure data.
    Using `id` is generally acceptable, but may bloat dev work.
    """
    id_method = None # hash # id

    def get_id_method(self):
        """Return the function used for the identification of a node.
        If None, the entity given during inspection is returned as the ID,

            g = Graph(id_method=None)
            g.connect('a', 'b')
            g['a'] == 'a'

        Other useful methods are `id`, `hash` or any function to produce a
        unique ID for the entity.
        """
        method = self.id_method
        if method is None:
            method = lambda x:x
        return method

    def get_ids(self, *items):
        """Return a tuple of IDS for all given items, calling upon `get_id`
        for each unit.
        """
        return tuple(self.get_id(x) for x in items)

    def get_id(self, item):
        """
        Return the ID of the given entity. If the `item` is a Node type,
        call to `item.get_value()`, else, call upon the `id_method`.

        The return type is any valid dict key identifier
        """
        if hasattr(item, 'get_id'):
            return item.get_id()

        if isinstance(item, Node):
            item = item.get_value()
        method = self.get_id_method()
        return method(item)


ONLY = '_only_'


class CounterTree(object):
    """A Tree binds all the connections of the info dict, associated to a graph (dict) type.
        """
    def __init__(self, direction=None):
        self.forward = self.get_store()
        self.reverse = self.get_store()
        self.forward_edges = defaultdict(set)
        self.reverse_edges = defaultdict(set)

    def get_store(self):
        return defaultdict(Counter)

    def __getitem__(self, k):
        return getattr(self, k)

    def get_connected(self, name, direction='forward'):
        _tree = self[direction]

        if name in _tree:
            return _tree[name]

    def get_edges(self, name_a, name_b, direction='forward'):

        edges = f"{direction}_edges"
        _edge_tree = self[edges]
        name = f'{name_a}{name_b}'

        if name in _edge_tree:
            _edges = _edge_tree[name]
            r = ()
            for _e in _edges:
                r += (_e.render(name_a, name_b),)
                # if (getattr(_e, 'factory', None) or False) is True:
                #     r += (_e(name_a, name_b),)
                #     continue
                # r += (_e, )

            return tuple(r)

        return ()

    def bind(self, a, b, edge=None, meta_data=None, meta_append=None):
        """Connect entity A to entity B through the given edge. The two entities
        should be key hasable.
        """
        self.set_bound_meta(a,b, meta_data)
        if meta_append is not None:
            self.update_meta(a,b, meta_append)

        if edge is not None:
            self.add_edge(a,b, edge)

        return tuple(self.forward[a]).index(b)

    def add_edge(self, a,b, edge):
        _fe = self.forward_edges[f"{a}{b}"]
        _re = self.reverse_edges[f"{b}{a}"]
        _fe.add(edge)
        _re.add(edge)
        return len(_fe), len(_re)

    def set_bound_meta(self, a,b, meta_data=None):
        self.forward[a][b] += (meta_data or 1)
        self.reverse[b][a] += (meta_data or 1)

    def get_meta_chain(self, a, b=None, direction='forward'):
        g = self.get_meta_data
        C = ChainMap
        if b in [None, ONLY]:
            return C(g(a, direction=direction), )
        return C(g(a, direction=direction), g(a,b,  direction=direction),)

    def get_meta_data(self, a, b=None, direction='forward'):
        b = b or ONLY
        return self[direction][a][b]


class DictTree(CounterTree):

    direction_pair = (
            ('forward', 'reverse',),
        )

    def get_store(self):
        return defaultdict(self.get_internal_store)

    def get_internal_store(self):
        return defaultdict(dict)

    def set_bound_meta(self, a, b, meta_data=None):
        """The 'forward' structure bind meta data for a node and its _next_
        counterpart in a nested dict - alike 3D data.

        Applying meta:

            {
                '0.40': {
                    '0.91': {'foo': 'egg'}
                },
                '0.91': {
                    '0.30': {'foo': 'bar'},
                    '0.40': {'foo': 'egg'}
                }
            }
        """

        d = (meta_data or {})

        # self.forward[a][b] = d
        # self.reverse[b][a] = d

        self.update_meta(a,b, meta=d, replace=True)
        # self.update_node_meta(a,ONLY, meta=d, replace=True)
        # self.update_node_meta(b,ONLY, meta=d, replace=True)

    def update_meta(self, a, b=ONLY, meta=None, replace=False):
        """
        >>> g.tree.update_meta('0.40', '0.91', {"egg3": 2})
        >>> pp(g.tree.forward["0.40"])
        defaultdict(<class 'dict'>,
                    {'0.91': {'egg': 2, 'egg3': 2, 'foo': 'bar'},
                     '_only_': defaultdict(<class 'dict'>,
                                           {'egg': 2,
                                            'egg3': 2)})

        >>> g.tree.update_meta('0.40', meta={"ham": 2})
        defaultdict(<class 'dict'>,
                    {'0.91': {'egg': 2, 'egg3': 2, 'foo': 'bar'},
                     '_only_': defaultdict(<class 'dict'>,
                                           {'egg': 2,
                                            'egg3': 2,
                                            'ham': 2})})
        """
        d = (meta or {})
        self.update_nodes_pair_meta(a,b, meta=d, replace=replace)

    def update_nodes_pair_meta(self, a,b, meta=None, replace=False):
        d = (meta or {})
        # self.forward[a][b].update(d)
        # self.reverse[b][a].update(d)
        self.update_node_meta(a, other=b, meta=d)
        # self.update_nodes_only_meta(a,b, meta=d, replace=replace)

    def update_nodes_only_meta(self, *nodes, meta=None, replace=False):
        for n in nodes:
            self.update_node_meta(n, other=ONLY, meta=meta, replace=replace)

    def update_node_meta(self, node, other=ONLY, meta=None, replace=False):
        d = (meta or {})
        for fw_n, rv_n in self.direction_pair:
            fw, rv = (self[fw_n], self[rv_n], )

            if replace:
                fw[node][other] = self.get_internal_store()
                rv[other][node] = self.get_internal_store()

        fw[node][other].update(d)
        rv[other][node].update(d)


Tree = DictTree
# Tree = CounterTree


class GetNextMixin(object):


    def get_node(self, node_name):
        if isinstance(self.data.get(node_name), NodeBase):
            return self.data[node_name]
        return self.node_class(self, node_name)

    def get_next(self, current_node=None):
        if not isinstance(current_node, (Node, NodeBase, self.node_class)):
            current_node = self.get_node(current_node)

        current_node = current_node or self.get_start_node()
        print('get_next', current_node)
        return current_node.graph.start_pins

    def get_chain(self, start=None, end=None, **kw):
        """Get a chain of nodes, if None is passed use the relative baked node
        """
        start = start or self.get_start_node()
        end = end or self.get_end_node()
        stash = { '_': random.random()}
        v = chains.get_chains(self, start, end, stash=stash, **kw)

        # pp(new_stash)
        stash.pop('_')
        return tuple(chains.Chain(self, x) for x in stash.values())

    def get_edges(self, a, b, direction='forward'):
        _next = self.tree.get_edges(a,b, direction=direction)
        return _next

    def get_parapaths(self, paths=None):
        """

            p = (4, 1, 1, 0, 1, 0)
            p2= (0, 2, 0, 1, 0, 1)
            p3 = (1, 0, 0, 0, 0, 0, 0, 0, 0)

            dict_res = g.get_parapaths( (p, p2, p3))
            pp(dict_res)

            pp(g.get_parapaths(tuple(g.positions)))

        """
        paths = paths or tuple(self.positions)
        start_node = self.get_start_node()

        max_len = max(tuple(len(x)+1 for x in paths))
        # A dict for each path, { p: (1,2,3), n: () }
        d = { i: {'p': paths[i], 'n': (), } for i in range(len(paths)) }

        res = {}

        for lr_index in range(max_len):
            # step the path into the left-right position
            # and record.
            pops = ()
            for path_index in d:
                path_dict = d[path_index]
                path = path_dict['p']

                try:
                    current_index = path[lr_index]
                except IndexError:
                    # path is complete
                    res[path] = chains.Chain(self, path_dict['n'])
                    pops = (path_index, )
                    # Stop here to ensure the stepper doesn't continue stacking
                    # for this path - as continuation _is_ possible if
                    # the node is futher connected past the given path.
                    continue

                try:
                    last_node = path_dict['n'][lr_index-1].node
                except IndexError:
                    last_node = start_node

                # step the item
                next_node = last_node.next[current_index]

                # edges = chains.get_edges(self, last_node, next_node)
                # el = chains.EdgeLink(edge, last_node, next_node, x=current_index, y=lr_index)
                # Consider X as the Left-right walk of a chain,
                # and Y as the edge step
                cl = chains.ChainLink(next_node, x=lr_index, y=current_index)
                # path_dict['n'] += edges + (cl,)
                path_dict['n'] += (cl,)

            for path_index in pops:
                d.pop(path_index)

        return tuple(res.values())

    def get_path(self, path):
        v = self.get_parapaths((path,))
        return v


class Positions(object):
    """Positions identify the _step path_ of a walker through the edges of
    nodes, from the original _start_ node to the _end_ node.

    Unlike an ID list, the positions are relative to the node, and its indexed
    edges.

    ID List:
        ('ive', 'information', 'vegetable', 'animal', 'and', 'mineral')

    A relative positions list:

        (8, 10, 0, 1, 3, 0, 0, 1),

    To reduce, begin at the _start_ node for index item `8`, resulting in node
    "ive". Next step to edge `10` into node "information". The next edge at index `0`
    is "vegetable", an so on.

    """
    def clear_positions(self):
        self.key_chains = set()
        self.positions = set()

    def record_positions(self, id_chain, positions):
        self.key_chains.add(id_chain)
        self.positions.add(positions)

    def path_get(self, *path):
        # given a path, return a list of nodes.
        pass


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class Connect(object):

    def pair_connect(self, items, pin_ends=True, **kw):
        """
            g = graph.Graph(id_method=None)
            g.pair_connect(values, pinned=False)
            g.pin_ends(values)
        """
        # vv = tuple(pairwise(items))
        for i, (a,b) in enumerate(pairwise(items)):
            self.connect(a,b, **kw)
        self.pin_ends(items)

    def connect(self, *nodes, edge=None, pinned=True, **kw):
        """Perform a store and bind of all given nodes in linear order,
        return list of positions for the edge path.

            g = Graph()
            g.connect(*'ABCDEF')
            g.connect(*'ADPOEF')

        The "nodes" may be any storable dict entity such as a string,
        number or callable. The identity of the node is discovered during the
        linear connect.

        Usually a unique ID per node is created but this is dependent upon the
        input data. E.g, strings are always the same string.
        """
        pairs, positions = self.linear_connect(nodes, pinned=pinned, edge=edge, **kw)

        # edge_positions = tuple((1+i)*(x+1)-1 for i,x in enumerate(positions))
        edge_positions = tuple(f"{i}_{x}" for i,x in enumerate(positions))
        node_path = tuple(x[0] for x in pairs) + (pairs[-1][-1] ,)

        if self.paths is not None:
            self.paths.connect(*edge_positions)

        self.record_positions(node_path, positions)
        return positions

    """
        >>> list(permutations('abcd',2))
        [('a', 'b'), ('a', 'c'), ('a', 'd'), ('b', 'a'), ('b', 'c'), ('b', 'd'), ('c', 'a'), ('c', 'b'), ('c', 'd'), ('d', 'a'), ('d', 'b'), ('d', 'c')]
        >>> list(combinations('abcd',2))
        [('a', 'b'), ('a', 'c'), ('a', 'd'), ('b', 'c'), ('b', 'd'), ('c', 'd')]
    """
    def linear_connect(self, items, pinned=True, init_position=-1, edge=None, **meta):
        """Connect left to right - all entities within the given list.
        Return a tuple of (pairs, postions). Pairs of A->B sibling and all
        positions for each branch pair.
        """
        pairs = ()
        items = tuple(items)

        id_first, id_last = self.get_ids(items[0], items[-1])


        if pinned:
            self.start_pins[id_first] += 1
            self.end_pins[id_last] += 1

        if init_position == -1:
            # position from pinned_node
            try:
                init_position = tuple(self.start_pins).index(id_first)
            except ValueError:
                print('Position not in start pins:', id_first)

        positions = (init_position,)# {}

        for i, node in enumerate(items):
            to_node = None

            if i+1 < len(items):
                # The next node does exist, grab its name to connect _this_
                # as a forward relation.
                to_node = items[i+1]

            if len(items) == i+1:
                continue

            *ids, branch_position = self.bind_pair(node, to_node, edge=edge, meta_append=meta)
            positions += (branch_position,)
            pairs += (ids, )

        return pairs, positions


class Reset(object):

    def reset(self):

        self.clear_positions()
        self.reset_tree()
        self.reset_pins()
        self.reset_paths()

    # def get_init_tree(self, direction=None):
    #     return Tree(direction) #defaultdict(set)

    def reset_tree(self):
        tree = self.get_init_tree
        self.tree = tree()

    def reset_paths(self):
        self.paths = None
        if self.depth < self.max_depth:
            self.paths = self.__class__(id_method=self.id_method, depth=self.depth)

    def reset_pins(self):
        self.start_pins = defaultdict(int)# set()
        self.end_pins = defaultdict(int)# set()


class Pins(object):
    """The `Pins` mixin provides thin functions for the start
    and end pins of a graph, used by linear connection.
    """
    def get_start_node(self):
        return ExitNode(self, START)

    def get_end_node(self):
        return ExitNode(self, END)

    def pin_ends(self, nodes, edge=None):
        """
        Given a list of 1n nodes, pin 0 and -1 to start and end respectively,
        return a triple of tuples

            (start_node_id, end_node_id),
            (node[0]_id, node[-1]_id),
            (position[0], position[-1])

        of which can be unpacked neatly:

            values = (1,2,3,4,5,)
            pins, nodes, positions = graph.pin_ends(values)

        items `0` and `-1` will pin to _start_ and _end_ as a standard bound pair.

        """
        a1, b1, p1 = self.bind_pair(self.get_start_node(), nodes[0], edge=edge)
        a2, b2, p2 = self.bind_pair(nodes[-1], self.get_end_node(), edge=edge)
        return (b1, a2,), (a1, b2), (p1, p2)


class RenderMixin(object):

    def to_json(self, name, **options):
        p = f"./view/{name}.json"
        p2 = f"./view/{name}_paths.json"
        render.to_visjs_json(self.paths, p2, **options)
        return render.to_visjs_json(self, p, **options)


class Graph(UserDict, IDMethod, GetNextMixin, Positions, Connect, Reset, Pins, RenderMixin):

    node_class = Node
    max_depth = 3

    def __init__(self, initdata=None, id_method=None, depth=-1, **kw):
        super().__init__(initdata)
        self.depth = depth + 1
        self.id_method = id_method or self.id_method
        self.__dict__.update(kw)
        self.reset()

    def get_init_tree(self, direction=None):
        return Tree(direction) #defaultdict(set)

    def add_edge(self, a,b, edge):
        id_a, id_b = self.get_ids(a,b)
        edge_positions = self.tree.add_edge(id_a, id_b, edge)
        return id_a, id_b, edge_positions

    def bind_pair(self, a, b, edge=None, meta_append=None):
        id_a, id_b = self.get_ids(a,b)
        # record data attributes to flat _self_ dict
        r = {}
        for x,_id in zip((a,b),(id_a, id_b)):
            v = x
            if hasattr(x, 'get_value') and (not isinstance(x, NodeBase)):
                v = x.get_value()
            r[_id]=v
        # r = {x:x for x in (id_a, id_b) if x not in self} # {id_a:a,id_b:b}
        self.store_items(r)
        # Build an a to b connection through e
        branch_position = self.bridge(id_a, id_b, edge=edge, meta_append=meta_append)
        return id_a, id_b, branch_position

    def bridge(self, a, b, edge=None, meta_append=None):
        # print('bridge', a, '=>', b)
        return self.tree.bind(a, b, edge=edge, meta_append=meta_append)

    def store_items(self, d):
        # print('store', d)
        self.update(d)

    def get_bar_walker(self, start_node=None):
        start_node = start_node or self.get_start_node()
        return walker.bar_walk(start_node)
