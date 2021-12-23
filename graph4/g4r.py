import sys
from collections import defaultdict
from itertools import tee
from pprint import pprint as pp

from g4.pins import Pins
from g4.tree import TreeStore
# from g4.edge import Edges
from g4.nodes.node import ExitNode
from g4.enums import *
from g4.connect import Connections


class CustomEdge(object):
    factory=False

    def __init__(self, parent, uuid, direction):
        print('New Custom Edge')
        self.parent = parent
        self.uuid = uuid
        self.direction = direction

    def update(self, parent, uuid, direction):
        print(f'{self.__class__.__name__} update')


def main():
    example()


def example():
    es = Connections()
    es.connect(*'ABCDE')
    es.connect(*'CAB')
    v=es.connect(*'HORSE')
    g=es
    # pp(vars(es))
    print(v)

    # Getting pinned first nodes.
    # g.node(uuid='start', tree_name='pins').get_entry()
    # Or a key node.
    c=g.node('A').get_edges()
    e=ExitNode(g, 'start', 1)
    print(c)

    a={'foo': 2}
    b={'red': 3}
    g.connect(a,b, data={'egg': 'butter'})
    assert g.node(a).edges[0].data['egg'] == 'butter'

    ab_rev = g('B', direction=-1).edges[0] ==  g('A').edges[0]
    assert ab_rev == True

    def mycaller(*a, **kw):
        print('mycaller', a, kw)
        return "sausages"

    es.connect(*'AP', edge=mycaller)

    es.connect(*'QS', edge=CustomEdge(es, 1, 1))
    es.connect(*'RS', edge=CustomEdge)#(es, 1, 1))


    es.connect(*'DT', edge={})


if __name__ == '__main__':
    main()
