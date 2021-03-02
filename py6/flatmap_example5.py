from collections import defaultdict
from importlib import reload
from pprint import pprint as pp
from flatmap import FlatGraph

def main():
    g = FlatGraph()
    g.connect('hallway', 'bedroom')
    g.connect('hallway', 'small-room')
    g.connect('hallway', 'bathroom')
    g.connect('hallway', 'livingroom')
    g.connect('hallway', 'kitchen')

    g.connect('bedroom', 'bed', 'pillows')
    g.connect('bed', 'blanket')
    g.connect('bedroom', 'lamp')
    g.connect('house', 'hallway')
    g.connect('hallway', 'front-door')

    #get('hallway', _g=g)
    pp(g.flat_chains(g.chains('lamp', with_parent=True, reverse=True)))
    return g


def get(*a, _g=None, **kw):
    _g = _g or globals().get('g')
    c=_g.chains(*a, **kw)
    pp(c)
    v = _g.flat_chains(
        c,
        keep_temp=False, allow_partial=False
    )
    pp(v)

    f = _g.filter_complete(v)
    print('Count', len(f))
    pp(f[0:50])

    return f

if __name__ == '__main__':
    g = main()

