from collections import UserDict
from pprint import pprint as pp
from itertools import chain
from collections import Counter
from collections import defaultdict


def main():
    global g
    g=functions()
    # g=alphabet()
    pp(vars(g))
    pp(vars(g.tree))
    return g

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
    res = g.call_chain(include_edges=True)
    print('call_chain result', res)
    return g


def fa(v):
    return v + 1


def fb(v):
    return v + 2


def fc(v):
    return v + 3


def fd(v):
    return v + 4


class CallableMixin(object):

    def call_chain(self, include_edges=True):
        """Return a tuple of tuples. Each list within as a callchain from start
        to end. Each row is a stepping through edge connections
        """
        start = self.get_start_node()
        for item in iter(start):
            print("  call_chain: ", item)
        return (
            )


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

    def bind(self, a, b, edge=None, meta_data=None):
        """Connect entity A to entity B through the given edge. The two entities
        should be key hasable.
        """
        self.set_bound_meta(a,b, meta_data)

        if edge is not None:
            self.set_edges(a,b, edge)

        return tuple(self.forward[a]).index(b)

    def set_edges(self, a,b, edge):
        self.forward_edges["{a}{b}"] = edge
        self.reverse_edges["{b}{a}"] = edge

    def set_bound_meta(self, a,b, meta_data=None):
        self.forward[a][b] += (meta_data or 1)
        self.reverse[b][a] += (meta_data or 1)



class PlainTree(object):
    def __init__(self, direction=None):
        self.forward = defaultdict(dict)
        self.reverse = defaultdict(dict)
        self.forward_edges = defaultdict(set)
        self.reverse_edges = defaultdict(set)

    def bind(self, a, b, edge=None):
        """Connect entity A to entity B through the given edge. The two entities
        should be key hasable.
        """
        self.forward[a][b] = 1
        self.reverse[b][a] = 1

        if edge is not None:
            self.forward_edges["{a}{b}"] = edge
            self.reverse_edges["{b}{a}"] = edge

        return tuple(self.forward[a]).index(b)


Tree = CounterTree


class GraphWalker(object):
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start_node = start_node
        self.current_node = None

    def __iter__(self):
        return self

    def __next__(self):
        return self.step()

    def step(self):
        # change the current path step the to the next one and return the
        # node from the graph
        print(f'Perform GraphWalker step - startnode: "{self.start_node}"')
        if self.current_node is None:
            return NodeList(self.start_node.next_nodes())
        raise StopIteration

    def __repr__(self):
        name = self.__class__.__name__
        return f'<{name} {id(self)} {self.graph}: Start: "{self.start_node}">'


class NodeList(object):

    def __init__(self, nodes):
        self._nodes = nodes


class GraphNode(object):

    def __init__(self, graph, node=None):
        self._graph = graph
        self.node = node

    def next_nodes(self):
        if self.node is None:
            return self._graph.start_pins
        import pdb; pdb.set_trace()  # breakpoint d9b57306 //

    def __iter__(self):
        return GraphWalker(self._graph, self.node or self)


class Graph(UserDict, IDMethod, CallableMixin):

    def __init__(self, initdata=None, id_method=None, depth=-1):
        super().__init__(initdata)
        self.depth = depth + 1
        self.id_method = id_method or self.id_method
        self.reset()

    def __iter__(self):
        return GraphWalker(self, self.get_start_node())

    def __next__(self):
        gw = GraphWalker(self, self.get_start_node())
        return next(gw)

    def __getitem__(self, x):
        """Return the literal entity by the hash key.

            def fb(v): return v + 1

            g = Graph(id_method f: f.__name__)
            g.connect(fb)

            g['fb']
            <function fb at 0x0000000002A85158>
        """

        # return the attribute at the position in the tree.
        return self.data[x]
        # return self.data[self.get_id(x)]

    def get_start_node(self):
        return GraphNode(self)

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

    def connect(self, *nodes):
        pairs, positions = self.linear_connect(nodes)
        if self.paths is not None:
            self.paths.connect(*positions)

        return positions

    def linear_connect(self, items, pinned=True, init_position=-1):

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

            *ids, branch_position = self.bind_pair(node, to_node)
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

    def bridge(self, a, b, edge=None):
        # print('bridge', a, '=>', b)
        return self.tree.bind(a, b, edge=edge)

    def store_items(self, d):
        # print('store', d)
        self.update(d)





if __name__ == '__main__':
    main()
