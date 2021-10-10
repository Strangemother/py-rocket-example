"""Simulate more Device <> plugged into <> device.
"""
from feed import wait_info
from afs import BaseSystem
from aio import forever_futures


def main(**config):
    base = BaseSystem()
    # loop, future = create_loop(new_system(base, **config))
    async_cos = (
        base.loop(),
        wait_info(base),
    )

    return forever_futures(async_cos)


if __name__ == '__main__':
    main()


