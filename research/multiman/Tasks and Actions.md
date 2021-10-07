A Task can be run, send events and perform other actions.The event machine should message events to the correct parents for other procedures to continue.


+ Can be interjected with other immediate tasks
+ has a unique name, given to the owning process to ensure it's complete.

# Weighting

task weighting for the immediacy of an incoming event ensures spwaned events nominally override the current tasks.

Considering the scenario of driving but requiring a toilet break. The task of driving is most important until the toilet break is immediate. The the character is unable to stop they will soil themselves.

With this the 'toilet requirement' weight gradually raises until it overcomes the driving weight.

The task weighting is computed through its parents

    task            weight
    driving         .5
        navigate    .9
    toilet          .4
        navigate    .8

---

Task cancelling can become complex, with the potential to _cancel_ a cancel event. A cancel procedure on tasks that _can_ drop determines the backout clause. This may propogate more events of which take longer to complete than wanted, however this is a side effect of cause->effect tasking, and should be handled in-game.


```py
class ToiletBreak(Proedure):

    def on_cancel():
        """ Cancelling the toilet break will still run
        'perform' and likely soil ones cloths.
        """
        return [self.tasks.get('perform')]
```
---

A new task generates the required sub processes and submits them to the event machine. Each subtask runs its actions in sequence, initiating a callback on the original procedure

The owning procedure will step a full process of its own tasks - and is aware and children tasks, however the spawn owner of a task, manages its own children. As an example, we can expand the "get ready for work" procedure as all possible tasks.


    Get ready for work
        shower
            navigate to bathroom
            get undressed
            start shower
            get in shower
            scrub scrub
            turn off shower
            get out shower
            dry-self
        get dressed
            navigate to bedroom
            get cloths
            put on cloths
            brush hair
        eat breakfast
            navigate to kitchen
            make cereal
            eat cereal
    drive to work
        go to car
            navigate route
                walk to place
        get in car
            open door
            get in
            close door
        start car
        plot route
        navigate route
            drive to waypoint #1 (driveway junction)
            ...
        park car
        walk to office/desk
            get out car
                open door
                get in
                close door


## Task Filling

As a Task or procedure is processed it may require ingame logical extras, for example _get in car_ requires car keys. The character may already own the keys, or should go look for them.

The procedure 'start car' requires _keys_ and should be considered at "go to car" procedure. If the requirement is missing at event time - a backout clause may enact. In this case we can _go find keys_ and in the future we can "remember" to get the keys before navigating to the car.

```py
class StartCar(Task):

    requirements = ['keys']

    def perform(self):
        if not self.has_requirement('keys'):
            self.event('find_keys')
```

Notably the 'find keys' procedure should be a named process, else nothing occurs

```py
class Search

class FindKeys(Process):

    steps = (
            navigate_to('living-room'),
            search_room(
                look_for='keys',
                on_success=found_keys,
                time_limit=60#seconds
                )
        )

    def found_keys(self, task):
        self.keys = task.keys
```
