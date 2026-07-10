# Alarm history persistence for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import json
import logging
import os
from datetime import datetime


class AlarmHistory:
    """Persistent alarm history storage.

    Records all alarm events to JSON and optional text log file.
    Supports querying, clearing, and acknowledging alarms.

    Config format:
        [alarm_history]
        history_file: ~/alarm_history.json
        max_entries: 1000
        log_to_text: true
        text_log_file: ~/alarm_log.txt
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()

        # Configuration
        self.max_entries = config.getint("max_entries", 1000, minval=10)
        self.log_to_text = config.getboolean("log_to_text", True)

        # JSON history file
        history_file = config.get(
            "history_file", "~/alarm_history.json"
        )
        self._history_file = self._resolve_path(config, history_file)

        # Text log file
        text_log_file = config.get(
            "text_log_file", "~/alarm_log.txt"
        )
        self._text_log_file = self._resolve_path(config, text_log_file)

        # Load history
        self._history = self._load_history()

        # Register event handlers
        self.printer.register_event_handler(
            "servo_alarm:triggered", self._on_servo_alarm
        )
        self.printer.register_event_handler(
            "safety_monitor:alarm", self._on_safety_alarm
        )
        self.printer.register_event_handler(
            "emergency_stop:triggered", self._on_estop
        )
        self.printer.register_event_handler(
            "safety_door:opened", self._on_safety_door
        )

        # Register G-code commands
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_ALARM_HISTORY",
            self.cmd_QUERY_ALARM_HISTORY,
            desc="Query alarm history",
        )
        gcode.register_command(
            "CLEAR_ALARM_HISTORY",
            self.cmd_CLEAR_ALARM_HISTORY,
            desc="Clear alarm history",
        )
        gcode.register_command(
            "ACKNOWLEDGE_ALARM",
            self.cmd_ACKNOWLEDGE_ALARM,
            desc="Acknowledge an alarm",
        )

        logging.info(
            "AlarmHistory '%s': file=%s, max=%d",
            self.name,
            self._history_file,
            self.max_entries,
        )

    def _resolve_path(self, config, path):
        """Resolve file path relative to config directory."""
        if path.startswith("~/"):
            return os.path.expanduser(path)
        elif not os.path.isabs(path):
            config_dir = os.path.dirname(
                config.get_printer().get_start_args().get(
                    "config_file", "."
                )
            )
            return os.path.join(config_dir, path)
        return path

    def _load_history(self):
        """Load alarm history from JSON file."""
        try:
            if os.path.exists(self._history_file):
                with open(self._history_file, "r") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "alarms" in data:
                    return data
        except Exception as e:
            logging.error(
                "AlarmHistory: failed to load history: %s", e
            )
        return {"alarms": [], "statistics": {"total_alarms": 0}}

    def _save_history(self):
        """Save alarm history to JSON file."""
        try:
            data_dir = os.path.dirname(self._history_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir)
            with open(self._history_file, "w") as f:
                json.dump(self._history, f, indent=2)
        except Exception as e:
            logging.error(
                "AlarmHistory: failed to save history: %s", e
            )

    def _add_entry(self, alarm_type, source, details):
        """Add an alarm entry to history."""
        entry = {
            "id": len(self._history["alarms"]) + 1,
            "time": datetime.now().isoformat(),
            "type": alarm_type,
            "source": source,
            "details": details,
            "acknowledged": False,
        }
        self._history["alarms"].append(entry)

        # Trim to max entries
        if len(self._history["alarms"]) > self.max_entries:
            self._history["alarms"] = self._history["alarms"][
                -self.max_entries :
            ]

        # Update statistics
        stats = self._history["statistics"]
        stats["total_alarms"] = stats.get("total_alarms", 0) + 1
        if "by_type" not in stats:
            stats["by_type"] = {}
        stats["by_type"][alarm_type] = (
            stats["by_type"].get(alarm_type, 0) + 1
        )

        # Save to JSON
        self._save_history()

        # Save to text log
        if self.log_to_text:
            self._write_text_log(entry)

        # Fire event
        try:
            self.printer.send_event(
                "alarm_history:recorded", self.name, entry
            )
        except Exception:
            pass

    def _write_text_log(self, entry):
        """Write alarm entry to text log file."""
        try:
            data_dir = os.path.dirname(self._text_log_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir)
            with open(self._text_log_file, "a") as f:
                ack = " [ACK]" if entry["acknowledged"] else ""
                line = (
                    "%s | %-15s | %-20s | %s%s\n"
                    % (
                        entry["time"],
                        entry["type"],
                        entry["source"],
                        json.dumps(entry["details"]),
                        ack,
                    )
                )
                f.write(line)
        except Exception as e:
            logging.error(
                "AlarmHistory: failed to write text log: %s", e
            )

    def _on_servo_alarm(self, source, alarm_type, details):
        """Handle servo_alarm events."""
        self._add_entry("servo_alarm", source, details)

    def _on_safety_alarm(self, source, alarm_type, details):
        """Handle safety_monitor events."""
        self._add_entry("safety_" + alarm_type, source, details)

    def _on_estop(self, source, details):
        """Handle emergency_stop events."""
        self._add_entry("emergency_stop", source, details)

    def _on_safety_door(self, source, details):
        """Handle safety_door events."""
        self._add_entry("safety_door", source, details)

    def get_status(self, eventtime=None):
        """Return alarm history status."""
        stats = self._history.get("statistics", {})
        recent = self._history.get("alarms", [])[-5:]  # Last 5
        unacknowledged = sum(
            1
            for a in self._history.get("alarms", [])
            if not a.get("acknowledged", False)
        )
        return {
            "total_alarms": stats.get("total_alarms", 0),
            "unacknowledged": unacknowledged,
            "recent_alarms": recent,
            "by_type": stats.get("by_type", {}),
        }

    def cmd_QUERY_ALARM_HISTORY(self, gcmd):
        """Query alarm history."""
        count = gcmd.get_int("COUNT", 10, minval=1, maxval=100)
        alarms = self._history.get("alarms", [])[-count:]

        if not alarms:
            gcmd.respond_info("No alarm history")
            return

        stats = self._history.get("statistics", {})
        lines = [
            "Alarm History (total=%d, showing last %d):"
            % (stats.get("total_alarms", 0), count),
            "",
            "%-5s %-20s %-15s %-20s %s"
            % ("ID", "Time", "Type", "Source", "Ack"),
            "-" * 80,
        ]

        for alarm in alarms:
            ack = "Yes" if alarm.get("acknowledged") else "No"
            time_str = alarm.get("time", "")[:19]  # Trim microseconds
            lines.append(
                "%-5d %-20s %-15s %-20s %s"
                % (
                    alarm.get("id", 0),
                    time_str,
                    alarm.get("type", ""),
                    alarm.get("source", ""),
                    ack,
                )
            )

        gcmd.respond_info("\n".join(lines))

    def cmd_CLEAR_ALARM_HISTORY(self, gcmd):
        """Clear alarm history."""
        self._history = {"alarms": [], "statistics": {"total_alarms": 0}}
        self._save_history()
        # Clear text log too
        if self.log_to_text:
            try:
                with open(self._text_log_file, "w") as f:
                    f.write("")
            except Exception:
                pass
        gcmd.respond_info("Alarm history cleared")

    def cmd_ACKNOWLEDGE_ALARM(self, gcmd):
        """Acknowledge an alarm."""
        alarm_id = gcmd.get_int("ID", minval=1)
        alarms = self._history.get("alarms", [])
        for alarm in alarms:
            if alarm.get("id") == alarm_id:
                alarm["acknowledged"] = True
                self._save_history()
                gcmd.respond_info(
                    "Alarm #%d acknowledged" % alarm_id
                )
                return
        gcmd.respond_info("Alarm #%d not found" % alarm_id)


def load_config(config):
    """Load [alarm_history] config section."""
    return AlarmHistory(config)
