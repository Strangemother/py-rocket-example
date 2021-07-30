
class Edge(object):

    @property
    def name(self):
        return self.__class__.__name__

    def get_value(self):
        return self.caller

    def caller(self, *a, **kw):
        print(f'{self.name} caller')


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

