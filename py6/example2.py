
import asyncio
from things import Lamp

async def main():
    global lamp


    lamp = Lamp()
    await lamp.setup()
    await plug_on(2)

    print('Toggle on switch')
    lamp.switch.toggle()

    # lamp.switch.toggle()

    # await fix_fuse()



async def fix_fuse():
    await lamp.plug.off()
    print('\nfix fuse')
    # Ooh no, I hope that didn't really explode
    lamp.fuse.broken = False


async def plug_on(amps=None):
    if amps is not None:
        lamp.plug.amps = amps
    await lamp.plug.on()
    await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
