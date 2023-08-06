"""The primary mixin and function for running a stepper position.
"""
from collections import defaultdict
from pprint import pprint as pp
from edge import Edge

## Looks like it is replaed by DefaultMotion
# class MergePointerMotion(object):

#     async def alpha_merge_pointers_dict(self, pointer_dict):
#         c = 0
#         res = {}
#         lost = {}
#         pdv = pointer_dict.values()
#         for i, (pointer, v) in enumerate(pdv):

#             c += 1
#             new_pointers_dict = await self.run_pointers_next(pointers, v, i, i_nodes)
#             # i_nodes = await pointer.get_next(path=self.path, as_index=True)
#             # pointers = self.as_pointers(i_nodes, pointer, index=i, as_index=True)
#             # a, kw = v
#             # new_pointers_dict = await self.run_pointers(pointers, *a, **kw)

#             if len(new_pointers_dict) == 0:
#                 lost[pointer.uname()] = pointer, v

#             res.update(new_pointers_dict)

#         if c == 0:
#             await self.flag_detected_run_empty()
#         return res, lost


class DebugTools(object):

    def debug_printout(self, merge_nodes, pointer_dict, re_nodes):
        print('\n -- merge_nodes (concats):')
        pp(dict(merge_nodes))
        print('\n -- pointer_dict (orig):')
        pp(pointer_dict)
        print('\n -- re_nodes (new):')
        pp(dict(re_nodes))
        print('--')

    def io_print(self, iters, res, prefix=''):
        print(f'\n - IO - {prefix} (given):')
        pp(iters)
        print(f'\n - IO - {prefix} (result):')
        pp(res)


class MergeModePointerMotion(DebugTools):

    async def run_merge_pointers_dict(self, pointer_dict):
        """The `run_merge_pointers_dict_v2` function accepts a {pointer,(a,kw)}
        dict to execute the pointers through the chain.

        For this method, if a `merge_mode` node recieves calls from many nodes
        within the same frame, the argument pack is concatented into one call -
        merging many calls into a single:

                    -> -5  -> 5  >
            in (10) -> +10 -> 20 -- merge ->  sum (29)
                    -  -6  -> 4  >

        Instead of:


                    -> -5  -> 5  --> sum (5)
            in (10) -> +10 -> 20 --> sum (20)
                    -  -6  -> 4  --> sum (4)

        ---

        Internally the method performs:

        1. Given the pointers, decorate with the _next nodes_ and (next node) count
        2. Reindex froma tuple of pointer names, to sets of destination node name
        3. Convert to runnable shapes by flattening the pointers list to flat args
        4. Run the converted list and gather the _next_ pointers
        5. Announce any empty flags
        6. Build thick objects of pointer calls, concatenated on the (future) node name
        7. convert the thick objects to a pointers dict shape.
        8. return the converted pointer dict

        """
        c, triples_dict = await self.append_next_nodes(pointer_dict)
        # self.io_print(pointer_dict, triples_dict, 'run_merge_pointers_dict_v2')
        concat_triples = self.concat_on_next_node(triples_dict) if triples_dict else {}
        # self.debug_printout(triples_dict, pointer_dict, concat_triples)
        pointer_triples = self.flatten_destination_params(concat_triples, keep_next=True)
        pointer_list = tuple(pointer_triples.values())
        next_pointer_dict, lost = await self._run_active_next_pointers(pointer_list)

        if c == 0:
            await self.flag_detected_run_empty()

        concatenated_pointers = self.concat_on_pointer_node_name(next_pointer_dict)
        res_pointer_dict = self.shape_as_pointers_dict(concatenated_pointers)

        # self.io_print(next_pointer_dict, res_pointer_dict, 'run_merge_pointers_dict_v2 end')
        return res_pointer_dict, lost

    async def append_next_nodes(self, pointer_dict):
        """ populate the pointer next nodes.

                given:

                    {'P_49900464_0': (<Pointer P_49900464_0 depth=0 index=None for Node(in_node)>,
                                      ((10,), {}))}

                returns:

                    {'P_49900464_0': ((<Pointer P_49900464_0 depth=0 index=None for Node(in_node)>,
                                       ((10,), {}),
                                       ((0, <N_49926496: op_add_10>),
                                        (1, <N_49926352: op_sub_5>),
                                        (2, <N_45831360: op_sub_6>))),)}

                calling forward may yield next_nodes for individual pointers:

                given:

                    {'P_50273728_1': (<Pointer P_50273728_1 depth=1 index=0 for Node(op_add_10)>,
                                      ((20,), {})),
                     'P_50273776_1': (<Pointer P_50273776_1 depth=1 index=1 for Node(op_sub_5)>,
                                      ((5,), {})),
                     'P_50273824_1': (<Pointer P_50273824_1 depth=1 index=2 for Node(op_sub_6)>,
                                      ((4,), {}))}

                returns:

                    {'P_50273728_1': ((<Pointer P_50273728_1 depth=1 index=0 for Node(op_add_10)>,
                                       ((20,), {}),
                                       ((0, <N_49926640: add_all>),)),),
                     'P_50273776_1': ((<Pointer P_50273776_1 depth=1 index=1 for Node(op_sub_5)>,
                                       ((5,), {}),
                                       ((0, <N_49926640: add_all>),)),),
                     'P_50273824_1': ((<Pointer P_50273824_1 depth=1 index=2 for Node(op_sub_6)>,
                                       ((4,), {}),
                                       ((0, <N_49926640: add_all>),)),)}

                If the node destination is a 'merge' mode, the result name may be a node
                not a pointer.

                given :

                    {'P_50486624_2': (<Pointer P_50486624_2 depth=2 index=0 for Node(add_all)>,
                                  ((29,), {}))}

                    # ? select_next_nodes of 0 - for next of <Node "N_49926640": add_all>

                returns:

                    {'N_49926640': ((<Pointer P_50486624_2 depth=2 index=0 for Node(add_all)>,
                                 ((29,), {}),
                                 ()),)}
        """
        pop_orig = pointer_dict.copy()
        merge_nodes = defaultdict(tuple)
        count = 0

        for i, (pointer, a_kw) in enumerate(pointer_dict.values()):
            count += 1
            next_nodes = await pointer.get_next(path=self.path, as_index=True)
            new_entry = (pointer, a_kw, next_nodes)

            #? First check if the end node is this node.
            node = pointer.node
            node = node.b if isinstance(node, Edge) else node

            node_uname = node.uname()
            pointer_uname = pointer.uname()

            use_name = node_uname if node.merge_pointers else pointer_uname
            merge_nodes[use_name] += (new_entry,)
            pop_orig.pop(pointer_uname)

        assert len(pop_orig) == 0, 'Pointers missed during merge.'
        return count, dict(merge_nodes)

    def concat_on_next_node(self, triples_dict):
        """
            Pointers (given):

                {'P_49835264_1': ((<Pointer P_49835264_1 depth=1 index=2 for Node(op_sub_6)>,
                                   ((4,), {}),
                                   ((0, <N_49861248: add_all>),)),),
                 'P_49835312_1': ((<Pointer P_49835312_1 depth=1 index=1 for Node(op_sub_5)>,
                                   ((5,), {}),
                                   ((0, <N_49861248: add_all>),)),),
                 'P_49835360_1': ((<Pointer P_49835360_1 depth=1 index=0 for Node(op_add_10)>,
                                   ((20,), {}),
                                   ((0, <N_49861248: add_all>),)),)}

            Pointers (result):

                {'N_49861248': ((<Pointer P_49835360_1 depth=1 index=0 for Node(op_add_10)>,
                                 ((20,), {}),
                                 ((0, <N_49861248: add_all>),)),
                                (<Pointer P_49835312_1 depth=1 index=1 for Node(op_sub_5)>,
                                 ((5,), {}),
                                 ((0, <N_49861248: add_all>),)),
                                (<Pointer P_49835264_1 depth=1 index=2 for Node(op_sub_6)>,
                                 ((4,), {}),
                                 ((0, <N_49861248: add_all>),)))}
        """
        # recombobulate the the merged into a pointer dict shape, merging
        # args
        triples_res = defaultdict(tuple)
        # print('\nMerging Nodes')
        for pointer_name, pointer_set in triples_dict.items():

            all_kw = {}
            all_args = ()
            all_next_nodes = ()
            all_pointers = ()

            for (pointer, (a,kw), next_nodes) in pointer_set:
                _pointers, (a, kw) = self._pull_edge(pointer, *a, **kw)
                all_pointers += _pointers
                all_args += a
                all_kw.update(kw)
                all_next_nodes += next_nodes

            clean_next_nodes = tuple(set(all_next_nodes))
            new_pointer = all_pointers[0]
            new_entry = (new_pointer, (all_args, all_kw,), clean_next_nodes)

            node_or_pointer_name = pointer_name
            try:
                node_or_pointer_name = clean_next_nodes[0][1].uname()
                # print(' -- concat on', node_or_pointer_name)
            except IndexError:
                print(' xx Cannot concat on future node name')

            triples_res[node_or_pointer_name] += (new_entry,)

        # self.io_print(dict(triples_dict), dict(re_nodes), 'concat_on_next_node')
        return triples_res

    def flatten_destination_params(self, triples_dict, keep_next=True):
        """
            given

                {'N_49922688': ((<Pointer P_49896848_1 depth=1 index=0 for Node(op_add_10)>,
                                 ((20,), {}),
                                 ((0, <N_49922688: add_all>),)),
                                (<Pointer P_49896752_1 depth=1 index=1 for Node(op_sub_5)>,
                                 ((5,), {}),
                                 ((0, <N_49922688: add_all>),)),
                                (<Pointer P_49896800_1 depth=1 index=2 for Node(op_sub_6)>,
                                 ((4,), {}),
                                 ((0, <N_49922688: add_all>),)))}

            result

                {'N_49922688': (<Pointer P_49896800_1 depth=1 index=2 for Node(op_sub_6)>,
                                ((20, 5, 4), {}))}

            if keep_next is True

                {'N_49922688': (<Pointer P_49896800_1 depth=1 index=2 for Node(op_sub_6)>,
                                ((20, 5, 4), {}),
                                 ((0, <N_49922688: add_all>),)}

        """
        pointer_dict = {}
        for node_uname, pointer_list in triples_dict.items():
            all_args = ()
            all_kwargs = {}
            for pointer, (args, kwargs), next_nodes in pointer_list:
                all_args += args
                all_kwargs.update(kwargs)
            pointer_dict[node_uname] = (pointer, (all_args, all_kwargs))
            if keep_next:
                pointer_dict[node_uname] += (next_nodes, )
        # self.io_print(dict(triples_dict), pointer_dict, 'FLATTEN')
        return pointer_dict

    async def _run_active_next_pointers(self, pointers_dict_or_triples, use_next_nodes=True):
        """ Given a tuple of tuples`(pointer, (args, kwargs))`,
            call each, returning the _next_ pointers and results.

            Enter into the pointer with the arg and kwargs, returning the
            result of that point node call and the next pointer node.

                given:

                    (
                        <Pointer P_50158992_1 depth=1 index=2 for Node(op_sub_6)>, (
                            (20, 5, 4), {}
                        )
                    )

                result:

                    {'P_50544848_2': (
                            <Pointer P_50544848_2 depth=2 index=0 for Node(add_all)>,
                            ( (29,), {})
                        )
                    }

            At times the result the edges result to many results. Each result
            will be in the next pointer iteration.

                given

                    {
                        <Pointer P_50158512_0 depth=0 for Node(in_node)>: (
                                (10,), {}
                            )
                    }

                result

                    {
                     'P_50158848_1': (<Pointer P_50158848_1 depth=1 index=1 for Node(op_sub_5)>,
                                      ((5,), {})
                                      ),
                     'P_50158944_1': (<Pointer P_50158944_1 depth=1 index=0 for Node(op_add_10)>,
                                      ((20,), {})
                                     ),
                     'P_50158992_1': (<Pointer P_50158992_1 depth=1 index=2 for Node(op_sub_6)>,
                                      ((4,), {})
                                     )
                    }
        """
        pointer_dict = {}
        lost = {}

        for i, d in enumerate(pointers_dict_or_triples):
            pointer, (a, kw), next_nodes = await self.extract_pointer_dict_next(d, use_next_nodes)

            pointers = self.as_pointers(next_nodes, pointer, index=i, as_index=True)
            new_pointers_dict = await self.run_pointers(pointers, *a, **kw)

            if len(new_pointers_dict) == 0:
                lost[pointer.uname()] = pointer, (a,kw)
            pointer_dict.update(new_pointers_dict)

        # self.io_print(iters, pointer_dict, '_run_active_next_pointers')
        return pointer_dict, lost

    async def extract_pointer_dict_next(self, pointer_position, use_next_nodes=True):
        """Safely extract the (pointer, (args, kwargs), next_nodes) of the
        given pointer_position. If the next nodes don't exist, call upon the
        `pointer.get_next`, useing the `self.path`

        If the pointer_position is not a triple, it will not contain the next nodes

        Return a tuple: (pointer, (args, kwargs), next_nodes)
        """
        next_nodes = None

        c = len(pointer_position)
        if c == 2:
            pointer, a_kw = pointer_position

        if c == 3:
            pointer, a_kw, next_nodes = pointer_position

        i_nodes = next_nodes if use_next_nodes else None
        if i_nodes is None:
            i_nodes = await pointer.get_next(path=self.path, as_index=True)

        return pointer, a_kw, i_nodes

    def _pull_edge(self, pointer, *a, **kw):
        """If the given entity is an Edge (rather than a typical pointer),
        run the intermediate step, resolving the results.
        the result presents as the _next_ arguments at the tip of the edge and
        given as the input. of the B side

            A (3) -> e -> B (6)
                     |
                     |= intermediate(*2)
        """
        _pointers = (pointer,)

        if isinstance(pointer, Edge):
            a, kw = pointer.run_intermediate(*a, **kw)
            _pointers = self.as_pointers((0, pointer.node.b),
                                        pointer,
                                        index=pointer.index,
                                        as_index=True)
        return _pointers, (a, kw)

    def concat_on_pointer_node_name(self, pointer_dict):

        out_res = defaultdict(self._make_new_item)
        for pname, (pointer, (a, kw)) in pointer_dict.items():
            node_uname = pointer.node.uname()
            item = out_res[node_uname]
            item['pointers'].add(pointer)
            item['args'] += a
            item['kwargs'].update(kw)

        return dict(out_res)

    def _make_new_item(self):
        return {
            'args': (),
            'kwargs': {},
            'pointers': set(),
        }

    def shape_as_pointers_dict(self, out_res):

        out_res_2 = {}
        for node_name, item in out_res.items():
            pointer = tuple(item['pointers'])[-1]
            a = item['args']
            kw = item['kwargs']
            out_res_2[pointer.uname()] = (pointer, (a, kw))

        return out_res_2


