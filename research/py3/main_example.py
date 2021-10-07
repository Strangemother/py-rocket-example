"""Simulate more Device <> plugged into <> device.
"""
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from feed import wait_info
from afs import BaseSystem
import time
from aio import forever_futures


def main(**config):
    base = BaseSystem()
    # loop, future = create_loop(new_system(base, **config))
    async_cos = (
        base.loop(),
        wait_info(base),
    )

    return forever_futures(async_cos)



def old_main(**config):
    base = BaseSystem()
    # loop, future = create_loop(new_system(base, **config))
    future = asyncio.gather(
        base.loop(),
        wait_info(base),
        )

    print('Init future', future)
    future.add_done_callback(sys_done)
    # append_task(loop, wait_info(base))
    # co_run(wait_info,base)
    # loop.run_until_complete(future)
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Top Keyboard Interrupt')
        loop.stop()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    return future



async def new_system(base, **config):
    print('New System')
    print('Perform init')
    # base = make(**config)

    try:
        await base.loop()
    except asyncio.CancelledError as e:
        raise e
    except Exception as e:
        traceback.print_exc()

    return base


def make(**config):
    base = BaseSystem()
    return base


if __name__ == '__main__':
    main()


