
from time import sleep

from machine import Machine
from toys import *


import asyncio
from pprint import pprint as pp

def main():
    return asyncio.run(async_main(), debug=True)

async def async_main():
    funcs = (
        # run_chain_step_once,
        # run_chain_concat,
        # run_chain_arrow,
        # run_chain_6_infinite,
        # run_chain_6_limited,
        # run_chain_path,
        # run_chain_path,
        # run_edge,
        # run_chain_concat_4_branch,
        # run_chain_run_one2one,
        run_chain_pointer_merge_v2,
    )

    others = (
        run_chain_pointer_merge, # I think this is broken.
    )

    v = None
    for func in funcs:
        # sleep(.2)
        print(f'\n-- Running {func.__name__} --\n')
        v = await func()

    return v


def tap_add_two(a,b,edge, *ta, **tkw):
    return ( (ta[0] + 2,), tkw,)

def tap_add_three(a,b,edge, *ta, **tkw):
    return ( (ta[0] + 3,), tkw,)


sub_5 = op('sub', 5)
add_10 = op('add', 10)


async def add_all(*v, **kw):
    print('!!! add_all function recieved', v)
    return sum(v)


async def in_node(*v, **kw):
    return ..., v, kw



async def run_chain_pointer_merge():
    """Two pointers for the same node on the same step can merge
    their input results, allowing one call to one node with multiple arguments

            +10
        10 --  --> (20, 5)
             -5

    This setup
                       +10 (20) ----------->
        in_node(10) -> -5  (5)  -----------> M add_all (29) -> out
                       -6  (4)  -- e ------>
                                -> *2 (8)
    """

    m = Machine()

    # in_node -> add_10 -> add_all
    _, _, node_add_all_a = await m.a_connect(in_node, add_10, add_all)
    # in_node -> sub_5 -> add_all
    await m.a_connect(in_node, sub_5, node_add_all_a)
    # in_node -> sub_6 -> add_all
    _, node_sub_6, node_add_all = await m.a_connect(in_node, sub_6, node_add_all_a)

    # sub_6 -> multiply_by(2)
    await m.a_connect(node_sub_6, multiply_by)
    # await m.a_connect(node_add_all_a, void)

    assert node_add_all_a is node_add_all
    edge = m.edge_bind(node_sub_6, node_add_all)

    node_add_all_a.merge_pointers = False

    print('\n\n --- Running Tree 1 --- \n')
    stepper, pointers = await m.start_chain(10)
    expected = (20, 8, 5, 4)
    test_expected(pointers, expected)
    return m, stepper

    print('\n\n --- Running Tree 2 (with tap) --- \n')
    ## Then add the tap to the function, adding between the `-6 -> add_all`
    await edge.add_tap(tap_add_three)
    stepper, pointers = await m.start_chain(10)
    expected = (20,5,8,7)

    test_expected(pointers, expected)

    print('\n\n --- Running Tree 3 (with merge and tap) --- \n')
    node_add_all_a.merge_pointers = True
    stepper, pointers = await m.start_chain(10)
    pargs(pointers)

    return m, stepper




async def run_chain_pointer_merge_v2():
    """Two pointers for the same node on the same step can merge
    their input results, allowing one call to one node with multiple arguments

            +10
        10 --  --> (20, 5)
             -5

    This setup
                  +10 ------->
        in_node -> -5 -------> M add_all -> == (29)
                   -6 ------->

    If stepper.merge_mode is False:

                  +10 -------> add_all -> 10
        in_node -> -5 -------> add_all -> 5
                   -6 -------> add_all -> 4

    """

    m = Machine()
    _, _, node_add_all_a = await m.a_connect(in_node, add_10, add_all)
    await m.a_connect(in_node, sub_5, node_add_all_a)
    _, node_sub_6, node_add_all = await m.a_connect(in_node, sub_6, node_add_all_a)
    # await m.a_connect(node_add_all_a, void)
    assert node_add_all_a is node_add_all
    # edge = m.edge_bind(node_sub_6, node_add_all)

    # node_add_all_a.merge_pointers = True
    node_add_all.merge_pointers = True

    print('\n\n --- Running Tree 1 --- \n')
    stepper, pointers = await m.start_chain(10)
    ## The 'start_chain' executes the in_node.
    # 10 + 10 == 20
    # 10 - 5  == 5
    # 10 - 6  == 4
    ## The last node should _merge_ the values into a
    ### single value:
    # 29...
    expected = (29,)
    test_expected(pointers, expected)

    return m, stepper


async def run_edge():
    m = Machine()
    na, nb = await m.a_connect(add_two, multiply_by)
    _, nc = await m.a_connect(na, minus_3, unique=True)
    edge = m.edge_bind(na,nb)
    # e = await m.get_edges(na, nb)
    # print(e)
    stepper, pointers = await m.start_chain(1)

    expected = (0,6,)
    ## untapped == (1 + 2) * 2
    test_expected(pointers, expected)

    await edge.add_tap(tap_add_two)
    stepper, pointers = await m.start_chain(1)
    ## Tapped == (1 + 2 [+ 2]) * 2
    expected = (0,10,)
    test_expected(pointers, expected)

    return m, stepper


async def run_chain_run_one2one():

    m = Machine()
    await m.a_connect(add_two, multiply_by)
    # m.connect(add_two, add_10)
    m.connect(multiply_by, minus_3)
    await m.a_connect(minus_3, opadd_10)
    m.connect(minus_3, div_2)
    await m.a_connect(div_2, sub_6)
    m.connect(div_2, add_5)
    await m.a_connect(add_5, add_12)
    # m.connect(minus_3, void)
    m.connect(opadd_10, void)
    await m.a_connect(opadd_10, op_add_10_2)
    m.connect(op_add_10_2, op('add', 10))

    stepper, pointers = await m.start_chain(1)
    # stepper = m.step_chain(1)

    expected = (-4.5, 13, 18.5, 33)
    test_expected(pointers, expected)
    return m, stepper


async def run_chain_concat_4_branch():

    m = Machine()
    await m.a_connect(add_two, multiply_by, minus_3, opadd_10, op_add_10_2, op('add', 10))
    await m.a_connect(minus_3, div_2, sub_6)
    await m.a_connect(div_2, add_12)
    await m.a_connect(opadd_10, void)

    stepper, pointers = await m.start_chain(1)

    expected = (13, -4.5, 13.5, 33)
    test_expected(pointers, expected)
    """
    (
        {
            'P_42867200': (
                <Pointer P_42867200 for <Node "N_42824608": op_add_10>>,
                 ((33,), {})
            )
        },

        {
            'P_42867200': (
                    <Pointer P_42867200 for <Node "N_42824608": op_add_10>>,
                    ((33,), {})
                ),
            'P_42867344': (
                    <Pointer P_42867344 for <Node "N_42737376": void>>,
                    ((13,), {})
                ),
            'P_42867440': (
                    <Pointer P_42867440 for <Node "N_42823744": op_sub_6>>,
                    ((4.5,), {})
                ),
            'P_42867536': (
                    <Pointer P_42867536 for <Node "N_42824032": op_add_12>>,
                    ((13.5,), {})
                )
        }
    )
    """

    return m, stepper


async def run_chain_step_once():

    m = Machine()
    await m.a_connect(add_two, multiply_by, minus_3, opadd_10, op_add_10_2, div_2)
    await m.a_connect(minus_3, div_2, sub_6)
    await m.a_connect(div_2, add_12, sub_6)
    await m.a_connect(div_2, void)
    await m.a_connect(op_add_10_2, op('add', 4))
    await m.a_connect(op('add', 4), op('mul', 2))

    # c = m.step_chain(1)
    stepper = m.get_stepper()

    pc, pr = await stepper.run_step(1)
    test_expected(pc, (3,))

    return m, stepper


async def run_chain_concat():

    m = Machine()
    await m.a_connect(add_two, multiply_by, minus_3, opadd_10, op_add_10_2, div_2)
    await m.a_connect(minus_3, div_2, sub_6)
    await m.a_connect(div_2, add_12, sub_6)
    await m.a_connect(div_2, void)
    await m.a_connect(op_add_10_2, op('add', 4))
    await m.a_connect(op('add', 4), op('mul', 2))


    # stepper = m.get_stepper()
    # pc, pr = stepper.run_step(1)

    res = await m.start_chain(1)
    stepper, pc = res[1]
    test_expected(pc, [-4.5, 1.5, 5.5, 7.5, 11.5, 17.5, 27])

    return m, stepper


async def run_chain_arrow():

    m = Machine(unique_nodes=True)
    _ = m.C
    na = _ > add_two
    na > _(multiply_by) > _(minus_3) > _(opadd_10) > _(op_add_10_2) > div_2

    r = m.C > _(minus_3) > _(div_2) > _(sub_6)

    r > _(div_2) > _(add_12) > sub_6
    m.C > _(div_2) > _(void)

    opn = _(op('add', 4))
    m.C > _(op_add_10_2) > opn
    m.C > opn  > _(op('mul', 2))

    res = await m.start_chain(1)
    stepper, pc = res
    c = pc[1]

    test_expected(pc,  [41])

    return m, stepper


async def run_chain_path():

    m = Machine()
    na, nb, nc = await m.a_connect(add_two, multiply_by, add_two, unique=True)
    _, nd = await m.a_connect(nb, add_4, unique=True) # 10
    _, n_add10 = await m.a_connect(nb, opadd_10, unique=True) # 16
    _, nf = await m.a_connect(n_add10, add_5, unique=True) # 21
    _, ng = await m.a_connect(n_add10, minus_6, unique=True) # 10
    _, ng = await m.a_connect(n_add10, sub_6, unique=True)

    ## subtract is flipped - likely all operators occur this way.

    stepper, pc = await m.start_chain(1)
    c = pc[1]
    expected = [8, 10, 21, 10, 10]
    test_expected(pc,  expected)

    res = {}

    path = [0, 0, 0]

    stepper1, pc = await m.conf_start_chain(args=(1,), path=path)
    res[0] = pargs(pc)

    path = [0, 1,1]
    stepper2, pc = await m.conf_start_chain(args=(1,), path=path)
    res[1] = pargs(pc)


    path = [0, 2, 1]
    stepper4, pc = await m.conf_start_chain(args=(1,), path=path)
    res[3] = pargs(pc)

    path = [0, 2, 2]
    stepper5, pc = await m.conf_start_chain(args=(1,), path=path)
    res[4] = pargs(pc)

    path = [0, 2, 0]
    stepper3, pc = await m.conf_start_chain(args=(1,), path=path)
    res[2] = pargs(pc)

    p = tuple(pc[0].values())[0][0]
    sequence_match_test(p.history, path, sort=False, as_type=tuple)

    c = pc
    # test_expected(pc,  [8, 10, 21, 10, 10])
    result_values = tuple(x[0] for x in res.values())

    sequence_match_test(result_values, expected)
    return m, c# stepper


async def run_chain_6_infinite():

    m = Machine()
    await m.a_connect(add_two, multiply_by, add_two)

    stepper, pointers = await m.conf_start_chain(args=(1,), kwargs={}, loop_limit=6)
    test_expected(pointers[0], (38,))

    return m, stepper


async def run_chain_6_limited():

    m = Machine()

    # 1, +2, *3, +2 == 8
    # (1 + 2) * 2 + 2
    na, nb, nc = await m.a_connect(add_two, multiply_by, add_two, unique=True)

    stepper, pointers = await m.conf_start_chain(args=(1,), kwargs={})
    test_expected(pointers[0], (8,))

    ## The chain has ended and we asset the function.
    ## Now bind a new chain onto the end (node c).
    await m.a_connect(nc, add_two, add_two, multiply_by, unique=True)

    latest_pointers, released_pointers = await stepper.run_pointers_dict_recurse(*pointers)
    ## The latest pointers are the current graph; this isn't the same as the
    ## original `pointers`
    #
    ## Released pointers will include the latest pointer, as the recurse
    ## function returns the pointers before failure.

    ## Latest pointers contains one released leaf
    test_expected(latest_pointers, (24,))
    ## Released contains anything unhooked. The previous (8,) and the current (24,)
    test_expected(released_pointers, (8, 24,))

    return m, stepper

"""
# node events

A node may emit an event - this should be collected by a machine or stepper.

If the machine has access a new stepper is spawned and the context is isolated

However a path relative context could occur, where only _steppers_ with the
node within the future path can eventize.
The stepper collects event and moves onward.

## pointer history

To discover the path of a chain, the pointer steps from the origin node
is required. This can be collected similar to the _depth_, with a limit on length
"""


if __name__ == '__main__':
    m, c = main()