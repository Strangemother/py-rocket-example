# Power

The power of a unit is a terse calculation of electric, given a flat compute table and the edge list. Each node power calculates as the chain computes. For now a linear chain of multipliers.


> This is a rewrite of 8.1: [first-concept](first-concept.md) -

## Ideas.

Given the nodes are connected, we can traverse the nodes in reverse, starting with the most distant node (or the instigator node), walking up the tree until it hits a power node, and beyond...

The walk in reverse (hopefully) collects a thin chain up to a power provider, This assigns an easy to compute chain - assigning a 'drain' value to the power cell.

Other chains within this reverse walk may also lead to power nodes. Give the first chain is computed, the next chains assign the same calulations, and an addition of the _n_ chains total the full result of the initial node request value.

    B == 50     40.29
    - == .9
    - == .9
    - == .9
    N == 10     9.70

With junctions the active paths assign a compute value:


             B == 50
             - == .9
                |
       |------- J ------|
    - == .9             |
    - == .9            - == .9
    N == 10 -> 9.70    N == 25 -> 20.2  (E)
            == .19              == .4   (%)


1. Gather the reverse path to the power provider _B_
2. compute to output value _NE_ through `N --< B` = 9.70
3. Ascertain the pecent of _B_ over _NE_ = .19

In this case we Battery has excess `20.1`, thus connecting more chains would reduce the others

---

!! Note, this doesn't look right - consider

    Na / B == 10 / 50 == .2
    Nb / B == 25 / 50 == .5 +
                         .7 ==
request proof

    50 * .7 == 35

provide

    Na == (.70 * 100 ) * .2 == 14.0
    Nb == (.70 * 100 ) * .5 == 35.0

finally through the resistance:

    Na == 14 * (.99 ** 3) == 13.58
    Nb == 35 * (.99 ** 2) == 34.3


---

Another:

    Na / B == 10 / 50 == .2
    Nb / B == 25 / 50 == .5
    Nc / B == 20 / 50 == .4

                         == 1.1
                         50 / (50 * 1.1)
                         == 0.909        (overflow)

provide

    50 * 0.909  == 45.45
    Na == 45.45 * .2 ==  9.090
    Nb == 45.45 * .5 ==  22.725
    Nb == 45.45 * .4 ==  18.180


finally through the resistance:

    Na ==  9.090 * (.99 ** 3) == 8.82
    Nb == 22.725 * (.99 ** 2) == 22.27
    Nc == 18.180 * (.99 ** 2) == 17.81

System draw: 48.91100841, Eff: 0.97% loss: 0.027%


---

Another:

    Na / B == 10 / 50 == .2
    Nb / B == 25 / 50 == .5
    Nc / B == 20 / 50 == .4
    Nd / B == 30 / 50 == .6

                         == 1.7
                         50 / (50 * 1.7)
                         == 0.588        (overflow)

provide

    50 * 0.588  == 29.4
    Na == 29.4 * .2 ==  5.88
    Nb == 29.4 * .5 ==  14.7
    Nb == 29.4 * .4 ==  11.76
    Nd == 29.4 * .6 ==  17.63


finally through the resistance:

    Na == 5.88  * (.99 ** 3) == 5.70
    Nb == 14.7  * (.99 ** 2) == 14.407
    Nc == 11.76 * (.99 ** 2) == 11.52
    Nd == 17.63 * (.99)      == 17.45

System draw: 49.077, Eff: 0.98% loss: 0.02%

if Nd distance was 5:

    # 0.98%
    >>> 17.63 * (.99**5)
    16.765954579737
    >>> (5.7 + 14.407 + 11.52 + 16.76) / 50
    # 0.967%

additional loss of `0.014` %

---

+ `B` may only ADD, B+B == B*2,
+ A B with power in will disappaite as heat
+ regarable B recieves as a 'digestor' and 'emittor'
+ Each node has its own chain.The batter is aware of the total nodes.
+ 10,800 coulombs == 3000 miliampere-hours of electricity
+ 1 coulomb == 6,250,000,000,000,000,000 electrons.
+ A coulomb is approximately equal to 6.2415093×10^18 elementary charges (such as electrons), one ampere is approximately equivalent to 6.2415093×10^18 elementary charges moving past a boundary in one second,

## coulomb

Since one coulomb per second is equal to 1 ampere, you can use this simple formula to convert:

    coulombs per second = amperes ÷ 1

The electric current in coulombs per second is equal to the amperes divided by 1. For example, here's how to convert 5 amperes to coulombs per second using the formula above.

    5 A = (5 ÷ 1) = 5 C/s

---

Thus a single unit may have coulombs, relative to a per second;

    1 LED == 200mA, 3v == 0.066 (coulombs per second)


 Since a coulomb is approximately equal to 6.2415093×1018 elementary charges (such as electrons), one ampere is approximately equivalent to 6.2415093×1018 elementary charges moving past a boundary in one second,

---

Therefore every slice of 1 second (the sub tick) siphons 1/t to _power_ the device for that amount of time. This sub tick value can be computed once, as the power value changes.

The rate of charge per second is `n*(given_cps-target_cps)` for ramp and loss.
