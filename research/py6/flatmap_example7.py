from collections import defaultdict
from importlib import reload
from pprint import pprint as pp
from flatmap import FlatGraph


def my_func(*a, **kw):
    print('my_func')


class GraphNode(object):
    """An inline executable to handle fancy chain tooling,
    Append against a chosen UUID or apply to the graph as a callable
    """
    def on_hit(self, *a, **kw):
        """A hook method executed automatically when this graphnode is _hit_ in
        the event chain, e.g. every "path generate" of a walk.

        By default this does nothing.
        """
        print('GraphNode _hit_ during chaining.', a, kw)


def main():
    g = FlatGraph()
    g.connect('first', 'second')
    g.connect('second', my_func)
    g.connect(my_func, 'third')
    g.connect('third', 'forth')
    g.connect('forth', 'fifth')

    g.bind('forth', GraphNode())

    #                                                     GraphNode()
    #                                                         |
    # chain applies - first -> second -> my_func -> third -> forth -> fifth

    pp(g.flat_chains(g.chains('second', with_parent=True, reverse=True)))
    return g


if __name__ == '__main__':
    g = main()

