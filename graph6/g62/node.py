# from g4.edges.live import LiveEdge
from .enums import EMPTY


class NodeBase(object):
    """The NodeBase is a simple abstraction of helper functions to read the
    parent trees (graph `Connections`) and step to ajoining _nodes_.

    Extend the NodeBase to something more convenient, complete with the
    target Edge type:

        class Edge:
            pass

        class Node(NodeBase):
            edge_class = Edge

    Generally this class isn't exposed as the upper abstract, in favour of
    a `LiveNode`.
    """

    def __init__(self, parent, node_id, direction, tree_name='trees'):
        """A NodeBase `__init__` requires a `parent`, `node` and `direction`.

        A `parent` should the parent _graph_ - an instance of Connections.
        The `node_id` is the explicit identity of the target node.
        The `direction` denotes the key sub tree root. In general cases this
        can be `enum.FORWARD` or `1`.
        """
        self.parent = parent
        self.node_id = node_id
        self.direction = direction
        self.tree_name = tree_name

    def get_entry(self):
        """Return the _current_ tree entry using the internal `get_uuid()`.
        This will be the sub data for the node item, by default a set of
        edge ids.

            >>> self.get_entry()
            {'3_4', '3_5'}

        Synonymous to:

            self.parent.trees[direction][uuid]

        To gather a tuple of resolved edge entities, consider `self.get_edges()`
        """
        return self.get_tree()[self.get_uuid()]

    def get_edges(self, direction=None):
        """Return a tuple of Edge instances for this node.

            >>> self.get_edges()
            (
                <Edge 1 "3_4" (<Node "3" Valid>, <Node "4" Valid>)>,
            )
        """
        edge_ids = self.get_entry()
        di = direction or self.direction
        func = self.spawn_edge_instance

        res = (func(self.parent, x, di, i) for i, x in enumerate(edge_ids))

        return tuple(res)

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
        edge_or_class = self.gather_edge_class(edge_id)

        kw = {'parent': parent,
              'uuid': edge_id,
              'direction': direction,
              'index': index}

        if callable(edge_or_class):
            return edge_or_class(**kw)

        # Is a dict type or has an update function.
        if hasattr(edge_or_class, 'update'):
            edge_or_class.update(**kw)
        return edge_or_class

    def gather_edge_class(self, edge_id):
        """Return a class for the edge instance by collecting a custom edge class
        or returning the default.

        If the found class is a _factory class_, and `factory` is True, A new
        instance of the class is given, reglardless of its current instansiation

            class MyEdge(Edge):
                factory = True

            g.connect(*'AB', edge=MyEdge)

        When collecting a list of edges the `spawn_edge_instance` function
        generates new Edge (or custom edges) for each bound pair.

        If `factory` is False, or does not exist on the found edge instance or
        class, the _found_ edge is returned, this may return a runtime instance.
        """
        edge_class = self.parent.datas['edge_units'].get(edge_id, None)
        is_factory = getattr(edge_class, 'factory', False) is True

        if edge_class is None: edge_class = self.get_edge_class()

        if (not callable(edge_class)) and is_factory:
            # TODO: This may need to change as an edge_class instance may indeed
            # be callable; as such - the factory test should be more literal
            # to the runtime.
            edge_class = edge_class.__class__

        return edge_class

    # def get_edge_class(self):
    #     return LiveEdge

    def get_node_class(self):
        """Return the class used for the Node reference.
        As this is a Node base, it's assumed this unit is a _Node_ as such
        returns self.__class__.

        override this function to return a new node type from the Connections
        or edge
        """
        return self.__class__

    def get_next_nodes(self, direction=None):
        """Return a list of nodes in the forward direction across the
        edge connections. This doesn't _call_ the edge.
        """
        di = self.direction if direction is None else direction
        return tuple(x.get_nodes(di)[-1] for x in self.get_edges())

    def direction_is_valid(self):
        """Return a boolean for a test of the UUID within the directional tree
        of this node. If this node exists within the `self.direction` tree
        return True, else return False

        This differs to the alternative `is_valid`, by testing one direction.


        In a chain of `A, B, C` - node `A` direction_is_valid will be True, as
        it connects _forward_ to `B`, however `C` will return False:

            g = Connections()
            g.connect(*'ABC')
            g('A').is_valid() is True
            g('A').direction_is_valid() is True
            g('C').direction_is_valid() is False

        However the `C` node will validate in the revese direction, as an edge
        exists to `<= B`:

            g('C').direction_is_valid() is False
            g('C', direction=-1).is_valid() is True

        Node `A` would fail a reverse direction validation:

            g('A', -1).direction_is_valid() is False

        Node the `is_valid` alternative will return True in both cases

            g('A').is_valid() is True
            g('C').is_valid() is True
        """
        return self.get_uuid() in self.get_tree()

    def is_valid(self):
        """The `is_valid` returns a test for the unique id of the node within
        the parent node_references.

        Return True if this node is a valid unit, return False if the
        uuid is not within the parent.node_references.


            g = Connections()
            g.connect(*'ABC')
            g('C').direction_is_valid() is False
            g('C').is_valid() is True


        Unlike `direction_is_valid` This function does not assert if the
        self.direction (e.g. _forward_) has valid edges

        """
        return self.get_uuid() in self.get_refs()# self.parent.datas['nodes_references']

    def get_uuid(self):
        """Return the internal node id - of which is the same id used within the
        parent connections trees.

            >>> node = graph.node(3)
            >>> node.get_uuid()
            3
        """
        return self.node_id

    def get_tree(self):
        """Return the associated direction tree from the parent. Synonymous to:

            self.parent.trees[direction]
        """
        return getattr(self.parent, self.tree_name)[self.direction]

    def get_refs(self):
        """Return all the `node_references` from the parent data-sets.
        """
        return self.parent.datas['nodes_references']

    def get_reference(self, quiet=False, default=None):
        """Return the node references for this instance from the parent dataset
        using the `self.get_refs` function.
        The "node reference" is the original node data given upon instansiation,
        regardless of the reference type.

            g.connect(1,2,3)
            g(3).get_reference() == 3

        Notably the reference to the entity is dependant upon the given
        reference _type_, and how that hashes when an ID is generated.

        When implementing a _node_ the reference applied should be persistent.
        In this example the assertion yields False, as a _new_ entity for
        each call yields unique ids:

            g.connect({}, {})
            g({}).get_reference() != {}

        Although this feels inaccurate, the lib will generate a functioning
        unique edge:
            >>> g.connect({}, {})
            (<ThinEdge "41033536_43049536" ({}, {})>,)

        But the reference is lost:

            >>> g({})
            <Node "{}" Not Valid>

        However building a variable (a gc safe memory pointer) and then
        connecting objects:

            >>> v = {}, other = {}
            >>> g.connect(v, other)
            (<ThinEdge "43112320_43112320" ({}, {})>,)

        Allows correct inspection of the nodes existence because the pointer
        is still alive:

            >>> g(v)
            <Node "{}" Valid>
            >>> g(v).get_reference()
            {}

        Notably calling the `get_reference()` function on an invalid node yields
        an error:

            >>> g('bad name')
            <Node "bad name" Not Valid>

            >>> g('bad name').get_reference()
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
              File "graph6/g62/node.py", line 292, in get_reference
                raise KeyError(err_s)
            KeyError: 'Key "bad name" does not exist in parent references'

        Pass `quiet` as True for the first argument to silence the error -
        however by doing so, you may desensitize the data reference to None and
        other nully results.

            >>> g('bad name').get_reference(quiet=True)
            None
        """
        key = self.get_uuid()
        result = self.get_refs().get(key, EMPTY)
        if result != EMPTY: return result
        if quiet is True: return default

        raise KeyError(f'Key "{key}" does not exist in parent references')

    def __setattr__(self, k, v):
        """Override the default __setattr__ ensuring any changes to `self.data`
        is sent directly to the parent reference tree.

        If the given key does not equal `"data"`, super() is called for the
        default functionality.
        """
        if k != 'data':
            return super().__setattr__(k, v)

        self.get_refs()[self.get_uuid()] = v

    @property
    def data(self):
        """A convenience function to the `self.get_reference()`

            >>> Node(g, 'A').get_reference() == g.node('A').data

        Any data changes (_set_) into this object is pushed through the
        `self.set_data` function.
        """
        return self.get_reference()

    @data.setter
    def set_data(self, v):
        """Any data changes (_set_) into this object is pushed to the parent
        node reference:

            g.node('A').data['foo'] = 1

        synonymous to:

            Node(g, 'A').parent.datas['nodes_references'][uuid]['foo'] = 1
        """
        self.get_refs()[self.get_uuid()] = v

    @property
    def edges(self):
        """A convenience property method for the `self.get_edges()` function:

            >>> g.node('A').edges == Node(g, 'A').get_edges()
            (<Edge 1 "A_B" (<Node "A" Valid>, <Node "B" Valid>)>,)
        """
        return self.get_edges()

    @property
    def next_nodes(self):
        """A convenience property method for the `self.get_edges()` function.
        returns a tuple of Node types leading from any edges.

            >>> g.node('A').next_nodes == Node(g, 'A').get_next_nodes()
            (<Node "B" Valid>,)
        """
        return self.get_next_nodes()


class ImproperConfiguration(Exception):
    """An exception used if the node class of the NodeMixin is not configured
    correctly. To resolve this error, provide a `node_class`:

        class Unit(NodeMixin):
            node_class = Node

            def get_node_class(self):
                return self.node_class
    """
    pass


class NodesMixin(object):
    """ The "NodesMixin" provide a few convience function to an entity
    expecting to work with the graph connections. This includes the existing
    `LiveEdge` and `ExitNode` classes.

        class CustomNode(LiveNode, NodesMixin):

            def get_edges(self):
                'Utilise the NodeMixin get_nodes method'
                return tuple(x.get_edges() for x in self.get_nodes())

    """
    node_class = None

    def get_node_class(self):
        """Return the internal `self.node_class`. If the value is None raise
        an ImproperConfiguration exception.

            >>> g.get_node_class()
            Node
        """
        r = self.node_class  # or self.__class__
        if r is not None: return r

        err_s = f"Failed to yield a node_class: {self.__class__.__name__}"
        raise ImproperConfiguration(err_s)

    def get_parent_data(self, key=None):
        """Return the parent _general_ data content

        Keyword Arguments:
            key {str} -- Optionally provide a sub key of the parent data
                         (default: {None})

        Returns:
            Dict|Anything -- Return the value found at the parent data point. By
                             default this is a dict.
        """
        d = self.parent.datas
        return d if key is None else d[key]

    def get_connection(self):
        """Return the edge connection for the `self.uuid` entry.
        By default this is the edge IDS for each end of the connection:

            >>> a=g('A')
            >>> a.edges
            >>> a.edges[0].get_connection()
            ('A', 'B')

        """
        return self.get_parent_data('edge_connections')[self.uuid]

    def get_nodes(self, direction=None):
        """Return a tuple of resolved "Node" types for every connection of this
        node (uuid).

            >>> a = g('A')
            >>> a.edges[0].get_nodes()
            (<Node "A" Valid>, <Node "B" Valid>)

        If the given `direction` is `None`, use the internal `self.direction`
        """
        di = self.direction if direction is None else direction
        NodeClass = self.get_node_class()
        res = (NodeClass(self.parent, x, di) for x in self.get_connection())
        return tuple(res)

    @property
    def nodes(self):
        """A convenience property method for `self.get_nodes()`.
        Return a tupe of Node types.
        """
        return self.get_nodes()
