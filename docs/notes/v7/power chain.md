# Power Chain

Once a circuit creates a closed loop though a looptest event, we can build a graph of power configurations for each Unit in the chain, complete with _variables_ to chain the power cycle for each step.

Every Unit receives a PowerConfig prepared by the previously chained sibling. Once the power chain records all configs, we run the chain by processing the _energy_ each unit receives per iteration.

We can consider the power chain as an ordered table of indexed Units. Each unit provides a _requirement_ of power, such as _voltage_, _amps_, etc. The PowerChain lives independently of the units, signalling power changes when a unit within the chain alters its power specifications.

1. Circuit collects closed "loops"
2. Circuit requests `power_config` for each unit (including wires)
    vars include:
    + required voltage
    + required amps
    + resistence
3. A PowerChain stores all power config within a closed loop as a matrix.
4. The PowerChain cycles at X FPS, passing "configurations" to chained siblings.


https://www.mrsolar.com/what-does-volts-amps-ohms-and-watts-mean/

---

To Simplify the whole _replicate a circuit_. The technical task is broken into thinner subsets

1. The circuit finds closed loops
2. A Power Chain builds a state machine of the loop.
3. The chain iterate at (e.g.) 100FPS

Each Unit provides a linear equation list, or a custom compute function. The custom function is not preferred as the calculations may not be isolated to an indepedent chain, however I foreesee complex units performing complex calculations.

> A near to working version of a circuit - not a recreation

Energy is tranferred as _power_ in a single packet marking a continious stream. This packet provides a _ramp up_ value for each cycle.

One timestep contains many frames e.g 100. A unit iteration (one frame) computes the total accumulated coulombs the unit may digest over a timestep. As such a _drain_ of coulombs occurs over a timestemp for a power-outage.

A Unit computes the amount of coulombs given the previous packet total remaining, removing a portion from the _voltage_ divider.

Unit Digest table:

    Item        Add    Draw     Amps    Phase   Resistance
    *Battery    ~12             +3      60      0
    LED                2        .2      60      0
    Next                                30      * 0.0001
    Next               3        -1      60      * .00001


---

In the matrix of compute vars, this can be rewritten as a sparse table. Missing
values are replaced with a nully sum.

    # power modules
    add_volts: Add additional voltage without amp alteration
    add_amps: Add Amps without voltage change
        phase is automatically the default circuit (app) value. e.g 60htz

    reshape_amps: Recompute volts given new amps (width)
    reshape_volts: recompute amps given new volts (height)
    reshape_phase: recompute volts and amps given a phase change

    ohms_drop: Drop by a resistance value with the remaining as heat emission
        same as a wire 'resistance'




---

## Phase

A Powered cell may output xVoltage and xAmps, a unit computes this to coulombs. A Power cell adds voltage but ignores amps in series, and ignores voltage and multiply amps in parrallel.

The Phase calculates the cycle rate of the input signal and add coulombs upon a phase direction.
Phases compute the rate coulombs enter the unit. e.g. if a unit converts a 60phase to a 30phase signal, the accumulation of energy over time is reduces and power is doubled.

Phase:

    volts * amps * (previous_phase / current_phase) * (1 - resistance)
---

To implement a logical phasing method, each unit receives a continious power packet, calculating the total charge per cycle given the previous siblings, and storing the total charge for a period.
The unit _uses_ a part of the total charge to perform work.

To compute input charge, the input power contains a _phase_ such as "60" and the current unit _accepts_ a target phase - again "60". For each unit cycle the amount of coulombs stored is a cosine total of the phase normalised. If the previous power is 5V 1A 60P, then the peak of the cosine phase loop return _most_ power.

In an LED _phasing_ isn't a factor, so we choose our favourite and use it as a baseline.

    LED 5V, 0.3A, 60P == 100%

The given power packet nearly matches, we can reshape it to match.

    > In these simple circuits, Volts is set (from the emitter) and amps will be the _max_ unit on the line. If other units have AMP ranges outside others on the line, they break.
    Values can be reshaped to match expected (3V step up to 5V), but this alters the power ratios.

    Power: 3V 1A 60P

Stepping up Volts, drops Amps. changing phases will alter amps and volts in a ratio to itself.
With this you can phase change and voltage step to any value on the chain.

    new_amp = amp * (volt_in / volts_required)

    coulombs = amps * phase
    rephased_cou = coulombs / new_phase

    timestep_cou_chunk = coulombs / circuit_frequency # e.g. freq 100


    First:      3V  1A   60P
    Altered:    5V .8A   60P
           :    6V .5A   60P


### Perceived Power Percentile

A Power event is has a set _frequency_ to cycle the circuit units and emite tests and general loop care. Upon a single ( modulo 0) of the sequence the power chain computes the _power step_, applying the single event chunk to the existing units. On every step of the frequency a reduction in _current power value_ applies changes to the existing energy state of a unit.

The discrete chunks of coulombs for each unit provide a _percent_ of power. If the power is affected the amount of coulombs in the charge cycle will not amount to the expected amount, and the unit looses power.

A target LED computes at:

    LED 5V, 0.3A, 60P == 100%

The Battery should provide a 5V supply, with 3A max.

    Battery 5V, 3A, --P


## Volts

The amount of power the unit is requires for power.
The battery unit provides a set amount of Volts, equal to the amount required across all live devices.

A Unit may have a 'forward voltage' as the amount of volts wanted for 100% functioning.

The closed circuit is tested for _digest_ units,

## Amps

The size of throughput to collect power.

The amps given on the circuit is the maximum required on a circuit. If the amps of a unit is
greater than its siblings allow, other units on the circuit may die.

amp is the sum of all resistance / the count of resistors.
    9v / (2o + 1o) == 3amp

To compensate a Amp step convertor (a resister) should be applied before the unit.

## Heat

All units push extra energy as heat. If a unit overheats, it will _explode_. LED's would become overly bright for a brief second, wires would burn red hot.

All units have a max heat sum to calculate from the norm (22C room temp). This may be derived from its components or a hard limit. In the case of LED's this is about 120C before burning out.

The heat ramp is proportional to the input _extra_ heat and the timesteps. All units will normalise to the room temperature if not overheated. If an element is attached to a _heatsink_, the heat is distributed.

Heat disaparation occurs within a separate thread of work.

    LED: input 5V, 3A, 60P
    2.4A output at 60P
    (current ** 2) * resistence
    resistence raises with more heat
    volts = V_curr - V_prev is the voltage drop across the element.
    power = resistance * volts



## Ohms


The total resistance of resistors connected in series is the sum of their individual resistance values.

The total resistance of resistors connected in parallel is the reciprocal of the sum of the reciprocals of the individual resistors.
E.g. a 10 ohm resistor connected in parallel with a 5 ohm resistor and a 15 ohm resistor produces


    1/ (1/10 + 1/5 + 1/15)

ohms of resistance, or

    30/11 = 2.727 ohms.


    Voltage     ( V ) [ V = I x R ] V (volts) = I (amps) x R (Ω)
    Current     ( I ) [ I = V ÷ R ] I (amps) = V (volts) ÷ R (Ω)
    Resistance  ( R ) [ R = V ÷ I ] R (Ω) = V (volts) ÷ I (amps)
    Power       (P) [ P = V x I ] P (watts) = V (volts) x I (amps)
