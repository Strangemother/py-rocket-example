Power events provide energy through a circuit to mimick a standard electronic circuit (with a lot of simplification).

As energy acts like discrete units over time, we want to copy this without sending many events through the chain. Instead we provide connection, update and stop events for the circuit to proagate to sequenced units.

1. The circuit manages closed loops of power sources
2. The circuit handles signaling of power changes through an active chain
3. The power event handles energy distribution - until its own death
4. the circuit passes the power event through a 'fuzz' test phase.

---

A single unit must compute its own _given_ energy and should know the power phase of the previous device. To manage this the circuit manages a single event clock, iterating all live units on a circuit. If a units _power modulo_ reaches 0, the unit gains the expected power amount.

A Power event reads as "volts" and "amps" for simplicity, coupled with a _hertz phase_ (such as 60htz) of the frequency cycle. As such a unit may receive `V*A * Hertz`. This is important for capacitor like devices, to store power over time, releasing a larger power event at a slower rate.

---

During the circuit "Fuzz" phase, each unit _answers_ the event through its nominated terminals with a Power event altered to fit its expected output. They may entail "-volts" and "-amps" (how much used), but may contain a _phase variance_, such as "+volts", "+amps", "-phase".

The next device (e.g. an LED) recieves the power event phased at the previous amplitude. Upon resyncing the power charge, the resultant (normalised) power value may be less than the expected "5v/200ma" and thus reduce in brightness.

Other more-complex devices may simply error, or in fun cases explode.

---

For phase change power events, the cycling phase values dictate how the next entity will compute its energy step value. This will hasten or slow the per frame cosine step phase. When the phase hits `0` A new _charge_ for the unit internal state allows another moment of work.


In this example we have a powerful _thing_ such as a motor. The power setting provides a stepping formula and cycle downcharge time may deplete before the next capacitor charge cycle.

    Circuit:
        Phase: 100
    Battery:
        IN - (Thing)
        out: V: 12
             A: 3
             P: 60
    Capacitor:
        in:  V: 12
             A: 1
             P: 60
        out: V: 48
             A: 4
             P: 15
    Thing:
        in:  V: 24
             A: 2
             P: 30
        OUT: - (battery)


The compute cycle for each phase is done within the circuit. The device must _act_ upon an internal power change state if required, else wait for power update or _loss_ due to other factors.

---

The Unit provides a waveform calculation for the circuit to apply during its single process loop. The power event keeps its "next siblings", therefore the circuit simply _times_ the event passing given a clock rate - the sum of V,A,P and other circuit factors.

The frequency of step is based upon a spinning consine. The radius `tan` is altered per iteration, changing the timing of the power for subsequent steps. The values stored are undecided, however we can visualise the circuit step continuity through a matrix of calculations

    Entity      V   A   P     _f_

    Battery     12  3   60     1
    capacitor   12  1   60     1
    thing       24  4   15     .25
    led         5   .2  30     2
