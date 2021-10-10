"""Feeds connect elements like an event listener / pusher
"""

from collections import defaultdict
import asyncio
import time


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

    print_log = False

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
            entity = await self.resolve(uuid)
            if entity is None:
                continue

            try:
                final_event = await self.run_taps(event)
            except DropEvent as drop_error:
                tap = drop_error.args[0]
                await self.log('Dropped Exception:', tap.key)
                continue

            await self.log('emitting to', entity, event)
            await entity.on_feed(event)
        await self.log('Done', _id, cons)

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
            tap_ids = self.taps.get(feed_id, ())
            for t in tap_ids:
                tap_unit = await self.resolve(t)
                event = await tap_unit.perform(event)
        return event

    async def add_tap(self, tap, other):
        _id = tap.get_id()
        other_id = other.get_id() if hasattr(other, 'get_id') else other

        self.taps[other_id].add(_id)
        self.references[_id] = tap

        return other_id


class DropEvent(Exception):
    pass


class MemoryFunc(object):
    """A single method to recall the Memory instance for this unit to
    reference. As the Memory exists without interaction, _using_ a memory
    will produce the correct feed stack.

        mem = MemoryFunc().get_memory('default')
        mem.connect(a,b)
    """

    memory_name = 'default'
    _mem = None

    def get_memory(self):
        if self._mem is None:
            self._mem = Memory.get_memory(self.memory_name)
        return self._mem

    def get_id(self):
        return id(self)


class ClassID(object):
    """Apply one method get_id() to return self.uuid or the class name
    if UUID is none.
    """
    uuid = None

    def get_id(self):
        return self.uuid or self.__class__.__name__


    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.get_id()}">'

class Tap(ClassID, MemoryFunc):
    """A 'tap' captures an event upon the _watched item_ `emit_feed`

    Connect a Tap to the feedable unit

        a = FeedEmit('A')
        tap_a = Tap()
        await tap_a.connect(a)

        f_a_b = Feed().connect(a, other)
        tap_f_a_b = Tap()
        tap_f_a_b.say = "{id} Feed tap meddle to {other}"
        tap_f_a_b.key = 'monkey'
        await tap_f_a_b.connect(f_a_b)
    """

    enabled = True

    passthrough = False
    say = "Tap meddled"
    key = 'meddled'

    def __init__(self, uuid=None, connect=None):
        self.uuid = uuid
        self.connected = connect

    async def connect(self, a=None):
        mem = self.get_memory()
        item = a or self.connected
        other_id = await mem.add_tap(self, item)
        self.other = other_id

    async def perform(self, event):
        if self.enabled is False:
            print(f'{self.key} dropping event')
            # return DROP
            raise DropEvent(self)

        if self.passthrough:
            print(f'Sleeping Tap {self.key}')
            return event

        return await self.tap(event)

    async def tap(self, event):
        s = self.say.format(**self.__dict__, id=self.get_id())
        print(s)
        event._data[self.key] = True
        return event


class Event(ClassID):
    origin = None
    _data = None

    def __init__(self, origin, data):
        self.uuid = id(self)
        _origin = origin
        if isinstance(origin, str) is False:
            _origin = origin.get_id()
        self.origin = _origin
        self._data = data


class FeedMixin(MemoryFunc):

    event_class = Event

    async def emit_feed(self, event):
        """Send a feed event to feed acceptors, populating the given
        event with the owner ID
        """
        if isinstance(event, Event) is False:
            event = self.event_class(self, event)
        _id = self.get_id()
        # event['_owner'] = _id
        event.owner = _id
        #print('Emit event', _id, event.owner, event._data)
        # time.sleep(0.8)
        mem = self.get_memory()
        await mem.emit(event)

    async def on_feed(self, event):
        """A connected Feed called upon this unit with the given event.
        Digest the event returning nothing
        """
        # Tap here.
        owner = event._owner
        print(f'Feed to {self} from {owner}')


class Feed(ClassID, MemoryFunc):

    def __init__(self, uuid=None, a=None, b=None):
        self.uuid = uuid
        self.a = a
        self.b = b

    # _owner = None
    async def connect(self, a=None, b=None):
        # _id = self.get_id()
        mem = self.get_memory()
        ida, idb = await mem.connect(a or self.a, b or self.b, feed=self)
        self.ida = ida
        self.idb = idb


class FeedEmit(ClassID, FeedMixin):

    def __init__(self, uuid=None):
        self.uuid = uuid

    async def on(self):
        print('a.on()')
        await self.emit_feed({'on': True})

    async def off(self):
        print('a.off()')
        await self.emit_feed({'on': False}, )

    async def on_feed(self, event):
        uuid = self.get_id()
        print(f'{uuid} recv on_feed', event.get_id(), event._data)
        await self.emit_feed(event)



async def main():
    a = FeedEmit('A')
    b = FeedEmit('B')
    c = FeedEmit('C')
    d = FeedEmit('D')

    f_a_b = Feed()
    await f_a_b.connect(a, b)

    f_b_c = Feed()
    await f_b_c.connect(b, c)

    f_c_d = Feed()
    await f_c_d.connect(c, d)

    tap_a = Tap()
    await tap_a.connect(a)

    tap_f_a_b = Tap()
    tap_f_a_b.say = "{id} Feed tap meddle to {other}"
    tap_f_a_b.key = 'monkey'
    await tap_f_a_b.connect(f_a_b)

    await a.on()
    await c.on()


if __name__ == '__main__':
    asyncio.run(main())
# print('\nanother:')
# tap.passthrough = True
# tap.enabled = False
# # tapb.passthrough = True
# a.on()

