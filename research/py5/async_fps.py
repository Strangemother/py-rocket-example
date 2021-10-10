import time
from aio import forever_futures

T_FPS = 100

import asyncio
from concurrent.futures import ProcessPoolExecutor

import asyncio
import concurrent.futures

def blocking_io():
    # File operations (such as logging) can block the
    # event loop: run them in a thread pool.
    time.sleep(4)

def cpu_bound():
    # CPU-bound operations will block the event loop:
    # in general it is preferable to run them in a
    # process pool.
    return sum(i * i for i in range(10 ** 7))



async def main():
    loop = asyncio.get_running_loop()

    # # 2. Run in a custom thread pool:
    # with concurrent.futures.ThreadPoolExecutor() as pool:
    #     result = await loop.run_in_executor(
    #         pool, blocking_io)
    #     print('custom thread pool', result)

    # 3. Run in a custom process pool:
    with concurrent.futures.ProcessPoolExecutor() as pool:
        resulta = await loop.run_in_executor(pool, blocking_io)
        result = await loop.run_in_executor(pool, cpu_bound)
        print('custom process pool', result)

asyncio.run(main())



def run_futures(_id):
    # loop, future = create_loop(new_system(base, **config))
    # async_cos = (
    #     async_main(_id),
    #     # async_main('2'),
    # )

    asyncio.run(async_main(_id))
    # return forever_futures(async_cos)


async def async_main(name):
    FPS = 1
    target_fps = 1.0 / T_FPS
    fps_l = ()
    AVG = 100

    while 1:

        f_sl = fps_l[-AVG::]
        start_time = time.time() # start time of the loop
        avg_fps = round(sum(f_sl)/AVG)
        # if FPS != nFPS:
        #     dv = round(T_FPS / FPS, 5)
        #     print("FPS: ", nFPS, round(diff, 5), dv, target_fps)
        nFPS = await loop_step(start_time, name, target_fps, avg_fps, FPS,)

        # target_fps = 1.0 / (T_FPS * dv)
        # if nFPS > (nFPS * .1):
        #     target_fps = dv
        fps_l = f_sl + (nFPS,)
        FPS = nFPS

async def loop_step(start_time, name, target_fps, avg_fps, FPS,):

    await run_all(name, target_fps, FPS, avg_fps)
    diff = (time.time() - start_time)
    # FPS = 1 / time to process loop
    try:
        nFPS = round(1.0 / diff)
    except ZeroDivisionError:
        return 1
    return nFPS

data = { 'count': 100_000}


async def run_all(name, delay, c_fps, avg_fps):
    v = 0 if avg_fps == T_FPS else -20
    if avg_fps > T_FPS:
        v = 20

    data['count'] += v
    d = [x for x in range(data['count'])]
    print(f"FPS {name}: {c_fps:<3}, {avg_fps:<3} - count: {data['count']}")

    # time.sleep(delay)

# if __name__ == '__main__':
#     main()
