from collections import defaultdict


class Pins(object):

    def __init__(self):
        print('Setup Pins')
        super().__init__()
        self.pins = defaultdict(lambda: defaultdict(set))

    def pin_ends(self, edges, direction):
        first_first_id = edges[0].first
        last_last_id = edges[-1].last

        v = self.quick_pin(direction, start=first_first_id, end=last_last_id)
        vr = self.quick_pin(-direction, start=last_last_id, end=first_first_id)
        return {direction:v, -direction: vr}

    def quick_pin(self, direction, **kw):
        """
            _pins = (
                ('start', first_first_id,),
                ('end', last_last_id,),
            )

            self.pin_direction(direction, _pins)
        """
        return self.pin_direction(direction, kw.items())

    def pin_direction(self, _direction, _pins):
        """
            # pins_dir = self.pins[-direction]
            _pins = (
                ('start', last_last_id,),
                ('end', first_first_id,),
            )

            pins_dir = self.pins[direction]
            pins_dir['start'].add(first_first_id)
            pins_dir['end'].add(last_last_id)

            pins_dir = self.pins[-direction]
            pins_dir['start'].add(last_last_id)
            pins_dir['end'].add(first_first_id)
        """
        pins_dir = self.pins[_direction]
        for name, node_id in _pins:
            # self.pins[direction]['start'].add(node_id)
            pins_dir[name].add(node_id)
