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

        cli_client.add_edge(*node_ids)
        self._edge_names.add(node_ids)

        return temp_edge

    def connect(self, *units, direction=g3.FORWARD, data=None, edge=None):

        unit_set = set(units)
        new_node_names = unit_set - self._names
        self._names.update(unit_set)

        self.send_new_units(new_node_names)

        edges = super().connect(*units,
                                direction=direction,
                                data=data, edge=edge)

    def send_new_units(self, nodes):
        print('Send new units', nodes)
        for name in nodes:
            cli_client.add_node(name)

    def make_id(self, unit):
        return str(unit)


c = ViewConnections(123)
from time import sleep

print('Running Slow Loop')
# c.connect(0,1,2,3)
# es = Connections()
sleep(1)
c.connect(*'ABCDE')
sleep(2)
c.connect(*'CAB')
sleep(2)
v = c.connect(*'HORSE')
