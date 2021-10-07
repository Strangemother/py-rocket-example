Simulated Pipe Feeding.

Two connected elements serve as _value_ connected pipe. Consider Power or a condiute.
Through paring the devices a pipe feed persists any throughput the two modules apply.

By simulating the feed value, the two modules connect through a persistent data feed - cycled at X htz - to the feeding utility. By only defining the feed out and feed in clauses for a pipe, the information doesn't actually flow at X htz, rather the two pipe _ends_ define one state to work upon, altered later by a connected device.

    Device 1 (A Lightbulb)
        |- pipe requires 1W, == or just `1` per 60Htz cycle.
        |
    Device 2 (A plug socket)

device 1 _connects_ to device 2 to begin power draw at 1 per cycle. The overall system _hertz_ defines a framerate for the compute cycles. As such device 2 receives _`60` per second_ - unit through the pipe.

Device 1 may change its _draw_ to `2`, requiring `120` units per second. Regarding technical appliance, the device _pipe_ is a definition calulated within a loop.

The loop identifies the system table list of devices - iterated in speed term "hertz". the application definition applies a massive list, iterated each cycle updating configs

Coupling the API with the _system_ emerges as pseudo simulated siblings - in memory, bound to a 3D (scene) object with an ID, calling the API procedures as expected for the attached device.

---

The interesting "pipe" functionality allows two hemogenous items to connect though a "plug type", or a more complex config dict for the pipe-end. For example a standard _plug_ with live, neutral, and ground, binds as one pipe configuration "uk plug". When performing a _connect_ of the devices, the _plug_ should align all pipe ends, or rather, device 2, connects to device 1 with a matching object.
Another small example may by a speaker, with positive and negative poles as a "phono type", accepted by a "phono socket".

Indeed they may connect like a plug - Phono+ to LIVE. Of which would flow 120units per second rather than the preferred (example) .02units per second. The Phono receiver would technically "blow", throwing an exception. Within the game, the _blow_ may manifest as a texture change to a fuse within the 3d Interface of the speaker.
Again the example fuse may have a psuedo bound unit connected to a 3d stage object.

# Port

A port Type is essentially a MALE, FEMALE device connection a PIPE keeps as a config for the two bound units.
for example a standard UK PLUG PORT as a male "plug" and a female "socket". A pipe should apply two two ends, bound to two objects,

    pipe = Pipe(device1.plug, device2.socket)
    device1.on()
    # start power draw.

4.1.3 Optical data network interconnects between computer cores, main bridge, and other key systems


Engineering Hull optical data network > Main Computer (EH)
    Main Engineering                  > interconnect umbilicals
    |                                 > Main Computer (EH)
    Warp Drive Systems                > Main Computer (EH)
    |
    Impulse Drive Systems             > Main Computer (EH)
    |
    Battle Bridge                     > Main Computer (EH)
    |
    Tactical Systems
    |
    Sensor Array
    Other departments

Primary Hull optical data network
    main bridge
    |
    Tactical Systems
    |
    Sensor arrays
    Other Department

Interconnect
umbilicals
ODN network links Protected ODN backup links
sors can be installed as needed to support mission-specific
