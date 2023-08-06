import inspect
from node import Node


class Edge(Node):

    prefix = 'E_'

    def __init__(self, a, b, func=None, unique=False):
        self._nodes = a,b
        self._func = self.anon
        self.unique = unique
        self._tap_functions = ()

    @property
    def name(self):
        n = self._nodes
        return f"{n[0].uname()}__{n[1].uname()}"

    @property
    def a(self):
        return self._nodes[0]

    @property
    def b(self):
        return self._nodes[1]


    async def anon(self, *a, **kw):
        print(f' == Edge.anon: {self} called with:', a, kw)
        return await self.run_all(*a, **kw)

    async def run_all(self, *a, **kw):
        na, nkw = await self.run_intermediate(*a, **kw)
        return await self.execute_node(*na, **nkw)

    async def run_intermediate(self, *a, **kw):
        na, nkw = await self.tap_function(a, kw)
        return na, nkw

    async def execute_node(self, *a, **kw):
        return await self._nodes[1].execute(*a, **kw)

    async def add_tap(self, f):
        self._tap_functions += (f, )

    async def tap_function(self, a, kw):
        # print('Node.execute', self, 'with', a, kw)
        taps = self._tap_functions
        na, nkw = a, kw
        for f in taps:
            if inspect.iscoroutinefunction(f):
                na, nkw = await f(*self._nodes, self, *na, **nkw)
            na, knw = f(*self._nodes, self, *na, **nkw)
        return na, nkw

    def fname(self):
        return self.name

    def uname(self):
        # unique name
        n = id(self)
        us = f'_{n}' if self.unique else ''
        return f'{self.prefix}{self.name}{us}'
