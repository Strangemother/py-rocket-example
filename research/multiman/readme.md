# Multi Character Manager

A Behaviour event tree for characters and actions in an event suite, performing timely tasks through graph applied jobs.


A When an actor performs a task - it may take an amount of time, or wait upon an expected event. Futhermore certain actions will yield tasks, or be cancelled by other tasks.

The event work should occur across three primary threads. The input thread to allow interaction with the throughput, the event thread as a message bus to all clients, and the event clock timer to action tasks and enact upon messages through events.

---

The event thread simply allows task (functions) to call upon and resolve to other functions without directly calling the unit. The decoupling allows events to action other tasks automatically.


Each task may perform an action over a period of time. The example "actor morning to work" for a character to perform the tasks to complete a routine

1. Wake up upon alarm
2. get ready for work
3. drive to work
4. \* Many tasks between each step.

## Example process

To wake up we intiate an environment event of an alarm. The character hears the alarm and proceeds to "wake up". The success depends upon other factors.

1. Alarm sends event
2. Character _hears_ event
3. Character "wake" process

If the character can wake-up, their behaviour mode should shift into "get ready" for work, whilst actioning other demanding events.

The 'get ready for work' is a procedure grouping many actionable tasks into one thread of continious work. For each success the procedure may step to the next task. The task also contains sub tasks and processes, all running within the one _framed_ procedure.


In the "get ready for work" procedure, it may run like:


1. shower
2. get dressed
3. eat breakfast
4. drive to work

Each task has a subset of other tasks to run. A procedure may run another procedure such as "drive to work", or a single task such as "go to room"


# A Task

A single task can operate the character and perform actions. When loading a task, it defines _what_ it does and which actions it reacts to. A task may run as a timed process, an event _waiting_, or until the attached procedures are complete. By running the task management through a database, they may interlock.


## Timed

A timed task runs an action for a specified length of time such as "sit still for 1 minute". The time length is set against the internal game clock - a delta computed datetime running all scheduled events.


## Schedule

A Scheduled task will run at a specified datetime relative to the internal clock through a measure of _units_. By default 1 unit is 1 second, therefore adding an event `"sleep", 8 hours` manifests as an `event('sleep', units=60 * 60 * 8)`. Depending on the task, this can be changed or cancelled


## Waiting

A standard waiting task runs when another monitoring process occur.
Most tasks will produce additional sub-tasks, to be completed before the parent continues.

As an example a waiting task pushes additional events to occur

    event('drive to work', until_event=got_to_work)

This will produce the navigation processes for driving. _Logical_ marked with \* events don't infer character interactivity.

1. go to car
2. get in car
3. start car
4. \*plot route
5. navigate route
6. park car
7. walk to office/desk

Each step defines sub routines. The master event should wait until all events complete.

# Game Clock

The clock and schedule runs within the game as an internal datetime. Whilst the game is running the game clock ticks relative to the delta (or by a manual tick event). The tick tests for scheduled events and executes the tasks in a timely manner.

For example the character must _sit_ for 3 minutes. Given the internal "time unit" is mapped `1 for 1` with realtime seconds, we apply a task of "site" for `180 units` of internal time.

---

With this we can schedule events to run at a certain datetime (relative to the internal clock) or after a set delay. Some Examples of implementation:

Sit for 1 minute:

    event(sit, units=100)

in game event 2 hours after start

    seconds = 60 * 60 * 2
    event(send_aliens, on_time_units=seconds)

---

The game clock is pushed by the delta or a manual update 'tick' event

    # start game
    events.set_time(0)


    events.tick_update(delta)
    internal_time += delta

