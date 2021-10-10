from collections import defaultdict
import asyncio
import time

from exceptions import DropEvent

mem_store = {}


class Singleton(object):

    @classmethod
    def get_memory(cls, name='default'):
        mem = mem_store.get(name, None)
        if mem is None:
            print('Buidling mem')

            mem_store[name] = mem = cls()
        return mem


class Memory(Singleton):

    print_log = True

    def __init__(self):
        self.connections = defaultdict(set)
        self.references = {}
        self.taps = defaultdict(set)
        self.feeds = defaultdict(set)

    async def resolve(self, uuid):
        return self.references.get(uuid, None)

    async def connect(self, a, b, feed=None):

        ida = a.get_id()
        idb = b.get_id()
        self.connections[ida].add(idb)
        self.references[ida] = a
        self.references[idb] = b

        if feed is None:
            return ida, idb

        _id = feed.get_id()
        self.references[_id] = feed
        self.feeds[ida].add(_id)

        return ida, idb

    async def log(self, *a):
        if self.print_log:
            print(*a)

    async def emit(self, event):
        _id = event.owner
        await self.log('Finding', _id)

        cons = self.connections.get(_id, ())

        for uuid in cons:
            await self.emit_to(uuid, event)
        if len(cons) == 0:
            import pdb; pdb.set_trace()  # breakpoint 62e58c56 //

        await self.log('Done', _id, cons)

    async def emit_to(self, uuid, event):
        """Call "on_feed" for the resolved entity of the given UUID
        with the given event. If the uuid resolves None, do nothing.

        Run taps on the event for entity.on_feed. If any Tap raises a DropEvent
        The on_feed is not called.

        Return Nothing.
        """
        entity = await self.resolve(uuid)
        if entity is None:
            print('Could not resolve', uuid)
            return # continue

        try:
            event = await self.run_taps(event)
        except DropEvent as drop_error:
            tap = drop_error.args[0]
            await self.log('Dropped Exception:', tap.key)
            return # continue

        await self.log('emitting to', entity, event)
        await entity.on_feed(event)

    async def run_taps(self, event):
        """Alter the event with any waiting maps.
        """
        tap_id = event.owner
        _taps = self.taps.get(tap_id, ())
        print('running taps for', tap_id, _taps)

        for tap_uuid in _taps:
            tap_unit = await self.resolve(tap_uuid)
            event = await tap_unit.perform(event)

        for feed_id in self.feeds[tap_id]:
            feed = await self.resolve(feed_id)
            if feed:
                event = await feed.perform(event)

            tap_ids = self.taps.get(feed_id, ())
            for t in tap_ids:
                tap_unit = await self.resolve(t)
                event = await tap_unit.perform(event)
        return event

    async def add_tap(self, tap, other):
        _id = tap.get_id()
        other_id = other.get_id() if hasattr(other, 'get_id') else other
        print('Tap', other_id, 'with', tap)
        self.taps[other_id].add(_id)
        self.references[_id] = tap

        return other_id


class MemoryFunc(object):
    """A single method to recall the Memory instance for this unit to
    reference. As the Memory exists without interaction, _using_ a memory
    will produce the correct feed stack.

        mem = MemoryFunc().get_memory('default')
        mem.connect(a,b)
    """

    memory_name = 'default'
    _mem = None
    a = None
    b = None

    def __init__(self, uuid=None, a=None, b=None):
        self.uuid = uuid
        self.a = a
        self.b = b

    def get_memory(self):
        if self._mem is None:
            self._mem = Memory.get_memory(self.memory_name)
        return self._mem

    def get_id(self):
        return id(self)


    # _owner = None
    async def connect(self, a=None, b=None, owner=None):
        if owner:
            self.set_owner(owner)
        # _id = self.get_id()
        #
        a,b = a or self.a, b or self.b

        if (a is None) or (b is None):
            return

        mem = self.get_memory()
        # print('Feed::MemoryFunc::connect', a, b)
        ida, idb = await mem.connect(a,b, feed=self)
        self.ida = ida
        self.idb = idb

