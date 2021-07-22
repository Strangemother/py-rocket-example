from pprint import pprint as pp
from itertools import chain
from collections import defaultdict


def main():
    global g
    g=alphabet()
    pp(vars(g))
    return g

def alphabet():
    g = Graph(id_method=id)
    g.connect(*'ABCD')
    g.append(*'DEFGHIJKL')

    return g


def functions():
    g = Graph(id_method=lambda f: f.__name__)
    g.connect(fa, fb, fc, fd)
    return g


def fa():
    pass

def fb(): pass
def fc(): pass
def fd(): pass


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


class GraphWalker(object):
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start_node = start_node

    def __next__(self):
        return self.step()

    def step(self):
        # change the current path step the to the next one and return the
        # node from the graph

        raise StopIteration

    def __repr__(self):
        name = self.__class__.__name__
        return f'<{name} {id(self)} {self.graph}: Start: "{self.start_node}">'


class NullNode(object):

    @property
    def __name__(self):
        return self.get_name()

    def get_name(self):
        return f'{self.__class__.__name__} "{self.value}"'

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'<{self.get_name()}>'

    def __id__(self):
        return self.value

    def __hash__(self):
        return self.value


class GraphNodes(object):

    def __init__(self, graph, items):
        self.items = items
        self.graph = graph

    def __getitem__(self, index):
        return GraphNode(self.graph, self.items[index])

    def __repr__(self):
        return self.items.__repr__()


class GraphNode(object):

    def __init__(self, graph, node):
        self.graph = graph


    def __iter__(self):
        return GraphWalker(self, self.node)

    def __next__(self):
        return self.next_nodes()

    # def next_nodes(self):
    #     return tuple(self.graph.next_nodes(self.get_value()))

    def next_nodes(self):
        return GraphNodes(self.graph, tuple(self.graph.next_nodes(self.node)))

    def get_value(self):
        return self.graph.get_value(self.node)

    def __repr__(self):
        name = self.__class__.__name__
        return f'<{name} {id(self)} {self.graph}: "{self.node}">'


class GraphStore(object):
    data = None

    def prepare_store(self):
        self.data = {}

    def store_items(self, content):
        res = {}

        for key, value in content.items():
            res[key] = self.store_item(key, value)
        return res

    def store_item(self, key, value):
        self.data[key] = value
        return key in self.data

    def get_value(self, key):
        return self.data[key]


FORWARD = 'forward'
REVERSE = 'reverse'


class Graph(IDMethod, GraphStore):

    graph_node = None

    def __init__(self, id_method=None):
        self.graph_node = GraphNode
        self.id_method = id_method or self.id_method
        self.reset()

    def reset(self):
        self.start_node = NullNode(0)
        self.end_node = NullNode(-1)

        tree = self.get_init_tree
        self.tree_forward = tree(FORWARD)
        self.tree_reverse = tree(REVERSE)
        self.prepare_store()

    def get_init_tree(self, direction=None):
        return defaultdict(set)

    def __getitem__(self, node):
        return self.graph_node(self, node)

    def connect(self, *nodes, start_node=True):
        """Given two or more nodes to connect linearly, iterate each and
        collect or generate an internal name - applied to the internal word
        dictionary. Iterate the name indices connecting N to N+1.

            append('a', 'b', 'c')
            a -> b
            b -> c
        """

        """Ensure an explicit start node. If `True` use the default start node.
        If None, no start node is applied. Anything else (such as another node)
        is applied as the first entity within the list of items to linear connect.

            connect(*'ABC', start='B')

        """
        start = self.start_node if start_node is True else None
        start_set = ()
        if start is not None:
            start_set += (start,)

        end = self.end_node

        items = chain(start_set, nodes, (end,))
        return self.linear_connect(items)

    def append(self, from_node, *nodes):
        """Append to the existing chain from the first node. This does not
        assign the START node.
        """
        items = tuple(chain((from_node,), nodes))
        return self.connect(*items, start_node=None)

    def linear_connect(self, items):

        pairs = ()
        items = tuple(items)
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

            ids = self.bind_pair(node, to_node)
            pairs += (ids, )

        return pairs

    def bind_pair(self, a, b):
        id_a, id_b = self.get_ids(a,b)
        self.tree_forward[id_a].add(id_b)
        self.tree_reverse[id_b].add(id_a)
        self.store_items({id_a:a,id_b:b})
        return id_a, id_b

    def get_ids(self, *items):
        return tuple(self.get_id(x) for x in items)

    def get_id(self, item):
        method = self.get_id_method()
        return method(item)

    def __repr__(self):
        name = self.__class__.__name__
        return f'<{name} {id(self)}>'

    def next_nodes(self, current_node=0, direction=FORWARD):
        """Return the next node withim the graph relative to the given
        (true value) node.

            >>> g.connect(*'AC')
            >>> g.connect(*'ABCD')

            >>> list(g.next_nodes())
            ['A']
            >>> list(g.next_nodes('A'))
            ['B', 'C']
            >>> list(g.next_nodes('C'))
            ['D', -1]
            >>> list(g.next_nodes('D'))
            [-1]
        """

        cid = self.get_id(current_node)
        next_ids = getattr(self, f'tree_{direction}')[cid]
        return (self.data[x] for x in next_ids)



if __name__ == '__main__':
    main()
