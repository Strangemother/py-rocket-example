START = '_start_'
END = '_end_'



class Node(object):

    def __init__(self, graph, name=None):
        self.graph = graph
        self.name = name

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.name}">'

    def get_value(self):

        try:
            gid = self.get_id()
            return self.graph.data[gid]
        except KeyError as e:
            if self.name in [START, END]:
                return ExitNode(self.graph, self.name).get_value()
            raise e

    def get_id(self):
        return self.name

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

    def get_next(self, direction='forward'):
        """Return a single list of next attached nodes in one direction.
        """
        next_ids = self.get_next_ids(direction)
        return NodeList(self.graph, next_ids, self.name)

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

    def __init__(self, graph, names, origin=None):
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

    def get_value(self):
        return self.name
