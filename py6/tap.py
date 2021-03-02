"""Feeds connect elements like an event listener / pusher
"""

from collections import defaultdict
import asyncio
import time
from memory import MemoryFunc
from base import ClassID

from exceptions import DropEvent


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


