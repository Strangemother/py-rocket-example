
### Turing Complete in-game 3D functionality

Each physical unit in the game represents an object in the framework, complete with sub logic and built in variables. One notable var for all entities is "age" as most items will degrade over time.


#### Circuitry

All flight systems (hardware and software) exist as a "patch panel" for editing. A general ship has may system modules connected via wires. Each unit within the circuit may be swapped with something comparable.

+ The flight system is a graph of functionality, connected by 'wires'
+ All components represent a in game 'real life' unit
+ Anything can break, and be replaced with anything.


This opens the game for a wealth of _junkyard_ fixing, allowing a player to install or manipulate every found device to salvage components. This should include:

+ The ship base (its frame)
+ Engines, and any attachable components
+ Internals: from chairs to floorplates.

Each unit is built of certain materials. For example as a _floor plate_ is metal, it will conduct electricity. In an emergency a player could patch an wiring break with piece of flooring; until a new component is found.


#### Engine sounds

The audio system is procedural allowing the game to render sounds relative to the installed components. As such all configured machines persist a unique engine sound, of which will change through age and damage.


### Inputs

On average I expect developer to use keyboard/mouse and/or a joypad. However the PoC accepts the following:

+ Joypads,
+ JoyStick (flight sticks)
+ Steering Wheels and the any Foot accessories

All of which I personally want in the game ready for a user to map at-will. In addition the framework accepts any a websocket connection for an exposed API. A play will have the ability to integrate any 3rd party source, to interact with the game - such as a "button" on an external device.


Some considerations are:

+ A mobile device, using the accelerometer
+ "Button panels" on 2nd monitors (or a tablet)
+ Custom hardware integration; such as a raspberry pi sensor emitting a 'shoot' signal.

This is surprisingly easy and with the existing "Adam Flight System", we can may any external caller to any ship system.


### VR

The game is initially a 'pancake view' and playable on a standard desktop. This game lends itself nicely to the VR world - running around my own ship is the dream. hover it requires delicate development - something of which can wait.
