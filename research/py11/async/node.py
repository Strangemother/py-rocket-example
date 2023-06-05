import inspect

class Node(object):
    """An entity on the chain, caring for the function
    """
    def __init__(self, func, unique=False):

        self._func = func
        self.unique = unique

    def uname(self):
        # unique name
        n = id(self)
        us = f'_{n}' if self.unique else ''
        return f'N_{str(id(self._func))}{us}'

    def fname(self):
        return self._func.__name__

    async def execute(self, *a, **kw):
        # print('Node.execute', self, 'with', a, kw)
        f = self._func
        if inspect.iscoroutinefunction(f):
            return await f(*a, **kw)
        return f(*a, **kw)

    def __str__(self):
        return f'<Node "{self.uname()}": {self.fname()}>'

    def __repr__(self):
        return f'<{self.uname()}: {self.fname()}>'

    def __gt__(self, other):
        return self.__class__(other)

    def __name__(self):
        return self.uname()