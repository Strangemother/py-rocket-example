
class FailureExample(object):

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
