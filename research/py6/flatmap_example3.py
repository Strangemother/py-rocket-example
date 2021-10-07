from collections import defaultdict
from importlib import reload
from pprint import pprint as pp
from flatmap import FlatGraph

def main():
    g = FlatGraph()
    # g.append(*'ABCDEFGH')
    # g.append(*'CEOP')
    # g.append(*'CKL')
    # g.append(*'LMOP')

    g.append(*'AB')
    g.append(*'AD')
    g.append(*'AE')
    g.append(*'AG')
    g.append(*'AV')
    g.append(*'BC')
    g.append(*'BG')
    g.append(*'BH')
    g.append(*'GTUV')
    g.append(*'BPQR')

    # g.append(*'AFG')
    # g.append(*'AHI')
    # g.append(*'WINDOWS')
    # g.append(*'SOFA')
    # g.append(*'ECHO')
    # g.append(*'HORSE')
    # g.append(*'WXY')


    chains = g.chains('A', max_depth=10, until='W', with_parent=False)
    fc = g.flat_chains(chains)
    pp(fc)
    f = g.filter_complete(fc)
    print('Count', len(f))
    pp(f[0:50])


    return g

def get(*a, **kw):
    v = g.flat_chains(
        g.chains(*a, **kw),
        keep_temp=False, allow_partial=False
    )
    pp(v)
    return v

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
