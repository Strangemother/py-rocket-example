# from g4.live.node import LiveNode


class NodesMixin(object):

    def get_parent_data(self, key=None):
        if key:
            return self.parent.datas[key]
        return self.parent.datas

    def get_connection(self):
        return self.get_parent_data('edge_connections')[self.uuid]

    def get_nodes(self, direction=None):
        di = self.direction if direction is None else direction
        LiveNodeClass = self.get_edge_class()
        return tuple(LiveNodeClass(self.parent, x, di) for x in self.get_connection())
        # return tuple(LiveNode(self.parent, refs[x], di) for x in self.get_connection())

    @property
    def nodes(self):
        return self.get_nodes()
