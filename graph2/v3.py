from collections import UserDict
from pprint import pprint as pp
from itertools import chain
from collections import Counter
from collections import defaultdict

from collections import UserList
import random


def main():
    global g
    global c
    g=functions()
    # g=alphabet()
    pp(vars(g))
    pp(vars(g.tree))

    c = g.get_chain(keep_noedge=True)
    pp(c)
    # print(c)
    print(len(c))
    t = (
        "_start_, NoEdge, fa, Edge, fb, Edge, fc, Edge, fd, NoEdge, _end_",
        "_start_, NoEdge, fa, NoEdge, fab, NoEdge, fac, NoEdge, fad, NoEdge, _end_",
        "_start_, NoEdge, b_a, Edge, b_b, Edge, b_c, Edge, b_d, NoEdge, _end_"
        )

    assert_paths(c,t)


def assert_paths(c,t):
    r = ()
    for row in c:
        names = ()
        for item in row:
            names += (item.node.name,)
        v = ', '.join(names)
        r += (v, )


    try:
        assert t == r
        print('Match success.')
        return
    except AssertionError as e:
        print('Error', e)

    for x,y in (tuple(zip(t,r))):
        print(x)
        print(y)
        print('')

    # pp(r)

def poppins():
    word = "supercalifragilisticexpialidocious"
    g = Graph(id_method=id)
    v= g.connect(*word)
    print(v)
    s = 'Um diddle, diddle diddle, um diddle ay'
    v= g.connect(*s)
    v= g.connect(*s)
    v= g.connect(*s)
    v= g.connect(*s)
    return g


def alphabet():
    """

    Each graph connection builds a bridged path, for chained execution
    across the graph through the given nodes. Notice the path index is
    deterministic for early and late positions, (ABCD and APPLES),
    and intial-referencing, for example "P" to "P" is of index 0, noting the
    first graphed for the Node "P" was "P".

        ABCD      (0, 0, 0, 0)
        DEFGHIJKL (1, 0, 0, 0, 0, 0, 0, 0, 0)
        DOGGY     (1, 1, 0, 1, 2)
        HORSE     (2, 1, 1, 0, 0)
        MOUSE     (3, 0, 2, 0, 0)
        BANANA    (4, 1, 1, 0, 1, 0)
        APPLES    (0, 2, 0, 1, 0, 1)

    To read a path, iterate each index relative to the graph position of the
    previous node:

        BANANA    (4, 1, 1, 0, 1, 0)

    The first value is the start _pin_:

        tuple(g.start_pins)[4]
        "B"

    from B we can walk forward with the path `[1, 1, 0, 1, 0]`. Each node
    resolves to an ordered list of _next_ keys (no edges involved)

        >>> tuple(g.tree.forward['B'])
        ('C', 'A')

    Full path:

        v=('B',)
        p = (1,1,0,1,0)

        for i in p:
           n = tuple(g.tree.forward[v[-1]])[i]
           v += (n,)

        print(v)
        ('B', 'A', 'N', 'A', 'N', 'A')

    """
    g = Graph(id_method=None)#id)
    v= g.connect(*'ABCD')
    print('ABCD     ', v)
    v= g.connect(*'DEFGHIJKL')
    print('DEFGHIJKL', v)
    v= g.connect(*'DOGGY')
    print('DOGGY    ', v)
    v= g.connect(*'HORSE')
    print('HORSE    ', v)
    v= g.connect(*'MOUSE')
    print('MOUSE    ', v)
    v= g.connect(*'BANANA')
    print('BANANA   ', v)
    v= g.connect(*'APPLES')
    print('APPLES   ', v)

    return g



def id_method(v):
    if isinstance(v, (int, float)):
        return v
    return v.__name__


def functions():
    g = Graph(id_method=id_method)
    g.connect(fa, fb, fc, fd)
    g.connect(fa, fab, fac, fad)
    g.connect(b_a, b_b, b_c, b_d, edge=Edge())
    g.connect(fa, fb, fc, fd, edge=Edge())

    # g.add_edge(fc, fd, edge=Edge())
    # g.add_edge(fc, fd, edge=Edge())
    # g.add_edge(fc, fd, edge=Edge())
    # g.add_edge(fc, fd, edge=Edge())
    # g.add_edge(fc, fd, edge=Edge())
    # g.add_edge(fc, fd, edge=Edge())
    return g


class Edge(object):

    @property
    def name(self):
        return self.__class__.__name__



def fa(v):
    return v + 1


def fb(v):
    return v + 2


def fc(v):
    return v + 3


def fd(v):
    return v + 4



def b_a(v):
    return v + 1


def b_b(v):
    return v + 2


def b_c(v):
    return v + 3


def b_d(v):
    return v + 4




def fab(v):
    return v + 2


def fac(v):
    return v + 3


def fad(v):
    return v + 4




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
        method = self.id_method
        if method is None:
            method = lambda x:x
        return method

    def get_ids(self, *items):
        return tuple(self.get_id(x) for x in items)

    def get_id(self, item):
        method = self.get_id_method()
        return method(item)


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
            return tuple(_edge_tree[name])

        return ()

    def bind(self, a, b, edge=None, meta_data=None):
        """Connect entity A to entity B through the given edge. The two entities
        should be key hasable.
        """
        self.set_bound_meta(a,b, meta_data)

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


Tree = CounterTree

class ChainLink(object):
    short_name = 'L'

    def __init__(self, node, x, y):
        self.node = node
        self.x = x
        self.y = y

    def get_short_name(self):
        return self.short_name or self.__class__.__name__

    def __repr__(self):
        n = self.get_short_name()
        return f'<{n}({self.x:>2},{self.y:>2}) "{self.node}">'


class EdgeLink(object):

    short_name = '_'

    def __init__(self, edge, node_a, node_b, x, y):
        self.edge = edge
        self.node_a = node_a
        self.node_b = node_b
        self.x = x
        self.y = y

    @property
    def node(self):
        return self.edge


    def get_short_name(self):
        return self.short_name or self.__class__.__name__

    def str_name(self):
        n = self.get_short_name()
        return f'{n}({self.x:>2},{self.y:>2}) {self.edge}: "{self.node_a}" "{self.node_b}"'

    def __repr__(self):
        return f'<{self.str_name()}>'

    def __str__(self):
        return self.str_name()


def add_link(r, node, x, y):
    link = ChainLink(node, x, y)
    r.append(link)
    return r


def add_edge_link(r, edge, a_node, b_node, x, y):
    link = EdgeLink(edge, a_node, b_node, x, y)
    r.append(link)
    return r


class NoEdge(Edge):

    def str_name(self):
        return f'{self.__class__.__name__}'

    def __repr__(self):
        return f'<{self.str_name()}>'


def flat_get_chains(graph, start, end, root_start_node=None, depth=-1, r=None,
    index=-1, stash=None, edge_count=-1, keep_exit_node=True, keep_noedge=None):
    """
    If None, The system checks for NoEdge and drops the edge.
    If True, enforce the edge keep, allowing a null edge within the result
    If False, do not add any edge; (edgeless)
    """
    # keep_noedge = True

    stash = stash or {}
    r = r or []

    if depth > 10:
        print(' --- Recurse protection.')
        return r

    nodelist = start.get_next()

    ignore_node = False
    if isinstance(start, ExitNode):
        if keep_exit_node is False:
            ignore_node = True

    if ignore_node is False:
        r = add_link(r, start, depth, index)

    # stash[id(start)] = depth
    for i, node_name in enumerate(nodelist):
        # r = r.copy()
        # print(' '*depth, node_name)
        next_node = nodelist[node_name]

        edges = graph.get_edges(start.name, node_name)
        print('edges:', edges)
        if len(edges) == 0:
            edges = (NoEdge(), )


        orig_r = r.copy()

        for edge_i, e in enumerate(edges):
            is_noedge = isinstance(e, NoEdge)
            has_edge = keep_noedge if keep_noedge is not None else (not is_noedge)

            if has_edge:
                r = orig_r.copy()
                edge_count += 1
                add_edge_link(r, e, start, next_node, edge_count, edge_i)

            if isinstance(next_node, ExitNode):
                if keep_exit_node is not False:
                    add_link(r, next_node, depth+1, i)
                # print('STOP', r)

                stash[id(r)] = Chain(graph, r)
                return r

            v = flat_get_chains(
                graph=graph,
                start=next_node,
                end=end,
                root_start_node=root_start_node or start,
                depth=depth+1,
                r=r,
                index=i,
                stash=stash,
                edge_count=edge_count,
                keep_exit_node=keep_exit_node,
                keep_noedge=keep_noedge,
                )

    return r


def get_chains(graph, start, end, root_start_node=None, depth=-1, r=None,
    index=-1, stash=None, edge_count=-1, keep_exit_node=True, keep_noedge=None):
    """
    If None, The system checks for NoEdge and drops the edge.
    If True, enforce the edge keep, allowing a null edge within the result
    If False, do not add any edge; (edgeless)
    """
    # keep_noedge = True

    stash = stash or {}
    r = r or []

    if depth > 10:
        print(' --- Recurse protection.')
        return r

    nodelist = start.get_next()

    ignore_node = False
    if isinstance(start, ExitNode):
        if keep_exit_node is False:
            ignore_node = True

    if ignore_node is False:
        r = add_link(r, start, depth, index)

    # stash[id(start)] = depth
    for i, node_name in enumerate(nodelist):
        # r = r.copy()
        # print(' '*depth, node_name)
        next_node = nodelist[node_name]
        chain_step(
            graph=graph,
            current_node=start,
            next_node=next_node,
            end=end,
            root_start_node=root_start_node or start,
            depth=depth+1,
            r=r,
            index=i,
            stash=stash,
            edge_count=edge_count,
            keep_exit_node=keep_exit_node,
            keep_noedge=keep_noedge,
            node_name=node_name,
        )
    return r


def chain_step(graph, current_node, next_node, **kw):
    edges = get_edges(graph, current_node.name, next_node.name)
    return chain_edges(graph, edges, current_node, next_node, **kw)


def get_edges(graph, start_name, next_name):
    edges = graph.get_edges(start_name, next_name)
    print('edges:', edges)
    if len(edges) == 0:
        edges = (NoEdge(), )
    return edges


def chain_edges(graph, edges, current_node, next_node, **kw):

    orig_r = kw.get('r').copy()

    for edge_index, edge in enumerate(edges):
        v = chain_through_edge(
                graph=graph,
                edge=edge,
                current_node=current_node,
                next_node=next_node,
                orig_r=orig_r,
                edge_index=edge_index,
                **kw
            )
    return kw.get('r')


def store_history(graph, history, stash):
    v = Chain(graph, history)
    stash[id(history)] = v
    return v


def is_exit_node(node):
    return isinstance(node, ExitNode)


def chain_through_edge(graph, edge, current_node, next_node, **kw):

    g = kw.get

    edge_count = g('edge_count')
    keep_noedge = g('keep_noedge')

    is_noedge = isinstance(edge, NoEdge)
    keep_edge = keep_noedge if keep_noedge is not None else (not is_noedge)

    if keep_edge:
        orig_r = g('orig_r')
        edge_index = g('edge_index')

        history = orig_r.copy()
        kw['edge_count'] += 1

        add_edge_link(history, edge, current_node, next_node, kw['edge_count'], edge_index)

    return continue_chain(graph, current_node, next_node, history, **kw)


def continue_chain(graph, current_node, next_node, history, **kw):
    g = kw.get
    depth = g('depth')
    stash = g('stash')
    index = g('index')
    keep_exit_node = g('keep_exit_node')

    if is_exit_node(next_node):
        if keep_exit_node is not False:
            add_link(history, next_node, depth+1, index)
        return store_history(graph, history, stash)

    return get_chains(
        graph=graph,
        start=next_node,
        end=g('end'),
        root_start_node=g('root_start_node') or current_node,
        depth=depth+1,
        r=history,
        index=index,
        stash=stash,
        edge_count=g('edge_count'),
        keep_exit_node=keep_exit_node,
        keep_noedge=g('keep_noedge'),
    )




class Chain(UserList):

    def __init__(self, graph, data):
        self.data = data
        self.graph = graph


    # def __repr__(self):
    #     return f'<Chain: {self.data}>'


class GetNextMixin(object):


    def get_node(self, node_name):
        return Node(self, node_name)

    def get_next(self, current_node=None):
        if not isinstance(current_node, Node):
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
        v = get_chains(self, start, end, stash=stash, **kw)

        # pp(new_stash)
        stash.pop('_')
        return tuple(stash.values())

    def get_edges(self, a, b, direction='forward'):
        _next = self.tree.get_edges(a,b, direction=direction)
        return _next


class Node(object):

    def __init__(self, graph, name=None):
        self.graph = graph
        self.name = name

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.name}">'

    def get_value(self):
        return self.graph.data[self.name]

    def get_next(self, direction='forward'):
        """Return a single list of next attached nodes in one direction.
        """
        next_ids = self.get_next_ids(direction)
        return NodeList(self.graph, next_ids, self.name)

    def _opposite_tree(self, direction):
        op_dir ={
            'forward': 'start_pins',
            'reverse': 'end_pins',
        }

        op_dir.pop(direction)
        op_dir = tuple(op_dir.values())[0]

        return getattr(self.graph, op_dir)

    def get_next_ids(self, direction):
        _next = self.graph.tree.get_connected(self.name, direction=direction)

        if _next is None:
            opposite_tree = self._opposite_tree(direction)
            if self.name in opposite_tree:
                return (END,)

            return ()

        return tuple(_next.keys())


class NodeList(object):

    def __init__(self, graph, names, origin=None):
        self.graph = graph
        self.origin = origin
        self.names = names

    def get_origin_node(self):
        return self.graph.get_node(self.origin)

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.names}" from "{self.origin}">'

    def keys(self):
        return self.names

    def values(self):
        return (self.graph[x] for x in self.names)

    def as_dict(self):
        g = self.graph
        return {x: self.get_node(x) for x in self.names}

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        return iter(self.as_dict())

    def __getitem__(self, key):
        return self.get_node(key)

    def get_node(self,key):
        classmap = {
            START: ExitNode,
            END: ExitNode,
            'default': Node,
        }

        # print('Get', key)

        if key in self.names:
            Class = classmap.get(key) or classmap['default']
            return Class(self.graph, key)

        if isinstance(key, int):
            found = self.names[key]
            Class = classmap.get(found) or classmap['default']
            return Class(self.graph, found)

    def get_value(self, key):
        if key in self.names:
            return self.graph[key]
        return self.graph[self.names[key]]


class ExitNode(Node):

    def get_next_ids(self, direction):

        funcs = {
            START: 'start_pins',
            END: 'end_pins',
        }

        _next = getattr(self.graph, funcs[self.name])

        opposite_tree = self._opposite_tree(direction)

        if _next is None and self.name in opposite_tree:
            return 'end'

        return tuple(_next.keys())


START = '_start_'
END = '_end_'

class Graph(UserDict, IDMethod, GetNextMixin):

    def __init__(self, initdata=None, id_method=None, depth=-1):
        super().__init__(initdata)
        self.depth = depth + 1
        self.id_method = id_method or self.id_method
        self.reset()

    def get_start_node(self):
        return ExitNode(self, START)

    def get_end_node(self):
        return ExitNode(self, END)

    def reset(self):
        tree = self.get_init_tree
        self.tree = tree()
        self.start_pins = defaultdict(int)# set()
        self.end_pins = defaultdict(int)# set()
        self.paths = None
        if self.depth < 3:
            self.paths = self.__class__(id_method=self.id_method, depth=self.depth)

    def get_init_tree(self, direction=None):
        return Tree(direction) #defaultdict(set)

    def connect(self, *nodes, edge=None):
        pairs, positions = self.linear_connect(nodes, edge=edge)
        if self.paths is not None:
            self.paths.connect(*positions)

        return positions

    def linear_connect(self, items, pinned=True, init_position=-1, edge=None):

        pairs = ()
        items = tuple(items)

        id_first, id_last = self.get_ids(items[0], items[-1])
        if pinned:
            # self.start_pins.add(items[0])
            self.start_pins[id_first] += 1
            # self.end_pins.add(items[-1])
            self.end_pins[id_last] += 1

        if init_position == -1:
            # position from pinned_node
            init_position = tuple(self.start_pins).index(id_first)

        positions = (init_position,)# {}

        for i, node in enumerate(items):
            # print(f"Inserting node #{i} '{ni}'", node, end='')
            to_node = None

            if i+1 < len(items):
                # The next node does exist, grab its name to connect _this_
                # as a forward relation.
                to_node = items[i+1]

            # next_node = self.get_entry(to_node)
            # print(' next:', next_node)
            #
            if len(items) == i+1:
                # print(' - done')
                continue

            *ids, branch_position = self.bind_pair(node, to_node, edge=edge)
            # positions[i] = branch_position
            positions += (branch_position,)
            pairs += (ids, )

        return pairs, positions

    def bind_pair(self, a, b, edge=None):
        id_a, id_b = self.get_ids(a,b)
        # record data attributes to flat _self_ dict
        self.store_items({id_a:a,id_b:b})
        # Build an a to b connection through e
        branch_position = self.bridge(id_a, id_b, edge=edge)
        return id_a, id_b, branch_position

    def add_edge(self, a,b, edge):
        id_a, id_b = self.get_ids(a,b)
        edge_positions = self.tree.add_edge(id_a, id_b, edge)
        return id_a, id_b, edge_positions

    def bridge(self, a, b, edge=None):
        # print('bridge', a, '=>', b)
        return self.tree.bind(a, b, edge=edge)

    def store_items(self, d):
        # print('store', d)
        self.update(d)





if __name__ == '__main__':
    main()
