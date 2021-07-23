def get_chains(graph, start, end, root_start_node=None, depth=-1, r=None,
    index=-1, stash=None, edge_count=-1, keep_exit_node=True, keep_noedge=None):
    """
    If None, The system checks for NoEdge and drops the edge.
    If True, enforce the edge keep, allowing a null edge within the result
    If False, do not add any edge; (edgeless)
    """
    # keep_noedge = True

    stash = stash or {}
    r = r or []

    if depth > 10:
        print(' --- Recurse protection.')
        return r

    nodelist = start.get_next()

    ignore_node = False
    if isinstance(start, ExitNode):
        if keep_exit_node is False:
            ignore_node = True

    if ignore_node is False:
        r = add_link(r, start, depth, index)

    # stash[id(start)] = depth
    for i, node_name in enumerate(nodelist):
        # r = r.copy()
        # print(' '*depth, node_name)
        next_node = nodelist[node_name]
        chain_step(
            graph=graph,
            current_node=start,
            next_node=next_node,
            end=end,
            root_start_node=root_start_node or start,
            depth=depth+1,
            r=r,
            index=i,
            stash=stash,
            edge_count=edge_count,
            keep_exit_node=keep_exit_node,
            keep_noedge=keep_noedge,
            node_name=node_name,
        )
    return r


def chain_step(graph, current_node, next_node, **kw):
    edges = get_edges(graph, current_node.name, next_node.name)
    return chain_edges(graph, edges, current_node, next_node, **kw)


def get_edges(graph, start_name, next_name):
    edges = graph.get_edges(start_name, next_name)
    print('edges:', edges)
    if len(edges) == 0:
        edges = (NoEdge(), )
    return edges


def chain_edges(graph, edges, current_node, next_node, **kw):

    orig_r = kw.get('r').copy()

    for edge_index, edge in enumerate(edges):
        v = chain_through_edge(
                graph=graph,
                edge=edge,
                current_node=current_node,
                next_node=next_node,
                orig_r=orig_r,
                edge_index=edge_index,
                **kw
            )
    return kw.get('r')


def store_history(graph, history, stash):
    v = Chain(graph, history)
    stash[id(history)] = v
    return v


def is_exit_node(node):
    return isinstance(node, ExitNode)


def chain_through_edge(graph, edge, current_node, next_node, **kw):

    g = kw.get

    edge_count = g('edge_count')
    keep_noedge = g('keep_noedge')

    is_noedge = isinstance(edge, NoEdge)
    keep_edge = keep_noedge if keep_noedge is not None else (not is_noedge)

    if keep_edge:
        orig_r = g('orig_r')
        edge_index = g('edge_index')

        history = orig_r.copy()
        kw['edge_count'] += 1

        add_edge_link(history, edge, current_node, next_node, kw['edge_count'], edge_index)

    return continue_chain(graph, current_node, next_node, history, **kw)


def continue_chain(graph, current_node, next_node, history, **kw):
    g = kw.get
    depth = g('depth')
    stash = g('stash')
    index = g('index')
    keep_exit_node = g('keep_exit_node')

    if is_exit_node(next_node):
        if keep_exit_node is not False:
            add_link(history, next_node, depth+1, index)
        return store_history(graph, history, stash)

    return get_chains(
        graph=graph,
        start=next_node,
        end=g('end'),
        root_start_node=g('root_start_node') or current_node,
        depth=depth+1,
        r=history,
        index=index,
        stash=stash,
        edge_count=g('edge_count'),
        keep_exit_node=keep_exit_node,
        keep_noedge=g('keep_noedge'),
    )
