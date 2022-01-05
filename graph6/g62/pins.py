from collections import defaultdict


class Pins(object):
    """A 'Pin' marks the start or end of a connected chain. Pin functions
    assign values to the `self.pins` data structure

        >>> edges = (
            <Edge 1 "A_B" (<Node "A" Valid>, <Node "B" Valid>)>,
            ...
            <Edge 10 "H_I" (<Node "H" Valid>, <Node "I" Valid>)>,
            )
        >>> p = Pins
        >>> p.pin_ends(edges, direction=1)
        # 1 and 10 are start and end pins
    """

    def __init__(self):
        print('Setup Pins')
        super().__init__()
        self.pins = defaultdict(lambda: defaultdict(set))

    def pin_ends(self, edges, direction):
        """Given a list of edges and a single direction, pin the first and
        last nodes of the first and last edges.

        """
        first_first_id = edges[0].first
        last_last_id = edges[-1].last

        self.quick_pin(direction, start=first_first_id, end=last_last_id)
        self.quick_pin(-direction, start=last_last_id, end=first_first_id)

        return {direction:first_first_id, -direction: last_last_id}

    def quick_pin(self, direction, **kw):
        """
            _pins = (
                ('start', first_first_id,),
                ('end', last_last_id,),
            )

            self.pin_direction(direction, _pins)
        """
        return self.pin_direction(direction, kw.items())

    def pin_direction(self, direction, pins):
        """ Push the each node_id within the tuple of tuples in the pins,
        into the correct direction of self.pins

            # pins_dir = self.pins[-direction]
            _pins = (
                ('start', last_last_id,),
                ('end', first_first_id,),
            )

            self.pin_direction(1, _pins)

        Synonymous to:

            pins_dir = self.pins[direction]
            pins_dir['start'].add(first_first_id)
            pins_dir['end'].add(last_last_id)
        """
        pins_dir = self.pins[direction]
        for name, node_id in pins:
            # self.pins[direction]['start'].add(node_id)
            pins_dir[name].add(node_id)
