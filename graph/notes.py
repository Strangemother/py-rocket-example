"""
Recurse Detection.

Whilst en event is flowing through the event machine, it keeps history.

g.connect(*'LMONKEY')
g.connect(*'HORSE')
g.connect(*'HOUSE')

To produce a recursive event, we apply a short of any key within a _flow_,
connected to a node within the same flow.

    g.connect(*'YO')

Here, when the event tree hits "Y", the junction "O" will continue through "ONKEYONK..."
A single `g.pump()` for a "in recurse" event:

>>> e = g.pump()
(<Event(0x2ac6d90) from 45181896>, )
>>> w=e[0]
>>> g.get_entities(w.history)
('M', 'O', 'N', 'K', 'E', 'Y', 'O', 'N', 'K', 'E', 'Y', 'O', 'U', 'S')

If this event was allowed to bubble forever the machine may recurse.

"""

class OldGraphTree(object):

    def __init__(self):
        self._create_kv()
        self._create_names()

    def _create_names(self):
        # print('_create_names')
        self.names = {}
        self.names_reverse = {}

    def _create_kv(self):
        # print('_create_kv')
        self.kv = defaultdict(set)
        self.reverse_kv = defaultdict(set)

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

    def get_add_name(self, word):
        """Return the integer position of the given word from the internal
        names dictionary. If the word is not within the names index a new
        entry is generated.

        The returned integer is used within the graph as a replacement for the
        text. Reverse the int with `get_entry(get_add_name('cherry'))`
        """
        pos = self.names.get(word)
        l = len(self.names)
        if pos is None:
            pos = l+1
            self.names[word] = pos
            self.names_reverse[pos] = word
        return pos

    def connect(self, *nodes):
        """Given two or more nodes to connect linearly, iterate each and
        collect or generate an internal name - applied to the internal word
        dictionary. Iterate the name indices connecting N to N+1.

            append('a', 'b', 'c')
            a -> b
            b -> c
        """
        name_indices = tuple(self.get_add_name(node) for node  in nodes)
        # print('append', tuple(name_indices))
        print('name_indices', name_indices, nodes)

        for (i, ni), node in zip(enumerate(name_indices), nodes):
            # print(f"Inserting node #{i} '{ni}'", node, end='')
            to_node = None

            if i+1 < len(name_indices):
                # The next node does exist, grab its name to connect _this_
                # as a forward relation.
                to_node = name_indices[i+1]

            # next_node = self.get_entry(to_node)
            # print(' next:', next_node)
            #
            if len(name_indices) == i+1:
                # print(' - done')
                continue

            self.bind_nodes(ni, to_node)

