"""The primary mixin and function for running a stepper position.
"""
from collections import defaultdict
from pprint import pprint as pp
from edge import Edge


class DefaultMotion(object):

    async def run_pointers_dict_alpha(self, pointer_dict, ):
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
                lost[pointer.uname()] = pointer, v

            res.update(new_pointers_dict)

        if c == 0:
            await self.flag_detected_run_empty()
        return res, lost
