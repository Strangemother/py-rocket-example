import nodes

class Event(object):

    recursive_entropy = 1
    min_entropy = .2
    recursive_penalty = .6
    max_depth = 9
    depth = -1

    def clone(self):
        v = self.__class__()
        v.__dict__.update(self.__dict__.copy())
        return v

    def above_entropy(self):
        return self.recursive_entropy > self.min_entropy

    def __str__(self):
        return f"<{self.__class__.__name__} {repr(self)}>"

    def __repr__(self):
        return f'entr. {self.depth}/{self.recursive_entropy:.2f}, {self.score():.2f}'

    def score(self):
        return 1.0/(1+(self.depth*self.recursive_entropy))



def bar_walk(node_or_nodelist, event=None, depth=0):
    """
    Given a start node, step forward for each connection, Keeping
    a list of the path edges; the last node in all chains.

    Consider it like a bar scanner, from left every node is scanned and
    a "bar" of nodes as the next steps. Scanning all nodes reveals zero
    or more next nodes.

    Each step yields a column. Recursive after Z >A ..

        A > B > C > D > E
                X > Y > Z > A > B
            G > H > I           G
                    E           P
            P > Q > R > S > V
                V
    """
    e = event or Event()
    e.depth = depth
    step = True
    _nodes = node_or_nodelist.get_next_flat()

    res = {x.name: x for x in _nodes}

    is_exit = lambda x: isinstance(x, nodes.ExitNode)

    while step:
        v = res.values()
        step = bool(len(v))
        yield tuple(v)

        new_res = {}
        for name, node in res.items():
            if is_exit(node): continue
            _next = node.get_next_flat()

            for next_node in _next:
                if is_exit(next_node): continue
                new_res[next_node.name] = next_node
        res = new_res

    # raise StopIteration


def walk(node, event=None, depth=0):
    """A Dumb walker to traverse any given step until max depth
    """
    e = event or Event()
    e.depth = depth
    sp = '  ' * (depth)
    if depth > e.max_depth:
        print(sp, '! HIT DEPTH:', node)
        return e

    nl = node.next
    l = len(nl)

    for node_name in nl:
        next_node = nl[node_name]
        if isinstance(next_node, nodes.ExitNode):
            # We don't step through an exit node
            print(sp, 'X EXIT')
            continue

        if node.name == next_node.name:
            e.recursive_entropy *= e.recursive_penalty

        walk_next(e.clone(), node, next_node, depth, do_line=l>1)


def walk_next(event, node, entity, depth=0, do_line=False):

    edges = node.graph.get_edges(node, entity)
    sp = '  ' * (depth)
    l = '|' if do_line else '-'
    can_continue = (depth < event.max_depth) and event.above_entropy()
    print(sp, "X" if not can_continue else l, entity, event)

    for i, edge in enumerate(edges):
        enode = edge.on_event(event, index=i, edges=edges)
        if enode.name != entity.name:
            print('Edge returned an alternative end node')
            walk_next(node, enode)
    else:
        if can_continue:
            return walk(entity, event, depth+1)


"""
A dumb single walker does not split, but instead walks as a single stepper
Upon death it restarts at the last fork to proceed again.

If the walker steps through an already visited node, it may cease the walk,
and proceed with other walks
"""
