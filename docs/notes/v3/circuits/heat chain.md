# Heat

Is is computed within a unique graph dedicated to heat transmission.

The unit will disperse excess energy as heat. The connected components and surroundings account for heat transfer.

All units are connected in a sparse graph, with each node equating its heat value. Given its material the unit will gradually heat the neighbours, connected by distance across the circuit, or the surroundings.

The amount of heat transferred is an average of the connected components and the room temperature.

Each unit is connected in a table to other units:

    Battery > LED > WIRE > Battery

with a general temperature of 22C. A component has an operating temperature, and a nomonial heat task - such as Dispersing heat as Light (or even room heat).

If a unit reaches past its operating temperatures, it _overheats_ in the form of _melting_ or _exploding_.

---

The power chain will emit "Heat Dispersal" events into the 'heat thread', and accept large lists of results to emit through the unit digest tables. The numbers represent a relative heat association with the input _100_ (they mean nothing):


    power chain> disperse LED: 100
    Heat chain> return LED: 110, WIRE: 99, Battery: 50

## Ambient

All nodes have a relative position within the space. This may be given to the heat thread as data to account for distances. During the heat-up phase, A unit emits heat to the surroundings, affecting other units within a distance.

In theory the heat connected elements are relatively static, therefore the distances for each target node may be tested before the heat disperse stage.
