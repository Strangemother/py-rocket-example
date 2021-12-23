import asyncio

async def main():
    print('Hello ...')
    f= Foo()
    v = await f.fruit()
    print('... World!', v)

class Foo(object):

    async def fruit(self):
        return 'apple'

    def fruit(self):
        return 'apple'


# Python 3.7+
asyncio.run(main())
print('after async')
