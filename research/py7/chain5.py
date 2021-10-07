"""Simplified #4

Upon a major power tick, a unit may emit an event consisting of many
Goumbles (A calc of amp * volts).

The power event travels to the attached siblings, of which _store_ the goubmles at the
start of each major power cycle. For every minor tick a unit will digest a percentile
of the current goubmles reservoir to use as energy.

The power event will cycle through the attached siblings until it reaches the original client.
Any _unused_ goubmles apply back as energy, likely heat.


       Battery 2.09, sending 0.02
    Wire recieve_power - charge: 0.23
       Wire 0.21, sending 0.02
       Resistor 9.41, sending 0.03
    LED recieve_power - charge: 0.32
>>     LED 0.28, sending 0.03
    Wire recieve_power - charge: 0.32
       Wire 0.29, sending 0.03
      Nothing to send to Wire

       Battery 2.06, sending 0.02
    Wire recieve_power - charge: 0.23
       Wire 0.21, sending 0.02
       Resistor 9.40, sending 0.03
    LED recieve_power - charge: 0.32
>>     LED 0.28, sending 0.03
    Wire recieve_power - charge: 0.32
       Wire 0.29, sending 0.03
      Nothing to send to Wire

"""

def main():
    global t
    t = Table()
    t.tick()

import time

class Table(object):

    def new_units(self):
        self.units = (
            Battery(volts=5),
            Wire(),
            Wire(),
            Wire(),
            Resistor(ohms=300),
            Wire(),
            Wire(),
            Wire(),
            LED(volts=2, amps=.2),
            Wire(),
            )

    def __init__(self):
        self.new_units()
        for i, unit in enumerate(self.units):
            unit.table = self
            unit.index = i

    def send_to_next(self, unit, power):
        i = unit.index+1
        if i >= len(self.units):
            print('  Nothing to send to', unit.name, '\n')
            return

        self.units[i].recieve_power(power)

    def tick(self, timeout=.02):
        t = 0
        # self.major()
        while True:
            time.sleep(timeout)
            t += 1
            self.minor()
            if t % 60 == 0:
                # print('done 100')
                self.major()
                # break

    def major(self):
        """Start a major tick on the units.
        """

        for unit in self.units:
            unit.major(self, self.units)

    def minor(self, count=1):
        """Start a major tick on the units.
        """
        for i in range(count):
            for unit in self.units:
                unit.minor()


class Unit(object):

    # how many slices per major tick
    minor_delta = 10
    # The length of time for a power event (1 sec)
    time_delta = 1
    charge = 0
    charge_slice = 0
    resistance = 0.01
    _power = None

    def __init__(self, **kw):
        self.name = self.__class__.__name__
        self.charge = 0
        self.__dict__.update(kw)
        self.setup()

    def setup(self):
        pass

    def recieve_power(self, power):
        self._power = power
        self.charge += power.goubmles()
        # print(self.name, 'recieve_power - charge: {:.2f}'.format(self.charge))

    def major(self, table, units):
        """Start a major tick on the units.
        """
        pass

    def get_charge_slice(self):
        """return one minor-tick percentile of the given reservoir of charge
        in goubmles/
        """
        return self.charge * (self.minor_delta * self.resistance)

    def minor(self):
        return self.pump_power_slice()

    def pump_power_slice(self):
        if self._power is None:
            print(self.name, 'no charge')
            return

        v = self.get_charge_slice()
        charge_slice = Goumbles(v, volts=self._power.volts, amps=self._power.amps)
        # charge_slice.count = v
        # v = self.charge * cv * (self.resistance)
        self.charge -= v
        print('  ',self.name, f'{self.charge:.2f}, sending {v:.2f}')
        self.table.send_to_next(self, charge_slice)


class Power(object):

    volts = 1
    amps = .1

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def goubmles(self):
        return self.volts * self.amps


class Goumbles(object):

    def __init__(self, count, **kw):
        self.count = count
        self.__dict__.update(**kw)

    def goubmles(self):
        return self.count


class Battery(Unit):
    resistance = 1/1000
    total = 1000 # goubmles

    def setup(self):
        peak_amps = self.get_peak_amps()
        power = Power(volts=self.volts, amps=peak_amps)
        self._power = power
        self.charge = power.goubmles()

    def get_peak_amps(self):
        """Return the peak amps the battery should emit given
        the circuit setup.
        """
        return 1

    def major(self, table, units):
        # Emit a power event.
        pg = self._power.goubmles()

        self.charge = pg


class Wire(Unit):
    ohms = .001

class Resistor(Unit):
    ohms = 300

    def recieve_power(self, power):
        self._power = power
        gb = power.goubmles()
        self.charge += gb
        self.minor_drop = self._power.amps / self.ohms


    def get_charge_slice(self):
        """return one minor-tick percentile of the given reservoir of charge
        in goubmles/
        """

        return (self.charge * self.minor_drop)


class LED(Unit):
    pass


if __name__ == '__main__':
    main()
