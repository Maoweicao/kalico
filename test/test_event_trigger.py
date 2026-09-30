# Tests for the generic event listener + delayed action scheduler
# (klippy/extras/event_trigger.py)
#
# Uses lightweight fakes for the printer/reactor/gcode/macro interfaces to
# exercise the scheduling logic deterministically.

import math

import pytest

from klippy.extras import event_trigger


class FakeReactor:
    NOW = 0.0
    NEVER = 9999999999999999.0

    def __init__(self):
        self.t = 1000.0
        self.timers = []

    def monotonic(self):
        return self.t

    def register_timer(self, callback, waketime):
        handle = FakeTimer()
        handle.callback = callback
        handle.waketime = waketime
        self.timers.append(handle)
        return handle

    def update_timer(self, handle, waketime):
        handle.waketime = waketime

    def fire(self, handle, eventtime=None):
        if eventtime is None:
            eventtime = self.t
        return handle.callback(eventtime)

    def advance(self, dt):
        self.t += dt


class FakeTimer:
    def __init__(self):
        self.callback = None
        self.waketime = FakeReactor.NEVER


class _Mutex:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeGCode:
    error = Exception

    def __init__(self):
        self.mux = {}
        self.scripts = []
        self.mutex = _Mutex()
        self.msgs = []

    def register_mux_command(self, cmd, key, value, func, desc=None):
        self.mux.setdefault(cmd, {})[value] = func

    def get_mutex(self):
        return self.mutex

    def run_script_from_command(self, script):
        self.scripts.append(script)

    def respond_info(self, msg):
        self.msgs.append(msg)


class FakeTemplate:
    """Records the context it was executed/render with."""

    def __init__(self, render_result="True"):
        self.context = None
        self.ran = 0
        self.render_result = render_result

    def run_gcode_from_command(self, context):
        self.context = context
        self.ran += 1

    def render(self, context):
        self.context = context
        return self.render_result


class FakeMacro:
    def __init__(self, action, condition=None):
        self.action = action
        self.condition = condition
        self.contexts = []

    def load_template(self, config, option):
        if option == "condition":
            return self.condition
        return self.action

    def create_template_context(self):
        return {"printer": object(), "math": math}


class FakePrinter:
    command_error = Exception

    def __init__(self, reactor, gcode, macro):
        self.reactor = reactor
        self.gcode = gcode
        self.macro = macro
        self.handlers = {}

    def get_reactor(self):
        return self.reactor

    def lookup_object(self, name):
        if name == "gcode":
            return self.gcode
        raise KeyError(name)

    def load_object(self, config, name):
        if name == "gcode_macro":
            return self.macro
        raise KeyError(name)

    def register_event_handler(self, event, callback):
        self.handlers.setdefault(event, []).append(callback)

    def send_event(self, event, *params):
        for cb in self.handlers.get(event, []):
            cb(*params)


class FakeConfig:
    def __init__(self, printer, name="event_trigger test", **opts):
        self.printer = printer
        self.name = name
        self.opts = opts
        self.error = Exception

    def get_printer(self):
        return self.printer

    def get_name(self):
        return self.name

    def get(self, option, default=None, note_valid=True):
        return self.opts.get(option, default)

    def getfloat(self, option, default=None, minval=None, maxval=None):
        value = self.opts.get(option, default if default is not None else 0.0)
        value = float(value)
        if minval is not None and value < minval:
            raise self.error("below min")
        return value


def _build(action_render="True", events="print_stats:complete_printing",
           delay="0.0", condition=None):
    reactor = FakeReactor()
    gcode = FakeGCode()
    action = FakeTemplate(render_result=action_render)
    cond = FakeTemplate() if condition is not None else None
    macro = FakeMacro(action, cond)
    printer = FakePrinter(reactor, gcode, macro)

    opts = {"events": events, "delay": delay, "gcode": "DUMMY"}
    if condition is not None:
        opts["condition"] = condition
    config = FakeConfig(printer, **opts)

    trig = event_trigger.EventTrigger(config)
    trig._handle_ready()
    return reactor, gcode, printer, action, cond, trig


def test_parses_events_and_subscribes():
    reactor, gcode, printer, action, cond, trig = _build(
        events="print_stats:complete_printing\nprint_stats:cancelled_printing"
    )
    assert trig.events == [
        "print_stats:complete_printing",
        "print_stats:cancelled_printing",
    ]
    assert "print_stats:complete_printing" in printer.handlers
    assert "print_stats:cancelled_printing" in printer.handlers
    # Mux commands registered
    assert "test" in gcode.mux["RUN_EVENT_TRIGGER"]
    assert "test" in gcode.mux["CANCEL_EVENT_TRIGGER"]


def test_event_fires_immediately_when_delay_zero():
    reactor, gcode, printer, action, cond, trig = _build(delay="0.0")
    printer.send_event("print_stats:complete_printing")
    # Timer armed at NOW
    handle = trig.timer_handler
    assert handle.waketime == reactor.NOW
    assert trig.pending is False
    reactor.fire(handle)
    assert action.ran == 1


def test_event_fires_after_delay():
    reactor, gcode, printer, action, cond, trig = _build(delay="10.0")
    printer.send_event("print_stats:complete_printing")
    handle = trig.timer_handler
    assert handle.waketime == reactor.monotonic() + 10.0
    assert trig.pending is True
    # Before the delay elapses, nothing runs.
    reactor.advance(5.0)
    assert action.ran == 0
    # After the delay it runs.
    reactor.fire(handle)
    assert action.ran == 1


def test_event_params_injected():
    reactor, gcode, printer, action, cond, trig = _build(
        delay="0.0", events="filament:runout"
    )
    printer.send_event("filament:runout", 123.0, "sensor_1")
    reactor.fire(trig.timer_handler)
    assert action.context["event"] == "filament:runout"
    assert action.context["params"] == (123.0, "sensor_1")


def test_condition_false_blocks_execution():
    reactor, gcode, printer, action, cond, trig = _build(
        delay="0.0", condition="printer.idle_timeout.state == 'Idle'"
    )
    cond.render_result = "False"
    printer.send_event("print_stats:complete_printing")
    reactor.fire(trig.timer_handler)
    assert action.ran == 0


def test_condition_true_allows_execution():
    reactor, gcode, printer, action, cond, trig = _build(
        delay="0.0", condition="printer.idle_timeout.state == 'Idle'"
    )
    cond.render_result = "True"
    printer.send_event("print_stats:complete_printing")
    reactor.fire(trig.timer_handler)
    assert action.ran == 1


def test_cancel_event_trigger():
    reactor, gcode, printer, action, cond, trig = _build(delay="10.0")
    printer.send_event("print_stats:complete_printing")
    assert trig.pending is True
    # Fire the CANCEL command via the registered mux handler.
    gcmd = FakeGCodeCommand()
    gcode.mux["CANCEL_EVENT_TRIGGER"]["test"](gcmd)
    assert trig.timer_handler.waketime == reactor.NEVER
    assert trig.pending is False


def test_run_event_trigger_manual():
    reactor, gcode, printer, action, cond, trig = _build(delay="5.0")
    gcmd = FakeGCodeCommand({"DELAY": "0.0"})
    gcode.mux["RUN_EVENT_TRIGGER"]["test"](gcmd)
    reactor.fire(trig.timer_handler)
    assert action.ran == 1


def test_run_event_trigger_override_delay():
    reactor, gcode, printer, action, cond, trig = _build(delay="5.0")
    gcmd = FakeGCodeCommand({"DELAY": "2.0"})
    gcode.mux["RUN_EVENT_TRIGGER"]["test"](gcmd)
    assert trig.timer_handler.waketime == pytest.approx(
        reactor.monotonic() + 2.0
    )


def test_empty_events_rejected():
    with pytest.raises(Exception):
        _build(events="   \n")


class FakeGCodeCommand:
    def __init__(self, params=None):
        self.params = params or {}

    def get_float(self, item, default=None, minval=None, min=None):
        if item in self.params:
            return float(self.params[item])
        return float(default) if default is not None else minval

    def get_command_parameters(self):
        return self.params

    def respond_info(self, msg):
        pass
