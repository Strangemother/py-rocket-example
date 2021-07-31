import pathlib
import json



def add_ends(graph):
    nodes = ()
    edges = []
    # Add as nodes
    for enode in (graph.get_start_node(), graph.get_end_node(),):
        nn = enode.name
        n = {
            "label": str(nn),
            "id": nn,
            "color": '#e36d6d'
        }

        nodes += (n,)

    enode = graph.get_start_node()
    for next_name in enode.get_next_ids('forward'):
        item = {
            "from": enode.name,
            "to": next_name,
            }
        edges.append(item)

    enode = graph.get_end_node()
    for next_name in enode.get_next_ids('forward'):
        item = {
            "from": next_name,
            "to": enode.name,
            }
        edges.append(item)

    return nodes,edges


def add_split_ends(graph):
    nodes = ()
    edges = []


    ## Add as single nodes
    # for enode in (graph.get_start_node(), graph.get_end_node(),):
    #     nn = enode.name
    #     n = {
    #         "label": str(nn),
    #         "id": nn,
    #         "color": '#e36d6d'
    #     }

    #     nodes += (n,)

    START_NODE_COLOR = '#d9ed53'
    enode = graph.get_start_node()
    for ni, next_name in enumerate(enode.get_next_ids('forward')):
        nn = enode.name
        _id = f'{nn}_{ni}'
        item = {
            "from": _id,
            "to": next_name,
            }

        n = {
            "label": str(nn),
            "id": _id,
            "color": {
                "background": START_NODE_COLOR,
                "border": START_NODE_COLOR,
                'highlight': {
                    "background": "#444",
                }
            }
        }

        edges.append(item)
        nodes += (n,)


    enode = graph.get_end_node()
    for ni, next_name in enumerate(enode.get_next_ids('forward')):
        nn = enode.name
        _id = f'{nn}_{ni}'
        item = {
            "from": next_name,
            "to": _id,
            }

        n = {
            "label": str(nn),
            "id": _id,
            "color": '#e36d6d'
        }
        nodes += (n,)
        edges.append(item)

    return nodes,edges



def to_visjs_json(g, path='./g_vis.json',  split_ends=True, exit_nodes=True, direction='forward'):

    i = 0
    ft = g.tree[direction]
    node_names = tuple(g.data.keys())
    edges = []
    nodes = ()

    if exit_nodes:
        nodes ,edges = [add_ends, add_split_ends][split_ends](g)
    # nodes,edges = add_split_ends(g)

    # nodes
    for index, nn in enumerate(node_names):
        node = g.get_node(nn)
        _node = {
                "id": nn,
                "label": str(nn),
                # "size": 5,
                # "x": node.x,
                "group_index": index,
            }
        nodes += (_node,)

    # edges
    for node_index, (node_name, d) in enumerate(ft.items()):
        for edge_i, (other_node, count) in enumerate(d.items()):
            i += 1
            item = {
                    "from": node_name,
                    "to": other_node,
                    "meta": count,# (float(count) * 1.0 ) + 2,
                    "title": count,
                    "node_index": node_index, # x
                    "edge_index": edge_i, # y
                    "x": node_index,
                    "y": edge_i,
                    }
            edges.append(item)

    fp = pathlib.Path(path)
    content = {
        "edges": edges,
        "nodes": nodes,
    }
    _json = json.dumps(content, indent=4)
    fp.write_text(_json)


def to_sigmajs_json(graph, path='./g.json'):
    # nodes
    # edges
    r = []
    i = 0
    ft = graph.tree.forward
    node_names = tuple(graph.data.keys())
    nodes = ()
    for index, nn in enumerate(node_names):
        node = graph.get_node(nn)
        _node = {
                "id": nn,
                "label": nn,
                "size": 5,
                "x": index,
            }
        nodes += (_node,)

    for node_name, d in ft.items():
        for other_node, count in d.items():
            i += 1
            item = {
                    "source": node_name,
                    "target": other_node,
                    "weight": count,
                    "id": i
                    }
            r.append(item)

    fp = pathlib.Path(path)
    content = {
        "edges": r,
        "nodes": nodes,
    }
    _json = json.dumps(content, indent=4)
    fp.write_text(_json)

