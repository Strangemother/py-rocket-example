"""

(env) F:/godot/python-rocket-software/py5>py example.py
Buidling mem

a.on()
Returning plug conf
running taps for Plug {'fuse'}
Fuse Tap
test_wire_power

<Fuse "fuse">pop!
Fuse Tap False
Fuse death

a.off()
Returning plug conf
running taps for Plug {'fuse'}
Fuse Tap
<Fuse "fuse"> Bizzzfizz ... futz futz
Fuse Tap False
Fuse death

fix fuse

a.on()
Returning plug conf
running taps for Plug {'fuse'}
Fuse Tap
test_wire_power
power feed
Fuse Tap True
Tap meddled
test_wire_power
! brightness 0.5

a.on()
Returning plug conf
running taps for Plug {'fuse'}
Fuse Tap
test_wire_power
power feed
Fuse Tap True
Tap meddled
test_wire_power
! brightness 1.0

"""
import asyncio
from things import Lamp

async def main():
    global lamp

    lamp = Lamp()
    await lamp.setup()

    await plug_on(4)
    await fix_fuse()

    await plug_on(1)
    await plug_on(2)


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
