
class RecursiveStepper(object):

    async def run_pointers_dict_recurse(self, pointer_dict, lost_pointer_dict=None, loop_limit=None):
        """Run a pointers dictionary until the chain is released (whilst there
        are future nodes)

        Arguments:
            pointer_dict {dict} -- a concurrent pointers dict

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


