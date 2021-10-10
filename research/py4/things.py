import parts
import core
from sockets import PlugUK


class Lamp(core.Base, core.Connectable, core.StateManagerMixin, parts.OnOffSwitch):
    socket_type = PlugUK.MALE
    socket_class = PlugUK


class WallSocket(core.Base, core.Connectable, parts.OnOffSwitch):
    socket_type = PlugUK.FEMALE
    socket_class = PlugUK

