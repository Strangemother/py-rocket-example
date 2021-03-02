import asyncio
from parts import *

class BaseSystem(FemalePlate):
    """routines base runner for all async calls.
    """
    auto_draw_power = True

    def __init__(self):
        super().__init__()
        self.ticked = {}


    async def loop(self):
        """Run the async loop.
        """
        do_loop = self.start()
        print('Do loop', do_loop)
        while do_loop:
            await asyncio.sleep(.5)
            do_loop = self.tick()

    def start(self):
        print('BaseSystem::start - Connect first plug sockets to base system')
        p = FemalePlate(socket_count=5, eggs='bacon',
            auto_draw_power=self.auto_draw_power)# watts
        # self.add_ticked(p)
        #
        # parts.FemalePlate.connect -> tickable.plug.connect_to(plate)
        self.connect(p)
        self.create_base_parts(p)
        return 1

    def add_ticked(self, tickable):
        print('Add Tickable to base', self, tickable)
        self.ticked[id(tickable)] = tickable
        # parts.FemalePlate.connect -> tickable.plug.connect_to(plate)
        self.connect(tickable)

    def create_base_parts(self, plugs):
        """Build the very base system - the breadboard of a ship system, given
        the 'plugs' base component
        """
        self.plugs = plugs

        i = [Light(_watts=10),
            Light(_watts=10)]
        plugs.add(*i)

        # for l in i:
        #     l.on()

        return 1

    def tick(self, owner=None):
        """Tick the system, return int or bool to continue to syste, tick.
        """
        # tickable = self.ticked.values()
        tickable = self.sockets
        if owner == self:
            print('Cannot plug something into itself')
            return 0
        # print('Base Tick.', self.plugs.watts_avail)
        for item in tickable:
            item.owner.tick(self)
        return 1

