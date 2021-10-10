
class Edge(object):

    name = None

    def __init__(self, start_node=None, end_node=None):
        self.start_node = start_node
        self.end_node = end_node
        self.name = self.name or self.__class__.__name__
        print('Name', self.name)
        self.render = self.clone_render

    @property
    def node(self):
        return self.end_node

    def clone(self):
        r = self.__class__(self.start_node, self.end_node)
        r.__dict__ = self.__dict__.copy()
        return r

    @classmethod
    def render(cls, name_a, name_b):
        if (getattr(cls, 'factory', None) or False) is True:
            return cls(name_a, name_b)

    def clone_render(self, name_a, name_b):
        v = self.clone()
        v.start_node = name_a
        v.end_node = name_b
        return v

    # @property
    # def name(self):
    #     return self._name or self.__class__.__name__

    def get_value(self):
        return self.caller

    def caller(self, *a, **kw):
        print(f'{self.name} caller')

    def on_event(self, event, **kw):
        return self.end_node


class NoEdge(Edge):

    def str_name(self):
        return f'{self.__class__.__name__}'

    def __repr__(self):
        return f'<{self.str_name()}>'


class BlankEdge(Edge):
    def get_value(self):
        return self.caller

    def caller(self, *a, **kw):
        print('BlankEdge caller')

