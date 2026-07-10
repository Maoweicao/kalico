# Production counter and maintenance reminder for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import json
import logging
import os
import time
from datetime import datetime


class ProductionCounter:
    """Production counting and maintenance reminder.

    Tracks print completions, runtime hours, and maintenance intervals.
    Persists data to JSON file across restarts.

    Config format:
        [production_counter]
        count_on_complete: true
        maintenance_interval: 1000
        maintenance_hours: 500
        data_file: ~/production_data.json
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()

        # Configuration
        self.count_on_complete = config.getboolean(
            "count_on_complete", True
        )
        self.maintenance_interval = config.getint(
            "maintenance_interval", 1000, minval=0
        )
        self.maintenance_hours = config.getfloat(
            "maintenance_hours", 500.0, minval=0.0
        )

        # Data file path
        data_file = config.get("data_file", "~/production_data.json")
        if data_file.startswith("~/"):
            data_file = os.path.expanduser(data_file)
        elif not os.path.isabs(data_file):
            config_dir = os.path.dirname(
                config.get_printer().get_start_args().get(
                    "config_file", "."
                )
            )
            data_file = os.path.join(config_dir, data_file)
        self._data_file = data_file

        # Session tracking
        self._session_start_time = time.monotonic()
        self._print_start_time = None
        self._current_print_duration = 0.0

        # Load persisted data
        self._data = self._load_data()

        # Register event handlers
        self.printer.register_event_handler(
            "print_stats:complete_printing", self._on_print_complete
        )
        self.printer.register_event_handler(
            "print_stats:start_printing", self._on_print_start
        )
        self.printer.register_event_handler(
            "print_stats:paused_printing", self._on_print_pause
        )
        self.printer.register_event_handler(
            "klippy:shutdown", self._on_shutdown
        )

        # Register G-code commands
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_PRODUCTION",
            self.cmd_QUERY_PRODUCTION,
            desc="Query production statistics",
        )
        gcode.register_command(
            "RESET_PRODUCTION",
            self.cmd_RESET_PRODUCTION,
            desc="Reset production counters",
        )
        gcode.register_command(
            "MARK_MAINTENANCE",
            self.cmd_MARK_MAINTENANCE,
            desc="Mark maintenance as performed",
        )

        logging.info(
            "ProductionCounter '%s': total_prints=%d, interval=%d",
            self.name,
            self._data.get("total_prints", 0),
            self.maintenance_interval,
        )

    def _load_data(self):
        """Load production data from JSON file."""
        default_data = {
            "total_prints": 0,
            "session_prints": 0,
            "total_runtime_seconds": 0.0,
            "last_maintenance_prints": 0,
            "last_maintenance_time": None,
            "maintenance_history": [],
        }
        try:
            if os.path.exists(self._data_file):
                with open(self._data_file, "r") as f:
                    data = json.load(f)
                # Merge with defaults for missing keys
                for key, val in default_data.items():
                    if key not in data:
                        data[key] = val
                return data
        except Exception as e:
            logging.error(
                "ProductionCounter: failed to load data: %s", e
            )
        return default_data

    def _save_data(self):
        """Save production data to JSON file."""
        try:
            # Ensure directory exists
            data_dir = os.path.dirname(self._data_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir)
            with open(self._data_file, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            logging.error(
                "ProductionCounter: failed to save data: %s", e
            )

    def _on_print_start(self):
        """Called when print starts."""
        self._print_start_time = time.monotonic()

    def _on_print_pause(self):
        """Called when print pauses."""
        if self._print_start_time is not None:
            self._current_print_duration += (
                time.monotonic() - self._print_start_time
            )
            self._print_start_time = None

    def _on_print_complete(self):
        """Called when print completes."""
        # Calculate final print duration
        if self._print_start_time is not None:
            self._current_print_duration += (
                time.monotonic() - self._print_start_time
            )
            self._print_start_time = None

        # Update counters
        self._data["total_prints"] += 1
        self._data["session_prints"] += 1
        self._data["total_runtime_seconds"] += self._current_print_duration
        self._current_print_duration = 0.0

        # Check maintenance
        self._check_maintenance()

        # Save data
        self._save_data()

        # Fire event
        try:
            self.printer.send_event(
                "production_counter:print_completed",
                self.name,
                {
                    "total_prints": self._data["total_prints"],
                    "session_prints": self._data["session_prints"],
                },
            )
        except Exception:
            pass

    def _on_shutdown(self):
        """Called on printer shutdown - save any pending runtime."""
        if self._print_start_time is not None:
            self._current_print_duration += (
                time.monotonic() - self._print_start_time
            )
            self._print_start_time = None
        session_duration = time.monotonic() - self._session_start_time
        self._data["total_runtime_seconds"] += (
            session_duration - self._current_print_duration
        )
        self._save_data()

    def _check_maintenance(self):
        """Check if maintenance reminder should be triggered."""
        if self.maintenance_interval > 0:
            prints_since_maintenance = (
                self._data["total_prints"]
                - self._data["last_maintenance_prints"]
            )
            if prints_since_maintenance >= self.maintenance_interval:
                logging.warning(
                    "MAINTENANCE REMINDER: %d prints completed since "
                    "last maintenance (interval=%d)",
                    prints_since_maintenance,
                    self.maintenance_interval,
                )
                # Fire event
                try:
                    self.printer.send_event(
                        "production_counter:maintenance_due",
                        self.name,
                        {
                            "prints_since": prints_since_maintenance,
                            "interval": self.maintenance_interval,
                        },
                    )
                except Exception:
                    pass

    def get_status(self, eventtime=None):
        """Return production counter status."""
        total_runtime = self._data["total_runtime_seconds"]
        if self._print_start_time is not None:
            total_runtime += time.monotonic() - self._print_start_time

        prints_since_maintenance = (
            self._data["total_prints"]
            - self._data["last_maintenance_prints"]
        )
        maintenance_due = (
            self.maintenance_interval > 0
            and prints_since_maintenance >= self.maintenance_interval
        )

        return {
            "total_prints": self._data["total_prints"],
            "session_prints": self._data["session_prints"],
            "total_runtime_hours": total_runtime / 3600.0,
            "prints_since_maintenance": prints_since_maintenance,
            "maintenance_interval": self.maintenance_interval,
            "maintenance_due": maintenance_due,
            "last_maintenance_time": self._data["last_maintenance_time"],
        }

    def cmd_QUERY_PRODUCTION(self, gcmd):
        """Query production statistics."""
        status = self.get_status()
        lines = [
            "Production Statistics:",
            "  Total prints: %d" % status["total_prints"],
            "  Session prints: %d" % status["session_prints"],
            "  Total runtime: %.1f hours" % status["total_runtime_hours"],
            "  Prints since maintenance: %d / %d"
            % (
                status["prints_since_maintenance"],
                status["maintenance_interval"],
            ),
            "  Maintenance due: %s"
            % ("YES" if status["maintenance_due"] else "No"),
        ]
        if status["last_maintenance_time"]:
            lines.append(
                "  Last maintenance: %s" % status["last_maintenance_time"]
            )
        gcmd.respond_info("\n".join(lines))

    def cmd_RESET_PRODUCTION(self, gcmd):
        """Reset production counters."""
        if "TOTAL" in gcmd.get_command_parameters():
            self._data["total_prints"] = 0
            self._data["total_runtime_seconds"] = 0.0
            self._data["last_maintenance_prints"] = 0
            gcmd.respond_info("All production counters reset")
        else:
            self._data["session_prints"] = 0
            gcmd.respond_info("Session counter reset")
        self._save_data()

    def cmd_MARK_MAINTENANCE(self, gcmd):
        """Mark maintenance as performed."""
        self._data["last_maintenance_prints"] = self._data["total_prints"]
        self._data["last_maintenance_time"] = datetime.now().isoformat()
        if "maintenance_history" not in self._data:
            self._data["maintenance_history"] = []
        self._data["maintenance_history"].append(
            {
                "time": self._data["last_maintenance_time"],
                "prints": self._data["total_prints"],
                "runtime_hours": self._data["total_runtime_seconds"]
                / 3600.0,
            }
        )
        # Keep only last 100 entries
        if len(self._data["maintenance_history"]) > 100:
            self._data["maintenance_history"] = self._data[
                "maintenance_history"
            ][-100:]
        self._save_data()
        gcmd.respond_info(
            "Maintenance marked at print #%d"
            % self._data["total_prints"]
        )


def load_config(config):
    """Load [production_counter] config section."""
    return ProductionCounter(config)
