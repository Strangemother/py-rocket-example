"""
A programmed node should be allowed to send an event to the target edges,
given params in the caller response.
"""

from graph import Graph, Edge, Node, NodeList
import operator
import errors

def main():
    global g

    g = Graph()#node_class=OperatorNode)

    # Submit unbound nodes, to unpack into a node and the data value.
    a2 = Add(op_value=2, value=1)
    mp5 = Mul(op_value=.5, value=2)
    a1 = Add(op_value=1, value=2)

    g.connect(a2, mp5, a1)

    assert g.get_node('add_2') == a2
    assert g.get_node('add_1') == a1
    assert g.get_node('mul_0.5') == mp5
    # assert  g['add_2'] < g['mul_0.5']

class OperatorNode(Node):

    def __init__(self, graph=None, name=None, op_value=None, value=1):
        self.op_value = op_value
        self.graph = graph
        self.value = value
        self.name = name or self.dynamic_name()

    def dynamic_name(self):
        n = self.op.__name__.lower()
        return f"{n}_{self.op_value}"

    def get_value(self):
        try:
            return super().get_value()
        except errors.NoGraph as e:
            # print('No graph')
            return self.value

    def compute(self, value):
        return self.op(value, self.op_value)

class Add(OperatorNode):
    op = operator.add

class Mul(OperatorNode):
    op = operator.mul




if __name__ == '__main__':
    main()
