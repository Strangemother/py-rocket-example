
import asyncio

def create_loop(coro_func):
    """Perform an async start of a new_sysyem, returning a promise
    """
    print('Start', coro_func)
    loop = asyncio.get_event_loop()
    co_promise = loop.create_task(coro_func)
    return loop, co_promise


def append_task(event_loop, coro_func):
    return asyncio.ensure_future(coro_func, loop=event_loop)


def co_run(func, *a, **kw):
    """Perform an async start of a new_sysyem, returning a promise
    """
    loop = asyncio.get_event_loop()
    co_promise = loop.create_task(func(*a, **kw))
    return co_promise


def forever_futures(coroutines, **config):
    """Given a tuple of coroutine functions, apply to a gather and run
    the current event_loop.

    """
    # loop, future = create_loop(new_system(base, **config))
    future = asyncio.gather(*coroutines)
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


def sys_done(task):
    """store the task result to a global `system` variable, containing the
    newly created AdamFlightSystem
    """
    global fs
    fs = task.result()
    time.sleep(1)
    print('\nSystem Done', fs)

    # co_run(push_on_switch)
