from .base import DefaultMotion
from .recurse import RecursiveStepper
from .merge import MergeModePointerMotion


class StepperMotionMixin(DefaultMotion, MergeModePointerMotion, RecursiveStepper):
    merge_mode = False
    func_name = 'run_pointers_dict_alpha'
    merge_func_name = 'run_merge_pointers_dict'
    # merge_func_name = 'alpha_merge_pointers_dict'

    async def run_pointers_dict(self, pointer_dict):
        func_name = self.get_func_name()
        return await getattr(self, func_name)(pointer_dict)

    def get_func_name(self):
        if self.merge_mode:
            return self.merge_func_name

        return self.func_name
