"""Feeds connect elements like an event listener / pusher
"""

from collections import defaultdict
import asyncio
import time
from memory import MemoryFunc

from exceptions import DropEvent

class ClassID(object):
    """Apply one method get_id() to return self.uuid or the class name
    if UUID is none.
    """
    uuid = None
    _owner_id = None

    def get_id(self):
        _a = str(self._owner_id or '')
        _b = str(self.uuid or self.__class__.__name__)
        return '.'.join((_a, _b, str(id(_b))))

    def set_owner(self, owner):
        self._owner_id = owner.get_id() if hasattr(owner, 'get_id') else id(owner)


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

    def __init__(self, uuid=None, connect=None, **tap_opts):
        self.uuid = uuid
        self.connected = connect
        self.__dict__.update(tap_opts)


    async def connect(self, a=None, owner=None):
        if owner:
            self.set_owner(owner)
        mem = self.get_memory()
        item = a or self.connected
        other_id = await mem.add_tap(self, item)
        self.other = other_id

    async def perform(self, event):
        if self.enabled is False:
            print(f'Tap({self})::perform - {self.key} dropping event: {event}')
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

        # cast as event .e.g PowerEvent
        if isinstance(event, Event) is False:
            event = self.event_class(self, event)
        _id = self.get_id()
        # event['_owner'] = _id
        event.owner = _id
        #print('Emit event', _id, event.owner, event._data)
        # time.sleep(0.8)
        mem = self.get_memory()
        try:
            await mem.emit(event)
        except DropEvent as exc:
            await self.emit_error_dropevent(exc, event)

    async def emit_error_dropevent(self, exc, event):
        print(f'{self} next device dropped.', exc.args)

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

    async def perform(self, event):
        return event


class FeedEmit(ClassID, FeedMixin):

    def __init__(self, uuid=None):
        self.uuid = uuid

    async def on(self):
        print(f'{self}.on()')
        await self.emit_feed({'on': True})

    async def off(self):
        print(f'{self}.off()')
        await self.emit_feed({'on': False}, )

    async def on_feed(self, event):
        uuid = self.get_id()
        print(f'{uuid} {self}.on_feed({event})', event._data)
        await self.emit_feed(event)

    async def emit_error_dropevent(self, exc, event):
        print(f'{self} next device dropped.', exc.args)


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

