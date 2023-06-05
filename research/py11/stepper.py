from node import Node


class Pointer(object):
    """A Pointer acts as the execution unit for a function, spawn by s spetter
    when required. Being fairly transient, the main feature is calling the
    bound function and offer the next step for the stepper.

        pointer = Pointer(stepper, Node(add_two))
        pointer.run(2)
        # 4
    """
    # Wrap outbound if the value is a simple function result.
    function_wrapper = True

    def __init__(self, stepper, node, parent_pointer=None, index=None):
        self.stepper = stepper
        self.node = node
        self.index = index
        self.history = ()

        depth = 0
        if parent_pointer:
             depth = parent_pointer.depth + 1
             self.history = parent_pointer.history + (index, )
        self.depth = depth

    def uname(self):
        # unique name
        return f"P_{str(id(self))}_{self.depth}"


    def get_next(self, **kw):
        kw.setdefault('depth', self.depth)
        return self.stepper.get_next(self.node, **kw)

    def run(self, *a, **kw):
        #self.result =
        res = self.node.execute(*a, **kw)
        if self.function_wrapper:
            return (res, ), {}
        return res

    def __repr__(self):
        c = self.__class__.__name__
        return f'<{c} {self.uname()} depth={self.depth} index={self.index} for {self.node.fname()}>'


from time import sleep

class Base(object):

    @property
    def pointers(self):
        return tuple(self._stashed_pointers.values())

    def reset(self):
        self._stashed_pointers = None
        self._stashed_lost = {}
        self._complete = 0

    def get_next(self, node, as_index=False, **kw) -> tuple:
        """Return the _next_ node items from the machine through its connections
        """
        name = node.uname()
        next_names = self.machine.connections.get(name, ())
        i_next_names = self.select_next_nodes(node, next_names,
                                         depth=kw.get('depth'),
                                         path=kw.get('path')
                                         )
        return self.resolve_nodes(i_next_names, as_index)

    def select_next_nodes(self, node, names, depth=None, path=None):
        i_conns = tuple( (i, x) for i,x in enumerate(names) )

        print(f'  ? select_next_nodes of {len(names)} - for next of', node)


        if path is None:
            return i_conns

        if depth is None:
            return i_conns

        if len(names) == 0:
            print(f'  x No connections here, cannot select path[{depth=}]')
            return ()

        pos = path[depth]
        print(f'    Selected pathed index: {depth=}, {pos=}')

        try:
            i_conns = (i_conns[pos],)
            print(f'      = {i_conns=}')
        except IndexError as err:
            print(f'  ! Bad Path position "{pos=}" (above): {path}. {len(i_conns)=}', err)
            raise err

        return i_conns

    def resolve_nodes(self, i_conns, as_index=False) -> list: # Node
        items = ()
        for edge_i, n in i_conns:
            item = self.resolve(n)
            if item:
                if as_index:
                    items += ((edge_i, item,),)
                    continue
                items += (item,)

        return items

    def resolve(self, item) -> Node:
        """resolve the live chainable from a class or unname

        Return a Node type
        """
        n = getattr(item, 'unname', lambda: item)()
        existing = self.machine.nodes.get(n, None)
        if isinstance(item, Node):
            return item
        if existing is None:
            print('Could not resolve', item)

        return existing

    def as_pointers(self, nodes, parent_pointer=None, index=None, as_index=False) -> tuple:

        r = ()
        for x in nodes:
            node = x
            if as_index:
                index = x[0]
                node = x[1]

            r += (Pointer(self, node, parent_pointer, index=index),)
        return r
        # return tuple(Pointer(self, x, parent_pointer, index=index) for x in nodes)

    def pppd(self, pointer_dict, *aa):
        """pretty print pointer dictionary
        """
        s = 's' if len(pointer_dict) != 1 else ''
        print(*aa, f'{len(pointer_dict)} pointer{s}')
        for k, v in pointer_dict.items():
            spn  = str(v[0])
            print(f'      | {spn:<60}', v[1])

    def run_nodes(self, nodes, *a, **kw):
        """Convert the nodes to pointers and run the pointers.
        Return the dict result from `run_pointers`.

            {
                name: pointer, ((), {})
            }
        """
        pointers = self.as_pointers(nodes)
        return self.run_pointers(pointers, *a, **kw)

    def run_pointer_next(self, p, v, index=None):
        """Given a pointer an its concurrent value (the last value it returned)
        Find its next node pointers and run.

            run_pointer_next(pointer, ((), {}))
            # get next
            # run many pointers
            # return results dict

        Return a dict of pointers and their results, used for the next iteration.

            {
                name: pointer, ((), {})
            }
        """
        print(f'    Finding next ({index=}) at', p, ' - with last value:', v)
        i_nodes = p.get_next(path=self.path, as_index=True)
        # if index is not None:
        #     nodes = (nodes[index],)
        pointers = self.as_pointers(i_nodes, p, index=index, as_index=True)

        print('  x x PATH REDUCE HERE - using the P+1 index.')
        a, kw = v
        new_pointers_dict = self.run_pointers(pointers, *a, **kw)

        self.pppd(new_pointers_dict, '    new_pointers_dict: ')
        return new_pointers_dict

    def run_pointers(self, pointers, *a, **kw) -> dict:
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


class FlagFunctions(object):

    def flag_complete(self, exit_pointers, stashed_lost):
        """All pointers are complete. The `exit` pointers are the _last_
        nodes of which will not step in the next iteration. The dict
        `stashed_lost` maintains all previously end-released (lost) pointers
        with their last value

        If another iteration occurs without reseting the pointers,  The exit
        pointer will be an empty dict (no nodes in the _last_ iteration see...)

        The _first_ call to this function will call `on_chain_complete_first`.
        All calls thereafter head to `on_chain_complete`. This will reset
        with `stepper.reset()`.
        """
        print('\n\tChain complete\n')
        self._complete += 1

        if self._complete == 1:
            return self.on_chain_complete_first(exit_pointers, stashed_lost)
        return self.on_chain_complete(exit_pointers, stashed_lost)

    def flag_detected_run_empty(self):
        """The last call to the graph did not execute any nodes.
        """
        print('\n    Flat Detect Empty Run. Perform stepper.reset()')

    def on_chain_complete_first(self, exit_pointers, pointer_dict):
        """All chains are ocmplete. This is the first time for this graph all
        has completed.
        """
        print('    on_chain_complete_first', exit_pointers)
        # print('on_chain_complete', pointer_dict)

    def on_chain_complete(self, exit_pointers, pointer_dict):
        print('    on_chain_complete', exit_pointers)
        # print('on_chain_complete', pointer_dict)


class Stepper(Base, FlagFunctions):
    """A unit to handle walking a chain of calls across the graph
    Upon a step the Stepper executes the pointer context
    the pointer executes and returns a result.

    The stepper find the next nodes, proceeds and continues.

    The stepper maintains one context, shared across one to many pointers.
    The pointer runs the node. and yields the result to the stepper of which
    makes a decision to run graph steps.
    """
    def __init__(self, machine, origin, loop_limit=-1, path=None):
        self.machine = machine
        self.origin_node = origin
        self.loop_limit = loop_limit
        self.path = path
        self.reset()

    def run(self, *a, **kw):
        print('Run stepper', a, kw)
        # nodes = (self.origin_node,)
        # pointer_dict = self.run_nodes( nodes, *a, **kw)
        pointer_dict = self.first_run_pointers(*a,**kw)
        n, losses = self.run_pointers_dict_recurse(pointer_dict)
        return n, losses

    def first_run_pointers(self, *a, **kw):
        """Run the nodes starting with the origin node. This expects to first
        run and may reset a concurrent chain.
        """
        return self.run_nodes( (self.origin_node, ), *a, **kw)

    def run_step(self, *a, **kw):
        return self.run_pointers_stashed(*a,**kw)
        # return n, losses

    def run_pointers_dict_recurse(self, pointer_dict, lost_pointer_dict=None, loop_limit=None):
        """Run a pointers dictionary until the chain is released (whilst there
        are future nodes)

        Arguments:
            pointer_dict {dict} -- a conurrent pointers dict

        Returns:
            tuple -- a tuple of _live_ and _released_ pointers.
        """
        pointers = pointer_dict
        lost = lost_pointer_dict or {}
        # n, lost = self.run_pointers_dict(pointer_dict)
        loop = len(pointers) > 0
        count = 0
        _loop_limit = self.loop_limit if loop_limit is None else loop_limit

        while loop:
            count += 1
            # sleep(.3)
            new_pointers, new_lost = self.run_pointers_dict(pointers)
            lost.update(new_lost)

            if len(new_pointers) == 0:
                self.flag_complete(pointers, lost)
                return pointers, lost

            pointers = new_pointers
            ll = count+1 if _loop_limit == -1 else _loop_limit
            loop = len(pointers) > 0 and (count < ll)
            if count >= ll:
                print('Hit Recuse limit.', ll)

        return pointers, lost

    def run_pointers_stashed(self, *first_args, **first_kwargs):
        """Run one step of the _stashed_ pointers. If no stashed pointers
        exist, a first_run_pointers() is used.

        Return a tuple the concurrent, and released pointers
        """
        pointers = self._stashed_pointers
        lost = self._stashed_lost

        if pointers is None:
            print('Using first pointer arguments')
            pointers = self.first_run_pointers(*first_args, **first_kwargs)
            self._stashed_pointers = pointers
            return pointers, lost

        new_pointers, new_lost = self.run_pointers_dict(pointers)
        self._stashed_pointers = new_pointers

        # Update the concurrent lost with the stashed.
        # This will bloat unless the pointer is released.
        lost.update(new_lost)
        self._stashed_lost = lost
        # self._stashed_pointers = pointers
        #
        if len(new_pointers) == 0:
            self.flag_complete(pointers, lost)

        return pointers, lost

    def run_pointers_dict(self, pointer_dict, ):
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

        for i, (pointer, v) in enumerate(pointer_dict.values()):
            c += 1
            new_pointers_dict = self.run_pointer_next(pointer, v, i)
            if len(new_pointers_dict) == 0:
                # the newest call yielded nothing.
                # Cache back for this pointer may be applied.
                lost[pointer.uname()] = pointer, v
            res.update(new_pointers_dict)

        if c == 0:
            self.flag_detected_run_empty()

        return res, lost
