"""
The 'Machine' acts as the host for nodes (functions) and connection and spawns
a 'stepper' to walk the graph for function executions.

Functionally the machine doesn't do much - it spawns a stepper and maintains
a list of nodes. All important work offloads into the stepper

    machine = Machine()
    mschine.connect(fa, fb,fc)
    machine.step_chain(1)
"""
from collections import defaultdict
from stepper import Stepper
from node import Node


class Machine(object):
    """The machine maintains the function list and graphs
    """
    def __init__(self, unique_nodes=False):
        self.nodes = {}
        self.connections = defaultdict(tuple)
        self._stepper = None
        self.unique_nodes = unique_nodes

    async def a_connect(self, *items, node_class=None, **node_opts):
        # return self.connect(*items, node_class=node_class, **node_opts)
        node_opts = node_opts or {}
        nodes = ()
        for x in items:
            r  = await self.a_as_node(x, node_class, **node_opts)
            nodes += (r,)

        for i, node in enumerate(nodes):
            if len(nodes) == i+1:
                print(' x no next node')
                continue
            await self.a_bind(node, nodes[i+1])
        return nodes

    def connect(self, *items, node_class=None, **node_opts):
        """Connect nodes in pairs - A -> B.

            connect(func1, func2)

        This will bind nodes the edges for the given functions.
        Assign a node_class to alter the stored function _wrapper_. If an
        item is a node, the same reference is reused.

            >>> connect(node:<Node>, func, func, node_class=Other)
            # node, Other, Other

        Provide many functions to bind a chain without many calls:

            connect(func1,func2, func3, func4, func5, func6)

        Is functionally identical to:

            connect(func1,func2)
            connect(func2, func3)
            connect(func3, func4)
            connect(func4, func5)
            connect(func5, func6)
        """
        # connect A to B
        # na, nb = self.as_node(a), self.as_node(b)
        node_opts = node_opts or {}
        nodes = tuple(self.as_node(x, node_class, **node_opts) for x in items)
        for i, node in enumerate(nodes):
            if len(nodes) == i+1:
                print(' x no next node')
                continue
            self.bind(node, nodes[i+1])
        return nodes

    async def a_first_node(self):
        return self.first_node()

    def first_node(self):
        """Return the _first node_ in the chain. This is done through first
        inserted item of the nodes dict.
        """
        return self.nodes[tuple(self.nodes.keys())[0]]

    async def step_chain(self, *a, **kw):
        """Step the concurrent chain sequence by one iteration. If the existing
        stepper is None, generate a new stepper and initiate.

        The first call requires the expected arguments as the first node.
        After the first call, the given arguments are ignored.

        The `stepper.run_step(...)` performs one step of all waiting pointers.
        """
        # open a new stepper context
        fresh = False
        stepper = self.get_stepper() if fresh is False else self.new_stepper()
        # Program to walk the natural chain
        pointers, losses = await stepper.run_step(*a, **kw)
        await self.print_pointer_losses(pointers, losses)
        if self._stepper is None:
            self._stepper = stepper
        return stepper

    def get_stepper(self, **kw):
        """Return the current stepper or new stepper instance.
        """
        stepper = self._stepper
        if stepper is None:
            print('Making new Stepper')
            stepper = self.new_stepper(**kw)
        else:
            print('Reusing exising stepper')
        return stepper

    async def a_get_stepper(self, **kw):
        """Return the current stepper or new stepper instance.
        """
        stepper = self._stepper
        if stepper is None:
            print('Making new Stepper')
            stepper = await self.a_new_stepper(**kw)
        else:
            print('Reusing exising stepper')
        return stepper

    def new_stepper(self, origin_node=None, **kw):
        """Return a new instance of a Stepper complete with the origin first node
        and a reference to this machine
        """
        origin = origin_node or self.first_node()
        return Stepper(self, origin, **kw)

    async def a_new_stepper(self, origin_node=None, **kw):
        """Return a new instance of a Stepper complete with the origin first node
        and a reference to this machine
        """
        origin = origin_node or await self.a_first_node()
        return Stepper(self, origin, **kw)

    async def start_chain(self, *a, **kw):
        """Get or create a stepper, then run the pointers until completion.
        Return the exausted stepper.
        """
        # Program to walk the natural chain
        # step until death.
        return await self.conf_start_chain(a, kw)

    async def conf_start_chain(self, args, kwargs=None, **stepper_opts):
        kwargs = kwargs or {}
        stepper = await self.a_get_stepper(**stepper_opts)
        pointers, losses = await stepper.run(*args, **kwargs)
        await self.print_pointer_losses(pointers, losses)
        return stepper, (pointers, losses)

    async def print_pointer_losses(self, pointers, losses):
        """Print an output of the current (live) pointers, and pointers released
        at the end of a chain (losses) - the value returned from a `stepper.run`
        or `stepper.run_step`

            stepper = self.get_stepper()
            pointers, losses = stepper.run_step(*a, **kw)
            await self.print_pointer_losses(pointers, losses)

        """
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
        """Insert the twp nodes and connect from a to b using the _node_ `uname()`
        """
        self.insert_node(sender)
        self.insert_node(receiver)
        sn = sender.uname()
        self.connections[sn] += (receiver.uname(),)
        print(f'Updated connections for sender: {sn}', self.connections[sn])

    async def a_bind(self, sender, receiver):
        """Insert the twp nodes and connect from a to b using the _node_ `uname()`
        """
        await self.a_insert_node(sender)
        await self.a_insert_node(receiver)
        sn = sender.uname()
        self.connections[sn] += (receiver.uname(),)
        print(f'Updated connections for sender: {sn}', self.connections[sn])

    def insert_item(self, item, **opts):
        n = self.as_node(item, **opts)
        return self.insert_node(n)

    def insert_node(self, node:Node):
        name = node.uname()
        if name in self.nodes:
            return self.nodes[name]
        print('Insert node', name)
        self.nodes[name] = node
        return node

    async def a_insert_node(self, node:Node):
        return self.insert_node(node)

    def as_node(self, f, node_class=None, **opts):
        opts.setdefault('unique', self.unique_nodes)
            # the node may emit therefore needs the stepper.
        node_class = node_class or self.get_node_class()
        if isinstance(f, node_class):
            return f
        return node_class(f, **opts)

    async def a_as_node(self, f, node_class=None, **opts):
        opts.setdefault('unique', self.unique_nodes)
            # the node may emit therefore needs the stepper.
        node_class = node_class or (await self.a_get_node_class())
        if isinstance(f, node_class):
            return f
        return node_class(f, **opts)

    async def a_get_node_class(self):
        return self.get_node_class()

    def get_node_class(self):
        return Node


    @property
    def C(self):
        return Compound(self)


class Compound(object):

    def __init__(self, machine):
        self.machine = machine
        self._last = None

    def __call__(self, other):
        n = self.insert_node(other)
        if self._last is not None:
            print('connect from', self._last, n)
            self.machine.bind(self._last, n)
        self._last = n
        return n

    def insert_node(self, other):
        return self.machine.insert_item(other)

    def __gt__(self, other):
        print(other)
        return self.machine.as_node(other)