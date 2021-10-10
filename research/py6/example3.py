import asyncio
from things import Lamp
import parts

from functools import partial
from string import ascii_lowercase

from tap import Tap


class Device(parts.FeedEmit):
    enabled = True

    async def on_feed(self, event):
        uuid = self.get_id()
        print(f'{uuid} {self}.on_feed({event})', event)
        if self.enabled:
            try:
                return await self.emit_feed(event)
            except parts.DropEvent as exc:
                await self.emit_error_dropevent(exc, event)
        raise parts.DropEvent(self)


async def main():
    items = await get_items()
    feed, power = await connect_linear_feeds(items)

    # a = items[0]
    # print('\n switch on', a)
    # await a.on()

    # e=items[10]
    # print('e is',e)
    # e.enabled=False
    print('\n\n --- \n\n')
    for i in items:
        print('On:', i)
        await i.on()

    # import pdb; pdb.set_trace()  # breakpoint 3a5de20b //

    # await a.on()
    # mem = items[3]._mem

    return feed
    # import pdb; pdb.set_trace()  # breakpoint e5643923 //


async def get_items():
    items = tuple(Device(letter) for letter in ascii_lowercase)
    # item = items[-1]
    # item.on_feed = partial(announce_on_feed, item)

    return items


async def announce_on_feed(device, event=None):
    print(f'HIT! {device}', event)
    await device.emit_feed(event)


async def connect_linear_feeds(items):
    """Build a Feed from A to B for every item and its sibling.
    The last item will not have a unique feed

        items = (A, B,C[, ...])
        returns (
            Feed(A, B),
            Feed(B, C),
            [Feed(C, ...),]
        )
    """
    feeds = ()
    li = len(items)

    for i, _a in enumerate(items):
        i1 = i+1
        if i1 >= li: break

        feed = parts.Feed(uuid=f'feed-{i}-{i1}')
        await feed.connect(a=_a, b=items[i1])
        feeds += (feed,)

    power = await connect_power_chain(items)
    return feeds, power

from condition import Condition

async def connect_power_chain(items):
    t = {x.uuid: True for x in items}
    table = {x.uuid:int(x._on) for x in items}
    power = Condition(target=t, table=table)

    tap = Tap(owner=power)
    tap.tap = partial(tap_func, tap)
    for item in items:
        print('>> ', item)
        await tap.connect(item)
    # import pdb; pdb.set_trace()  # breakpoint c2130bb8 //

    return power

async def tap_func(tap, event):
    # print('Tap Event', tap.owner, event)
    ro = await tap.get_memory().resolve(event.owner)
    tap.owner.set(ro.uuid, event.get('on'))


if __name__ == '__main__':
    feeds = asyncio.run(main())
