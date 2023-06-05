import operator
from time import sleep

from machine import Machine



def main():
    funcs = (
        run_chain_run_one2one,
        run_chain_concat_4_branch,
        run_chain_step_once,
        run_chain_concat,
        run_chain_arrow,
        run_chain_6_infinite,
        run_chain_6_limited,
        run_chain_path,
    )

    v = None
    for func in funcs:
        # sleep(.2)
        v = func()

    return v

def add_two(a, b=2):
    return a + b

def add_10(a, b=10):
    return a + b

def minus_3(a, b=3):
    return a - b

def minus_6(a):
    return minus_3(a,6)


def multiply_by(a, b=2):
    return a * b


def div_2(a, b=.5):
    return a * b


def op(k='add', b=1):

    def f(a):
        return getattr(operator, k)(a, b)

    f.__name__ = f'op_{k}_{b}'
    return f


def void(*a, **kw):
    print(f'\n\nVoid Called {a} {kw}\n\n')
    return a[0]


opadd_10 = op('add', 10)
sub_6 = op('sub', 6)
add_5 = op('add', 5)
add_4 = op('add', 4)
add_12 = op('add', 12)
opadd_10_2 = op('add', 10)
op_add_10_2 = opadd_10_2

from unittest import TestCase

def test_expected(pointers, expected):
    """
        pointers_current, pr = stepper.run_step(1)
        pointers_current, pr = stepper.chain(1)

        test_expected(pointers_current, (1,2,3))
    """
    res = pargs(pointers)
    # print(res == expected, res)
    return sequence_match_test(res, expected)


def sequence_match_test(res, expected, sort=True, as_type=None):
    through = lambda x:x
    s = sorted if sort else through
    as_type = as_type or through

    def c(d):
        d = as_type(d)
        return s(d)

    return TestCase().assertEqual(c(res), c(expected))


def pargs(pointers):
    d = pointers

    if isinstance(d, tuple):
        d = pointers[1]

    return tuple(x[1][0][0] for x in d.values())


def run_chain_run_one2one():

    m = Machine()
    m.connect(add_two, multiply_by)
    # m.connect(add_two, add_10)
    m.connect(multiply_by, minus_3)
    m.connect(minus_3, opadd_10)
    m.connect(minus_3, div_2)
    m.connect(div_2, sub_6)
    m.connect(div_2, add_5)
    m.connect(add_5, add_12)
    # m.connect(minus_3, void)
    m.connect(opadd_10, void)
    m.connect(opadd_10, op_add_10_2)
    m.connect(op_add_10_2, op('add', 10))

    stepper, pointers = m.start_chain(1)
    # stepper = m.step_chain(1)

    expected = (-4.5, 13, 18.5, 33)
    test_expected(pointers, expected)
    return m, stepper


def run_chain_concat_4_branch():

    m = Machine()
    m.connect(add_two, multiply_by, minus_3, opadd_10, op_add_10_2, op('add', 10))
    m.connect(minus_3, div_2, sub_6)
    m.connect(div_2, add_12)
    m.connect(opadd_10, void)

    stepper, pointers = m.start_chain(1)

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


def run_chain_step_once():

    m = Machine()
    m.connect(add_two, multiply_by, minus_3, opadd_10, op_add_10_2, div_2)
    m.connect(minus_3, div_2, sub_6)
    m.connect(div_2, add_12, sub_6)
    m.connect(div_2, void)
    m.connect(op_add_10_2, op('add', 4))
    m.connect(op('add', 4), op('mul', 2))

    # c = m.step_chain(1)
    stepper = m.get_stepper()

    pc, pr = stepper.run_step(1)
    test_expected(pc, (3,))

    return m, stepper


def run_chain_concat():

    m = Machine()
    m.connect(add_two, multiply_by, minus_3, opadd_10, op_add_10_2, div_2)
    m.connect(minus_3, div_2, sub_6)
    m.connect(div_2, add_12, sub_6)
    m.connect(div_2, void)
    m.connect(op_add_10_2, op('add', 4))
    m.connect(op('add', 4), op('mul', 2))


    # stepper = m.get_stepper()
    # pc, pr = stepper.run_step(1)

    stepper, pc = m.start_chain(1)[1]
    test_expected(pc, [-4.5, 1.5, 5.5, 7.5, 11.5, 17.5, 27])

    return m, stepper


def run_chain_arrow():

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

    stepper, pc = m.start_chain(1)
    c = pc[1]

    test_expected(pc,  [41])

    return m, stepper


def run_chain_path():

    m = Machine()
    na, nb, nc = m.connect(add_two, multiply_by, add_two, unique=True)
    _, nd = m.connect(nb, add_4, unique=True) # 10
    _, n_add10 = m.connect(nb, opadd_10, unique=True) # 16
    _, nf = m.connect(n_add10, add_5, unique=True) # 21
    _, ng = m.connect(n_add10, minus_6, unique=True) # 10
    _, ng = m.connect(n_add10, sub_6, unique=True)

    ## subtract is flipped - likely all operators occur this way.

    stepper, pc = m.start_chain(1)
    c = pc[1]
    expected = [8, 10, 21, 10, 10]
    test_expected(pc,  expected)

    res = {}

    path = [0, 0]
    stepper1, pc = m.conf_start_chain(args=(1,), path=path)
    res[0] = pargs(pc)

    path = [0, 1]
    stepper2, pc = m.conf_start_chain(args=(1,), path=path)
    res[1] = pargs(pc)


    path = [0, 2, 1]
    stepper4, pc = m.conf_start_chain(args=(1,), path=path)
    res[3] = pargs(pc)

    path = [0, 2, 2]
    stepper5, pc = m.conf_start_chain(args=(1,), path=path)
    res[4] = pargs(pc)

    path = [0, 2, 0]
    stepper3, pc = m.conf_start_chain(args=(1,), path=path)
    res[2] = pargs(pc)

    p = tuple(pc[0].values())[0][0]
    sequence_match_test(p.history, path, sort=False, as_type=tuple)

    c = pc
    # test_expected(pc,  [8, 10, 21, 10, 10])
    result_values = tuple(x[0] for x in res.values())

    sequence_match_test(result_values, expected)
    return m, c# stepper


def run_chain_6_infinite():

    m = Machine()
    m.connect(add_two, multiply_by, add_two)

    stepper, pointers = m.conf_start_chain(args=(1,), kwargs={}, loop_limit=6)
    test_expected(pointers[0], (38,))

    return m, stepper


def run_chain_6_limited():

    m = Machine()

    # 1, +2, *3, +2 == 8
    # (1 + 2) * 2 + 2
    na, nb, nc = m.connect(add_two, multiply_by, add_two, unique=True)

    stepper, pointers = m.conf_start_chain(args=(1,), kwargs={})
    test_expected(pointers[0], (8,))

    ## The chain has ended and we asset the function.
    ## Now bind a new chain onto the end (node c).
    m.connect(nc, add_two, add_two, multiply_by, unique=True)

    latest_pointers, released_pointers = stepper.run_pointers_dict_recurse(*pointers)
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

from pprint import pprint as pp

if __name__ == '__main__':
    m, c = main()