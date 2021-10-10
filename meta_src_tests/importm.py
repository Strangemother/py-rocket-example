import importlib.machinery
import sys
import builtins

# For illustrative purposes only.
SpamMetaPathFinder = importlib.machinery.PathFinder
SpamPathEntryFinder = importlib.machinery.FileFinder
loader_details = (importlib.machinery.SourceFileLoader,
                  importlib.machinery.SOURCE_SUFFIXES + ['.foo'])

# Setting up a meta path finder.
# Make sure to put the finder in the proper location in the list in terms of
# priority.
sys.meta_path.append(SpamMetaPathFinder)

# Setting up a path entry finder.
# Make sure to put the path hook in the proper location in the list in terms
# of priority.
sys.path_hooks.append(SpamPathEntryFinder.path_hook(loader_details))

orig = builtins.__import__

def import_func(name, _globals, _locals, fromlist, level):
    print("import_func(",name, fromlist, level,")")
    return orig(name, _globals, _locals, fromlist, level)

builtins.__import__ = import_func


def drop(name):
    sys.modules.pop(name)
    globals().pop(name)
