# from collections import UserDict
# from pprint import pprint as pp
# from itertools import chain
# from collections import Counter
# from collections import defaultdict

# from collections import UserList
# import random

# from nodes import *
# from edges import *
# import chains
from pprint import pprint as pp
from itertools import repeat, accumulate
from itertools import tee

import string
import pathlib
import json
import random

import graph
import walker
from edges import Edge, BlankEdge
from render import *
import nodes




def main():
    global g
    global v

    func = body# alphabet#functions

    # g = output_run(alphabet, 'g')
    g = output_run(func, exit_nodes=True, split_ends=True)
    v= emit_event(g)
    pp(v)


def body():
    """

         w=walker.bar_walk(g.get_node('head'))

        >>> w=walker.bar_walk(g.get_node('head'))
        >>> w
        <generator object bar_walk at 0x000000000065DB88>
        >>> next(w)
        (<Node "neck">, <Node "face">, <Node "ears">, <Node "hair">)
        >>> next(w)
        (<Node "shoulders">, <Node "eyes">, <Node "nose">, <Node "mouth">)
        >>> next(w)
        (<Node "torso">, <Node "nostrils">, <Node "lips">)
        >>> next(w)
        (<Node "legs">, <Node "arms">, <Node "holes">)
        >>> next(w)
        (<Node "feet">, <Node "hands">)
        >>> next(w)
        (<Node "toes">, <Node "fingers">, <Node "thumbs">)
        >>> next(w)
        (<Node "fingernails">, <Node "thumbnails">)
        >>> next(w)
        ()

        v=tuple(w)
        pp(v)
        ((<Node "neck">, <Node "face">, <Node "ears">, <Node "hair">),
         (<Node "shoulders">, <Node "eyes">, <Node "nose">, <Node "mouth">),
         (<Node "torso">, <Node "nostrils">, <Node "lips">),
         (<Node "legs">, <Node "arms">, <Node "holes">),
         (<Node "feet">, <Node "hands">),
         (<Node "toes">, <Node "fingers">, <Node "thumbs">),
         (<Node "fingernails">, <Node "thumbnails">),
         ())
    """
    g = graph.Graph()
    g.connect(
    'head',
    'neck',
    'shoulders',
    'torso',
    'legs',
    'feet',
    'toes',
    )

    g.connect('head', 'face', 'eyes')
    g.connect('head', 'ears')
    g.connect('head', 'hair')

    g.connect('face', 'nose')
    g.connect('nose', 'nostrils', 'holes')
    g.connect('face', 'mouth', 'lips')

    g.connect('torso', 'arms', 'hands', 'fingers', 'fingernails')
    g.connect('hands', 'thumbs', 'thumbnails')

    return g
    # v = get_path(g)

def emit_event(g):
    return walker.walk(g.get_node('A'))

def get_path(g):
    p = (4, 1, 1, 0, 1, 0)
    p2= (0, 2, 0, 1, 0, 1)
    p3 = (1, 0, 0, 0, 0, 0, 0, 0, 0)
    # g.get_path(p)
    v =g.get_parapaths( (p, p2, p3))

    return v

def chain_main():
    global g
    global c
    g = functions()
    # g = alphabet()
    # g = pop_song()

    pp(vars(g))
    pp(vars(g.tree))

    c = g.get_chain(keep_noedge=True)
    pp(c)
    # print(c)
    print(len(c))

    t = (
        "_start_, NoEdge, fa, Edge, fb, Edge, fc, Edge, fd, NoEdge, _end_",
        "_start_, NoEdge, fa, NoEdge, fab, NoEdge, fac, NoEdge, fad, NoEdge, _end_",
        # "_start_, NoEdge, b_a, Edge, b_b, Edge, b_c, Edge, b_d, NoEdge, _end_",
        "_start_, NoEdge, b_a, BlankEdge, b_b, BlankEdge, b_c, BlankEdge, b_d, NoEdge, _end_",
        )

    # assert_paths(c,t)
    # to_sigmajs_json(g, './view/g.json')
    to_visjs_json(g, './view/g_vis.json')
    to_visjs_json(g.paths, './view/g_tree_vis.json')


def output_run(func, filename=None, **kw):
    g = func()
    filename = filename or func.__name__

    # to_sigmajs_json(g, f'./view/{filename}.json')
    to_visjs_json(g, f'./view/{filename}_vis.json', **kw)
    # to_visjs_json(g.paths, f'./view/g_{n}_paths_vis.json', split_ends=False, exit_nodes=False)
    # to_visjs_json(g.paths.paths, f'./view/g_{n}_paths_paths_vis.json', split_ends=True, exit_nodes=True)

    return g



def assert_paths(c,t):
    r = ()
    for row in c:
        names = ()
        for item in row:
            names += (item.node.name,)
        v = ', '.join(names)
        r += (v, )


    try:
        assert t == r
        print('Match success.')
        return
    except AssertionError as e:
        print('Error', e)

    for x,y in (tuple(zip(t,r))):
        print(x)
        print(y)
        print('')

    # pp(r)


def poppins():
    word = "supercalifragilisticexpialidocious"
    g = Graph(id_method=id)
    v= g.connect(*word)
    print(v)
    s = 'Um diddle, diddle diddle, um diddle ay'
    v= g.connect(*s)
    v= g.connect(*s)
    v= g.connect(*s)
    v= g.connect(*s)
    return g


def alphabet(print_table=True):
    """

    Each graph connection builds a bridged path, for chained execution
    across the graph through the given nodes. Notice the path index is
    deterministic for early and late positions, (ABCD and APPLES),
    and intial-referencing, for example "P" to "P" is of index 0, noting the
    first graphed for the Node "P" was "P".

        ABCD      (0, 0, 0, 0)
        DEFGHIJKL (1, 0, 0, 0, 0, 0, 0, 0, 0)
        DOGGY     (1, 1, 0, 1, 2)
        HORSE     (2, 1, 1, 0, 0)
        MOUSE     (3, 0, 2, 0, 0)
        BANANA    (4, 1, 1, 0, 1, 0)
        APPLES    (0, 2, 0, 1, 0, 1)

    To read a path, iterate each index relative to the graph position of the
    previous node:

        BANANA    (4, 1, 1, 0, 1, 0)

    The first value is the start _pin_:

        tuple(g.start_pins)[4]
        "B"

    from B we can walk forward with the path `[1, 1, 0, 1, 0]`. Each node
    resolves to an ordered list of _next_ keys (no edges involved)

        >>> tuple(g.tree.forward['B'])
        ('C', 'A')

    Full path:

        v=('B',)
        p = (1,1,0,1,0)

        for i in p:
           n = tuple(g.tree.forward[v[-1]])[i]
           v += (n,)

        print(v)
        ('B', 'A', 'N', 'A', 'N', 'A')

    """
    g = graph.Graph(id_method=None)#id)

    def _con(items):
        v = g.connect(*items)
        if print_table:
            print(f"{items:<10}", v)

    rows = (
        ('ABCD'),
        ('DEFGHIJKL'),
        ('DOGGY'),
        ('HORSE'),
        ('MOUSE'),
        ('BANANA'),
        ('APPLES'),
    )

    for row in rows:
        _con(row)

    # print('DEFGHIJKL', v)
    # print('DOGGY    ', v)
    # print('HORSE    ', v)
    # print('MOUSE    ', v)
    # print('BANANA   ', v)
    # print('APPLES   ', v)
    return g


def pop_song():
    lines = (
        "I am the very model of a modern Major-General,",
        "I've information vegetable, animal, and mineral,",
        "I know the kings of England, and I quote the fights historical",
        "From Marathon to Waterloo, in order categorical;",
        "I'm very well acquainted, too, with matters mathematical,",
        "I understand equations, both the simple and quadratical,",
        "About binomial theorem I'm teeming with a lot o' news,",
        "With many cheerful facts about the square of the hypotenuse.",
        "I'm very good at integral and differential calculus;",
        "I know the scientific names of beings animalculous:",
        "In short, in matters vegetable, animal, and mineral,",
        "I am the very model of a modern Major-General.",
        "I know our mythic history, King Arthur's and Sir Caradoc's;",
        "I answer hard acrostics, I've a pretty taste for paradox,",
        "I quote in elegiacs all the crimes of Heliogabalus,",
        "In conics I can floor peculiarities parabolous;",
        "I can tell undoubted Raphaels from Gerard Dows and Zoffanies,",
        "I know the croaking from The Frogs of Aristophanes!",
        "Then I can hum a fugue of which I've heard the music's din afore,",
        "And whistle all the airs from that infernal nonsense Pinafore.",
        "Then I can write a washing bill in Babylonic cuneiform,",
        "And tell you ev'ry detail of Caractacus's uniform:",
        "In short, in matters vegetable, animal, and mineral,",
        "I am the very model of a modern Major-General.",
        "In fact, when I know what is meant by \"mamelon\" and \"ravelin\",",
        "When I can tell at sight a Mauser rifle from a Javelin,",
        "When such affairs as sorties and surprises I'm more wary at,",
        "And when I know precisely what is meant by \"commissariat\"",
        "When I have learnt what progress has been made in modern gunnery,",
        "When I know more of tactics than a novice in a nunnery",
        "In short, when I've a smattering of elemental strategy",
        "You'll say a better Major-General has never sat a gee.",
        "For my military knowledge, though I'm plucky and adventury,",
        "Has only been brought down to the beginning of the century;",
        "But still, in matters vegetable, animal, and mineral,",
        "I am the very model of a modern Major-General.",
    )

    g = graph.Graph(id_method=None)#id)

    for i, line in enumerate(lines):
        clean_line = line
        clean_line = clean_line.translate(str.maketrans('', '', string.punctuation))
        vv = g.connect(*clean_line.lower().split(' '))

    return g


def shuffle_hotwire(g):
    v=list(g.keys())
    random.shuffle(v)
    g.pair_connect(v)
    return g


def shuffled_graph():

    g = graph.Graph()
    v = alpha_ints()
    g.update(v)
    g.connect(*g.keys())
    return shuffle_hotwire(g)

def alpha_ints():
    """Return a tuple of tuples as a list (char, int) from a through z.

    Useful to case a letter list of graph nodes.

        >>> g=graph.Graph()
        >>> v=alpha_ints()
        >>> g.update(v)
        >>> g.connect(*g.keys())
    """
    return tuple((c,i) for i,c in enumerate(string.ascii_lowercase))


def id_method(v):
    if isinstance(v, (int, float)):
        return v
    return v.__name__ if hasattr(v, '__name__') else v


def functions():
    g = graph.Graph(id_method=id_method)
    g.connect(fa, fb, fc, fd)
    g.connect(fa, fab, fac, fad)
    g.connect(b_a, b_b, b_c, b_d, edge=BlankEdge())

    # This applies edges to referenced functions above; essentially _overwriting_
    # the previoue "no edge" connections.
    g.connect(fa, fb, fc, fd, edge=Edge())

    g.add_edge(fc, fd, edge=Edge())
    g.add_edge(fc, fd, edge=Edge())
    # g.add_edge(fc, fd, edge=Edge())
    g.connect(fb, fd)
    g.connect(fa, fd)
    g.connect(fc, fab)
    g.connect(fab, b_a)
    g.connect(b_c, fad)
    # g.add_edge(fc, fd, edge=Edge())
    # g.add_edge(fc, fd, edge=Edge())
    # g.add_edge(fc, fd, edge=Edge())
    return g


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def log_map():
    # Chaotic recurrence relation https://en.wikipedia.org/wiki/Logistic_map
    # >>> logistic_map = lambda x, _:  r * x * (1 - x)
    # >>> r = 3.8
    # >>> x0 = 0.4
    # >>> inputs = repeat(x0, 36)     # only the initial value is used

    # # >>> [format(x, '.2f') for x in accumulate(inputs, logistic_map)]
    # # ['0.40', '0.91', '0.30', '0.81', '0.60', '0.92', '0.29', '0.79', '0.63',
    # #  '0.88', '0.39', '0.90', '0.33', '0.84', '0.52', '0.95', '0.18', '0.57',
    # #  '0.93', '0.25', '0.71', '0.79', '0.63', '0.88', '0.39', '0.91', '0.32',
    # #  '0.83', '0.54', '0.95', '0.20', '0.60', '0.91', '0.30', '0.80', '0.60']

    logistic_map = lambda x, _:  r * x * (1 - x)
    r = 3.8
    x0 = 0.4
    inputs = repeat(x0, 100)     # only the initial value is used
    values = [format(x, '.2f') for x in accumulate(inputs, logistic_map)]

    g = graph.Graph(id_method=None)
    g.pair_connect(values, pinned=False, foo='bar')
    g.pin_ends(values)
    # print('pin ends')
    # g.bind_pair(g.get_start_node(), values[0])
    # g.bind_pair(values[-1], g.get_end_node())


    # vv = tuple(pairwise(values))
    # for a,b in vv:
    #     g.connect(a,b,)
    return g

def fa(v):
    return v + 1


def fb(v):
    return v + 2


def fc(v):
    return v + 3


def fd(v):
    return v + 4



def b_a(v):
    return v + 1


def b_b(v):
    return v + 2


def b_c(v):
    return v + 3


def b_d(v):
    return v + 4


def fab(v):
    return v + 2


def fac(v):
    return v + 3


def fad(v):
    return v + 4


def flat_get_chains(graph, start, end, root_start_node=None, depth=-1, r=None,
    index=-1, stash=None, edge_count=-1, keep_exit_node=True, keep_noedge=None):
    """
    If None, The system checks for NoEdge and drops the edge.
    If True, enforce the edge keep, allowing a null edge within the result
    If False, do not add any edge; (edgeless)
    """
    # keep_noedge = True

    stash = stash or {}
    r = r or []

    if depth > 10:
        print(' --- Recurse protection.')
        return r

    nodelist = start.get_next()

    ignore_node = False
    if isinstance(start, ExitNode):
        if keep_exit_node is False:
            ignore_node = True

    if ignore_node is False:
        r = add_link(r, start, depth, index)

    # stash[id(start)] = depth
    for i, node_name in enumerate(nodelist):
        # r = r.copy()
        # print(' '*depth, node_name)
        next_node = nodelist[node_name]

        edges = graph.get_edges(start.name, node_name)
        print('edges:', edges)
        if len(edges) == 0:
            edges = (NoEdge(), )


        orig_r = r.copy()

        for edge_i, e in enumerate(edges):
            is_noedge = isinstance(e, NoEdge)
            has_edge = keep_noedge if keep_noedge is not None else (not is_noedge)

            if has_edge:
                r = orig_r.copy()
                edge_count += 1
                add_edge_link(r, e, start, next_node, edge_count, edge_i)

            if isinstance(next_node, ExitNode):
                if keep_exit_node is not False:
                    add_link(r, next_node, depth+1, i)
                # print('STOP', r)

                stash[id(r)] = Chain(graph, r)
                return r

            v = flat_get_chains(
                graph=graph,
                start=next_node,
                end=end,
                root_start_node=root_start_node or start,
                depth=depth+1,
                r=r,
                index=i,
                stash=stash,
                edge_count=edge_count,
                keep_exit_node=keep_exit_node,
                keep_noedge=keep_noedge,
                )

    return r


if __name__ == '__main__':
    main()
