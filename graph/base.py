from collections import defaultdict


FORWARD = 'forward'
REVERSE = 'reverse'
BOTH = ['forward', 'reverse']

UNDEF = {}



class GraphNodeConnect(object):

    def __init__(self):
        self._create_kv()

    def _create_kv(self):
        # print('_create_kv')
        self.kv = defaultdict(self.get_tree_junction)
        self.reverse_kv = defaultdict(self.get_tree_junction)

    def get_tree_junction(self):
        return set()

    def bind_nodes(self, int_pos_a, int_pos_b, direction=BOTH, method='add'):
        return self._kv_set(int_pos_a, int_pos_b, direction=BOTH, method='add')

    def _kv_set(self, int_pos_a, int_pos_b, direction=BOTH, method='add'):
        """Given two index keys, record the forward relation n1 > n2 an a _reverse_
        relation, in which the same keys are applied n2 > n1.
        """
        # print(f' {int_pos_a} <> {int_pos_b}')
        if FORWARD in direction:
            getattr(self.kv[int_pos_a],method)(int_pos_b)

        if REVERSE in direction:
            getattr(self.reverse_kv[int_pos_b],method)(int_pos_a)

    def disconnect(self, int_pos_a, int_pos_b):
        """Remove the connection between two nodes
        """
        try:
            return self._kv_set(int_pos_a, int_pos_b, direction=BOTH, method='remove')
        except KeyError as err:
            print('cannot disconnect key', str(err))
            return
        # self.kv[int_pos_a].remove(int_pos_b)
        # self.reverse_kv[int_pos_b].remove(int_pos_a)

    def reset_position(self, pos):
        """Remove all connections of the given.
        """

        int_pos_bs = self.kv[pos].copy()
        for b in int_pos_bs:
            self.disconnect(pos, b)
        self.kv[pos].clear()
        return int_pos_bs

    def assign_position(self, int_pos_a, int_pos_b_set):
        for b in int_pos_b_set:
            self.bind_nodes(int_pos_a, b)
        # self.kv[int_pos_a].update(int_pos_b_set)
