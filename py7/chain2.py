"""
A more simple method to transfer "power" through a connected chain

# With the 'emitter' sending 1, each unit responds with a power config
divisional of the 1, for the next event (containing the real value) computes the
actual power chain


The voltage Back to a battery should be zero
The resistance on the line should incur 0 volts at the end.
Carefully managing volts allows amps throughput.

All resistance (requested volts and the resultant _amps_ through the )
"""

class Row(object):
    name = None
    out_v = None

    def __init__(self, *a):
        self.volts, self.resistance, self.out_v = a

    def compute(self, index, rows, prev):
        in_v = prev.out_v
        resistance = self.resistance
        amps = in_v / resistance
        print(f"{self.name}: {in_v}v, {resistance} Ohms - {amps} A")
        self.out_amps = amps
        self.out_v = in_v - self.volts

class Res(Row):

    def compute(self, index, rows, prev):
        self.set_out_volts(prev)

    def set_out_volts(self, prev):
        in_v = prev.out_v if prev else 0
        amps = (in_v * .999) / self.resistance
        self.out_v = self.resistance * float(amps)
        print(f"{self.name}: {in_v}v, {self.resistance} ohms out {self.out_v}v, {amps}A")


class Bat(Row):

    def compute(self, index, rows, prev):
        self.set_out_volts(prev)

    def set_out_volts(self, prev):
        in_v = prev.out_v if prev else 0
        self.out_v = self.out_v + in_v
        print(f"{self.name}: {in_v}v - out {self.out_v}v")


table = {#      volts,  resistance  out volts
    'Battery':  Bat(0,  1.0,        0.5),
    'Battery2': Bat(1,  1.0,        .5),
    'Resistor': Res(0,  300.0,      None),
    'LED':      Row(2.0,  15,         None),
    'LED2':      Row(2.0,  15,         None),
    'Resistor2': Res(0,  2.0,      None),
}


last = None

names = tuple(table.keys())
rows = tuple(table.values())

prev = None

for i, (name, row) in enumerate(zip(names, rows)):
    row.name = name
    row.compute(i, rows, prev)
    prev = row
