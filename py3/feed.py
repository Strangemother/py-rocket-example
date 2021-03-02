"""Asynchronous user input function including ainput
"""
import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
import sys
from parts import *


async def ainput(prompt: str = ""):
    with ThreadPoolExecutor(1, "AsyncInput", lambda x: print(x, end="", flush=True), (prompt,)) as executor:
        return (await asyncio.get_event_loop().run_in_executor(
            executor, sys.stdin.readline
        )).rstrip()


async def wait_info(base):
    print('wait_info', base)
    while True:
        await ei(base)

async def ei(base):
    res = await ainput('> ')
    if len(res) == 0:
        return
    try:
        er = eval(res)
        if er is not None:
            print('<', er)
    except Exception as exc:
        traceback.print_exc()
    except KeyboardInterrupt:
        print('Cancel')
        return


def add_light(base):
    global light
    l = Light(watts=4)
    base.plugs.add(l)
    light = l
    return l
