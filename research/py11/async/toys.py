import operator



async def add_two(a, b=2):
    return a + b

async def add_10(a, b=10):
    return a + b

async def minus_3(a, b=3):
    return a - b

async def minus_6(a):
    return await minus_3(a,6)


async def multiply_by(a, b=2):
    return a * b


async def div_2(a, b=.5):
    return a * b


def op(k='add', b=1):

    async def f(a):
        return getattr(operator, k)(a, b)

    f.__name__ = f'op_{k}_{b}'
    return f


async def void(*a, **kw):
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

