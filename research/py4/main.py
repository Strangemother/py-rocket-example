""" devices though simple Connections and more structured utilities """
from collections import defaultdict
# from base import Base, HOST
# from connection import Connectable, ConnectionManager
# from state import StateManagerMixin, get_state_manager


from sockets import PlugUK
import parts
import core
import things

import time

def example():
    system = core.BaseSystem()
    system.bake()

    wall_socket = things.WallSocket()
    # breadboard append.
    system.bind(wall_socket)

    lamp = things.Lamp()
    # Literal plug into wall.
    con = lamp.connect_to(wall_socket)
    print(con)

    lamp.switch_on()

    time.sleep(.8)

    lamp.switch_off()

if __name__ == '__main__':
    example()
