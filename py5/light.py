

def main():
    g = FlatGraph()




class FlatGraph(object):
    """
    Key value map of graph dependencies stored in a flat KV dictionary.
    """

class Switch(object):

    contact = None

    def toggle_off(self):
        self.contact.set(0)

    def toggle_on(self):
        self.contact.set(1)


class LED(Device):
    """Emits light given a power charge.
    """
    def brightness(self, v_perc)
        print('Set brightness %', v_perc)


class Light(Device, PowerConnected):

    def setup(self):
        condition('power', 'change', self.power_change)
        bulb = LED()
        switch = Switch()
        plug = PlugUK()

        Tap(plug, switch)
        Supply(Power(), self, plug)

    def power_change(self, event):
        power = event.value / self.bulb.max_power
        self.bulb.brightness(power)
