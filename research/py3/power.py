from pluggable import PowerReceiver

class PowerShare(PowerReceiver):
    # watts = 22

    # When speading the load, given one or more require a greater load
    # than given, vary to plugged values using the method defined.
    # If series, the sockets work in order, the last element loses most power.
    # If parallel, all sockets power equally.
    power_distribution = 'series' # parallel

    def get_distributed_powers(self, plugs):
        powers = ()
        for plug in plugs:
            powers += (plug.watts, )

        total = sum(powers)

        if total != self.last_total:
            print('FemalePlate data drain change. Total:', total)
            self.warn_low = True

        if total > self.available_power:

            if self.power_distribution == 'balance':
                powers = self.power_distribution_balance(powers)
            if self.power_distribution == 'parallel':
                # Each gain a equal part
                powers = self.power_distribution_parallel(powers)
            else:
                powers = self.power_distribution_series(plugs)

            if self.warn_low:
                print('Power drain unload. Available:', self.available_power)
                print(self.power_distribution, powers)
                self.warn_low = False
        self.last_total = total
        return powers

    def power_distribution_series(self, plugs):
        new_powers = ()
        avail = self.available_power
        for plug in plugs:
            used = plug.watts
            # print(f'used: {used}, avail: {avail}')
            if used > avail:
                used = avail
            new_powers += (used,)
            avail -= used
        return new_powers

    def power_distribution_parallel(self, powers):
        flat = self.available_power/len(powers)
        return (flat,) * len(powers)

    def power_distribution_balance(self, powers):
        return [x *(self.available_power/sum(powers)) for x in powers]

    # def __repr__(self):
    #     return f'<{self.__class__.__name__} {id(self)}>'


class PowerEmitter(PowerShare):

    def __init__(self):
        super().__init__()

        self.streams = {}
        self.watts_avail = -1
        self.last_total = 0
        self.warn_low = True
        self.created()

    def created(self):
        print('PowerEmitter', self)

    def begin_draw_power(self, plug):
        """Called upon by the given plug when power draw starts.
        Append the item to the list of 'streams' for the event tick to
        calculate.
        """
        # append pull of watts from other side.
        print('begin draw', self, plug)
        self.streams[id(plug)] = plug

    def stop_draw_power(self, plug):
        """Remove the item from the list of working streams.
        Return the popped plug, of which should be the same as the given plug.
        """
        # append pull of watts from other side.
        try:
            pplug = self.streams.pop(id(plug))
            print('stop draw', self, plug)
        except KeyError:
            print('not inserted for "on" in {self}')
            return None
        pplug.set_given_power(0)
        return pplug

    def tick(self, system):
        """A system tick called upon by the async loop ticker.
        Run the "hertz" tick.
        """
        if self.is_off():
            return 1
        self.stream_power()

    def stream_power(self):
        plugs = self.streams.values()
        powers = self.get_distributed_powers(plugs)
        self._powers = powers
        total = sum(powers)
        for plug, power in zip(plugs, powers):
            plug.set_given_power(power)

        self.watts_drain =  total
        self.watts_avail = self.watts - total
