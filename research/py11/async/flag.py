
class FlagFunctions(object):
    """A Range of simple hooks to capture events from an executing chain such
    as _on_chain_complete_.
    """
    async def flag_complete(self, exit_pointers, stashed_lost):
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
            return await self.on_chain_complete_first(exit_pointers, stashed_lost)
        return await self.on_chain_complete(exit_pointers, stashed_lost)

    async def flag_detected_run_empty(self):
        """The last call to the graph did not execute any nodes.
        """
        print('\n    Flat Detect Empty Run. Perform stepper.reset()')

    async def on_chain_complete_first(self, exit_pointers, pointer_dict):
        """All chains are ocmplete. This is the first time for this graph all
        has completed.
        """
        print('    on_chain_complete_first', exit_pointers)
        # print('on_chain_complete', pointer_dict)

    async def on_chain_complete(self, exit_pointers, pointer_dict):
        print('    on_chain_complete', exit_pointers)
        # print('on_chain_complete', pointer_dict)