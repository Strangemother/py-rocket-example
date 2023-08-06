

class Pointer(object):
    """A Pointer acts as the execution unit for a function, spawn by a stepper
    when required. Being fairly transient, the main feature is calling the
    bound function and offer the next step for the stepper.

        pointer = Pointer(stepper, Node(add_two))
        pointer.run(2)
        # 4
    """
    # Wrap outbound if the value is a simple function result.
    function_wrapper = True

    def __init__(self, stepper, node, parent_pointer=None, index=None, function_wrapper=True):
        self.stepper = stepper
        self.node = node
        self.index = index
        self.history = ()
        self.function_wrapper = function_wrapper

        depth = 0
        if parent_pointer:
             depth = parent_pointer.depth + 1
             self.history = parent_pointer.history + (index, )
        self.depth = depth

    def uname(self):
        # unique name
        return f"P_{str(id(self))}_{self.depth}"

    async def get_next(self, **kw):
        kw.setdefault('depth', self.depth)
        return await self.stepper.get_next(self.node, **kw)

    async def run(self, *a, **kw):
        #self.result =
        res = await self.node.execute(*a, **kw)
        return await self.format_outbound_args(res)

    async def format_outbound_args(self, result):

        if isinstance(result, tuple) and result[0] is Ellipsis:
            return result[1:]

        if self.function_wrapper:
            return (result, ), {}

        return res

    def __repr__(self):
        c = self.__class__.__name__
        t = self.node.__class__.__name__
        return f'<{c} {self.uname()} depth={self.depth} index={self.index} for {t}({self.node.fname()})>'

