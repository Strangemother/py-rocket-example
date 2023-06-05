"""

NOdes are transparent,
Functions load with optional connections
The graph is maintained within the machine
The stepper holds context for many pointers.

A stepper forks and moves events
The pointer manages execution of the node and pushes events
The node manages the function call and expected IO
"""
import operator


def main():
    return run_chain()


def add_two(a, b=2):
    return a + b


def add_10(a, b=10):
    return a + b


def minus_3(a, b=3):
    return a - b


def multiply_by(a, b=2):
    return a * b


def div_2(a, b=.5):
    return a * b


def op(k='add', a=1):
    def f(b):
        return getattr(operator, k)(a, b)

    f.__name__ = f'op_{k}_{a}'
    return f


opadd_10 = op('add', 10)
sub_6 = op('sub', 6)
add_5 = op('add', 5)
add_12 = op('add', 12)
opa2 = op('add', 10)

def run_chain():

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
    m.connect(opadd_10, opa2)
    m.connect(opa2, op('add', 10))

    m.start_chain(1)
    return m


def run_chain():

    m = Machine()
    m.connect(add_two, multiply_by, minus_3, opadd_10, opa2, op('add', 10))
    m.connect(minus_3, div_2, sub_6)
    m.connect(div_2, add_12)
    m.connect(opadd_10, void)

    c = m.start_chain(1)
    return m, c


def _run_chain():

    m = Machine()
    m.connect(add_two, multiply_by, minus_3, opadd_10, opa2, div_2)
    m.connect(minus_3, div_2, sub_6)
    m.connect(div_2, add_12, sub_6)
    m.connect(div_2, void)
    m.connect(opa2, op('add', 4))
    m.connect(op('add', 4), op('mul', 2))

    # c = m.step_chain(1)
    c = m.get_stepper()

    return m, c


def void(*a, **kw):
    print(f'\n\nVoid Called {a} {kw}\n\n')
    return a[0]


class Node(object):
    """An entity on the chain, caring for the function
    """
    def __init__(self, func):
        self._func = func

    def uname(self):
        # unique name
        return f'N_{str(id(self._func))}'

    def execute(self, *a, **kw):
        # print('Node.execute', self, 'with', a, kw)
        return self._func(*a, **kw)

    def __str__(self):
        return f'<Node "{self.uname()}": {self._func.__name__}>'

    def __repr__(self):
        return f'<{self.uname()}: {self._func}>'


from pprint import pprint as pp

from collections import defaultdict


class Machine(object):
    """The machine maintains the function list and graphs
    """
    def __init__(self):
        self.nodes = {}
        self.connections = defaultdict(tuple)
        self._stepper = None

    def connect(self, *items):
        # connect A to B
        # na, nb = self.as_node(a), self.as_node(b)
        nodes = tuple(self.as_node(x) for x in items)
        for i, node in enumerate(nodes):
            if len(nodes) == i+1:
                print(' x no next node')
                continue
            self.bind(node, nodes[i+1])

    def first_node(self):
        return self.nodes[tuple(self.nodes.keys())[0]]

    def step_chain(self, *a, **kw):
        # open a new stepper context
        fresh = False
        stepper = self.get_stepper() if fresh is False else self.new_stepper()
        # Program to walk the natural chain
        pointers, losses = stepper.run_step(*a, **kw)
        self.print_pointer_losses(pointers, losses)
        if self._stepper is None:
            self._stepper = stepper
        return stepper

    def get_stepper(self):
        stepper = self._stepper
        if stepper is None:
            print('Making new Stepper')
            stepper = self.new_stepper()
        else:
            print('Reusing exising stepper')
        return stepper

    def new_stepper(self):
        origin = self.first_node()
        return Stepper(self, origin)

    def start_chain(self, *a, **kw):
        """Get or create a stepper, then run the pointers until completion.
        Return the exausted stepper.
        """
        stepper = self.get_stepper()
        # Program to walk the natural chain
        # step until death.
        pointers, losses = stepper.run(*a, **kw)
        self.print_pointer_losses(pointers, losses)
        return stepper, (pointers, losses)

    def print_pointer_losses(self, pointers, losses):
        print('\n- pointers -')
        for name, (pointer, values) in pointers.items():
            # Each item is an end result of the chain
            print('>  ', name, values)

        print('- complete -')
        for name, (pointer, values) in losses.items():
            # Each item is an end result of the chain
            print('>> ', name, values)
        print(' ')

    def bind(self, sender, receiver):
        """Insert the nodes and connect from a to b
        """
        self.insert_unit(sender)
        self.insert_unit(receiver)
        sn = sender.uname()
        self.connections[sn] += (receiver.uname(),)
        print(f'Updated connections for sender: {sn}', self.connections[sn])

    def insert_unit(self, unit):
        name = unit.uname()
        if name in self.nodes:
            return
        print('Insert unit', name)
        self.nodes[name] = unit

    def as_node(self, f):
        if isinstance(f, Node):
            return f
        return Node(f)


class Pointer(object):

    # Wrap outbound if the value is a simple function result.
    function_wrapper = True

    def __init__(self, stepper, node, parent_pointer=None):
        self.stepper = stepper
        self.node = node

    def uname(self):
        # unique name
        return f"P_{str(id(self))}"


    def get_next(self):
        return self.stepper.get_next(self.node)

    def run(self, *a, **kw):
        #self.result =
        res = self.node.execute(*a, **kw)
        if self.function_wrapper:
            return (res, ), {}
        return res

    def __repr__(self):
        c = self.__class__.__name__
        return f'<{c} {self.uname()} for {self.node}>'


from time import sleep


class Stepper(object):
    """A unit to handle walking a chain of calls across the graph
    Upon a step the Stepper executes the pointer context
    the pointer executes and returns a result.

    The stepper find the next nodes, proceeds and continues.

    The stepper maintains one context, shared across one to many pointers.
    The pointer runs the node. and yields the result to the stepper of which
    makes a decision to run graph steps.
    """
    def __init__(self, machine, origin):
        self.machine = machine
        self.origin_node = origin
        self.reset()

    @property
    def pointers(self):
        return tuple(self._stashed_pointers.values())

    def run(self, *a, **kw):
        print('Run stepper', a, kw)
        # nodes = (self.origin_node,)
        # pointer_dict = self.run_nodes( nodes, *a, **kw)
        pointer_dict = self.first_run_pointers(*a,**kw)
        n, losses = self.run_pointers_dict_recurse(pointer_dict)
        return n, losses

    def reset(self):
        self._stashed_pointers = None
        self._stashed_lost = {}
        self._complete = 0

    def run_step(self, *a, **kw):
        print('Run single stepper', a, kw)
        n, losses = self.run_pointers_stashed(*a,**kw)
        # pp(losses)
        return n, losses

    def run_pointers_stashed(self, *first_args, **first_kwargs):
        sp = self._stashed_pointers

        if sp is None:
            print('Using first pointer arguments')
            sp = self.first_run_pointers(*first_args, **first_kwargs)
            self._stashed_pointers = sp
            return self._stashed_pointers, self._stashed_lost

        n, lost = self.run_pointers_dict(sp)
        self._stashed_pointers = n
        if len(n) == 0:
            print('    .. no where to go', sp)
            self.flag_complete(sp, self._stashed_lost)
        self._stashed_lost.update(lost)
        return self._stashed_pointers, self._stashed_lost

    def flag_complete(self, exit_pointers, stashed_lost):
        print('\n\tChain complete\n')
        self._complete += 1

        if self._complete == 1:
            return self.on_chain_complete_first(exit_pointers, stashed_lost)
        return self.on_chain_complete(exit_pointers, stashed_lost)

    def flag_detected_run_empty(self):
        print('\n    Empty run. Perform stepper.reset()')

    def on_chain_complete_first(self, exit_pointers, pointer_dict):
        print('    on_chain_complete_first', exit_pointers)
        # print('on_chain_complete', pointer_dict)

    def on_chain_complete(self, exit_pointers, pointer_dict):
        print('    on_chain_complete', exit_pointers)
        # print('on_chain_complete', pointer_dict)

    def first_run_pointers(self, *a, **kw):
        return self.run_nodes( (self.origin_node, ), *a, **kw)

    def run_pointers_dict_recurse(self, pointer_dict):
        n, lost = self.run_pointers_dict(pointer_dict)
        print('First losses', lost)

        while len(n) > 0:
            # print(f'    Stepping because n>0 (=={len(n)})')
            sleep(.4)
            nv, nlost = self.run_pointers_dict(n)
            lost.update(nlost)
            if len(nv) == 0:
                print('.. end of branch', n)
                return n, lost
            n = nv
            # print('    losses; ', lost)
        return n, lost

    def pppd(self, pointer_dict, *aa):
        s = 's' if len(pointer_dict) != 1 else ''
        print(*aa, f'{len(pointer_dict)} pointer{s}')
        for k, v in pointer_dict.items():
            spn  = str(v[0])
            print(f'      | {spn:<60}', v[1])

    def run_pointers_dict(self, pointer_dict):
        """
        Given a pointers dict, return a `pointer, losses` tuple

        the dict value is the `pointer` and a tuple of args, kwargs
        from the previous call - ready for the next call.

            {
                123: (pointer, ((1 ), {},))
                124: (pointer, ((10), {},))
            }
        """
        self.pppd(pointer_dict, '    Stepper.run_pointers_dict with')
        # Unpack pointers into many sub pointers.
        # Then run pointer (results pointer_dict)

        res = {}
        lost = {}
        c = 0
        for i, (p, v) in enumerate(pointer_dict.values()):
            c += 1
            print('    Finding next at', p, ' - with last value:', v)
            nodes = p.get_next()
            # Generate new pointer from the current
            pointers = tuple(Pointer(self, x, p) for x in nodes)
            a, kw = v
            new_pointers_dict = self.run_pointers(pointers, *a, **kw)
            self.pppd(new_pointers_dict, '    new_pointers_dict: ')
            if len(new_pointers_dict) == 0:
                # the newest call yielded nothing.
                # Cache back for this pointer may be applied.
                lost[p.uname()] = p, v
            res.update(new_pointers_dict)

        if c == 0:
            self.flag_detected_run_empty()
        # print('Losses', lost)
        return res, lost

    def as_pointers(self, nodes, parent_pointer=None):
        return tuple(Pointer(self, x, parent_pointer) for x in nodes)

    def run_nodes(self, nodes, *a, **kw):
        """Convert the nodes to pointers and run the pointers.
        Return the dict result from `run_pointers`.

            {
                name: pointer, ((), {})
            }
        """
        pointers = self.as_pointers(nodes)
        return self.run_pointers(pointers, *a, **kw)

    def run_pointers(self, pointers, *a, **kw):
        """Return a dict of single executed pointers `pointer.run`

            {
                name: pointer, ((), {})
            }
        """
        res = {}
        l = len(pointers)
        for i, p in enumerate(pointers):
            print(f'    Running pointer #{i+1}/{l}: {p}')
            v = p.run(*a, **kw)
            res[p.uname()] = p, v
            # print('storing', v)
        return res

    def get_next(self, node):
        name = node.uname()
        conns = self.machine.connections.get(name, ())
        print(f'    ? Found {len(conns)} for next of', name)
        items = ()
        for n in conns:
            item = self.resolve(n)
            items += (item,) if item else ()
        return items

    def resolve(self, item):
        """resolve the live chainable from a class or unname
        """
        n = getattr(item, 'unname', lambda: item)()
        existing = self.machine.nodes.get(n, None)
        if isinstance(item, Node):
            return item
        if existing is None:
            print('Could not resolve', item)

        return existing

if __name__ == '__main__':
    m, c = main()