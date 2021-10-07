from collections import defaultdict
from importlib import reload
from pprint import pprint as pp
from flatmap import FlatGraph

def main():
    g = FlatGraph()
    g.append('A', 'B', 'C', 'D')
    g.append('A', 'F', 'G',)
    g.append('A', 'H', 'I',)
    g.append('W', 'X', 'Y',)

    l = 'A'
    u = 'C'

    # r = g.get_flows(l, with_parent=True, until=u)
    # print(r)

    v = g.last_linear_chain(l)
    e = ('A', 'B', 'C', 'D', 'F', 'G', 'H', 'I')
    va = g.as_names(v)
    assert e == va

    v = g.as_names(g.last_linear_chain(l, drop_self=True))
    e = ('B', 'C', 'D', 'F', 'G', 'H', 'I')
    assert e == v


    e = ('A', 'B', 'F', 'G', 'H', 'I')
    v = g.last_linear_chain(l, until=u)
    va = g.as_names(v)
    assert e == va


    g.append('D', 'E', 'F')

    e = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'F', 'G', 'H', 'I')
    v = g.last_linear_chain(l)
    va = g.as_names(v)
    assert e == va


    e = ('A', 'B', 'F', 'G', 'H', 'I')
    v = g.last_linear_chain(l, until=u)
    va = g.as_names(v)
    assert e == va


    e = ('B', 'F', 'G', 'H', 'I')
    v = g.last_linear_chain(l, until=u, drop_self=True)
    va = g.as_names(v)
    assert e == va

    return g

if __name__ == '__main__':
    g = main()
