# Project Quick Writeup

We intend to produce a game, focused on the flying mechanics of a vehicle. Given a range of _engines_ and controls, the user will develop upon existing vehicles to customise the system. The unique feature for this project, is to allow complete control of the vehicles _operating system_ and the literal patch panel of wires, switches, and controls within the dashboard.

Fundamentally a user could start with a raw base of a battery and two wires, to start the engine. We have a clear direction for the game  vehicles, 3d control integration, and _software layer_, but we're struggling with the _wiring_ of all devices within a control panel - and passing "power" across them.

+  Core Game Concept  [one.md](one.md)
+  Circuity Writeup [game-system.md](game-system.md)

---

More accurately we're struggling with modelling a 'power system', to share _some sort_ of energy across a graph of nodes. It would be great for the system to act like an electronic breadboard - however an _in game_ simulated alternative is also a great option.


## The Micro Example

A suite of "electronics" the user can reconfigure (rewire within the game), to alter the control system and outputs of the game vehicle.

At the base, the "power system" should be able to connect:

1. An LED
2. A battery
3. A switch
4. A 'wire' connecting them.

In game the user will enable the switch, causing a simulated power event to light the LED.

## The Macro Goal

Once this works, we'll wire up **eveything** in the system; and give it to the user, as both a software coding environment; and in-game.
Within [flight system](flight-system.md), you'll see examples of the _systems_ we will implement. Notably the 'node graph' system we're using works very well (see `py8/` and `graph2/` source). Our current issue mostly resides within sharing some sort of _power_ across connected nodes.

**What we can do**

1. We have a good node graph system (`graph2/` for the most recent working example)
2. Build sub systems and "Devices"
3. Build the flight system and _data_ to move data through the "system"


**Assistance required (What we can't do)**

We are struggling with writing an effective power event sharing system - to pass "power" (not chunks of data) across connected nodes. For our attempts we cannot efficiently mimic "plugged in power" (exactly like an electronics breadboard).

We are hoping you can help us invent and model an effective system to:

1. Built this "control panel" of units, sharing a _power_ across them
2. Power for a single unit (A device charge), is affected by energy level changes
3. Expendable, and scalable; enough for a whole cockpit of controls

---

If the _power sharing_ system can be resolved, this solution should be usable across a few hundred nodes. In addition, we can multiprocess extremely large graphs of these nodes.

### Example Implementation

Given we have 1 battery and 1 LED, we can assume the LED brightness is 100%. If we apply 2 LEDs to the same battery, each LED gains 50%.

+ A 'node' being any on-graph device, such as a battery, led, insulators, conductors etc...
+ Power sharing across "nodes"
+ Power charge will change over time
+ Additional nodes will change the power flow

All future system will look like these:  [flight-system.md](flight-system.md)

#### What we've tried

Fundamentally _how_ it works is unimportant; only the _energy power_ for each computed unit at a given time. In the research code (`py3/` ~ `py7/`) you can see we've tackled "event sharing" using:

+ async event loop
+ flat graph
+ functional execution chains
+ pre-computed loops and paths

But we haven't truly adopted a method. However In `graph3/` we've built an excellent graph node connection routine of which we'll use as the "data graphing" for connected control items. [Paths.md](v3\Paths.md)

> All the source within this repo is research through these events. Please steal and abuse - but we're aware it's mostly scrap.

#### Failure points.

We're not electronics engineers and have struggled with replicating a standard _electronics board_ of which would allow us to build any platform. But we feel this complexity is not required, and rather find someone who can model a power chain system.

Things we've failed with:

+  Choosing an effective _energy_ type; e.g. "electricity" or a fantasy energy type with an easier modeling
+ Power "closed loops" and charge sharing (across devices)
+ Power drops and general signaling
+ If simulating an electric circuit; how do we solve for parallel or series circuits?

## Output Solution

We would like some proof of concept to power this switchboard of controls and interface units.

1. The ability to 50+ bind up _things_ units
2. Compete with Switches, energy producers (batteries) and energy sinks (anything accepting power)

However it doesn't need to be a "circuit solution". For example; a developer once supplied us with a (limited) scipy table solution.

With this solution our progression will be:

+ The ability to change units within this connective solution (users will upgrade parts)
+ Creating "Flight Systems" for structures like:  [Community Vehicles.md](Community Vehicles.md) and  [ships.md](ships.md)
+ Ran at 100fps

## Final Requirements

+ We'll pay for your idea, solution, and any best practice you think will work

  + We don't care if you find an off-the-shelf (such as a finished numpy solution!)
  + Or if you a completely different idea to model this

+ We're not paying for lines of code.

  + We'd **prefer** a less code. (Readability is key)

    if you found a 10 line solution - we'd accept it!

+ It'll be open-source, and the we'd like you to name the "power solution" if you wish :)





## Noted Requests

Some elements to consider for the output solution. These caveats help us integrate:

+ Try not to send 100 events per second per chained device (e.g we're running 100fps target).
  + If we have 50 connected devices (minimum), connected through 10 chains, and need to power at 100fps - that's 500k messages per second (bad idea)
  + A great idea is a flat list of pre-solved computed power event chains
  + (But whatever you prefer)
+ The final source will be open source and available for users to develop upon
  + We'll build ship system components to plug in

## QA:

+ How will it run?
  It'll run apart of the "flight system", as a separate thread to the 3D UI, controlling inputs and manipulating system hardware values. It will run at a steady clock rate (e.g. 100fps)

+ What happens with power loss?
  Every "device" we program is a python class with a standard "receive power" for example. A device can siphon power over a time delta.
  When no power events are received;

+ And energy overpower?

  Every device has a built-in power limit, and will emit an "explode" event - mapped to an ingame visual. These entities are flagged "broken" until fixed or replaced

+ What is a "device"?

  Any entity/component/unit on this swtichboard of connected items. these manifest as switches, buttons, dials, plugs, .. any general "device" you'd apply to a control panel (to drive a fantasy vehicle)

+ Wires and other _components_?

  All items should be connected by a set of pseudo _wires_, allowing the user to manipulate the wiring; or in game actions to change the wire state. We've had success with a literal AB (bi-directional) graph.

+ Do we need _real_ power?

  Nope. We've found it difficult to model effective `amps/volts` and the simulated electronic system. So no - anything that is useful enough to simulate time delta'd power. We've considered fantasy hydrogen fuel:  [ingame-fuel.md](ingame-fuel.md)

+ Why 100 FPS?

  The _flight system_ and all its control panel components will run at a steady clock on a separate thread. This will be an event loop locked at 100 cycles per second. This ensures we have a simple clock rate for in-game event calculations for console, 3D and VR system integration.

  The FPS is also known as the _system hertz_ - if possible this will run faster (200fps or more) given the solution can run at that speed.
  In-game actions may affect this to temporarily alter vehicle handling, e.g. an electronic storm.

