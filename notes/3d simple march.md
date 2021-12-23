

A 3d turtle to walk in space producing _pipes_

    Y: UP == 1

The start postion applied a direction:

    start: [xyz]
        pos [0, 0, 0]
        normal [0, 1, 0]

For each step walk a normal. For example, move up y+ 1, left x -1, forward z+ 1,

    [0, 1, 0]
    [-1, 0, 0]
    [0, 0, 1]

In each step deposit a node. These are relational positions, relative to the turtle
given the last step - pointing away from the direction of last index.

For example moving up forward cell, then 3 left positions will yield the initial position.
    dir      norm[ x,  y, z]
    [0,0,0]      [ 0,  1, 0]     # Start at 0, pointing up   [0, 0]
    [-1, 0, 0]   [-1,  0, 0]     # move left by one          [1, 0]
    [-1, 0, 0]   [ 0, -1, 0]     # move left by one          [1, 1]
    [-1, 0, 0]   [ 1,  0, 0]     # move left by one          [0, 1]

     < ---
     |    ^
      >-+ |


each dir is a 3 parts
each position direction gets a unique number, to save the minus attribute `-1 == 4`
