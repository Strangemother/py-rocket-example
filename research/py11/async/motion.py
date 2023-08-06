"""The primary mixin and function for running a stepper position.
"""
from collections import defaultdict
from pprint import pprint as pp
from edge import Edge


class DefaultMotion(object):

    async def alpha_run_pointers_dict(self, pointer_dict, ):
        """
        Given a pointers dict, return a `pointer, losses` tuple

        the dict value is the `pointer` and a tuple of args, kwargs
        from the previous call - ready for the next call.

            {
                123: (pointer, ((1 ), {},))
                124: (pointer, ((10), {},))
            }
        """
        await self.pppd(pointer_dict, '    Stepper.run_pointers_dict with')
        # Unpack pointers into many sub pointers.
        # Then run pointer (results pointer_dict)

        c = 0
        res = {}
        lost = {}
        pdv = pointer_dict.values()
        for i, (pointer, v) in enumerate(pdv):
            c += 1
            new_pointers_dict = await self.run_pointer_next(pointer, v, i)
            if len(new_pointers_dict) == 0:
                # the newest call yielded nothing.
                # Cache back for this pointer may be applied.
                lost[pointer.uname()] = pointer, v
            res.update(new_pointers_dict)

        if c == 0:
            await self.flag_detected_run_empty()
        return res, lost


class MergePointerMotion(object):

    async def alpha_merge_pointers_dict(self, pointer_dict, ):
        c = 0
        res = {}
        lost = {}
        pdv = pointer_dict.values()
        for i, (pointer, v) in enumerate(pdv):
            c += 1
            i_nodes = await pointer.get_next(path=self.path, as_index=True)
            pointers = self.as_pointers(i_nodes, pointer, index=i, as_index=True)

            a, kw = v
            new_pointers_dict = await self.run_pointers(pointers, *a, **kw)

            if len(new_pointers_dict) == 0:
                lost[pointer.uname()] = pointer, v
            res.update(new_pointers_dict)

        if c == 0:
            await self.flag_detected_run_empty()

        return res, lost


class MergeModePointerMotion(object):

    async def run_merge_pointers_dict_v2(self, pointer_dict, ):
        c, merge_nodes = await self.merge_pointers_by_node_name(pointer_dict)

        if merge_nodes:
            # recombobulate the the merged into a pointer dict shape, merging
            re_nodes = self.recombobulate(merge_nodes)

        self.debug_printout(merge_nodes, pointer_dict, re_nodes)

        pointer_dict = self.concat_pointer_lists_to_one(re_nodes)
        po = tuple(pointer_dict.values())
        res, lost = await self._run_active_next_pointers(po)

        if c == 0:
            await self.flag_detected_run_empty()

        out_res = self.concat_on_pointer_node_name(res)
        out_res_2 = self.shape_to_callable_pointers(out_res)
        print('\n -- out_res_2')
        pp(out_res_2)

        return out_res_2, lost

    def concat_pointer_lists_to_one(self, re_nodes):
        """
        Given a dictionary of

            node_uname: (
                            (pointer, (a, kw), next_nodes),
                            (pointer, (a, kw), next_nodes),
                            ...
                        )
            node_uname: ()

        return a dictionary of concatendated pointer lists.

            node_uname: (
                            (pointer, *a*a, **kw**kw),
                        )

        """
        re_pointers_dict = {}
        ## 2013/08/06: Iter the re_nodes
        for node_uname, pointer_list in re_nodes.items():
            all_args = ()
            all_kwargs = {}
            for pointer, (args, kwargs), next_nodes in pointer_list:
                # contact to (pointer (a, kw))
                all_args += args
                all_kwargs.update(kwargs)
            re_pointers_dict[node_uname] = (pointer, (all_args, all_kwargs))
        return re_pointers_dict

    async def merge_pointers_by_node_name(self, pointer_dict, ):
        res = {}
        lost = {}
        pop_orig = pointer_dict.copy()
        pdv = pointer_dict.values()
        merge_nodes = defaultdict(tuple)
        c = 0
        # pdv = self.concat_pointer_lists_to_one(merge_nodes).values()

        for i, (pointer, v) in enumerate(pdv):
            c += 1
            i_nodes = await pointer.get_next(path=self.path, as_index=True)
            ## concat by i node uname
            new_entry = (pointer, v, i_nodes)
            node = pointer.node

            if isinstance(node, Edge):
                print('is edge', node)
                # First check if the end node is this node.
                node = node.b

            nn = node.uname()
            pname = pointer.uname()

            if node.merge_pointers:
                merge_nodes[nn] += (new_entry,)
                pop_orig.pop(pname)
                continue
            merge_nodes[pname] += (new_entry,)
            pop_orig.pop(pname)

        assert len(pop_orig) == 0, 'Pointers missed during merge.'
        return c, merge_nodes

    def debug_printout(self, merge_nodes, pointer_dict, re_nodes):
        print('\n -- merge_nodes (concats):')
        pp(dict(merge_nodes))
        print('\n -- pointer_dict (orig):')
        pp(pointer_dict)
        print('\n -- re_nodes (new):')
        pp(dict(re_nodes))
        print('--')


    async def _run_active_next_pointers(self, iters):
        res = {}
        lost = {}
        for i, (pointer, (a, kw)) in enumerate(iters):
            i_nodes = await pointer.get_next(path=self.path, as_index=True)
            pointers = self.as_pointers(i_nodes, pointer, index=i, as_index=True)
            # a, kw = v
            print(' >> Executing Pointers of ', pointer, a, kw)
            print(' >>           Pointers', pointers)
            new_pointers_dict = await self.run_pointers(pointers, *a, **kw)

            if len(new_pointers_dict) == 0:
                lost[pointer.uname()] = pointer, (a,kw)
            res.update(new_pointers_dict)
        return res, lost


    def _pull_edge(self, pointer, *a, **kw):
        _pointers = (pointer,)

        if isinstance(pointer, Edge):
            a, kw = pointer.run_intermediate(*a, **kw)
            _pointers = self.as_pointers((0, pointer.node.b),
                                        pointer,
                                        index=pointer.index,
                                        as_index=True)
        return _pointers, (a, kw)

    def recombobulate(self, merge_nodes):
        # recombobulate the the merged into a pointer dict shape, merging
        # args
        re_nodes = defaultdict(tuple)
        print('\nMerging Nodes')
        for name, pointer_set in merge_nodes.items():

            all_kw = {}
            all_args = ()
            all_next_nodes = ()
            all_pointers = ()

            for (pointer, (a,kw), i_nodes) in pointer_set:
                _pointers, (a, kw) = self._pull_edge(pointer, *a, **kw)
                all_pointers += _pointers
                all_args += a
                all_kw.update(kw)
                all_next_nodes += i_nodes

            clean_next_nodes = tuple(set(all_next_nodes))
            new_pointer = all_pointers[0]
            new_entry = (new_pointer, (all_args, all_kw,), clean_next_nodes)

            _name = name
            try:
                _name = clean_next_nodes[0][1].uname()
                print(' -- concat on', _name)
            except IndexError:
                print(' xx Cannot concat on future node name')

            re_nodes[_name] += (new_entry,)

        print('\n -- Pointers (used):')
        pp(all_pointers)
        return dict(re_nodes)

    def concat_on_pointer_node_name(self, res):

        out_res = defaultdict(self._make_new_item)
        for pname, (pointer, (a, kw)) in res.items():
            node_uname = pointer.node.uname()
            item = out_res[node_uname]
            item['pointers'].add(pointer)
            item['args'] += a
            item['kwargs'].update(kw)

        return out_res

    def _make_new_item(self):
        return {
            'args': (),
            'kwargs': {},
            'pointers': set(),
        }

    def shape_to_callable_pointers(self, out_res):
        out_res_2 = {}
        for node_name, item in out_res.items():
            pointer = tuple(item['pointers'])[-1]
            a = item['args']
            kw = item['kwargs']
            out_res_2[pointer.uname()] = (pointer, (a, kw))

        return out_res_2



class RecursiveStepper(object):

    async def run_pointers_dict_recurse(self, pointer_dict, lost_pointer_dict=None, loop_limit=None):
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
            new_pointers, new_lost = await self.run_pointers_dict(pointers)
            lost.update(new_lost)

            if len(new_pointers) == 0:
                await self.flag_complete(pointers, lost)
                return pointers, lost

            pointers = new_pointers
            ll = count+1 if _loop_limit == -1 else _loop_limit
            loop = len(pointers) > 0 and (count < ll)
            if count >= ll:
                print('Hit Recuse limit.', ll)

        return pointers, lost


class StepperMotionMixin(DefaultMotion, MergeModePointerMotion, RecursiveStepper):
    merge_mode = True
    func_name = 'alpha_run_pointers_dict'
    merge_func_name = 'run_merge_pointers_dict_v2'

    async def run_pointers_dict(self, pointer_dict, ):
        func_name = self.get_func_name()
        return await getattr(self, func_name)(pointer_dict)

    def get_func_name(self):
        if self.merge_mode:
            return self.merge_func_name

        return self.func_name
