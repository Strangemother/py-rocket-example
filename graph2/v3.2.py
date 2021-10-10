"""
A programmed node should be allowed to send an event to the target edges,
given params in the caller response.
"""

from graph import Graph, Edge, Node, NodeList


class ChoiceNode(Node):


    # def get_next(self, direction='forward'):
    def get_next(self, direction='forward', edge_filter=None):
        """Return a single list of next attached nodes in one direction.
        """
        value = self.get_value()
        _edge_filter = lambda e: e.name.lower() in value
        return super().get_next(direction, edge_filter or _edge_filter)


g = Graph(node_class=ChoiceNode)


class Poppy(Edge):
    factory=True


class SimPoppy(Edge):
    name = 'poppy'


g['a'] = ['egg', 'poppy']
g['b'] = ['poppy']
g['c'] = ['egg']
g['d'] = ['apples']

g.connect('a', 'b', edge=Poppy)
g.connect('a', 'c', edge=SimPoppy())
g.connect('a', 'd')

assert g['a'] == ['egg', 'poppy']
assert g['b'] == ['poppy']

a = g.get_node('a')
res = a.next.keys()
print(res)
assert res == ('b', 'c')

print('"a" next:', res)
