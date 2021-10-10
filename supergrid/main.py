from pprint import pprint as pp


from collections import defaultdict
import random

# A single layer of posibilities for a node.
layer = [
    'MNO',
    'WAE',
    'RST',
]

la = [
    'AAA',
    'AAA',
    'AAA',
]

la1 = [
    # ' D ',
    'DDD',
    # ' D ',
]


# The ready graph of connections, consisting of _all_ possibilities for each
# node. In this example "A" has connections in all directions.
# The Tree assigns compass directions for each node.
# g['A']['north'] == ['N', 'K']

mem = {
    (3,3): 'D',
}


dirs = {
    ( 0, 0):  ('place', 'A',),
    ( 0, 1):  ('east', 'E',),
    ( 0, -1): ('west', 'W',),
    ( 1, 0):  ('sorth', 'S',),
    (-1, 0):  ('nouth', 'N',),
    ( 1, 1):  ('SE', 'T',),
    ( 1, -1): ('SW', 'R',),
    (-1, -1): ('NW', 'M',),
    (-1, 1):  ('NE', 'O',),
}


def main():
    global connections
    global tree
    global g

    # Build the compass directions
    g=stash(['D', 'D', 'D'])
    g=stash(la1)
    # stash(la1, *g)

    # g=stash([
    #     'JKL',
    #     'IAP',
    #     'BNM',
    # ])

    # stash(layer, *g)
    connections, tree = g

    slurp_plot(2,5)
    slurp_plot(2,10)
    slurp_plot(2,15)



    d=collapse(6,3)
    collapse(6,4)
    collapse(6,5)
    collapse(6,6)
    collapse(7,6)
    collapse(8,6)
    print_mem()


def stash(layer, graph=None, compass=None):
    """Given a 2D layer, stach into the sparse matrix as compass positions.
    """
    print('R C V')

    cells = ()
    for row, line in enumerate(layer):
        print('-----')
        for col, node in enumerate(line):
            cell = (row, col, node)
            cells += (cell,)

    res = graph or defaultdict(set)
    dgr = compass or defaultdict(lambda: defaultdict(set))

    height = len(layer)
    width = len(layer[0])

    for row, col, node in cells:
        pos, comp = map_node(row, col, layer, width, height, node)

        for k, v in pos.items():
            # k _should_ be the same as node, however the
            # mapper may have supplied extra (currently not implemented)
            # # merge two sets.
            res[k].update(v)

        for node, dirs in comp.items():
            for dir_tuple, nodes in dirs.items():
                print(dir_tuple, nodes)
                dgr[node][dir_tuple].update(nodes)

    return res, dgr

def map_node(x, y, layer, width, height, node):
    """Given the x,y of the target node within a layer, map the compass
    and produce the direction graph.
    """

    t_node = layer[x][y]
    assert t_node == node
    # Find the offset then perform clock from -1 to 1
    left_offset = width - x
    top_offset = height - y

    print('LTN', left_offset, top_offset, node)

    rels = ()
    for ir in range(-1, 2):
        for ic in range(-1, 2):
            rels += ( (ir, ic,), )

    possible = defaultdict(set)
    compass = defaultdict(lambda:defaultdict(set))

    for ir, ic in rels:
        # Clock rotation starting top left
        sx = x + ir
        sy = y + ic
        v = (ir,ic)

        if v == (0,0,):
            print('   X', node, 'skip self')
            continue
        if sx > width:
            # print('Nothing futher')
            continue

        if sy > height:
            # print('nothing below')
            continue


        p = dirs[v][1]

        if sx < 0 or sy < 0:
            # prevent reverse stepping though lists and strings
            print('   X skip',p, sx, sy, p, node)
            continue

        try:
            other = layer[sx][sy]
            possible[node].add(other)
            compass[node][v].add(other)

            print('   >',p,'->', other, v, sx,sy)
        except IndexError:
            pass
            # print('    missing', p, sx, sy, 'for', node)
        # if node == 'A':
            # import pdb; pdb.set_trace()  # breakpoint 0928638a //

    compass = {x:dict(v) for x,v in compass.items()}
    return possible, compass

# Next we imagine a psuedo grid of empty space and request a _collapse_ at a point.
def collapse(x, y, force=False, store_none=True):
    """Given the XY, _collapse_ the node to a resolved _type_ and
    plot.

    During an expansion, uncollapsable steps may store as None, flagging
    a collapse was attempted but the node is null. If store_none is False,
    The newly discovered _None_ node is not stored, ensuring the mem grid
    does not grow during a research step.
    """
    v = (x,y)
    if v in mem:
        val = mem[v]

        r=val
        if val is None:
            # print('recollapse. missed space')
            r = resolve(x, y,force)
        elif force is False:
            # print('Already collapsed', x,y, mem[v])
            return mem[v]

    else:
        # nothing in this position, so gather allowances.
        r = resolve(x, y,force)

    if (r is None) and (store_none is False):
        return r

    # print('Store', v, r, 'store_none', store_none)
    mem[v] = r
    return r


def rel_spread():
    rels = ()
    for ir in range(-1, 2):
        for ic in range(-1, 2):
            rels += ( (ir, ic,), )
    return rels


def resolve(x, y,force=False):
    # find the best node for the given xy, testing siblings for allowances.
    # Get the neighbours and their _allowed_.
    r = spread_dict(x, y)
    allowed = get_allowed(x, y,force)
    # print(allowed)
    if len(allowed) == 0:
        # print('Did not collapse', x,y)
        return None
    # Weighting should occur here, selecting from lower entropies.
    return random.choice(tuple(allowed))


def get_allowed(x, y,force=False):
    """
    For each dict kv, collect the _allowed_ for the relative sibiling
    Each sibling should _flip_ to test.
    """
    # A grid surrounding the given position
    r = spread_dict(x, y)
    # Enforced allowed given by existing siblings
    all_allowed =()# set()
    # A node maflushy not provide a subset, as such _all_ of its nodes are allowed.
    flag_all = False

    # A list of 'All' connection for a single location, appended in a set
    all_connections = ()

    for dir_p, pos in r.items():
        # as we _clock_ around the given x,y, invert the direction to find
        # the opposite compass direction of the pos relative to the x,y.
        flip_dir = flip(dir_p)
        # print(dir_p, flip_dir)
        # print(d_char(dir_p), '->', d_char(flip_dir))
        # Using the Flip, gather the _allowed_ for the pos flipped
        if pos in mem:
            # This node is populated and asserts an allowance towards
            # the target x,y.
            value = mem[pos]
            # tree['A'][north] == 'A', 'B', 'D'
            allowed = tree[value][flip_dir]
            # print('allowed', allowed)
            # all_allowed.update(allowed)
            all_allowed += tuple(allowed)

        else:
            # As there is nothing in this position, it does not assert any
            # allowances (it's blank). As such all possible nodes are valid.
            # And _other_ nodes within this spread should take precedence
            # for selected nodes.
            flag_all = True
            # get allowed for position - such as the "area" of possible nodes.
            # - Alternatively, we could _spread_ and resolve _this_ position
            # discovering its allowances recursively until a collased state or
            # recurse limit.
            all_connections += ( set(tree.keys()), )

    if len(all_allowed) == 0 and (flag_all is True or force is True):
        # Delete any keys in all_connections that don't exist within
        # first merge all sets, then iterate, deleting any nodes
        # _not_ within a current list
        if force is False:
            # print('No allowed')
            return all_allowed

        _all = set().union(*all_connections)

        for subset in all_connections:
            """
            only keep the items common to both sets -  deleting items
            from _all if they don't exist within the subset.
            Ensuring a common list across all nodes.
            """
            inall = _all.intersection(subset)

        print('Nothing reduced, return all possible nodes')
        if len(_all) == 0 and force is True:
            return set(tree.keys())
        # print('all_connections', all_connections)
        # print('_all', _all)
        return _all

    return all_allowed


def d_char(dir_p):
    return dirs[dir_p][1]


def flip(dir_p):

    """
    For each dict kv, collect the _allowed_ for the relative sibiling
    Each sibling should _flip_ to test.

    (-1, -1)   (1, 1)     M -> T
    (-1, 0)    (1, 0)     N -> S
    (-1, 1)    (1, -1)    O -> R
    (0, -1)    (0, 1)     W -> E
    (0, 1)     (0, -1)    E -> W
    (1, -1)    (-1, 1)    R -> O
    (1, 0)     (-1, 0)    S -> N
    (1, 1)     (-1, -1)   T -> M

    -1  1  1      M N O
    -1  0  1      W A E
    -1 -1  1      R S T

    """
    return tuple(x * -1 for x in dir_p)


def spread_dict(x,y):
    """Given an XY spread out in all directions, returning 8 XY coords
    of siblings

        spread(4, 3)
        ((3, 2), (3, 3), (3, 4),
         (4, 2),       , (4, 4),
         (5, 2), (5, 3), (5, 4))
    """
    # First get the 8 cells surrounding this cell.
    coords = rel_spread()
    orig = (x, y)

    res = {}

    for rx, ry in coords:

        sx = x + rx
        sy = y + ry
        item = (sx, sy,)
        if item == orig:
            continue
        r_dir = (rx, ry,)
        res[r_dir] = item

    return res


def print_mem():
    """Generate a grid from the mem, building a 2D array of positions.
    """
    keys = mem.keys()
    ma, mb = (), ()
    for x, y in keys:
        ma += (x,)
        mb += (y,)

    rx = range(min(ma), max(ma)+1)
    ry = range(min(mb), max(mb)+1)

    h = ' '.join(map(str, tuple((' ', ' ', )) + tuple(x+0 for x in rx)))

    dashes = '-' * len(h)

    o = (dashes, )

    for x in rx:

        # l = (y, '|',)
        l = (x,'|', )#+ (' ' * (int(y)-min(ma)),)

        for y in ry:

            p = (x, y)
            v = mem.get(p, ' ')
            if v is None:
                v = '+'
            l += (v,)

        line = ' '.join(map(str,l))

        o += (line,)
    o += (dashes,)

    for l in o:
        print(l)


def plot(x,y, force=False, recurse=True, store_none=True):
    v = collapse(x,y, force, store_none=store_none)
    if v is None and recurse is True:
        vs = ()
        # print('Recuse collapsing')
        coords = spread_dict(x,y)
        for sx,sy in coords.values():
            vs += plot(sx,sy, recurse=False, store_none=store_none)
    else:
        vs = (v,)

    return vs


def slurp_plot(x,y, force=False, recurse=True, store_none=True):
    """Perform plotting. If any sibling is uncollapsed, perform collapse.
    """
    v = plot(x,y, force, recurse, store_none=store_none)
    coords = spread_dict(x,y)
    nones = filter_none(coords.values())
    for sx, sy in nones:
        plot(sx,sy, force, recurse, store_none=store_none)

    if v == (None,):
        # originally the plot as none, but the sibiling may be populated now,
        # so try again.
        v = plot(x,y,force,recurse, store_none=store_none)

    return nones

def filter_none(coords):
    """for a list of coordinates, iterate and filter the elements of _none_.
    return a list of nodes with the value of None.
    """
    r = ()
    for co in coords:
        if (co in mem) is False:
            continue

        if mem[co] is None:
            r += (co,)
    return r


def flush():
    for x in mem:
        mem[x] = None

    print_mem()

import time

def step_resolve(x=None,y=None):
    """Given a partial tree, resolve all None steps until all Nones are
    complete. This will recurse until fully exausted.
    """
    to_slurp = ( (x,y,), )

    if x is None:
        to_slurp = ()
        for xy, items in mem.items():
            if items is None:
                to_slurp += (xy,)

    nones = set()
    store_none = len(to_slurp) < 6
    for xy in to_slurp:
        r = slurp_plot(*xy, store_none=store_none)
        nones.update(set(r))

    do_loop = 1
    count = 0
    last_result = -1

    while do_loop:
        nn = set()
        print('Reading', len(nones), '"none" spaces.')
        time.sleep(.5)
        store_none = len(nones) < 6
        for xy in nones:
            v = slurp_plot(*xy, recurse=len(nones)<6, store_none=store_none)
            nn.update(v)
            count += 1
            if count > 50:
                break
                return nones
        nones = nn

        do_loop = last_result == len(nones)
        last_result = len(nones)
        if do_loop is False:
            print('No movement.')

    # pp(mem)
    print('Result', len(nones), 'None spaces')
    print_mem()


if __name__ == '__main__':
    main()
