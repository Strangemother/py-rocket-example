
class SignalEventHandler(object):

    def on_state_change(self, key, old, new):
        """Given the event "state">"change" call any method matching
        on_state_key, here key is the changed state key.
        """
        name = f"on_state_{key}"
        method = getattr(self, name, None)
        if method:
            method(old, new)

