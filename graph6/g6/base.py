# from g4.edges.live import LiveEdge


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
            _Class = self.get_edge_class()

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

    # def get_edge_class(self):
    #     return LiveEdge

    def get_node_class(self):
        return self.__class__

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



class ImproperConfiguration(Exception):
    pass


class NodesMixin(object):
    node_class = None

    def get_node_class(self):
        r = self.node_class # or self.__class__
        if r is None:
            raise ImproperConfiguration(f"Failed to yield a node_class: {self.__class__.__name__}")
        return r

    def get_parent_data(self, key=None):
        if key:
            return self.parent.datas[key]
        return self.parent.datas

    def get_connection(self):
        return self.get_parent_data('edge_connections')[self.uuid]

    def get_nodes(self, direction=None):
        di = self.direction if direction is None else direction
        LiveNodeClass = self.get_node_class()
        return tuple(LiveNodeClass(self.parent, x, di) for x in self.get_connection())
        # return tuple(LiveNode(self.parent, refs[x], di) for x in self.get_connection())

    @property
    def nodes(self):
        return self.get_nodes()
