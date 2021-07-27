"""An exmaple of a power chain set.
"""
from collections import defaultdict


name_index = defaultdict(int)

def new_indexed_name(name):
    name_index[name] +=1
    return f'{name}_{name_index[name]}'


class ohms(float):
    str_fix = 'Ohm'

    def __repr__(self):
        return f"{self.real} {self.str_fix}"

    def __str__(self):
        return f"{self.real} {self.str_fix}"


class PowerConfig(object):
    """All units own a power config
    """
    amps = None
    volts = None
    max_v_in = None
    max_a_in = None
    resistance  = ohms(.1)
    phase = 0 # no Phase, Direct.
    _uuid = None

    def uuid(self):
        if self._uuid is None:
            self._uuid = new_indexed_name(self.__class__.__name__)
        return self._uuid

    def c_volts(self, amps=None, resistance=None):
        return (amps or self.amps) * (resistance or self.c_resistance(amps=amps))

    def c_resistance(self, volts=None, amps=None):
        return (volts or self.volts) / (amps or self.amps)

    def c_current(self, volts=None, amps=None):
        return (volts or self.volts) * (resistance or self.c_resistance(amps=amps))

    def c_watts(self, volts=None, amps=None):
        return (volts or self.volts) / (amps or self.amps)

    def power_chain_check(self, powertest):
        return powertest


def divide_volts(volts, resistor_a_ohms,resistor_b_ohms,):
    """
    (5* (2**1) )/ (2+1)
    3.3333333333333335
    """
    return (volts* (resistor_a_ohms**2) )/ (resistor_a_ohms+resistor_b_ohms)


class Battery(PowerConfig):

    # general out
    amps = None # max ~10 for a 1.5v battery
    charge = 1.5 # amps
    resistance = 0
    volts = .5

    def power_chain_check(self, powertest):
        powertest.volts += self.volts or 0
        powertest.amps += self.amps or 0

        return powertest


class Wire(PowerConfig):
    resistance = ohms(.1)
    length = 1


class Resistor(PowerConfig):

    resistance = ohms(300)

    def power_chain_check(self, powertest):
        """Given the previous item in the chain, return the config
        to update the power unit for the next entity.

        Return a dict of overrides.
        """
        powertest.amps = powertest.volts / self.resistance
        return powertest



class LED(PowerConfig):

    # anything above forward voltage is heat
    forward_voltage = 2

    # resistance should produce 100% at 2V .2A
    resistance  = 15

    """
    For each internal cycle the LED _drinks_ some energy.
    Upon a lesser cycle this is refilled given the circuit chain.
    """
    def power_chain_check(self, powertest):
        """Given the previous item in the chain, return the config
        to update the power unit for the next entity.

        Return a dict of overrides.
        """
        powertest.amps = powertest.volts / self.resistance
        self.light_heat(powertest)
        return powertest

    def light_heat(self, powertest):
        given = (powertest.volts * powertest.amps)
        expected = (self.forward_voltage * powertest.amps)
        total = given / expected
        iv = int(total * 100)
        print(self.uuid(), 'output', iv)



class LED2(LED):
    forward_voltage = 1
    amps = .2

from pprint import pprint as pp

from collections import OrderedDict


class ChainManager(object):

    units = None
    table = None

    def __init__(self):
        self.units = OrderedDict()
        self.table = None

    def add(self, unit):
        self.units[id(unit)] = unit

    def build(self):
        """Build a table of build values.

        Unit        +Volt     +Amp      Phase   Resistance       Max V In     Max A In
        Battery      5        --        0       --               ---          ---
        Wire         0          0       --      .0001% (* len)   1k           15A
        Resisor     --        --        --      250 Ohm
        Wire         0          0       --      .0001% (* len)   1k           15A
        LED          0        -.200*    60      2v               3            .200
                     5        .200      60      ...              3            .200

        * Automated because resistance. and ohms
            amps = 2v / 250Ohm resistor

        """
        table = OrderedDict()

        for uuid, unit in self.units.items():
            name = unit.uuid()
            print(uuid, name)
            # read and tabulurize
            table[name] = {
                'add_volts': unit.volts,
                'add_amps': unit.amps,
                'phase': unit.phase,
                'resistance': unit.resistance,
                'max_v_in': unit.max_v_in,
                'max_a_in': unit.max_a_in,
            }
        self.table = table
        return table

    def compute(self):
        """Compute the built table, producing a flat ampage and forward voltage
        for the _event_ phase.

        starting from the top, waterfall populate empty values
        """
        # Volts emit at a constant for all units _forward_ of the emitter
        # volts compute each step, based upon the previous _given_ volts and
        # amps.

        # Amps is _max_ of all units, All units receive the circuit amps.

        # during iteration each _next_ unit recieves _line volts_, an
        # addition of the last compute
        push_volts = 0
        powertest = PowerChainTest()

        for unit in self.units.values():
            name = unit.uuid()
            row = self.table[name]

            # print('Reading', name)
            row['given_volts'] = push_volts
            push_volts += row['add_volts'] or 0
            powertest = unit.power_chain_check(powertest)
            print(f'Reading {name}: {powertest.volts} v, {powertest.amps} a')


class PowerChainTest(object):
    volts = 0
    amps = 0



cm = ChainManager()

# Batteries in series
cm.add(Battery())
b2 = Battery()
cm.add(b2)

# a = PowerConfig()
# cm.add(a)
cm.add(Resistor())
cm.add(LED())
cm.add(LED2())

t=cm.build()
cm.compute()
pp(t)
