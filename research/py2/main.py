"""Simulate more Device <> plugged into <> device.
"""

cache  = {
    "pipes": ()
}


def main():

    device = Device()
    plugs = PlugSockets()
    pipe_settings = dict(

        )

    pipe = pipe_connect(device, plugs, **pipe_settings)

    # Plug the two entities together (consider a wire connection)
    # And instansiate compatability checks (or hacks)
    pipe.plugup()

    # Then we turn on a device, (given the options available in the pipe or devices).
    # The two entities may already enable - such as auto pipes.
    # This may be done from both or one. Depending upon automatic enable.

    print('\non all')
    # enable power push
    plugs.on()

    print('\non pipe', pipe)
    # The plugs have many devices, therefore an index of plugs
    # should index which pipe to turn on, else turn on all.
    plugs.on(pipe)

    print('\non device', device)
    # enable power draw, enabling the pip for computing the two sides.
    device.on()
    # Device should turn on

class PipeOnOffMixin(object):
    """Provide an 'on', 'off' function to enable the pipe end.
    """
    def on(self, pipe=None):
        if isinstance(pipe, str):
            # Pipe index of many pipes.
            print('Turn on pipe by id', pipe)

        elif pipe is None:
            print('Turn on all pipes')
            return self.on_all()

        print('Turn on device or pipe', pipe)
        print('Turn on', self)

    def on_all(self):
        """Iterate all pipes and turn on.
        """
        for entity, pipe in self.connected_to:
            self.on_pipe(pipe, entity)

        for entity, pipe in self.connected_from:
            self.on_pipe(pipe, entity)

    def on_pipe(self, pipe, entity):
        print(f'tell pipe "{pipe}" (for {entity.name}),'
              f' this entity ({self.name}), is ON.')
        pipe.enable_feed(self)

    def off(self):
        print('Turn off', self)


class Pipe(object):
    """A single pipe connects A to B through settings to define the
    allowed connection e.g: A headphone (A) to walkman (B).

    Consider this like a wire between two components. The entities may be
    of any type, connecting through this pipe and its limitations.

    Potentially a pipe is omnidirectional. or bridge to other pipes.

    A pipe manages the throughput of the two connected devices. It may be a
    standard (A<=>B) connection, or more advanced such as a websocket pipe,
    a filtered pipe, crosswire/hotwire for many connection pipes.

    Firmly this pipe should simulate a mutated connection acting as cable
    types
    """
    def __init__(self, alpha, beta, **settings):
        """Provide A to B using settings.
        """
        self.settings = settings
        self.alpha = alpha
        self.beta = beta
        self._enable_alpha_feed = False
        self._enable_beta_feed = False

    def plugup(self):
        self.alpha.connect_to(self.beta, self)
        self.beta.connect_from(self.alpha, self)

    def enable_feed(self, entity, **kwargs):
        """Given an A or B entity, enable the pipe draw of the
        pipe end. If both are enabled, computation (a full feed) can start
        """
        print('Enabling', entity, 'in pipe', self)
        if entity is self.alpha:
            self.enable_alpha_feed(entity, **kwargs)

        if entity is self.beta:
            self.enable_beta_feed(entity, **kwargs)

    def enable_alpha_feed(self, entity, **kwargs):
        """The A side (from) pipe enable, such as called from `on()`
        """
        print('Enable Alpha')
        self._enable_alpha_feed = True
        if self._enable_beta_feed is True:
            self.all_enabled(entity)

    def enable_beta_feed(self, entity, **kwargs):
        """The B side (to) pipe enable, such as called from `on()`
        """
        print('Enable Beta')
        self._enable_beta_feed = True
        if self._enable_alpha_feed is True:
            self.all_enabled(entity)

    def all_enabled(self, instigator_entity):
        """All items in this pipe (A and B) flag enable,
        """
        print('All items on', self)

    def __repr__(self):
        return f"<Pipe: {self.alpha.name} to {self.beta.name}>"


def pipe_connect(a, b, **settings):
    """Produce a pipe for A connect to B.
    apply to the pipes list and return the new pipe.
    """
    p = Pipe(a, b, **settings)
    print('New pipe', p)
    cache['pipes'] += (p, )
    return p


class MaxConnections(Exception):
    pass


class AThing(object):
    """An entity to work on the graph
    """
    max_connected_to = -1
    max_connected_from = -1

    def __init__(self):
        self.connected_to = ()
        self.connected_from = ()
        self._name = None

    @property
    def name(self):
        return self._name or self.__class__.__name__

    def connect_to(self, entity, pipe):
        """This entity plugged into the given entity. The other side
        "entity.connect_from" recieves this instance through the pipe.
        """
        # print('This', self, 'connect to', entity, 'through', pipe)
        print(f'This "{self.name}" connect to "{entity.name}" through "{pipe}"')
        self.add_connected_to(entity, pipe)
        # Does this entity automatically push to the pipe

    def add_connected_to(self, entity, pipe):
        _max = self.max_connected_to
        if _max > -1 and (len(self.connect_to) >= _max):
            raise MaxConnections(self)

        self.connected_to += ((entity, pipe,),)

    def connect_from(self, entity, pipe):
        """Called after connect_to executed on the alpha.
        If this item is a B (acceptor), check the pipe is possible and
        store a from pipes.
        """
        print(f'This "{self.name}" connection from "{entity.name}" through "{pipe}"')
        self.add_connected_from(entity, pipe)

    def add_connected_from(self, entity, pipe):
        _max = self.max_connected_from
        if _max > -1 and (len(self.connect_from) >= _max):
            raise MaxConnections(self)

        self.connected_from += ((entity, pipe,),)

    def compute(self, pipe):
        """Perform the calculation and store the result into this class.
        for each unit, there will be computes. IF the device is a leaf
        node the compute occurs across multiple feeds
        """
        print('compute', self)

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.name}">'



class PlugSockets(AThing, PipeOnOffMixin):
    max_connected_to = 3


class Device(AThing, PipeOnOffMixin):
    max_connected_from = 1



if __name__ == '__main__':
    main()
