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
        # if index is not None:
        #     nodes = (nodes[index],)
        pointers = self.as_pointers(i_nodes, p, index=index, as_index=True)

        # print('  x x PATH REDUCE HERE - using the P+1 index.')
        a, kw = v
        new_pointers_dict = await self.run_pointers(pointers, *a, **kw)

        await self.pppd(new_pointers_dict, '    new_pointers_dict: ')
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
    merge_mode = True

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

    async def run_merge_pointers_dict_v1(self, pointer_dict):
        """Note 2023/08/06: Seems to be recusive and broken :(

            st 3 :
                (
                 (<Pointer P_49280672_1 depth=1 index=0 for op_add_10>,
                  ((20,), {}),
                  ((0, <N_49288384: add_all>),)),

                 (<Pointer P_49280768_1 depth=1 index=1 for op_sub_5>,
                  ((5,), {}),
                  ((0, <N_49288384: add_all>),)),

                 (<Pointer P_49280864_1 depth=1 index=2 for op_sub_6>,
                  ((4,), {}),
                  ((0, <N_49288384: add_all>),))
                  )

            With an edge, the end node doesn't present the same as other nodes
            Also an edge shouldn't receive the concat params. Instead is should
            receive its unique call. The _result_ is applied to the concat before
            the edge node finalises.

                      Na ------
                in -> Nb ------ -> out
                      Nc - E0 -

            The edge needs an intermediate step, called before the execution.
            The value from the edge call is the result of the stash.

                ((<Pointer P_49170512_1 depth=1 index=0 for op_add_10>,
                  ((20,), {}),
                  ((0, <N_49177792: add_all>),)),
                 (<Pointer P_49170608_1 depth=1 index=1 for op_sub_5>,
                  ((5,), {}),
                  ((0, <N_49177792: add_all>),)),
                 (<Pointer P_49170704_1 depth=1 index=2 for op_sub_6>,
                  ((4,), {}),
                  ((0, <E_N_43513456__N_49177792: N_43513456__N_49177792>),)))

            1. call forward any Edge types, replacing the _edge_ with the edge out node, and the value
            2. This is applied to the stash
            3. then merge args on destination.

            This results in (as shown) 1 pointer to `add_all` with values `(20, 5, 4+e)`.
            `e` is the edge operation

            ---

            if 'merge node'
            1. any edge with a merged designation is called early.
            2. the result stacks into the stash
            3. the pointer owning the current edge is recreate to point at the node,

            *update
            Therefore if 'mergenode' inspect the incoming references for the same name.
            perform the early edges for that node only.
        """

        ## Concat pointers:
        ends = set()

        res = {}
        lost = {}
        c = 0
        pdv = pointer_dict.values()
        noded_pointer_dict = ()
        merge_nodes = defaultdict(tuple)
        merge_edges = defaultdict(tuple)

        for i, (pointer, v) in enumerate(pdv):
            i_nodes = await pointer.get_next(path=self.path, as_index=True)
            new_entry = (pointer, v, i_nodes)
            node = pointer.node

            if isinstance(node, Edge):
                print('is edge')
                # First check if the end node is this node.
                node = node.b

            nn = node.uname()
            ends.add(nn)

            if node.merge_pointers:
                merge_nodes[nn] += (new_entry,)

            noded_pointer_dict += (new_entry,)

        if len(merge_nodes) > 0:
            print('merge_nodes detected')

        if len(ends) != len(noded_pointer_dict):
            # Pointer reduction detected.
            # find edges
            # # if the b node is in the set, then call the edge intermediate
            # function, then stash the result as the same enumeration point.
            print('Detected shared end node usage...')

        # i_nodes = tuple(set(st))

        ## here we need to merge args and kwargs of same destination pointers
        ## Delete any unused pointers.
        print(f'noded_pointer_dict {len(noded_pointer_dict)}:')
        pp(noded_pointer_dict)
        print('------')

        ## next cycle through the merge_nodes stack to gather args/kw
        concat_pointers = ()
        drop_pointers = set()
        for m_name, entries in merge_nodes.items():
            # if an edge, call to the intermediate func
            args_stack = ()
            kwargs_stack = {}

            for pointer, v, i_nodes in entries:
                node = pointer.node
                print('Node:', node)
                if isinstance(node, Edge):
                    nv = await node.run_intermediate(*v[0], **v[1])
                    print('  .. edge.run_intermediate, old', v, 'new:', nv)
                    v = nv
                    node = node.b
                a, kw = v

                args_stack += a
                kwargs_stack.update(kw)
                drop_pointers.add(pointer)

            stack_v = (args_stack, kwargs_stack,)
            nn = await self.resolve(m_name)
            pointers = self.as_pointers([nn], index=pointer.index, parent_pointer=pointer)
            np = pointers[0]
            new_entry = (np, stack_v, i_nodes)
            concat_pointers += (new_entry,)

        print('\n-- concat_pointers:')
        pp(concat_pointers)

        print('\n-- drop_pointers:')
        pp(drop_pointers)

        print('\n-- merge_nodes:')
        pp(merge_nodes)

        print('\n-- noded_pointer_dict:')
        pp(noded_pointer_dict)

        for pointer, v, i_nodes in noded_pointer_dict:
            if pointer in drop_pointers:
                continue
            new_entry = (pointer, v, i_nodes)
            concat_pointers += (new_entry,)

        print('\n-- concat_pointers (finalised?):')
        pp(concat_pointers)
        print('\n')
        # and replace the current pointer with a pointer to the func without edge.
        # pop any pointers in this merge_nodes from the nodes_pointer dict, as
        # those are rewritten as a new pointer with concat args.
        # This should result in a stack of noded_pointer_dict with less pointers

        for i, (pointer, v, i_nodes) in enumerate(concat_pointers):
            c += 1
            a, kw = v
            new_pointers_dict = await self.run_pointers((pointer,), *a, **kw)
            if len(new_pointers_dict) == 0:
                # the newest call yielded nothing.
                # Cache back for this pointer may be applied.
                lost[pointer.uname()] = pointer, v
            res.update(new_pointers_dict)
            print(new_pointers_dict)
        return res, lost

