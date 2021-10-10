from signal import SignalEventHandler


class OnOffSwitch(SignalEventHandler):
    """A simple on-off for the enablement of the default connection.
    """

    def on_state_enabled(self, old, new):
        """Capture th change state of the 'enabled' key
        """
        print('Plug state change "enabled"', old, new)
        if new is True:
            print(self, self.socket)
            return self.socket.enable_flow()
        return self.socket.disable_flow()

    def switch_on(self, connection_name='default'):
        print('flick on', self)
        connections = self.connections.get(self, connection_name)
        print('connections,', connections)
        for con in connections:
            #con.get_device(self).state_manager.enabled = True
            con.set_device_state(self, 'enabled', True)
            # self.state_manager.enabled = True
            # self.state_manager['enabled'] = True
            # self.state_manager.set_state('enabled', True)

    def switch_off(self, connection_name='default'):
        print('flick off', self)
        connections = self.connections.get(self, connection_name)
        print('connections,', connections)
        for con in connections:
            con.set_device_state(self, 'enabled', False)
