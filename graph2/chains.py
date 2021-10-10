from collections import UserDict
from pprint import pprint as pp
from itertools import chain
from collections import Counter
from collections import defaultdict

from collections import UserList
import random

from edges import *
from nodes import *



class Chain(UserList):

    def __init__(self, graph, data):
        self.data = data
        self.graph = graph

    def get_nodes(self):
        for item in self.data:
            yield item.node

    @property
    def nodes(self):
        return tuple(x for x in self.get_nodes())

    @property
    def path(self):
        return tuple(x.y for x in self)

    def values(self):
        res= ()
        for item in self.data:
            node = item.node
            try:
                value = node.get_value()
            except KeyError:
                # value = node.name
                value = f"{node.name}?get_value"
            except AttributeError:
                value = f"{node.name}?get_value"
            res += (value, )
        return res
    # def __repr__(self):
    #     return f'<Chain: {self.data}>'


class ChainLink(object):
    short_name = 'L'

    def __init__(self, node, x, y):
        self.node = node
        self.x = x
        self.y = y

    def get_short_name(self):
        return self.short_name or self.__class__.__name__

    def __repr__(self):
        n = self.get_short_name()
        return f'<{n}({self.x:>2},{self.y:>2}) "{self.node}">'


class EdgeLink(object):

    short_name = '_'

    def __init__(self, edge, node_a, node_b, x, y):
        self.edge = edge
        self.node_a = node_a
        self.node_b = node_b
        self.x = x
        self.y = y

    @property
    def node(self):
        return self.edge

    def get_short_name(self):
        return self.short_name or self.__class__.__name__

    def str_name(self):
        n = self.get_short_name()
        return f'{n}({self.x:>2},{self.y:>2}) {self.edge}: "{self.node_a}" "{self.node_b}"'

    def __repr__(self):
        return f'<{self.str_name()}>'

    def __str__(self):
        return self.str_name()


def add_link(r, node, x, y):
    link = ChainLink(node, x, y)
    try:
        r.append(link)
    except AttributeError:
        return [link]
    return r


def add_edge_link(r, edge, a_node, b_node, x, y):
    link = EdgeLink(edge, a_node, b_node, x, y)
    r.append(link)
    return r


def get_chains(graph, start, end, root_start_node=None, depth=-1, history=None,
    index=-1, stash=None, edge_count=-1, keep_exit_node=True,
    keep_noedge=None):
    """
    If None, The system checks for NoEdge and drops the edge.
    If True, enforce the edge keep, allowing a null edge within the result
    If False, do not add any edge; (edgeless)
    """
    # keep_noedge = True

    stash = stash or {}
    history = history or []

    if depth > 10:
        print(' --- Recurse protection.')
        return history

    nodelist = start.get_next()

    ignore_node = False
    if isinstance(start, ExitNode):
        if keep_exit_node is False:
            ignore_node = True

    if ignore_node is False:
        history = add_link(history, start, depth, index)

    # stash[id(start)] = depth
    for i, node_name in enumerate(nodelist):
        # r = r.copy()
        # print(' '*depth, node_name)
        next_node = nodelist[node_name]
        chain_step(
            graph=graph,
            current_node=start,
            next_node=next_node,
            end=end,
            root_start_node=root_start_node or start,
            depth=depth+1,
            history=history,
            index=i,
            stash=stash,
            edge_count=edge_count,
            keep_exit_node=keep_exit_node,
            keep_noedge=keep_noedge,
            node_name=node_name,
        )
    return history


def chain_step(graph, current_node, next_node, **kw):
    edges = get_edges(graph, current_node.name, next_node.name)
    return chain_edges(graph, edges, current_node, next_node, **kw)


def get_edges(graph, start_name, next_name):
    edges = graph.get_edges(start_name, next_name)
    print('edges:', edges)
    if len(edges) == 0:
        edges = (NoEdge(start_name, next_name), )
    return edges


def chain_edges(graph, edges, current_node, next_node, **kw):

    history = None
    if 'history' in kw:
        history = kw.pop('history').copy()

    for edge_index, edge in enumerate(edges):
        v = chain_through_edge(
                graph=graph,
                edge=edge,
                current_node=current_node,
                next_node=next_node,
                history=history,
                edge_index=edge_index,
                **kw
            )
    return kw.get('history')


def store_history(graph, history, stash):
    v = Chain(graph, history)
    stash[id(history)] = v
    return v


def is_exit_node(node):
    return isinstance(node, ExitNode)


def chain_through_edge(graph, edge, current_node, next_node, **kw):

    g = kw.get

    edge_count = g('edge_count')
    keep_noedge = g('keep_noedge')
    history = g('history')

    is_noedge = isinstance(edge, NoEdge)
    keep_edge = keep_noedge if keep_noedge is not None else (not is_noedge)

    try:
        kw.pop('history')
    except KeyError:
        pass

    if keep_edge:
        #history = g('history')
        edge_index = g('edge_index')

        history = history.copy()
        kw['edge_count'] += 1

        add_edge_link(history, edge, current_node, next_node, kw['edge_count'], edge_index)

    return continue_chain(graph, current_node, next_node, history, **kw)


def continue_chain(graph, current_node, next_node, history, **kw):
    g = kw.get
    depth = g('depth')
    stash = g('stash')
    index = g('index')
    keep_exit_node = g('keep_exit_node')

    if is_exit_node(next_node):
        if keep_exit_node is not False:
            history = add_link(history, next_node, depth+1, index)
        return store_history(graph, history, stash)

    return get_chains(
        graph=graph,
        start=next_node,
        end=g('end'),
        root_start_node=g('root_start_node') or current_node,
        depth=depth+1,
        history=history,
        index=index,
        stash=stash,
        edge_count=g('edge_count'),
        keep_exit_node=keep_exit_node,
        keep_noedge=g('keep_noedge'),
    )


