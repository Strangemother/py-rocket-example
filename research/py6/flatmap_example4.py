from collections import defaultdict
from importlib import reload
from pprint import pprint as pp
from flatmap import FlatGraph

def main():
    g = FlatGraph()
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

    g.splice('arms', 'elbows', 'forearms', 'wrists', 'hands')
    # disconnect arms, hands
    # connect arms -> ... hands

    # enforce a connection of all _outbound_ of 'hands' to palms
    # including fingers and thumbs.
    g.splice_all('hands', 'palms')
    get('arms', _g=g)

    g.split('wrists', 'hands')
    get('arms', _g=g)
    g.connect('wrists', 'hands')
    get('arms', _g=g)
    # same as:
    # g.splice('hands' 'palms' 'fingers')
    # g.splice('hands' 'palms' 'thumbs')

    get('face', _g=g)

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


# {'_complete': {('h', 0, 1),
#                ('h', 0, 2, 1, 1),
#                ('h', 0, 3, 1, 1, 1),
#                ('h', 0, 4),
#                ('h', 3, 1, 1, 1)},
#  '_toplevel': {(0, 0, 2), (0, 0, 1), (0, 0, 0), (0, 0, 4), (0, 0, 3)},
#  ('h', 0, 1): ['B', 'H'],
#  ('h', 0, 2, 1, 1): ['B', 'P', 'Q', 'R'],
#  ('h', 0, 3, 1, 1, 1): ['B', 'G', 'T', 'U', 'V'],
#  (0, 0, 1): ['D'],
#  (0, 0, 2): ['E'],
#  ('h', 0, 4): ['B', 'C'],
#  ('h', 3, 1, 1, 1): ['G', 'T', 'U', 'V'],
#  (0, 0, 0): ['B'],
#  (0, 0, 3): ['G'],
#  (0, 0, 4): ['V']}
# >>> g.disconnect(g.names.get('B'),g.names.get('P'))
# >>> pp(g.flat_chains(g.chains('A', max_depth=10), keep_temp=False, allow_partial=False))
# {'_complete': {('h', 0, 1),
#                ('h', 0, 2, 1, 1, 1),
#                ('h', 0, 3),
#                ('h', 3, 1, 1, 1)},
#  '_toplevel': {(0, 0, 2), (0, 0, 1), (0, 0, 0), (0, 0, 4), (0, 0, 3)},
#  ('h', 0, 1): ['B', 'H'],
#  ('h', 0, 2, 1, 1, 1): ['B', 'G', 'T', 'U', 'V'],
#  ('h', 3, 1, 1, 1): ['G', 'T', 'U', 'V'],
#  (0, 0, 0): ['B'],
#  (0, 0, 1): ['D'],
#  (0, 0, 2): ['E'],
#  (0, 0, 3): ['G'],
#  (0, 0, 4): ['V'],
#  ('h', 0, 3): ['B', 'C']}


# (
#     ['B', 'G', 'T', 'U', 'V'],
#     ['G', 'T', 'U', 'V'],
#     ['B', 'P', 'Q', 'R'],
#     ['B', 'C']
#     ['B', 'H'],
# )

# (
#     ['B', 'G', 'T', 'U', 'V'],
#     ['G', 'T', 'U', 'V'],
#     ['B', 'C'],
#     ['B', 'H']
# )
