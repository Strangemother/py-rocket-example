"""The "graph" tools provide the base abstraction for a Graph and its minor
components. The Graph accepts nodes connected through 'junctions', iterated with
Events through an EventMachine.

    g = Graph()
    g.connect('a', 'b')

Elements A and B may be anything such as strings, functions, objects or other complex
entities. Once applied to the graph, the connections yield chains through
_find_ calls.

    g.find('a')
    g.drain()
    (('a', 'b'),)

The 'find' applies a new Event to the events stack.

In default form the `EventMachine` is _drained_ after every iteration. Without
a drain, the event does nothing. Apply the `drain()` function to a simple
`while` loop to automate the event emit.
"""
from pprint import pprint as pp

from collections import defaultdict
from events import TreePump
from pointer import GraphPointer
from node import GraphNode
from tree import PointTree

from find import FindMixin

class GraphTree(PointTree, TreePump, FindMixin):

    UNDEF = {}

    def __init__(self):
        super().__init__()
        self.pointers = {}

    def get_node_id(self, entity):

        _id = id(entity)

        if isinstance(entity, GraphNode):
            _id = entity.get_uuid()

        return _id

    def add(self, a, b):
        """Connect two _real_ nodes by stashing the two entities as Pointers
        and building a connection within the KV set.
        """
        pa, pb = self.pointer_store(a, b)
        print('Pointers', pa, pb)

        # assert the 'uuid' of a pointer exists within the pointer dict.
        assert tuple(self.pointers.values())[0].uuid in self.pointers

        self.tree_connect_forward(pa, pb)
        assert pa.uuid in self.tree
        assert pb.uuid in self.tree[pa.uuid]

    def disconnect(self, a, b):
        return self.tree_disconnect_forward(a, b)

        # ida = self.get_pointer_by_name(a)
        # idb = self.get_pointer_by_name(b)
        # self.tree_disconnect_forward(ida, idb)

    def get_pointer_by_name(self, name):
        return self.pointers[self.get_node_id(name)]

    def get_entities(self, names):
        r = ()
        for x in names:
            r += (self.pointers[x].entity,)
        return r

    def replace(self, name, entity):
        """Switch the node indexed under "name" with the given entity, stored
        to the existing node(name) GraphPointer.
        Return the altered GraphPointer

        This doesn't affect the existing graph naming, allowing the
        "hot replacement" of a key with another value.

            g.add(*'LM')
            g.add(*'MONKEY')

            g.replace('M', {})

        Synonmous to:

            g.get_pointer_by_name('M').entity = {}

            >>> g.send('L')

            * end_event. <Event(44762280) from 7567432>
              history:   ('L', {}, 'O', 'U', 'S', 'E', 'Y')
              positions: (-1, 0, 0, 2, 0, 0, 0)

        """
        pointer = self.get_pointer_by_name(name)
        pointer.entity = entity
        return pointer

    def connect(self, *nodes):
        """Given two or more nodes to connect linearly, iterate each and
        collect or generate an internal name - applied to the internal word
        dictionary. Iterate the name indices connecting N to N+1.

            append('a', 'b', 'c')
            a -> b
            b -> c
        """

        for i, node in enumerate(nodes):
            # print(f"Inserting node #{i} '{ni}'", node, end='')
            to_node = None

            if i+1 < len(nodes):
                # The next node does exist, grab its name to connect _this_
                # as a forward relation.
                to_node = nodes[i+1]

            # next_node = self.get_entry(to_node)
            # print(' next:', next_node)
            #
            if len(nodes) == i+1:
                # print(' - done')
                continue

            self.add(node, to_node)

    def splice(self, start_entity, *nodes):
        """Apply one or more nodes between two existing nodes resulting in an
        extending chain for the given start entity.

            g.append('torso', 'arms', 'hands', 'fingers', 'fingernails')
            # get('arms') hands, fingers, fingernails

            g.splice('arms', 'elbows', 'forearms', 'wrists', 'hands')
            # get('arms') elbows, forearms, wrists, hands, fingers, fingernails

        Synonymous to:

            graph.disconnect(a, f)
            graph.append(a, c, d, e, f)
        """
        end_entity = nodes[-1]
        _g = self.get_pointer_by_name
        self.disconnect(_g(start_entity), _g(end_entity))
        self.connect(start_entity, *nodes)

    def resolve(self, pointer_id, default=UNDEF):
        """Given a pointer ID, resolve to the end unit - A GraphPointer
        """
        ps = self.pointers
        is_undef = default == self.UNDEF
        return ps[pointer_id] if is_undef else ps.get(pointer_id, default)


    def x_resolve(self, pointer_id, default=UNDEF):
        """Given a pointer ID, resolve to the end unit - A GraphPointer
        """
        if default == self.UNDEF:
            return self.pointers[pointer_id]

        return self.pointers.get(pointer_id, default)


    def pointer_store(self, *entities):
        """
        Store one or more entity objects and return the direct pointer, used
        for the graph reference. If the given entity is a Pointer, the same
        instance is returned.

        Provide many entities expecting an ordered tuple of pointers. If one
        entity is given, return a single pointer.
        """
        res = ()

        for entity in entities:
            pointer = self.create_pointer(entity)
            res += (pointer,)

        if len(entities) == 1:
            return res[0]

        return res

    def create_pointer(self, entity):
        """Return a Pointer type
        """

        _id = id(entity)

        if isinstance(entity, GraphNode):
            _id = entity.get_uuid()
            # return entity
            #
        # If the existing exists, return the pointer.
        pointer = self.pointers.get(_id)

        if pointer is None:
            # build new pointer, returning a _pointer_
            is_gp = isinstance(entity, GraphPointer)
            pointer = entity if is_gp else GraphPointer(_id, entity)
            self.pointers[_id] = pointer

        return pointer


# The user identified export.
Graph = GraphTree
