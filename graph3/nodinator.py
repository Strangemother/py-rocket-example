"""

The 'node-inator' takes a special "device" node and a "wire" edge.

Each device is an item with an IN/OUT terinal node attached (directionally)
"""

from g3 import Connections

def f_a(my_val, val):
    return val + my_val

def f_b(my_val, val):
    return val + my_val

def f_c(my_val, val):
    return val - my_val

def f_d(my_val, val):
    return val - my_val

def f_e(my_val, val):
    return val + my_val

import operator as op

c=Connections()
c.connect(f_a, f_b, f_c)
c.connect(f_c, f_d, )
c.connect(f_d, f_a, )
from collections import defaultdict
mem = defaultdict(int)

def compute_ids(ids):
    """If the start node is None, the start pin of all connections is used.
    else get the node from the tree.
    """
    r = ()
    for n in ids:
        r += compute_node(c.node(uuid=n))
    return r
    # a_myval = mem[edge.a.get_uuid()]


def compute_node(current_node=None):
    a_myval = mem[current_node.get_uuid()]

    res = ()
    for edge in current_node.edges:
        func = edge.b.data
        b_uuid = edge.b.get_uuid()
        b_myval = mem[b_uuid]
        b_newval = func(b_myval, a_myval)
        mem[b_uuid] = b_newval
        res += (b_uuid,)
    return res

def reset():
    keys = c.datas['nodes_references'].keys()
    for x in keys:
        mem[x] = 1



def pump(start_items=None):

    def _pump(items):
        if len(items) == 0:
            return compute_node(c.get_start_node())
        return compute_ids(items)

    cv = ()# _pump(() if start_items is None else start_items)

    while 1:
        cv = _pump(cv)
        yield cv

c.pp()
# cv = compute_node(c(f_a))
# print(cv)
# cv = compute_ids(cv if len(cv) > 0 else (c.get_start_node().get_uuid(),))
print(mem)
g = pump()
print(mem)
# get_node - > run [func(value) op g(func).data]
# store result in g(func).data
# get each next node
#
# get_node - > run [func(value) op g(func).data]
# store result in g(func).data
# get each next node
#
# get_node ...

