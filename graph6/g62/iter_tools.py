from itertools import tee


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def bridge_pairs(func, *units, **kw):
    """Call upon `func` with `pairwise` units pairs until all pairs are
    bridged with edges. Return a tuple of new entities _(edges)_ - being the result of the
    given `func`.
    """
    edges = ()
    # func = func or func.add_edge
    for unit_pair in pairwise(units):
        new_edge = func(unit_pair, **kw)
        edges += (new_edge, )
    return edges
