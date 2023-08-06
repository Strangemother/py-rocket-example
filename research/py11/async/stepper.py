from node import Node
from collections import defaultdict
from pprint import pprint as pp
from edge import Edge

from time import sleep
from motion import StepperMotionMixin
from flag import FlagFunctions
from pointer import Pointer


class Base(object):

    @property
    def pointers(self):
        return tuple(self._stashed_pointers.values())

    def reset(self):
        self._stashed_pointers = None
        self._stashed_lost = {}
        self._complete = 0

    async def get_next(self, node, as_index=False, **kw) -> tuple:
        """Return the _next_ node items from the machine through its connections
        """
        if isinstance(node, Edge):
            node = node.b
        name = node.uname()
        next_names = self.machine.connections.get(name, ())
        # wrap notes or drop edge ends.
        # ## This may need a zip order replacement to ensure edges
        # seat in the same location as the original name...
        # unedged = set(next_names) - set(edge_names)

        i_next_names = await self.select_next_nodes(node, next_names,
                                         depth=kw.get('depth'),
                                         path=kw.get('path')
                                         )

        # Get edges
        edge_names = await self.get_edge_names(name, next_names)

        ni_next_names = ()
        keep = ()
        # swap out edge named nodes for edges
        for i, v in i_next_names:
            if v in edge_names:
                print('Popping edge leaf', v, 'from next_names')

                keep += ( (i, v), )
                continue
            ni_next_names += ( (i, v), )

        edges_list = tuple(x for y in edge_names.values() for x in y)
        nodes = await self.resolve_nodes(ni_next_names, as_index)

        edges = ()
        for i,v in keep:
            edge = edge_names.get(v)
            edges += ( (i, edge[0]), )
        # edges = await self.resolve_edges(edge_name, as_index)
        # print(f'\n  {edges=}')
        # print(f'  {nodes=}\n')

        return nodes + edges

    async def get_edge_names(self, name, next_names):
        # get all edges from A to B.
        edge_names = defaultdict(tuple)

        for nn in next_names:
            en = f'E_{name}__{nn}'
            found = self.machine.edges.get(en, ())
            if len(found) > 0:
                edge_names[nn] += found
        return edge_names

    async def select_next_nodes(self, node, names, depth=None, path=None):
        i_conns = tuple( (i, x) for i,x in enumerate(names) )

        print(f'  ? select_next_nodes of {len(names)} - for next of', node)

        if path is None:
            return i_conns

        if depth is None:
            return i_conns

        if len(names) == 0:
            print(f'  x No connections here, cannot select path[{depth=}]')
            return ()
        try:
            pos = path[depth]
            print(f'    Selected pathed index: {depth=}, {pos=}')
        except IndexError as err:
            print(f'  ! Bad Path depth "{depth=}" (above): {path}. {len(path)}', err)
            raise err

        try:
            i_conns = (i_conns[pos],)
            print(f'      = {i_conns=}')
        except IndexError as err:
            print(f'  ! Bad Path position "{pos=}" (above): {path}. {len(i_conns)=}', err)
            raise err

        return i_conns

    async def resolve_nodes(self, i_conns, as_index=False) -> list: # Node
        items = ()
        for edge_i, n in i_conns:
            item = await self.resolve(n)
            if item:
                if as_index:
                    items += ((edge_i, item,),)
                    continue
                items += (item,)

        return items

    async def resolve_edges(self, i_conns, as_index=False) -> list: # Node
        items = ()
        for edge_i, n in i_conns:
            item = await self.resolve_edge(n)
            if item:
                if as_index:
                    items += ((edge_i, item,),)
                    continue
                items += (item,)

        return items

    async def resolve_edge(self, item) -> Edge:
        """resolve_edge the live chainable from a class or unname

        Return a Edge type
        """
        n = getattr(item, 'unname', lambda: item)()
        existing = self.machine.edges.get(n, None)
        if isinstance(item, Edge):
            return item

        if existing is None:
            print('Could not resolve_edge', item)

        return existing

    async def resolve(self, item) -> Node:
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

    async def pppd(self, pointer_dict, *aa):
        """pretty print pointer dictionary
        """
        s = 's' if len(pointer_dict) != 1 else ''
        print(*aa, f'{len(pointer_dict)} pointer{s}')
        for k, v in pointer_dict.items():
            spn  = str(v[0])
            print(f'      | {spn:<60}', v[1])

    async def run_nodes(self, nodes, *a, **kw):
        """Convert the nodes to pointers and run the pointers.
        Return the dict result from `run_pointers`.

            {
                name: pointer, ((), {})
            }
        """
        pointers = self.as_pointers(nodes)
        return await self.run_pointers(pointers, *a, **kw)

    async def run_pointer_next(self, p, v, index=None, i_nodes=None):
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

        i_nodes = i_nodes or await p.get_next(path=self.path, as_index=True)
        pointers = self.as_pointers(i_nodes, p, index=index, as_index=True)
        a, kw = v
        new_pointers_dict = await self.run_pointers(pointers, *a, **kw)

        # await self.pppd(new_pointers_dict, '    new_pointers_dict: ')
        return new_pointers_dict

    async def run_pointers(self, pointers, *a, **kw) -> dict:
        """Return a dict of single executed pointers `pointer.run`

            {
                name: pointer, ((), {})
            }
        """
        res = {}
        l = len(pointers)
        for i, p in enumerate(pointers):
            print(f'    Running pointer #{i+1}/{l}: {p} with args: {a}')
            v = await p.run(*a, **kw)
            res[p.uname()] = p, v
            # print('storing', v)
        return res


class Stepper(Base, FlagFunctions, StepperMotionMixin):
    """A unit to handle walking a chain of calls across the graph
    Upon a step the Stepper executes the pointer context
    the pointer executes and returns a result.

    The stepper find the next nodes, proceeds and continues.

    The stepper maintains one context, shared across one to many pointers.
    The pointer runs the node. and yields the result to the stepper of which
    makes a decision to run graph steps.
    """
    # merge_mode = True

    def __init__(self, machine, origin, loop_limit=-1, path=None):
        self.machine = machine
        self.origin_node = origin
        self.loop_limit = loop_limit
        self.path = path
        self.reset()

    async def run(self, *a, **kw):
        print('Run stepper', a, kw)
        # nodes = (self.origin_node,)
        # pointer_dict = self.run_nodes( nodes, *a, **kw)
        pointer_dict = await self.first_run_pointers(*a,**kw)
        n, losses = await self.run_pointers_dict_recurse(pointer_dict)
        return n, losses

    async def first_run_pointers(self, *a, **kw):
        """Run the nodes starting with the origin node. This expects to first
        run and may reset a concurrent chain.
        """
        return await self.run_nodes( (self.origin_node, ), *a, **kw)

    async def run_step(self, *a, **kw):
        # return n, losses
        return await self.run_pointers_stashed(*a,**kw)

    async def run_pointers_stashed(self, *first_args, **first_kwargs):
        """Run one step of the _stashed_ pointers. If no stashed pointers
        exist, await a first_run_pointers() is used.

        Return a tuple the concurrent, and released pointers
        """
        pointers = self._stashed_pointers
        lost = self._stashed_lost

        if pointers is None:
            print('Using first pointer arguments')
            pointers = await self.first_run_pointers(*first_args, **first_kwargs)
            self._stashed_pointers = pointers
            return pointers, lost

        new_pointers, new_lost = await self.run_pointers_dict(pointers)
        self._stashed_pointers = new_pointers

        # Update the concurrent lost with the stashed.
        # This will bloat unless the pointer is released.
        lost.update(new_lost)
        self._stashed_lost = lost
        # self._stashed_pointers = pointers
        #
        if len(new_pointers) == 0:
            await self.flag_complete(pointers, lost)

        return pointers, lost
