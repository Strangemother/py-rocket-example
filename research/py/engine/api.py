"""The main io for the engine.

The engine should be the entire running components of a system
"""

from .log import log
from .names import NAMES
import asyncio
import traceback
from collections import defaultdict

from collections import defaultdict

flight_systems = {}



def main():
    return new_system()

class Pipes(object):

    def __init__(self):
        self.items = defaultdict(tuple)

pipes = Pipes()

class Pipe():

    async def connect(self, a, b):
        print('Connect', a, b)
        pipes.items[a.name] += (b.name,)
        pipes.items[b.name] += (a.name,)
        return True


def get_system(manager, **config):
    """Perform an async start of a new_sysyem, returning a promise
    """
    loop = asyncio.get_event_loop()
    co_promise = loop.create_task(new_system(manager, **config))
    return co_promise


async def new_system(manager, **config):
    log('New System')
    afs = AdamFlightSystem(**config)
    log('Perform init')

    try:
        await afs.init(manager)
    except asyncio.CancelledError as e:
        raise e
    except Exception as e:
        log('an error has occurred', e)
        traceback.print_exc()
        afs.mounted = False
        afs.exception = e

    return afs


class Signals(object):
    """Application Signals serve to post messages through the API, not strictly
    bound to the game appliance, to allow communication across the app for
    in-game events and knowledge, such as a 'Device signal ready' to prompt an
    input step.
    """
    def __init__(self):
        self.handlers = defaultdict(list)

    async def emit(self, name, data=None):
        print(f'^ Emit {name}')
        for handler in self.handlers[name]:
            await handler(data)

    async def on(self, name, callback):
        print(f'< Signals.on {name}')
        self.handlers[name].append(callback)

    def on_sync(self, name, callback):
        print(f'< sync Signals.on {name}')
        self.handlers[name].append(callback)

    async def off(self, name, callback=None):
        if callback:
            return self.handlers[name].remove(callback)
        r = self.handlers[name]
        del self.handlers[name]
        return r


signals = Signals()


class LogBase(object):

    def __init__(self, **config):
        """The system with the initial config.
        """
        self.counter = 0
        self._name = self.__class__.__name__
        self.__dict__.update(config)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        print('Change name', self._name, ' == ', name)
        self._name = name

    async def log(self, *items):
        """Send a message from this plug item with builtin identity.
        """
        return self.log_sync(*items)

    def log_sync(self, *items):
        items = ' '.join(map(str, items))
        msg = f"{id(self)} | {items}"
        log(msg)
        return msg


    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self):
        return f'<{self.__module__}.{self.__class__.__name__}("{self.name}") at {id(self)}>'


class ComBase(LogBase):

    async def init(self, manager):
        """The instance is awake. Load CMOS.
        """
        log('AFS::CMOS', manager)
        manager.add_connection_reciever(self.receive_connection)
        manager.add_message_reciever(self.receive_manager_message)
        self.manager = manager
        await self.app_start()

    async def receive_connection(self, websocket):
        self.counter += 1
        name = NAMES[self.counter]
        websocket.friendly_name = name
        log('AFS::receive_connection', websocket.friendly_name)
        # self.counter -= 1
        # websocket.friendly_name = name
        await websocket.send_text(f'thank you {websocket.friendly_name}')

    async def receive_manager_message(self, data):
        log("AFS::receive_manager_message", data)
        await self.msg_in(data)

    async def start(self):
        """Start the flight system
        """
        log('AFS::Connect')
        self.manager.broadcast('Flight System Start')

    async def app_start(self):
        """API base for internal application management. Perform any
        class work here before the unit is applied to the game logic
        """
        pass


class Requirement(LogBase):
    """A Pluggable module may have a 'requirement' or dependency. To enable
    this functionality the list of expected modules should exist.
    """
    # A List of named modules to associate with this instance.
    requires = ()

    def __init__(self, **config):
        self.flight_systems = []
        super().__init__(**config)

    def get_requirements(self):
        """Return a the list of requirements from self.requires
        """
        return self.requires

    def get_flight_systems(self):
        return [flight_systems[x] for x in self.flight_systems]

    async def resolve_requirements(self):
        """Return the requirements as an ordered dict of mount system
        """
        res = {}
        ok = True

        for name in self.get_requirements():
            print('Resolving requirement', name)
            mds = await self.get_mounted_by_name(name)
            if len(mds) == 0:
                ok = False
                print('0 for', name)
            res[name] = mds
        return ok, res

    async def get_mounted_by_name(self, name):
        """Return the mounted modules by the given name. If the module
        is missing, return None
        """
        print('Finding', name, 'for', self.name)
        modules = ()
        for fs in self.get_flight_systems():
            module = await fs.get_mounted_by_type(name)
            print('Found', module)
            if module is None:
                print(f'Flight System {id(fs)} does not have module "{name}"')
                continue
            modules += module
        return modules


class Pluggable(Requirement):
    """
    All "modules" within the AFS can be _plugged in_, complete with power
    and _type_ etc.
    """
    # flag true when mount applied.
    mounted = False
    sys_type = ('blank', )

    def get_sys_types(self):
        return self.sys_type

    async def bus_in(self, data):
        """Raw data into layer 0 - likely from outside game events or base
        game executions.
        """
        print('DataNetwork::bus_in', len(data))

    async def bus_out(self, data):
        """send information outside the game to the AFS
        """
        print('DataNetwork::bus_out', len(data))

    async def log(self, *items):
        msg = self.log_sync(*items)
        await self.bus_out(msg)

    async def load_mount(self, flight_system):
        """First call of this pluggable when the AFS starts.
        Keeping a reference is not required as resolution of the AFS
        may be done through the global systems[flight_system.id]
        """
        # Call here as the origin `async init()` is called by the main
        # thread with a connection manager.
        await self.app_load()
        self.flight_systems.append(id(flight_system))
        mv = self.mount()
        self.mounted = True if mv is None else mv
        await self.log(self.__class__.__name__, "mounted")

    async def app_load(self):
        """API base for internal application management. Perform any
        class work here before the unit is applied to the game logic
        """
        pass

    def mount(self):
        """API method for the first function called by the plugin host.
        Optionally return a boolean to set `mounted`. If None is returned
        `mounted` is true.
        """
        print(self.name, 'mount')

    async def map_requirements(self, require_dict):
        """Given a dictionary of tuples, pick the devices and
        bind the requirement to _this_.

        Return a dictionary of tuples; success (bool, pluggable,)

            {"power", (Power(3), Power(2))}
            {
                'power': (True, Power(3), )
            }
        """
        # Successful filter of requirements.
        print('Map', self.name, 'to given requirements', require_dict)
        res = {}
        # choose
        for name, items in require_dict.items():
            pluggable = await self.pick_requirement(name, items)
            print('Selected for', self.name, ':', name, pluggable)
            ok = await self.bind_requirement(name, pluggable)
            res[name] = (ok, pluggable, )

        return res

    async def pick_requirement(self, name, items):
        """Given many items, pick one
        """
        return items[0]

    async def bind_requirement(self, name, pluggable):
        """Given a ready (mounted) plugin item and its name, perform the
        startup sequence to bind the reference plugin to _this_, the item
        referencing the plugin.

        Call to the mapping of _this_ and build a "pipe" between this and
        the pluggable through the API features.

        Consider the "DataNetwork" core utility and the "Power" are bound
        via a plug. The `DataNetwork.requires` must 'plug into' the power -
        through a pipe.
        """

        fn = f'bind_{name}_requirement'
        val = True
        # Call to the internal bind function.
        if hasattr(self, fn):
            val = await getattr(self, fn)(pluggable)

        print(f'Bound {name} to {self.name}: {val}')
        return val

    async def filter_requirements(self, requires_map):
        """Given all the resolve modules, select each type of preferred
        modules by calling to the internal requirement functions, filtering
        unwanted modules.
        """
        res = defaultdict(set)
        ok = True

        # Each item in the discovered 'requires'  map found by resolving
        # the expected requirements
        for name, items in requires_map.items():
            print('\nChecking map for', name)
            # e.g. power_requirement(): Power
            func_name = f"{name}_requirement".lower()
            matches = ()

            # Call upon the internal requirements for this module
            """
            class Example(api.OnOffSwitch)
                require = ('power', )

                def power_requirement(self):
                    return (Power(),)
            """
            if hasattr(self, func_name):
                # Check the internal requirement against the properties
                # of the loaded module.
                print('Resolving', self, func_name)
                # DataNetwork.power_requirement().match(item): Boolean
                req_content = getattr(self, func_name)()

                instance_siblings = (req_content,)
                if isinstance(req_content, (list, tuple)):
                    instance_siblings = req_content

                print(f'Received {len(instance_siblings)} item(s) for',
                    name, 'in', self.name)
                print(' ', instance_siblings)
                # With each item given from the requirement function,
                # test to see if they match the internal expectations.
                # If not, discard the unwanted item
                for other in instance_siblings:
                    print('\n  Evaluating', other)
                    _matches = await other.match_many(items)
                    matches += _matches
                    res[name] = res[name].union(set(_matches))

                if len(matches) == 0:
                    print('Failed', name)
                    ok = False
                # res[name] = matches
            print('Filtered', name, 'to', len(res[name]), 'items')
        return ok, res


class StateTool(object):
    current_state = None

    async def update_state(self, state):
        """Keep a mini map of requires states. When True for
        all keys in the given state dict, call to a 'complete'.
        state.
        """
        print('Updating state')
        current = await self.get_current_state()
        for key, (ok, pluggable) in state.items():
            print('Checking key', key, 'set to:', ok)
            if current.get(key, None) != ok:
                await self.state_changed(key, current.get(key), ok)
            current[key] = ok
        self.current_state = current
        cvs = tuple(set(current.values()))
        if len(cvs) == 1 and (cvs[0] is True):

            await self.state_complete()

    async def state_complete(self):
        """The 'requires' state has succeeded with all True, therefore the
        module is prepared to enable correctly.
        """
        print('Module requirements success', self.name,' - continue to load.')

    async def state_changed(self, key, old, new_):
        print(f'State Change: {self.name} {key} from {old} to {new_}')


    async def get_current_state(self):
        """Return a key boolean map of the current 'requires' states.
        """
        return self.current_state or {}


class OnOffSwitch(Pluggable, StateTool):
    """
    A 'turn on' button for the component
    """
    async def enable_on(self):
        """Perform an 'enable' of this component. This may fail due to internal
        requirements. Next step after a successful enable would be 'switch_on'
        """
        await self.log('enable_on')
        # for name, plugin in self.mounted_pluggables.items():
        print('Turning on', self.name)
        ok, res = await self.resolve_requirements()
        if ok is False:
            await self.enable_on_fail(res)
            return res

        print('Load', self.name, 'with modules', res)
        ok, fills = await self.filter_requirements(res)
        fills = dict({x:tuple(y) for x, y in fills.items()})

        if ok is False:
            await self.enable_on_fail(fills)
            return fills

        state = await self.map_requirements(fills)
        await self.update_state(state)

    async def enable_on_fail(self, res):
        """The 'switch on' method failed. Given a result of the resolved
        requirements
        """
        print('Could not turn on', self.name)


    def switch_off(self):
        """Turn the device off. By default if the device is a 'CRITICAL',
        it cannot be turned off until all requirements
        resolve acceptable.
        """
        # for name, plugin in self.mounted_pluggables.items():
            # pass


class PluginMount(ComBase):

    def get_module_names(self):
        return tuple(self.mounted_pluggables.keys())

    async def get_mounted_by_type(self, name):
        """Return a list of mounted plugins matching the sys_type with the
        given name,
            get_mounted_by_type('power')
            > (Power(),)
        """
        res = ()
        for m_name, item in self.mounted_pluggables.items():
            if name in item.get_sys_types():
                res += (item,)
        return res

    async def get_mounted_by_name(self, name):
        """Return a specific module from the mounted plugins.
            get_mounted_by_name('Power_1')
            Power("Power_1")
        """
        return self.mounted_pluggables.get(name)

    async def load_afs_modules(self):
        """Load class instance modules, preparing the AFS for 'pluggable' game
        modules
        """
        print('AdamFlightSystem::load_afs_modules:', len(self.pluggable))
        for i, pluggable in enumerate(self.pluggable):
            await self.load_afs_module(pluggable, index=i)

    async def load_afs_module(self, pluggable, index=0):
        """Given a Pluggable instance, perform load_mount and
        apply the pluggable to the mounted pluggables.

        return the name of the plugin

        The pluggable.name may change at this point; but this is mostly
        a reference and doesn't impact type selection.
        Provide a unique index number to alter the _postfix of the name
        if a collision is found:

            load_afs_module(Power(), index=3):
            # !!! Name collision
            'Power_3'
        """
        await pluggable.load_mount(self)
        name = pluggable.name
        if name in self.mounted_pluggables:
            print('!!! Name collision', name)
            name = f"{name}_{index}"
            print('Is now', name)
            pluggable.name = name
        self.mounted_pluggables[name] = pluggable
        return name


    async def suite_enable(self):
        """Send a 'turn on' signal through the loaded plugins
        """
        for name, pluggable in self.mounted_pluggables.items():
            print('Suite enable', name)
            await pluggable.enable_on()


class AdamFlightSystem(PluginMount):
    """Managing All aspects of the game engine; the AFS connects websockets
    and all pluggable components. A 'pluggable' should be in-game relevant
    """

    mounted_pluggables = None
    exception = None

    def __init__(self, **config):
        self.pluggable = ()
        self.mounted_pluggables = {}
        super().__init__(**config)
        self.global_store()

    def global_store(self):
        flight_systems[id(self)] = self

    async def append(self, plugin):
        self.pluggable += (plugin, )
        await self.load_afs_module(plugin)

    async def app_start(self):
        """A new manager in synchronous mode"""
        print('AdamFlightSystem::init')
        await self.load_afs_modules()
        await self.log(self.name, 'loaded modules', self.get_module_names())

    async def msg_in(self, data):
        """Text In -
        """
        print('msg_in', data)
        for pluggable in self.mounted_pluggables.values():
            await pluggable.bus_in(data)


if __name__ == '__main__':
    main()
