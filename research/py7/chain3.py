"""
The chain is ran on a circuit, computing at a circuit FPS

For every major tick (modulo 100) the power event _updates_ the amount
of goubmles to store within the unit (or wire), digesting the amount per minor tick
(a phase of the circuit modulo.)

Tick 0: Send Event 4v 3a
        Unit recieves event and stores 1k goubmles
tick n[+1]: every tick occurs at 1 cycle of the cicuit hertz (e.g. 1/100 of
            the cicuit modulo)
            The minor tick _digests_ and uses 1 charge cycle, with 1/100 goubmles

The amount of goubmles used, isa ratio of the 'optimum' over the given

Overpower

    Major Tick:    4v/1A == 100G   | 100 Mod
    LED:
        optimum:   2v/.5A == 50G  | 100 Mod
        minor (1/100):
            wanted: .5 (50G/100M)
            given: 1G (100G/100M)
            Out 2(% == *100) (1/.5)

Underpower:

    Major Tick:    1v/1A == 25G   | 100 Mod
    LED:
        optimum:   2v/1A == 50G  | 100 Mod
        minor (1/100):
            wanted: .5 (50G/100M)
            given: .25G (25G/100M)
            Out: .5(% == * 100) (.25/.5)

"Out" identifies the ratio (percent of wanted) energy for work. An LED wants 100%
To resist enough energy, producing an amp load, and excess heat.

This _out_ is converted to work through a resistance calcuation.

The extra should be a percentile of the overcharge, applied to each minor step
as a burn rate. For example, if an LED required 100 goubmles for 1 major, but recieves
200, the output is 101%, as 100% goubmles, and 100%/modulo extra.

    Major Tick:    1v/1A == 25G   | 100 Mod
    optimum:       1v/1A == 25G   | 100 Mod
    Minor          100% per tick

    Major Tick:    2v/2A == 100G   | 100 Mod
    optimum:       1v/1A == 25G    | 100 Mod
    Minor          100% per tick  + extra
"""

class PowerPacket(object):

    volts = 3
    amps = 1
    ticks = 100

    def goubmles(self, modulo):
        return self.volts * self.amps * modulo

    def goubmles_minor(self, modulo):
        return self.goubmles(modulo) / self.ticks

def make_minor(v=3, a=1):
    # Run a packet for 1 major
    main = PowerPacket()
    main.volts = v
    main.amps = a
    led = PowerPacket()
    led.volts = 3
    led.amps = .5

    # Circuit FPS
    modulo = 100

    mgm = main.goubmles_minor(modulo)
    lgm = led.goubmles_minor(modulo)
    led_minor = lgm, mgm
    return led_minor, ()
    """
    the extra is the percentile of the overall power as (goubmles / modulo)
    """

print("1, .5 ", make_minor(1,.5))
print("2, .5 ", make_minor(2,.5))
print("3, .5 ", make_minor(3,.5))
print("1, 1  ", make_minor(1,1))
print("2, 1  ", make_minor(2,1))
print("3, 1  ", make_minor(3,1))
