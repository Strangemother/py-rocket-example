import sys
sys.path.append('F:/godot/python-rocket-software/graph3')
# import main as g3
# from g3 import Connections
import g3

sys.path.append('F:/godot/python-rocket-software/webcom/cli_client')
import client as cli_client

cli_client.background_connect()


class ViewConnections(g3.Connections, cli_client.Client):

    _names = None
    _edge_names = None

    def __init__(self, uuid):
        print('Setup Pins')
        self._names = set()
        self._edge_names = set()
        self.client_id = uuid
        super().__init__()

    def store_edge(self, temp_edge, direction):
        temp_edge = super().store_edge(temp_edge, direction)
        node_ids = temp_edge.get_node_ids()
        print('Store and add edge', node_ids)

        if (node_ids in self._edge_names):
            print('Skipping (existing) edge send {node_ids}')
            return temp_edge

        self._edge_names.add(node_ids)
        self.send_edge(temp_edge)

        return temp_edge

    def send_edge(self, temp_edge):
        """Announce a new edge to the clients.
        """
        entities = temp_edge.get_entities()
        v = '-'.join(map(str, (safe(x).get('id') for x in entities)))
        styles = {
            "smooth": {
              # "type": "cubicBezier",
              "forceDirection": "none",
              "roundness": 0.75
            },
            'width':4,
            'label': None, #'', #v,
            'arrows': {
                'to': {
                    'enabled': True,
                    'type': 'circle',
                    'scaleFactor': .4,
                },
            },
            'font': {
                    "strokeColor": '#000',
                    "color": '#CCC'
                },
        }

        cli_client.add_edge(*temp_edge.get_node_ids(), **styles)

    def connect(self, *units, direction=g3.FORWARD, data=None, edge=None, **extra):

        unit_set = set(units)
        new_node_names = unit_set - self._names
        self._names.update(unit_set)

        self.send_new_units(new_node_names, **extra)

        edges = super().connect(*units,
                                direction=direction,
                                data=data, edge=edge)

    def send_new_units(self, nodes, **extra):
        print('Send new units', nodes)
        for name in nodes:
            cli_client.add_node(**safe(name), **extra)

    def make_id(self, unit):
        return id(unit)



def safe(entity):
    if hasattr(entity, 'to_json'):
        return entity.to_json()
    n = entity.__name__ if hasattr(entity, '__name__') else str(entity)
    return {'id': id(entity), 'label':n,}

# import json
class Compute(object):

    def __init__(self, name, op_val=1, value=1, **styles):
        self.name = name
        self._value = value
        self.op_val = op_val
        self.styles = styles
        # live push stack per steps until drain
        self.stack = ()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        cli_client.update_node(id(self), label=self.label)

    @property
    def label(self):
        return f"{self.name}({self.op_val}): {self.value:.2f}"

    def push(self, value):
        self.stack += (value, )

    def drain(self):
        """Change the internal value given the complete stack from
        any previous pushes.
        """
        res = sum(self.stack) * self.op_val
        print(f'Drain {self}:', self.stack, '==', res)
        self.stack = ()
        self.value = res

        return res


    def to_json_graph(self):


        r = {
            'id': id(self),
            'label': self.label,
            }
        return r

    def to_json_vis(self):
        r = {
            'id': id(self),
            'label': self.label,
            'color': '#288960',
            'shape': 'box',
            'font': {
                    'color': '#ddd'
                }
            }

        r.update(self.styles)
        return r

    def to_json(self):
        return self.to_json_graph()

    def __str__(self):
        return f'C({self.label})'

NOISE_GATE = 0.001

def step(g, nodes=None, values=None, start=None):
    if values is None:
        values = ()

    if nodes == None:
        # In the first instance, the live 'a' node is the only start list
        nodes = (g(start), )
        print('using node', nodes)

    r = set()
    for i, node in enumerate(nodes):
        value = 1
        if len(values) > i:
            value = values[i]
        if abs(value) < NOISE_GATE:
            # stop runaway 64 bit floars:
            value = 0

        next_nodes = push_value(node, value)
        r.update(set(next_nodes))

    vs = ()
    for node in nodes:
        vs += (node.data.drain(),)
    return tuple(r), vs

def push_value(node, value):
    node.data.push(value)
    return node.next_nodes


def run_main():

    g = ViewConnections(123)

    a = Compute('a', 1.3, color='#045633')
    b = Compute('b', 0.6)
    c = Compute('c', 0.7)
    d = Compute('d', 0.8)

    g.connect(a, b, c, d, a)


    """
    Now the step function is prepared we can perform some recursive loop
    """

    # The first run may be anonymous
    next_nodes, values = step(g, start=a)
    # followed by recursive stepping
    next_nodes, values = step(g, next_nodes, values)
"""
>>> next_nodes, values = step(next_nodes, values)
Drain C(c: 0.70): (0.3,) == 0.21
... Drain C(d: 0.80): (0.21,) == 0.168
... Drain C(a: 1.00): (0.168,) == 0.168
... Drain C(b: 0.30): (0.168,) == 0.0504
... Drain C(c: 0.21): (0.0504,) == 0.010584
... Drain C(d: 0.17): (0.010584,) == 0.001778112
... Drain C(a: 0.17): (0.001778112,) == 0.000298722816
... Drain C(b: 0.05): (0,) == 0.0
... Drain C(c: 0.01): (0,) == 0.0
... Drain C(d: 0.00): (0,) == 0.0
...
"""
# b_t = step(nodes=g(a).next_nodes, value=1)


# es = Connections()
# sleep(1)
# c.connect(*'ABCDE')
# sleep(2)
# c.connect(*'CAB')
# sleep(2)
# v = c.connect(*'HORSE')
