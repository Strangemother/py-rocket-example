"""

Every unit is a powered number
The units list generates from a mighty list of powered units.
"""

# 1a * 12v, / 100fps / 100cps
amps = 1
volts = 12
fps = 100
cps = 100

coombles_per_cycle = (amps * 1000 * volts) / fps / cps
battery_power = .98 # output efficiency.
bc = coombles_per_cycle * battery_power
units = {
    # 12 coombles per cycle battery
    'battery': bc,
    'a': 1,
    'b': 1,
    'c': 1,
    'd': 1,
    'e': 1,
}
"""
Coombles are units of power. If
    1a * 12v / 100cps
    (1000ma * 12) == 1200
    1200 / 100cps = 12
    a == 12 * 1
    ...
"""

# the power chain is computed
"""
Each units multiplies the value; for the node
Off == 0, on == 1, ramping == .5...
"""

# One loop cycle (never truly 1.0)
power_in = 1.01

from collections import defaultdict

values_out = defaultdict(int)
classes = defaultdict(int)
# The _previous_ of the loop,
# for the next in step the multiply upon.
last = power_in
for name, mul_val in units.items():
    #2. Each connection (wire) has a charge loss
    last *= .999
    comp  = last * mul_val
    # units receive the result of the multiplier push.
    values_out[name] += comp#int(comp)
    last = comp
"""
Now each item has a power; if the cycle rate (12 per loop) alters,
The node is event fired; only when changed.
"""
class A:
    overflow_charge = 0
    buffer_overflow = 30
    request_charge = 10

    def on_change(self, charge:float):
        max_charge = 20
        if charge > max_charge:
            self.explode(max_charge - charge)

    def explode(self, over_charge:float):
        """Explode destroys this units ability to emit
        a continuation charge.
        """
        self.overflow_charge += over_charge
        if self.overflow_charge > buffer_overflow:
            units[self.name] = 0

from pprint import pprint as pp

pp(dict(values_out))
# Syphon
"""Sucking data from the 'values_out' per loop
"""
# for name, mul_val in units.items():
#     # units receive the result of the multiplier push.
#     values_out[name] -= classes[name].request_charge


"""Connecting many items within a graph"""


def main():
    global g
    g = Graph()


class Graph(object):
    pass



if __name__ == '__main__':
    main()
