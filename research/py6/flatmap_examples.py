
from collections import defaultdict
from importlib import reload
from pprint import pprint as pp
from flatmap import FlatGraph

def main():
    main_a()
    print('---')
    main_b()
    print('---')
    main_c()
    print('---')
    main_d()
    print('---')
    main_e()
    print('---')
    main_f()
    print('---')


def print_internals(g):
    print(g.names)
    print(g.kv)
    print(g.reverse_kv)


def main_a():
    g = FlatGraph()
    g.append('A', 'B', 'C', 'D')
    g.append('A', 'B', 'C', 'D')
    g.append('A', 'D', 'T')
    g.append('T', 'V')

    #print_internals(g)
    assert g.names == {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'T': 5, 'V': 6}
    assert g.kv == {1: {2, 4}, 2: {3}, 3: {4}, 4: {5}, 5: {6}}
    assert g.reverse_kv == {2: {1}, 3: {2}, 4: {1, 3}, 5: {4}, 6: {5}}
    return g


def print_pr(pr):
    pp(pr)


def main_b():
    g = FlatGraph()
    g.append('A', 'B', 'C', 'D')
    g.append('A', 'B', 'C', 'D')
    g.append('T', 'V')
    g.append('A', 'D', 'T')

    #print_internals(g)
    """
        pr: (1, 2, 3, 4, 5, 6, 4, 5, 6)
        ('A', 'B', 'C', 'D', 'T', 'V', 'D', 'T', 'V')
        (1, 2, 3, 4, 5, 6, 4, 5, 6)

    """

    # pr = g.last_linear_chain('A')
    # gn = g.as_names(pr)
    # print(gn)
    # assert gn == ('A', 'B', 'C', 'D', 'T', 'V', 'D', 'T', 'V')

    # print_internals(g)


    pr = g.chains('A')
    # print_pr(pr)
    fc = g.flat_chains(pr,allow_partial=True, allow_top_partial=True)
    pp(fc)

    e =  {'0-0-0': ['B'],
        '0-0-1': ['D'],
         '_complete': {'h-1-1-1', 'h-0-1-1-1-1'},
         '_toplevel': {'0-0-0', '0-0-1'},
         'h-0-1-1-1-1': ['B', 'C', 'D', 'T', 'V'],
         'h-1-1-1': ['D', 'T', 'V'],
         'p-0-1': ['B', 'C'],
         'p-0-1-1': ['B', 'C', 'D'],
         'p-0-1-1-1': ['B', 'C', 'D', 'T'],
         'p-0-1-1-1-1': ['B', 'C', 'D', 'T', 'V'],
         'p-1-1': ['D', 'T'],
         'p-1-1-1': ['D', 'T', 'V'],
         't-0-1': ['B', 'C'],
         't-0-1-1': ['B', 'C', 'D'],
         't-0-1-1-1': ['B', 'C', 'D', 'T'],
         't-1-1': ['D', 'T']}

    assert fc == e

    # print_pr(pr)
    return g


def main_c():
    g = FlatGraph()
    g.append('A', 'B', 'C', 'D')
    g.append('A', 'B', 'C', 'D')
    g.append('T', 'V')
    g.append('A', 'D', 'T')
    g.append('D', 'E', 'F')

    #print_internals(g)
    pr = g.chains('A')
    # prd = {g.as_name(x): y for x, y in pr.items()}
    # print("pr:   ")
    pp(pr)
    # print('\n\n')
    e = (('B', ('C', ('D', ('T', ('V',)), ('E', ('F',))))),
         ('D', ('T', ('V',)), ('E', ('F',))))
    assert pr == e
    fc = g.flat_chains(pr)
    print('c:')
    e =  {'0-0-0': ['B'],
         '0-0-1': ['D'],
         '_complete': {'h-1-2-1', 'h-1-1-1', 'h-0-1-1-2-1', 'h-0-1-1-1-1'},
         '_toplevel': {'0-0-1', '0-0-0'},
         'h-0-1-1-1-1': ['B', 'C', 'D', 'T', 'V'],
         'h-0-1-1-2-1': ['B', 'C', 'D', 'E', 'F'],
         'h-1-1-1': ['D', 'T', 'V'],
         'h-1-2-1': ['D', 'E', 'F'],
         'p-0-1': ['B', 'C'],
         'p-0-1-1': ['B', 'C', 'D'],
         'p-0-1-1-1': ['B', 'C', 'D', 'T'],
         'p-0-1-1-1-1': ['B', 'C', 'D', 'T', 'V'],
         'p-0-1-1-2': ['B', 'C', 'D', 'E'],
         'p-0-1-1-2-1': ['B', 'C', 'D', 'E', 'F'],
         'p-1-1': ['D', 'T'],
         'p-1-1-1': ['D', 'T', 'V'],
         'p-1-2': ['D', 'E'],
         'p-1-2-1': ['D', 'E', 'F'],
         't-0-1': ['B', 'C'],
         't-0-1-1': ['B', 'C', 'D'],
         't-0-1-1-1': ['B', 'C', 'D', 'T'],
         't-0-1-1-2': ['B', 'C', 'D', 'E'],
         't-1-1': ['D', 'T'],
         't-1-2': ['D', 'E']}
    pp(fc)
    assert fc == e
    # print('names:', g.as_names(pr))

    return g


def main_d():
    g = FlatGraph()
    g.append('A', 'B', 'C', 'D')
    g.append('A', 'B', 'C', 'D')
    # g.append('T', 'V')
    g.append('A', 'D', 'T')
    g.append('A', 'D', 'V')
    g.append('C', 'E', 'V')
    # g.append('D', 'E', 'F')
    # g.append('C', 'F', 'O')
    # g.append('D', 'E', 'F', 'G', 'H')
    # g.append('A', 'H', 'I', 'J', 'K')
    # g.append('J', 'L')
    # g.append('F', 'G')
    # g.append('K', 'L')

    #print_internals(g)
    pr = g.chains('A')
    # prd = {g.as_name(x): y for x, y in pr.items()}
    # print("\n\npr:   ")
    # pp(pr)
    # print('\nChains:')
    fc = g.flat_chains(pr)
    expected = {'0-0-0': ['B'],
             '0-0-1': ['D'],
             '_complete': {'h-1-1', 'h-1-2', 'h-0-1-2-1', 'h-0-1-1-1', 'h-0-1-1-2'},
             '_toplevel': {'0-0-0', '0-0-1'},
             'h-0-1-1-1': ['B', 'C', 'D', 'T'],
             'h-0-1-1-2': ['B', 'C', 'D', 'V'],
             'h-0-1-2-1': ['B', 'C', 'E', 'V'],
             'h-1-1': ['D', 'T'],
             'h-1-2': ['D', 'V'],
             'p-0-1': ['B', 'C'],
             'p-0-1-1': ['B', 'C', 'D'],
             'p-0-1-1-1': ['B', 'C', 'D', 'T'],
             'p-0-1-1-2': ['B', 'C', 'D', 'V'],
             'p-0-1-2': ['B', 'C', 'E'],
             'p-0-1-2-1': ['B', 'C', 'E', 'V'],
             'p-1-1': ['D', 'T'],
             'p-1-2': ['D', 'V'],
             't-0-1': ['B', 'C'],
             't-0-1-1': ['B', 'C', 'D'],
             't-0-1-2': ['B', 'C', 'E']}
    pp(fc)
    assert fc == expected
    fc_less = g.flat_chains(pr, allow_partial=False, keep_temp=False)
    pp(fc)
    assert fc['_complete'] == expected['_complete']
    # print('names:', g.as_names(pr))

    return g

def main_e():
    g = FlatGraph()
    g.append('A', 'B', 'C', 'D')
    g.append('A', 'B', 'C', 'D')
    g.append('A', 'J', 'C', 'D')
    # g.append('T', 'V')
    g.append('A', 'D', 'T')
    g.append('A', 'D', 'V')
    g.append('F', 'A', 'D', 'V')
    g.append('C', 'E', 'V')
    g.append('O', 'P', 'F')

    # g.append('D', 'E', 'F')
    # g.append('C', 'F', 'O')
    # g.append('D', 'E', 'F', 'G', 'H')
    # g.append('A', 'H', 'I', 'J', 'K')
    # g.append('J', 'L')
    # g.append('F', 'G')
    # g.append('K', 'L')

    main_e_a(g)
    main_e_b(g)


def main_e_a(g):
    #print_internals(g)
    pr = g.chains('C', reverse=False)
    # pr = g.chains('C', reverse=False)
    # prd = {g.as_name(x): y for x, y in pr.items()}
    # print("\n\npr:   ")
    # print_pr(pr)
    fc = g.flat_chains(pr, allow_partial=True, allow_top_partial=True)
    pp(fc)

    values = tuple(fc.values())

    assert ['E', 'V'] in values
    assert ['D', 'V'] in values
    assert ['D', 'T'] in values


def main_e_b(g, letter='F'):
    print_internals(g)
    print(f'e: {letter}:')
    pr = g.chains(letter, reverse=False)
    # pr = g.chains('C', reverse=False)
    # prd = {g.as_name(x): y for x, y in pr.items()}
    # print("\n\npr:   ")
    print_pr(pr)
    pre = (('A',
              ('B', ('C', ('E', ('V',)), ('D', ('T',), ('V',)))),
              ('D', ('T',), ('V',)),
              ('J', ('C', ('E', ('V',)), ('D', ('T',), ('V',))))),)
    assert pr == pre
    # pr = g.last_linear_chain('A')
    fc = g.flat_chains(pr, allow_partial=True, allow_top_partial=True)
    pp(fc)
    e = {'0-0-0': ['A'],
         '_complete': {'h-0-1-1-1-1',
                       'h-0-1-1-2-1',
                       'h-0-1-1-2-2',
                       'h-0-2-1',
                       'h-0-2-2',
                       'h-0-3-1-1-1',
                       'h-0-3-1-2-1',
                       'h-0-3-1-2-2'},
         '_toplevel': {'0-0-0'},
         'h-0-1-1-1-1': ['A', 'B', 'C', 'E', 'V'],
         'h-0-1-1-2-1': ['A', 'B', 'C', 'D', 'T'],
         'h-0-1-1-2-2': ['A', 'B', 'C', 'D', 'V'],
         'h-0-2-1': ['A', 'D', 'T'],
         'h-0-2-2': ['A', 'D', 'V'],
         'h-0-3-1-1-1': ['A', 'J', 'C', 'E', 'V'],
         'h-0-3-1-2-1': ['A', 'J', 'C', 'D', 'T'],
         'h-0-3-1-2-2': ['A', 'J', 'C', 'D', 'V'],
         'p-0-1': ['A', 'B'],
         'p-0-1-1': ['A', 'B', 'C'],
         'p-0-1-1-1': ['A', 'B', 'C', 'E'],
         'p-0-1-1-1-1': ['A', 'B', 'C', 'E', 'V'],
         'p-0-1-1-2': ['A', 'B', 'C', 'D'],
         'p-0-1-1-2-1': ['A', 'B', 'C', 'D', 'T'],
         'p-0-1-1-2-2': ['A', 'B', 'C', 'D', 'V'],
         'p-0-2': ['A', 'D'],
         'p-0-2-1': ['A', 'D', 'T'],
         'p-0-2-2': ['A', 'D', 'V'],
         'p-0-3': ['A', 'J'],
         'p-0-3-1': ['A', 'J', 'C'],
         'p-0-3-1-1': ['A', 'J', 'C', 'E'],
         'p-0-3-1-1-1': ['A', 'J', 'C', 'E', 'V'],
         'p-0-3-1-2': ['A', 'J', 'C', 'D'],
         'p-0-3-1-2-1': ['A', 'J', 'C', 'D', 'T'],
         'p-0-3-1-2-2': ['A', 'J', 'C', 'D', 'V'],
         't-0-1': ['A', 'B'],
         't-0-1-1': ['A', 'B', 'C'],
         't-0-1-1-1': ['A', 'B', 'C', 'E'],
         't-0-1-1-2': ['A', 'B', 'C', 'D'],
         't-0-2': ['A', 'D'],
         't-0-3': ['A', 'J'],
         't-0-3-1': ['A', 'J', 'C'],
         't-0-3-1-1': ['A', 'J', 'C', 'E'],
         't-0-3-1-2': ['A', 'J', 'C', 'D']}
    assert fc == e



def main_f():
    g = FlatGraph()
    g.append('A', 'B', 'C', 'D')
    pr = g.chains('A')
    # pr = g.chains('C', reverse=False)
    # prd = {g.as_name(x): y for x, y in pr.items()}
    # print("\n\npr:   ")
    # print_pr(pr)
    fc = g.flat_chains(pr, allow_partial=True, allow_top_partial=True)
    pp(fc)

    # print('names:', g.as_names(pr))

    return g

if __name__ == '__main__':
    main()
