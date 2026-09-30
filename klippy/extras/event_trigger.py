# Generic event listener and delayed action scheduler
#
# This module listens for one or more printer events and, when they occur,
# executes a gcode (or Python) template after an optional delay in seconds.
# It reuses the [gcode_macro] rendering machinery so templates support the
# full Kalico programming feature set (Jinja2 for plain gcode, or a
# '!' prefixed Python script).
#
# Config format (one section per trigger, many allowed):
#
#   [event_trigger on_print_complete]
#   events:
#       print_stats:complete_printing
#       print_stats:cancelled_printing
#   delay: 10.0
#   condition:
#       printer.idle_timeout.state == "Idle"
#   gcode:
#       RESPOND MSG="Print is done"
#
#   # Python (programmable) flavour:
#   [event_trigger on_runout_log]
#   events:
#       filament:runout
#   delay: 2
#   gcode:
#       !
#       response = "runout on %s" % params[1]
#       respond_info(response)
#
# Runtime commands:
#   RUN_EVENT_TRIGGER ID=<name> [DELAY=<sec>]   - manually fire a trigger
#   CANCEL_EVENT_TRIGGER ID=<name>              - cancel a pending trigger
#
# The event payload (if any) is exposed to the template as `params` and the
# event name as `event`.
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import ast
import logging


class EventTrigger:
    def __init__(self, config):
        if len(config.get_name().split()) > 2:
            raise config.error(
                "Name of section '%s' contains illegal whitespace"
                % (config.get_name())
            )
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.name = config.get_name().split()[1]
        self.gcode = self.printer.lookup_object("gcode")
        self.gcode_macro = self.printer.load_object(config, "gcode_macro")

        # Parse the list of events to listen for (comma and/or newline
        # separated).
        raw_events = config.get("events")
        self.events = [
            e.strip()
            for e in raw_events.replace(",", "\n").split("\n")
            if e.strip()
        ]
        if not self.events:
            raise config.error(
                "Option 'events' in section '%s' must specify at least "
                "one event" % (config.get_name())
            )

        self.delay = config.getfloat("delay", 0.0, minval=0.0)

        # Load the action template (gcode or python) and the optional
        # condition (a Jinja expression evaluated before firing).
        self.action = self.gcode_macro.load_template(config, "gcode")
        self.condition = None
        if config.get("condition", None) is not None:
            self.condition = self.gcode_macro.load_template(
                config, "condition"
            )

        # Scheduling state
        self.timer_handler = None
        self.inside_timer = False
        self.pending = False
        self.repeat_request = None
        self.last_event = None
        self.params = ()
        self.last_triggered = None

        # Subscribe to every configured event.
        for event in self.events:
            self.printer.register_event_handler(
                event, self._make_subscription_handler(event)
            )

        self.printer.register_event_handler("klippy:ready", self._handle_ready)

        # Manual trigger / cancel commands, dispatched on ID.
        self.gcode.register_mux_command(
            "RUN_EVENT_TRIGGER",
            "ID",
            self.name,
            self.cmd_RUN_EVENT_TRIGGER,
            desc="Manually fire an event trigger",
        )
        self.gcode.register_mux_command(
            "CANCEL_EVENT_TRIGGER",
            "ID",
            self.name,
            self.cmd_CANCEL_EVENT_TRIGGER,
            desc="Cancel a pending event trigger",
        )

    def _make_subscription_handler(self, event):
        def handler(*params):
            self._arm(self.delay, event, params)

        return handler

    def _handle_ready(self):
        self.timer_handler = self.reactor.register_timer(
            self._timer_event, self.reactor.NEVER
        )

    def get_status(self, eventtime):
        return {
            "name": self.name,
            "events": list(self.events),
            "delay": self.delay,
            "last_event": self.last_event,
            "last_triggered": self.last_triggered,
            "pending": self.pending,
        }

    ######################################################################
    # Triggering
    ######################################################################

    def _arm(self, delay, event, params):
        self.last_event = event
        self.params = params
        if self.timer_handler is None:
            # Timer not yet created (before klippy:ready); schedule lazily.
            self.timer_handler = self.reactor.register_timer(
                self._timer_event, self.reactor.NEVER
            )
        if self.inside_timer:
            # The action is currently executing; run again afterwards.
            self.repeat_request = (delay, event, params)
            return
        self.pending = delay > 0.0
        waketime = self.reactor.NOW
        if delay > 0.0:
            waketime = self.reactor.monotonic() + delay
        self.reactor.update_timer(self.timer_handler, waketime)

    def _render_context(self):
        # Build a template context that carries the event payload plus the
        # standard gcode_macro helpers (printer, action_*, math, ...).
        if hasattr(self.gcode_macro, "create_template_context"):
            context = self.gcode_macro.create_template_context()
        else:
            context = {}
        context["event"] = self.last_event
        context["params"] = self.params
        return context

    def _check_condition(self):
        if self.condition is None:
            return True
        context = self._render_context()
        statement = self.condition.render(context)
        try:
            return bool(ast.literal_eval(statement))
        except (SyntaxError, ValueError) as e:
            logging.exception(
                "event_trigger '%s': invalid condition '%s'",
                self.name,
                statement,
            )
            raise self.gcode.error(
                "event_trigger '%s': invalid condition '%s': %s"
                % (self.name, statement, e)
            )

    def _timer_event(self, eventtime):
        self.inside_timer = True
        self.pending = False
        try:
            if self._check_condition():
                context = self._render_context()
                # Execute the action while holding the gcode mutex so both
                # plain gcode and python (programmable) templates run safely
                # from the reactor timer (which is not a command context).
                with self.gcode.get_mutex():
                    self.action.run_gcode_from_command(context)
                self.last_triggered = eventtime
        except Exception:
            logging.exception("event_trigger '%s' execution", self.name)
        # Determine the next wake time.
        nextwake = self.reactor.NEVER
        if self.repeat_request is not None:
            # An event fired while we were executing; handle it now.
            delay, event, params = self.repeat_request
            self.repeat_request = None
            self.last_event = event
            self.params = params
            self.pending = delay > 0.0
            nextwake = self.reactor.NOW
            if delay > 0.0:
                nextwake = eventtime + delay
        self.inside_timer = False
        return nextwake

    ######################################################################
    # G-code commands
    ######################################################################

    def cmd_RUN_EVENT_TRIGGER(self, gcmd):
        delay = gcmd.get_float("DELAY", self.delay, minval=0.0)
        self._arm(delay, self.name, gcmd.get_command_parameters())
        gcmd.respond_info(
            "event_trigger '%s': armed (delay %.3f s)" % (self.name, delay)
        )

    def cmd_CANCEL_EVENT_TRIGGER(self, gcmd):
        if self.inside_timer:
            self.repeat_request = None
        self.pending = False
        if self.timer_handler is not None:
            self.reactor.update_timer(self.timer_handler, self.reactor.NEVER)
        gcmd.respond_info("event_trigger '%s': cancelled" % (self.name,))


def load_config_prefix(config):
    return EventTrigger(config)
