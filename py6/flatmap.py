"""
Connect A > B > C > D ... through a flat map of (A,B), (B, C), (C, D) ...

This acts just like a binary tree, with each node traversal calculated through
the dependency stepper.

An `add` applies an A > B connection. If A exists, B applies to the existing
set, and A gains two children. Given the _edge_ type, A children are iterated
given the test on the edge.

A split may alter the connection of two nodes, through the given spliced entity.

    before: A > B > C
    graph.slice(A, B, through=D)
    after: A > D > B > C

Under-the-hood this moves all A references into the D chain, and apply A > D
alone.

The flatgraph will create the reverse automatically

Decend a graph through `decend` until the target. The target may be None, allowing
the walk to yield until a natural death

    # from => to
    graph.decend("mytarget", until='lastnode', limit=100)
    ()

Each entity given to the graph is converted to a string UUID id, then an index
int position within a primary _name_ map.
The int key is used through the graph, allowing graph key > content change without
altering the graph.
"""
from collections import defaultdict
from importlib import reload
from pprint import pprint as pp

FORWARD = 'forward'
REVERSE = 'reverse'
BOTH = ['forward', 'reverse']


UNDEF = {}


class GraphNameKeys(object):
    """A range of functions dedicated to name lists and an internal word
    dictionary for integer graph key conversions.
    """
    kv = None
    UNDEF = UNDEF

    def __init__(self):
        self._create_names()

    def _create_names(self):
        # print('_create_names')
        self.names = {}
        self.names_reverse = {}

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

    def get_entry(self, int_pos):
        """Return a word entry given the position integer. If the given
        position is not an int, assume as a 'word' and use the reversed name
        dictionary, resolving the "word" to an int.

        Notably this isn't clever if you always expect an int therefore
        `as_name` may be helpful
        """
        u = self.names_reverse if isinstance(int_pos, int) else self.names
        return u[int_pos]

    def get_position(self, entity, default=UNDEF):
        """Return the integer position of the given `entity` as a _word_ within
        the internal dictionary. If the entity is missing return default
        if default is not given, throw a KeyError
        """
        u = self.names
        try:
            return u[entity]
        except KeyError as err:
            if default == self.UNDEF:
                raise err
            return default

    def as_names(self, ints):
        """Given a list of word index integers, return a tuple of resolved
        words through the internal word dictionary.

            as_names(1,2,3)
            ('A', 'B', 'C')
        """
        return tuple(self.as_name(x) for x in ints)

    def as_name(self, x):
        """Return the word from the internal dictionary given the key index `x`
        """
        return self.names_reverse[x]


class GraphRecord(object):

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

    def get_next(self, pos):
        """Given a position index within the kv graph, yield each item
        within the _forward_ relationship

            append('a', 'b')
            append('a', 'c')
            append('a', 'e')
            append('b', 'f')
            append('e', 'b')

            get_next('a') -> gen
            ('b', 'c', 'e')
        """
        return self._yield_on(self.kv, pos)

    def get_next_reverse(self, pos):
        """Given a position index within the kv graph, yield each item
        within the _reverse_ relationship

            append('a', 'b')
            append('a', 'c')
            append('a', 'e')
            append('b', 'f')
            append('e', 'b')

            get_next('a') -> gen
            () # a has no parents

            get_next('b') -> gen
            ('e', 'a') # b has reverse (parents)
        """
        return self._yield_on(self.reverse_kv, pos)

    def _yield_on(self, parent, pos):
        keys = parent.get(pos, ())
        for key in keys:
            yield key


class GraphRead(object):
    tuple_key = True

    def last_linear_chain(self, start_entity, result=None, drop_self=False,
                          origin_pos=None, reverse=False, until=None, _head=True,
                          until_pos=None):
        """Return all nodes connected to the given entity *without* considering
        the graph, returning a linear list of nodes in a _forward_ flow

        g = FlatGraph()
        g.append('A', 'B', 'C', 'D')
        g.append('A', 'F', 'G',)
        g.append('A', 'H', 'I',)
        g.append('W', 'X', 'Y',)

        >>> g.as_names(g.last_linear_chain('A'))
        ('A', 'B', 'C', 'D', 'F', 'G', 'H', 'I')
        >>> g.as_names(g.last_linear_chain('A', drop_self=True))
        ('B', 'C', 'D', 'F', 'G', 'H', 'I')
        >>> g.as_names(g.last_linear_chain('B'))
        ('B', 'C', 'D')
        >>> g.as_names(g.last_linear_chain('C'))
        ('C', 'D')
        >>> g.as_names(g.last_linear_chain('W'))
        ('W', 'X', 'Y')
        >>> g.as_names(g.last_linear_chain('X'))
        ('X', 'Y')
        >>> g.as_names(g.last_linear_chain('H'))
        ('H', 'I')
        >>> g.as_names(g.last_linear_chain('D'))
        ('D',)
        >>> g.as_names(g.last_linear_chain('I'))
        ('I',)
        """

        if _head is True:
            # first phase on the recurse.
            until_pos = self.get_position(until, None)

        origin_pos = origin_pos or self.get_position(start_entity)
        pos = start_entity
        # print(' .>', result, pos)
        res = result or ()

        if result is None:
            pos = self.get_position(start_entity, None)

        drop_match = pos == origin_pos and (drop_self is True)
        res += () if drop_match else (pos,)
        next_func = self.get_next_reverse if reverse else self.get_next

        for v in next_func(pos):
            if v == until_pos:
                # print('Skip descendant of children', v, until)
                continue

            res = self.last_linear_chain(v,
                result=res,
                drop_self=drop_self,
                origin_pos=origin_pos,
                reverse=reverse,
                until=until,
                until_pos=until_pos,
                _head=False
                )

        return res

    def chains(self, start_entity, current_pos=None, index=None, depth=0,
               with_parent=False, reverse=False, until=None, self_stop=True,
               until_pos=None, max_depth=10, _head=True, start_entity_pos=None):

        if depth+1 > max_depth:
            print('Max depth exceeded', start_entity)
            return ()

        if _head is True:
            # first phase on the recurse.
            start_entity_pos = self.get_position(start_entity, None)
            until_pos = self.get_position(until, None)

        pos = current_pos or start_entity_pos or self.get_position(start_entity, None)

        # r = ()
        r = (self.as_name(pos),) if (depth == 0 and with_parent) else ()

        next_func = self.get_next_reverse if reverse else self.get_next
        children = tuple(next_func(pos))

        for child in children:
            np = self.as_name(child)
            if child == until_pos:
                print('break early on', child, )
                r += (np,)
                continue

            if child == start_entity_pos:
                continue

            # print('Append', np)

            v = (np,) + self.chains(start_entity, child,
                                    depth=depth+1,
                                    reverse=reverse,
                                    until=until,
                                    until_pos=until_pos,
                                    start_entity_pos=start_entity_pos,
                                    max_depth=max_depth,
                                    _head=False
                                )

            # print(' ' * depth, 'C:', v)
            r += (v,)

        if reverse:
            r = tuple(reversed(r))
        # pr = self.as_name(pos),
        # if (depth == 0 and with_parent):
        #     r = (pr,) + r
        return r


    def flat_chains(self, chains, index=0, route=None, routes=None,
        allow_partial=True, allow_top_partial=True, keep_temp=True):
        """

        allow_top_partial to capture the _parent_ unique flows initiating
        all sub flows.

        Given this example, `_toplevel` identify the two unique flows from
        the given parent node (in this case "A"). During traversal, the 0-0 and
        0-1 leaf nodes branches to more than 1 child.

            {'0-0': ['B', 'C'],
             '0-1': ['D'],
             '0-2': ['B', 'C', 'D'],
             '0-3': ['B', 'C', 'E', 'V'],
             '1-1': ['D', 'T'],
             '1-2': ['D', 'V'],
             '2-1': ['B', 'C', 'D', 'T'],
             '2-2': ['B', 'C', 'D', 'V'],
             '_complete': ('2-1', '2-2', '0-3', '1-1', '1-2'),
             '_toplevel': ('0-0', '0-1')}

        Converting flows _flattens_ the given graph to linear paths, each branch
        initiates a new _complete_ flow:

            (
                ('B', 'C', 'D',
                            ('T', 'V'),
                            ('E', 'F')
                    ),
                ('D',
                    ('T', 'V'),
                    ('E', 'F')
                    )
            )

        Will return the _complete tree of:

            'B', 'C', 'D', 'T', 'V'
            'B', 'C', 'D', 'E', 'F'
            'D', 'T', 'V'
            'D', 'E', 'F'

        """

        routes = {}
        route = route or []



        children = self.select_children(
                i=0,
                items=chains,
                chain=route,
                result=routes,
                parent=(),
            )
        for i, listable in enumerate(chains):
            # Render to a linear flow and a dictionary of K:[] sub flows.
            iv = (i,) if self.tuple_key else i

            v, rs = self.read_chain(iv, listable, route, routes,
                                    allow_partial=allow_partial,
                                    keep_temp=keep_temp,
                                    parent=chains)

            # print("top level read chain:", i, v)

            if allow_partial or allow_top_partial:
                # pollute the top level with early chains, for _toplevel
                # descendant tests
                key = (0, 0, i,) if self.tuple_key else f'0-0-{i}'
                routes[key] = v
                self.tag_complete(key, routes, '_toplevel')
            self.safe_merge(routes, rs)
            # routes.update(rs)
        return routes

    def read_chain(self, i, listable, r=None, rs=None, allow_partial=False,
                    keep_temp=True, parent=None):
        # print("read_chain", i, r, listable)
        rs = rs or {}
        r = r or []

        children = self.select_children(
                i=i,
                items=listable,
                chain=r,
                result=rs,
                parent=parent,
            )

        for sub_index, item in enumerate(listable):

            if self.is_tuple(item) is False:
                # There is no junction, append the item to the current running
                # list and step to the next.
                r.append(item)
                continue

            flat_id = i + (sub_index,) if self.tuple_key else f"{i}-{sub_index}"

            # if sub_index+1 == len(listable):
            #     print('  End:',i, sub_index, listable[sub_index])
            #     print('  End:', item, '\n')
            #     self.tag_complete(item, rs, '_junction')

            # Recurse into the child item of `tuple` type
            # A copy must occur else the parent list is appended with neighbours
            ars, subrs = self.read_chain(flat_id,
                                listable=item,
                                r=r.copy(),
                                allow_partial=allow_partial,
                                keep_temp=keep_temp,
                                parent=listable)

            if len(subrs) > 0:
                # print('Len subrs', len(subrs), subrs)
                # rs.update(subrs)
                self.safe_merge(rs, subrs)
                if keep_temp:
                    key = ('t',) + flat_id if self.tuple_key else  f't-{flat_id}'
                    rs[key] = ars
            else:
                # ars.append('!')
                fh = ('h',) + flat_id if self.tuple_key else  f'h-{flat_id}'
                rs = self.tag_complete(fh, rs)
                # print('hit', flat_id, ars)
                rs[fh] = ars

            if allow_partial:
                key = ('p',) + flat_id if self.tuple_key else  f'p-{flat_id}'
                rs[key] = ars

        return r, rs

    def select_children(self, i, items, chain, result, parent):
        """Choose the _next_ step the current chain should read, given a list
        of available steps.

            item: tuple     a list of next steps to iterate into the change
            chain: list     the current chain path to this children set
            name: str       the intended name of the chain.
            result: dict    The result dict containing all *in-process* paths.

        An example here shows the incoming (next) steps of the graph,
        and a count of potential choices for that node:

            _n = {x[0]:len(x) for x in items}
            print('Selecting from', _n)
            {'B': 5, 'D': 1, 'E': 1, 'G': 2, 'V': 4}
        """

        if len(items) > 1:
            _n = {x[0]:len(x) for x in items }
            print('Selecting from', _n)
        # print(f"i={i}\nitems={len(items)}")
        # pp(items)
        # print(f"\nchain={chain}\nparent=")
        # pp(parent)

        return items

    def safe_merge(self, rs, subrs):
        for k, v in subrs.items():
            d = rs.get(k, set())
            if str(k).startswith('_'):
                d |= v
            else:
                d = v
            rs[k] = d
        return rs

    def is_tuple(self, item):
        return isinstance(item, tuple)

    def tag_complete(self, tag, store, key='_complete'):
        _com = store.get(key, set())
        _com.add(tag)
        store[key] = _com
        return store

class Walker(object):
    i = 0
    max = 300

    def __init__(self, graph, start_entity):
        self.graph = graph
        self.start_entity = start_entity

    def __iter__(self):
        return self._step(self.graph.get_position(self.start_entity))
        # return self.step(self.start_entity)

    def __next__(self):
        if self.i > self.max:
            raise StopIteration()

    def step(self, start_entity):
        return self._step(self.graph.get_position(start_entity))


    def _step(self, pos, reverse=False, history=None):
        print('Accept', pos)
        history = history or ()
        next_func = self.graph.get_next_reverse if reverse else self.graph.get_next
        _next = tuple(next_func(pos))
        # children = tuple(_next)

        _next_children = self.graph.as_names(_next)
        print('next', _next_children)

        if len(_next) == 0:
            return

        child = self.graph.as_name(pos)
        self.i += 1

        yield (pos, _next_children, history)

        history += (pos,)
        print('>>next', _next_children)
        for c in _next:
            n = self.graph.as_name(c)
            print('>>. step child,', c, n)
            self._step(c, reverse, history)
            # child = self.graph.as_name(child_pos)
            # cc = tuple(next_func(child_pos))
            # _next_children = self.graph.as_names(cc)

        # raise StopIteration()




class GraphWalker(object):

    def walk(self, start_entity):
        return Walker(self, start_entity)#.step(start_entity)


class GraphNodeBind(object):
    """Provide functions to apply "bind" methods of graphnodes to
    the flatmap.
    """
    def bind(self, name, node):
        """Given the identity of the graph position, and an instance of the graph
        node, assign the node as a hook to the name.
        """
        print('Bind', name, node)


class FlatGraph(GraphNodeConnect, GraphNameKeys, GraphRecord, GraphRead, GraphWalker, GraphNodeBind):

    def __init__(self):
        super().__init__()
        self._create_names()

    def get_flows(self, entity, with_parent=False, rev=False, until=None):
        chain = self.chains(entity, reverse=rev, until=until)
        flat_chains = self.flat_chains(chain)
        rows = self.filter_complete(flat_chains)
        if len(rows) == 0:
            rows = self.filter_toplevel(flat_chains)

        if with_parent:
            return tuple( (entity,) + tuple(x) for x in rows)
        return rows

    def filter_toplevel(self, flatgraph):
        return self.filter_key(flatgraph, key='_toplevel')

    def filter_key(self, flatgraph, key='_complete'):
        com = flatgraph.get(key, ())
        return tuple(flatgraph[x] for x in com)

    def filter_complete(self, flatgraph):
        return self.filter_key(flatgraph, key='_complete')

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
        _g = self.get_add_name
        self.disconnect(_g(start_entity), _g(end_entity))
        self.connect(start_entity, *nodes)

    def split(self, start_entity, end_entity):
        _g = self.get_add_name
        return self.disconnect(_g(start_entity), _g(end_entity))

    def splice_all(self, start_entity, *nodes):
        """Apply one or more nodes as the inject after the given start entity,
        moving all relations to the last given node

            g.append('torso', 'arms', 'hands', 'fingers', 'fingernails')
            g.append('hands', 'thumbs', 'thumbnails')

            hands -> thumbs  -> thumbnails
                  -> fingers -> fingernails

            g.splice_all('hands', 'palms')

            hands -> palms -> thumbs  -> thumbnails
                           -> fingers -> fingernails

        """
        start_pos = self.get_position(start_entity)
        start_connections = set(self.get_next(start_pos))
        # start entity nodes should move to end node,
        removed = self.reset_position(start_pos)
        print('start_entity connections', removed)
        end_entity = nodes[-1]
        # then connect through
        self.connect(start_entity, *nodes)
        end_pos = self.get_position(end_entity)
        print('assign_position', end_pos, removed)
        self.assign_position(end_pos, removed)
        return removed
