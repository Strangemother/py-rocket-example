# Circuit

A Circuit manages many connected devices and the events between device terminals to transmit power or data.

Importantly the circuit handles the Power distribution to each Unit within the circuit. If a circuit loop is not closed, the power event will not iterate through the chain.

The circuit loop is handles automatically, isolated from the unit "enabled" or _switched_ device. As a new devices apply to a circuit through a terminal-to-terminal connection.

## Connections

A device connection is created through binding two entities.

```py
c = Circuit()
c.add(battery)
c.connect(battery.terminal_out, led.terminal_in, wire)
```

or automated:

```py
circuit = battery.terminal_out.connect_to(led.terminal_in)
```

The battery may emit a `power` event. The circuit captures the state as "POWERED" for the circuit, allowing the future loop flow of energy. The circuit manages the power state until a closed loop allows the power event to flow into all attached units. In this case the LED.

To close the loop and initiate the power flow we attach the led out terminal to the battery

```py
c.connect(led.terminal_out, battery.terminal_in)
```

As the circuit is POWERED with a continous power event from the attached battery, the event iteration start with the first entity. To mask the application management 'test power event' to the _in game_ lore, a "fuzz event" or low power event should iterate through the entire circuit of units to map the path. If the path resolves back to the originator (the battery), the loop is complete and the loop test is attempted.

A circuit should be mapped terminals correctly else _heat_ and other side effects will break devices. This is modelled within the circuit power event test, ensuring the power loop is correctly polarised, and each device emits the "fuzz" event correctly.

    Battery       LED
    IN- OUT+    IN+ OUT-
    |   |--------|    |
    |                 |
    |-----------------|



## Charging

Each unit within the circuit should receive the _type_ of energy required, matching voltage and amp etc. In game this isn't required, however _phasing_ of the circuit, and _charging_ of devices over a time period is required.

The circuit emits a "fuzz" power event, capturing the path and each devices requirement. Device chaining requires siblings to pass altered power events across the circuit - including delays - This manifests as as phase cycling of a consine for the time delta, using peak calculations derived through the power packet interchange.

Essentially, rather than passing many events down the chain (slowly), the unit reponds immediately to the circuit, with an expected functionality configuration. This includes the cycling changes to the power values for the next dependent.

When a unit calculates the _inbound_ energy packet - the continuous charge is calculated from a modulo of a cosine value.

---

The circuit keeps the modulo assignment for timely stepping of the power event. For phasing delay, the iteration time of the power event step dictates a wait time. Considering a capacitor to reduce the timely phase of the power whilst raising the frequency (voltage). The capcacitor responds with a sine-wave reduction formula to compute a _step delay_ for the outbound power package.

The event will only step to the next sibling if the device (and next device) are enabled.

