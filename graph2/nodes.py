import errors

START = '_start_'
END = '_end_'

class NodeBase(object):
    # graph = None
    name = None


    def get_id(self):
        return self.name

    def get_value(self):

        gid = self.get_id()
        g = self.get_graph()

        try:
            return g.data[gid]
        except KeyError as e:
            if self.name in [START, END]:
                return ExitNode(g, self.name).get_value()
            print(f'Unknown node {gid}')
        except AttributeError as attr_error:
            raise errors.NoGraph(self) from attr_error

    def get_graph(self):
        try:
            return self.graph
        except AttributeError as e:
            raise errors.NoGraph(self) from e

    def __lt__(self, other):
        return self.get_value() < other.get_value()

    def __gt__(self, other):
        return self.get_value() > other.get_value()

    def __eq__(self, other):
        return self.get_value() == other.get_value()

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.name}">'


class Node(NodeBase):

    def __init__(self, graph, name=None):

        self.graph = graph
        if isinstance(graph, self.__class__):
            self.__dict__.update(graph.__dict__)

        if name is not None:
            self.name = name

    def get_meta(self, b=None, direction='forward'):
        """
            >>> g.get_node("0.40").meta['pop'] = 'dave'
            >>> g.get_node("0.40").get_meta()
            {'pop': 'dave'}

            >>> g.get_node("0.40").get_meta('0.91')
            {'foo': 'bar'}

        Note the reverse is not the same meta data.

            # Is not the same, as forward, or 0.40 => 0.91
            g.get_node("0.40").get_meta('0.91', direction='reverse')
            {}

            # Is the same
            g.get_node("0.40").get_meta('0.91') == g.tree.reverse['0.91']['0.40']

        When applying to the tree, meta data is bound to the node, unless the
        _other_ is specified:

            >>> g.get_node("0.40").get_next(direction='reverse')[1].meta['horse'] = 'hands'
            >>> g.get_node("0.91").get_meta()
            {'horse': 'hands'}

        And that data does not exist within the directional meta:

            >>> g.get_node("0.91").get_meta('0.40')
            {}
            >>> g.get_node("0.91").get_meta('0.40', direction='reverse')
            {'foo': 'bar'}

            g.get_node("0.40").get_meta('0.91') == g.tree.reverse['0.91']['0.40']
            g.get_node("0.40").get_meta() == g.get_node("0.40").meta

        The base chainmap when empty:
            >>> g.get_node("0.40").get_meta()
            ChainMap({})

        The forward direction has unique content:

            >>> g.get_node("0.40").get_meta('0.91')
            ChainMap({}, {'foo': 'bar'})

        Add new meta to the base node and refetch the meta:

            >>> g.get_node("0.40").meta['horse'] = 'hands'
            >>> g.get_node("0.40").get_meta('0.91')
            ChainMap({'horse': 'hands'}, {'foo': 'bar'})

        Set some meta between two nodes in the forward direction:
            >>> g.tree.set_bound_meta('0.40', '0.91', {'spoon': 'dish'})

        Refetch the chainmap:

            >>> g.get_node("0.40").get_meta('0.91')
            ChainMap({'horse': 'hands'}, {'foo': 'bar', 'spoon': 'dish'}

            g.tree.forward['0.40' ]
            defaultdict(<class 'dict'>,
            {'0.91': {'foo': 'bar', 'spoon': 'dish', 'house': 'dish'},
            '_only_': {'horse': 'hands'}})
            >>> g.tree.reverse['0.40']
            defaultdict(<class 'dict'>, {'_start_': {}})
            >>> g.tree.reverse['0.91']
            defaultdict(<class 'dict'>,
            {'0.40': {'foo': 'bar', 'spoon': 'dish', 'house': 'dish'},
             '0.39': {'foo': 'bar'},
             '0.60': {'foo': 'bar'},
             '0.61': {'foo': 'bar'}})
        """
        return self.graph.tree.get_meta_chain(self.name, b=b, direction=direction)

    def get_next(self, direction='forward', edge_filter=None):
        """Choose the next nodes, given the edge matches a name within the
        value data
        """
        ids = None
        if edge_filter:
            ids = self.get_next_ids_through_filter(edge_filter, direction)

        return self.as_nodelist(ids or self.get_next_ids(direction))

    def as_nodelist(self, ids):
        return NodeList(self.graph, ids, self.name)
        # fids = filter(None, ids)
        # print(ids, fids)

    def get_next_ids_through_filter(self, edge_filter, direction='forward'):
        e_f = edge_filter
        ids = tuple(x.end_node for x in self.get_edges(direction) if e_f(x))
        return ids

    def get_edges(self, direction='forward'):
        _next = self.get_next_ids(direction)
        res = ()
        n = self.name
        for nid in _next:
            edges = self.graph.tree.get_edges(n, nid, direction)
            res += edges
        return res

    def get_next_flat(self):
        return self.get_next().nodes()

    @property
    def next(self):
        return self.get_next()

    @property
    def meta(self):
        return self.get_meta()

    def is_valid(self):
        try:
            self.get_value()
            return True
        except KeyError:
            return False

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

    def __init__(self, graph=None, names=None, origin=None):
        self.graph = graph
        self.origin = origin
        self.names = names

    def get_origin_node(self):
        return self.graph.get_node(self.origin)

    def __repr__(self):
        cn = self.__class__.__name__
        ns = self.names
        return f'<{cn} from "{self.origin}"({len(ns)}) "{ns}">'

    def keys(self):
        return self.names

    def values(self):
        return tuple(self.graph[x] for x in self.names)

    def as_dict(self):
        g = self.graph
        return {x: self.get_node(x) for x in self.names}

    def items(self):
        return self.as_dict().items()

    def nodes(self):
        return tuple(self.as_dict().values())

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        return iter(self.as_dict())

    def __getitem__(self, key):
        return self.get_node(key)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            self.graph = self.graph or other.graph
            self.origin = self.origin or other.origin

        if self.names is None:
            self.names = ()
        if hasattr(other, '__iter__'):
            self.names += other.names
        return self

    def get_node(self,key):
        classmap = {
            START: ExitNode,
            END: ExitNode,
            'default': Node,
        }

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

    def get_next(self):
        def r(x):
            if hasattr(x, 'next'):
                return x.next
            return x

        return itertools.chain((r(x) for x in self.nodes()))

    def get_next_flat(self):
        """
        >>> g.get_node('A').get_next().get_next_flat()
        (<Node "C">, <Node "A">, <Node "A">, <Node "P">, <Node "L">)


        >>> g.get_node('A').get_next()
        <NodeList from "A"(3) "('B', 'N', 'P')">

        >>> g.get_node('A').get_next()[0].get_next()
        <NodeList from "B"(2) "('C', 'A')">

        >>> g.get_node('A').get_next()[1].get_next()
        <NodeList from "N"(1) "('A',)">

        >>> g.get_node('A').get_next()[2].get_next()
        <NodeList from "P"(2) "('P', 'L')">
        """
        r = ()
        for nl in self.get_next():
            r += tuple(nl.nodes())
        return r


import itertools


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

    def get_value(self):
        return self.name
