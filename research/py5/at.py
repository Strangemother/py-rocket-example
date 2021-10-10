import asyncio


class MyThing(object):
    def say(self):
        print('sync Apples')

    async def say(self):
        print('async Apples')



async def main():
    loop = asyncio.get_running_loop()

    t = MyThing()
    await t.say()
    # # 2. Run in a custom thread pool:
    # with concurrent.futures.ThreadPoolExecutor() as pool:
    #     result = await loop.run_in_executor(
    #         pool, blocking_io)
    #     print('custom thread pool', result)

asyncio.run(main())
