# Tap

A Tap identifies an injectable unit to capture and affect Feed events as they
emit from a provider.

```py
class Tap:

    ok = False

    def perform(self, event):
        if self.ok:
            return event
        # meddle.
        event.energy = Energy(volts=0, amps=0)
        return event

tap = Tap(a, b)
```

When A emits to B, the Tap will capture the Feed event from A.emit_feed before
the B.on_feed receives the event. Tap.on_feed returns any event to _continue_
to the next taps or the final emit stage.

