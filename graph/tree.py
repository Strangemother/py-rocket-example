from collections import defaultdict


class PointTree(object):

    def __init__(self):
        self._tree = defaultdict(self.get_tree_junction)

    @property
    def tree(self):
        return dict(self._tree)

    def get_tree_junction(self):
        return set()

    def tree_connect_forward(self, pointer_a, pointer_b, method='add'):
        """Bind two pointers in a forward direction within the graph.

        Once done the pointer UUID maps the internal tree to the literal values.
            >>> g.tree
            {32830880: {33006312}, 7987072: {7987128}, 7987128: {32821352}}
            >>> g.pointers
            {32830880: <GraphPointer(0x1f73650) "{}">,
            33006312: <GraphPointer(0x1f735f0) "{1, 2, 3}">,
            7987072: <GraphPointer(0x1f735b0) "egg">,
            7987128: <GraphPointer(0x1f73670) "button">,
            32821352: <GraphPointer(0x1f73690) "food">}
        """
        a = pointer_a.uuid
        b = pointer_b.uuid
        print(f'Appending pointer {a} => {b}')
        method = getattr(self._tree[a], method) # pointer.add
        return method(b) # tree[pointer_a].add(pointer_b)

    def tree_disconnect_forward(self, pointer_a, pointer_b, method='remove'):
        return self.tree_connect_forward(pointer_a, pointer_b, method)

    def get_junction(self, pointer_id):
        return self._tree[pointer_id]

