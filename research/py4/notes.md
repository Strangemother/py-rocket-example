
```bash
F:\godot\python-rocket-software\py3>py main.py
New plug for <BaseSystem 7453664 () on:False>
PowerEmitter <BaseSystem 7453664 () on:False>
PowerEmitter <BaseSystem 7453664 () on:False>
Init future <_GatheringFuture pending>
BaseSystem::start - Connect first plug sockets to base system
New plug for <FemalePlate 50198008 () on:False>
PowerEmitter <FemalePlate 50198008 () on:False>
PowerEmitter <FemalePlate 50198008 () on:False>
Connect plug <FemalePlate 50198008 () on:False> to <BaseSystem 7453664 () on:False>
connected <FemalePlate 50198008 () on:False> to <BaseSystem 7453664 () on:False> == True
New plug for <Light 50198120 10 watts on:False>
new light 10
New plug for <Light 50198232 10 watts on:False>
new light 10
Connect plug <Light 50198120 10 watts on:False> to <FemalePlate 50198008 () on:False>
connected <Light 50198120 10 watts on:False> to <FemalePlate 50198008 () on:False> == True
Connect plug <Light 50198232 10 watts on:False> to <FemalePlate 50198008 () on:False>
connected <Light 50198232 10 watts on:False> to <FemalePlate 50198008 () on:False> == True
Do loop 1
wait_info <BaseSystem 7453664 () on:False>
> base.plugs.stream_power()
> base.plugs.sockets[0].owner.on()
Turn on <Light 50198120 10 watts on:False>
Draw Power <Light 50198120 10 watts on:True> <FemalePlate 50198008 () on:False> 10
begin draw <FemalePlate 50198008 () on:False> <MalePlug 45773040 of <Light 50198120 10 watts on:True>>
> base.plugs.sockets[0].owner
< <Light 50198120 10 watts on:True>
> base.plugs.sockets[0].owner.is_on()
< True
> base.plugs
< <FemalePlate 50198008 () on:False>
> base.plugs.on()
Turn on <FemalePlate 50198008 () on:False>
Draw Power <FemalePlate 50198008 () on:True> <BaseSystem 7453664 () on:False> 3
begin draw <BaseSystem 7453664 () on:False> <MalePlug 50197952 of <FemalePlate 50198008 () on:True>>
> FemalePlate data drain change. Total: 10
Power drain unload. Available: 0.002
series (0.002,)
base.plugs.sockets[0].owner.is_on()
< True
> base.plugs.sockets[0].owner.on()
Turn on <Light 50198120 10 watts on:True>
Draw Power <Light 50198120 10 watts on:True> <FemalePlate 50198008 (0.002,) on:True> 10
begin draw <FemalePlate 50198008 (0.002,) on:True> <MalePlug 45773040 of <Light 50198120 10 watts on:True>>
> Top Keyboard Interrupt

F:\godot\python-rocket-software\py3>
```
