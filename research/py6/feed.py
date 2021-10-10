"""Feeds connect elements like an event listener / pusher
"""

from collections import defaultdict
import asyncio
import time

from memory import MemoryFunc
from exceptions import DropEvent
from base import ClassID
from base import Event


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
    _on = False

    def __init__(self, uuid=None):
        self.uuid = uuid

    async def on(self):
        print(f'{self}.on()')
        self._on = True
        await self.emit_feed({'on': self._on})

    async def off(self):
        print(f'{self}.off()')
        self._on = False
        await self.emit_feed({'on': self._on})

    async def on_feed(self, event):
        uuid = self.get_id()
        print(f'{uuid} {self}.on_feed({event})', event._data)
        await self.emit_feed(event)

    async def emit_error_dropevent(self, exc, event):
        print(f'{self} next device dropped.', exc.args)

