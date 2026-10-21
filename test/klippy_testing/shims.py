import threading
import typing

import klippy.configfile
import klippy.extras.danger_options
import klippy.gcode


class Restart(Exception): ...


class ReactorShim:
    """A minimal stand-in for klippy.reactor.Reactor.

    It exposes the small part of the reactor API that modules use when they
    are exercised without a real printer: a controllable clock, timers and
    mutexes.
    """

    NEVER = 9999999999.999

    def __init__(self):
        self._now = 0.0
        self._timers = {}
        self._next_timer = 0

    def monotonic(self):
        return self._now

    def advance(self, delta):
        """Move the clock forward by "delta" seconds."""
        self._now += delta

    def register_timer(self, callback, waketime=None):
        self._next_timer += 1
        handle = ("timer", self._next_timer)
        self._timers[handle] = (callback, waketime)
        return handle

    def update_timer(self, handle, waketime):
        callback, _ = self._timers[handle]
        self._timers[handle] = (callback, waketime)

    def unregister_timer(self, handle):
        self._timers.pop(handle, None)

    def get_timer_waketime(self, handle):
        return self._timers[handle][1]

    def mutex(self, is_locked=False):
        return threading.RLock() if is_locked else threading.Lock()


class PrinterShim:
    class GCode:
        error = Exception

        def __init__(self):
            self.ready_gcode_handlers = {}
            self.responses = []
            self.scripts = []

        def register_command(self, cmd, func, *_, **__):
            self.ready_gcode_handlers[cmd.upper()] = func

        def register_mux_command(self, cmd, key, func, *_, **__):
            self.ready_gcode_handlers[cmd.upper()] = func

        def respond_info(self, msg):
            self.responses.append(msg)
            print("info", msg)

        def respond_raw(self, msg):
            self.responses.append(msg)
            print("raw", msg)

        def run_script_from_command(self, script):
            self.scripts.append(script)

        def request_restart(self, reason):
            raise Restart(reason)

        def call(self, cmdline):
            command, *paramlist = cmdline.split()
            func = self.ready_gcode_handlers[command.upper()]
            params = dict(param.split("=", 1) for param in paramlist)
            gcmd = klippy.gcode.GCodeCommand(
                self, command, cmdline, params, False
            )
            print("Calling", func, params)
            func(gcmd)

    def __init__(self, start_args):
        self.start_args = start_args
        self.objects = {}
        self.reactor = ReactorShim()
        self.event_handlers = {}
        self.shutdowns = []
        self.add_object("gcode", self.GCode())
        self.add_object("configfile", klippy.configfile.PrinterConfig(self))

        self.call = self.lookup_object("gcode").call

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def get_start_args(self):
        return self.start_args

    def get_reactor(self):
        return self.reactor

    def add_object(self, name, obj):
        self.objects[name] = obj

    def register_event_handler(self, name, cb):
        self.event_handlers.setdefault(name, []).append(cb)

    def send_event(self, name, *args):
        for cb in list(self.event_handlers.get(name, [])):
            cb(*args)

    def invoke_shutdown(self, msg):
        self.shutdowns.append(msg)

    @typing.overload
    def lookup_object(self, name: typing.Literal["gcode"]) -> GCode: ...
    @typing.overload
    def lookup_object(
        self, name: typing.Literal["configfile"]
    ) -> klippy.configfile.PrinterConfig: ...

    def lookup_object(self, name, default=None):
        return self.objects.get(name, default)

    def lookup_objects(self, pfx=""):
        if pfx:
            pfx = pfx + " "
        return [(k, v) for k, v in self.objects.items() if k.startswith(pfx)]

    def load_config(self):
        config = self.lookup_object("configfile").read_main_config()
        self.add_object(
            "danger_options",
            klippy.extras.danger_options.load_config(
                config.getsection("danger_options")
            ),
        )
        return config

    def set_rollover_info(self, *_): ...
