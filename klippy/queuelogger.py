# Code to implement asynchronous logging from a background thread
#
# Copyright (C) 2016-2019  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import logging.handlers
import os
import queue
import threading
import time

# Tracked modules for per-module logging
TRACKED_MODULES = {
    "heaters": "klippy.extras.heaters",
    "toolhead": "klippy.toolhead",
    "stepper": "klippy.stepper",
    "mcu": "klippy.mcu",
    "extruder": "klippy.kinematics.extruder",
    "gcode": "klippy.gcode",
    "probe": "klippy.extras.probe",
    "endstop_phase": "klippy.extras.endstop_phase",
    "bed_mesh": "klippy.extras.bed_mesh",
    "adc_temperature": "klippy.extras.adc_temperature",
    "thermistor": "klippy.extras.thermistor",
}

# Module loggers registry
_module_loggers = {}
_module_handlers = {}
_component_interactions_enabled = False

# Filter for per-module log routing
class ModuleFilter(logging.Filter):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name

    def filter(self, record):
        return record.name == self.module_name


# Class to forward all messages through a queue to a background thread
class QueueHandler(logging.Handler):
    def __init__(self, queue):
        logging.Handler.__init__(self)
        self.queue = queue

    def emit(self, record):
        try:
            self.format(record)
            record.msg = record.message
            record.args = None
            record.exc_info = None
            self.queue.put_nowait(record)
        except Exception:
            self.handleError(record)


# Class to poll a queue in a background thread and log each message
class QueueListener(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, rotate_log_at_restart):
        if rotate_log_at_restart:
            logging.handlers.TimedRotatingFileHandler.__init__(
                self, filename, when="S", interval=60 * 60 * 24, backupCount=5
            )
        else:
            logging.handlers.TimedRotatingFileHandler.__init__(
                self, filename, when="midnight", backupCount=5
            )
        self.bg_queue = queue.Queue()
        self.bg_thread = threading.Thread(target=self._bg_thread)
        self.bg_thread.start()
        self.rollover_info = {}

    def _bg_thread(self):
        while True:
            record = self.bg_queue.get(True)
            if record is None:
                break
            self.handle(record)

    def stop(self):
        self.bg_queue.put_nowait(None)
        self.bg_thread.join()

    def set_rollover_info(self, name, info):
        if info is None:
            self.rollover_info.pop(name, None)
            return
        self.rollover_info[name] = info

    def clear_rollover_info(self):
        self.rollover_info.clear()

    def doRollover(self):
        logging.handlers.TimedRotatingFileHandler.doRollover(self)
        lines = [
            self.rollover_info[name] for name in sorted(self.rollover_info)
        ]
        lines.append(
            "=============== Log rollover at %s ==============="
            % (time.asctime(),)
        )
        self.emit(
            logging.makeLogRecord(
                {"msg": "\n".join(lines), "level": logging.INFO}
            )
        )


MainQueueHandler = None


def setup_bg_logging(filename, debuglevel, rotate_log_at_restart):
    global MainQueueHandler
    ql = QueueListener(
        filename=filename, rotate_log_at_restart=rotate_log_at_restart
    )
    MainQueueHandler = QueueHandler(ql.bg_queue)
    root = logging.getLogger()
    root.addHandler(MainQueueHandler)
    root.setLevel(debuglevel)
    return ql


def clear_bg_logging():
    global MainQueueHandler
    if MainQueueHandler is not None:
        root = logging.getLogger()
        root.removeHandler(MainQueueHandler)
        root.setLevel(logging.WARNING)
        MainQueueHandler = None


def setup_module_logging(log_dir, log_module_categories):
    """Set up per-module log files for hardware component interaction tracking.

    When log_module_categories is True, creates separate log files for each
    tracked module (heaters, toolhead, stepper, mcu, etc.) in the specified
    log_dir. Each module gets its own named logger that routes to that file.
    """
    global _module_loggers, _module_handlers, _component_interactions_enabled

    if not log_module_categories:
        return

    os.makedirs(log_dir, exist_ok=True)

    for short_name, module_name in TRACKED_MODULES.items():
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True  # Also send to main log

        log_file = os.path.join(log_dir, f"module_{short_name}.log")
        handler = logging.handlers.TimedRotatingFileHandler(
            log_file, when="midnight", backupCount=5
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
        )
        handler.setFormatter(formatter)
        handler.addFilter(ModuleFilter(module_name))
        logger.addHandler(handler)

        _module_loggers[short_name] = logger
        _module_handlers[short_name] = handler


def set_component_interactions_enabled(enabled):
    """Enable/disable verbose hardware component interaction logging."""
    global _component_interactions_enabled
    _component_interactions_enabled = enabled


def get_module_logger(module_name):
    """Get a named logger for a tracked module.

    Args:
        module_name: Short name (e.g., 'heaters', 'toolhead') or full dotted
                     name (e.g., 'klippy.extras.heaters')

    Returns:
        logging.Logger instance for the module, or the root logger if the
        module isn't tracked.
    """
    if module_name in _module_loggers:
        return _module_loggers[module_name]
    # Try full dotted name
    for short_name, full_name in TRACKED_MODULES.items():
        if full_name == module_name:
            return _module_loggers.get(short_name, logging.getLogger())
    return logging.getLogger(module_name)


def should_log_component_interactions():
    """Check if hardware component interaction logging is enabled.

    Modules should wrap their verbose debug logs with this check:
        if should_log_component_interactions():
            logger.debug(...)
    """
    return _component_interactions_enabled
