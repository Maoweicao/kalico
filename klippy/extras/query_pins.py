# Utility for querying MCU pin/bus configuration and detecting conflicts
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.


class QueryPins:
    def __init__(self, config):
        self.printer = config.get_printer()
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_PINS", self.cmd_QUERY_PINS, desc=self.cmd_QUERY_PINS_help
        )

    cmd_QUERY_PINS_help = (
        "Report MCU pin/bus configuration. "
        "Usage: QUERY_PINS [MCU=<name>] [PIN=<pin_name>]"
    )

    def cmd_QUERY_PINS(self, gcmd):
        mcu_name = gcmd.get("MCU", None)
        pin_name = gcmd.get("PIN", None)
        ppins = self.printer.lookup_object("pins")
        if mcu_name is not None:
            self._report_mcu_pins(gcmd, ppins, mcu_name, pin_name)
        else:
            self._report_all_mcus(gcmd, ppins, pin_name)

    def _report_all_mcus(self, gcmd, ppins, pin_name):
        chips = list(ppins.chips.items())
        if not chips:
            gcmd.respond_info("No chips registered")
            return
        lines = ["Registered chips:"]
        for chip_name, chip in sorted(chips):
            chip_type = type(chip).__name__
            info = "  %s (%s)" % (chip_name, chip_type)
            if hasattr(chip, "get_constants"):
                try:
                    constants = chip.get_constants()
                    mcu_type = constants.get("MCU", "")
                    if mcu_type:
                        info += " [%s]" % (mcu_type,)
                except Exception:
                    pass
            if hasattr(chip, "get_enumerations"):
                try:
                    enums = chip.get_enumerations()
                    bus_types = sorted(
                        k for k in enums
                        if k in ("spi_bus", "i2c_bus", "pin")
                    )
                    if bus_types:
                        bus_summary = []
                        for bt in bus_types:
                            bus_summary.append(
                                "%s(%d)" % (bt, len(enums[bt]))
                            )
                        info += " " + ", ".join(bus_summary)
                except Exception:
                    pass
            lines.append(info)
        if pin_name:
            lines.append("")
            lines.extend(self._find_pin_usage(ppins, pin_name))
        gcmd.respond_info("\n".join(lines))

    def _report_mcu_pins(self, gcmd, ppins, mcu_name, pin_name):
        if mcu_name not in ppins.chips:
            available = sorted(ppins.chips.keys())
            msg = "Unknown chip '%s'" % (mcu_name,)
            if available:
                msg += "\nAvailable chips: %s" % (", ".join(available),)
            gcmd.respond_info(msg)
            return
        chip = ppins.chips[mcu_name]
        lines = ["MCU '%s' pin configuration:" % (mcu_name,)]
        # MCU type and version
        if hasattr(chip, "get_constants"):
            try:
                constants = chip.get_constants()
                mcu_type = constants.get("MCU", "unknown")
                lines.append("  MCU type: %s" % (mcu_type,))
            except Exception:
                lines.append("  (MCU not yet connected)")
        # Bus enumerations
        if hasattr(chip, "get_enumerations"):
            try:
                enums = chip.get_enumerations()
                for param in sorted(enums):
                    if param in ("spi_bus", "i2c_bus", "pin"):
                        bus_names = sorted(enums[param].keys())
                        if bus_names:
                            lines.append("  %s: %s" % (
                                param, ", ".join(bus_names)))
            except Exception:
                pass
        # BUS_PINS_* constants
        if hasattr(chip, "get_constants"):
            try:
                constants = chip.get_constants()
                bus_pins = sorted(
                    (k, v) for k, v in constants.items()
                    if k.startswith("BUS_PINS_")
                )
                if bus_pins:
                    lines.append("  Bus pin mappings:")
                    for key, value in bus_pins:
                        bus_name = key[9:]  # strip "BUS_PINS_"
                        lines.append("    %s: %s" % (bus_name, value))
                # RESERVE_PINS_* constants
                reserve_pins = sorted(
                    (k, v) for k, v in constants.items()
                    if k.startswith("RESERVE_PINS_")
                )
                if reserve_pins:
                    lines.append("  Reserved pin constants:")
                    for key, value in reserve_pins:
                        reserve_name = key[13:]  # strip "RESERVE_PINS_"
                        lines.append("    %s: %s" % (reserve_name, value))
            except Exception:
                pass
        # Pin resolver data
        if mcu_name in ppins.pin_resolvers:
            resolver = ppins.pin_resolvers[mcu_name]
            if resolver.reserved:
                lines.append("  Reserved pins:")
                for pin, reason in sorted(resolver.reserved.items()):
                    lines.append("    %s -> %s" % (pin, reason))
            if resolver.aliases:
                lines.append("  Pin aliases:")
                for alias, pin in sorted(resolver.aliases.items()):
                    lines.append("    %s -> %s" % (alias, pin))
        # Active pins on this MCU
        active = {
            k: v for k, v in ppins.active_pins.items()
            if v.get("chip_name") == mcu_name
        }
        if active:
            lines.append("  Active pins (in use by config):")
            for share_name in sorted(active):
                params = active[share_name]
                pin = params.get("pin", "?")
                desc = params.get("description", None)
                share_type = params.get("share_type", None)
                parts = [pin]
                if share_type:
                    parts.append("type=%s" % (share_type,))
                if desc:
                    parts.append("section=%s" % (desc,))
                inv = params.get("invert", 0)
                pull = params.get("pullup", 0)
                if inv or pull:
                    flags = []
                    if inv:
                        flags.append("invert")
                    if pull:
                        flags.append("pullup=%d" % (pull,))
                    parts.append("flags=%s" % (",".join(flags),))
                lines.append("    %s: %s" % (share_name, " ".join(parts)))
            # Conflict detection
            conflicts = self._detect_conflicts(ppins, mcu_name, resolver)
            if conflicts:
                lines.append("  CONFLICTS DETECTED:")
                lines.extend("    " + c for c in conflicts)
        elif not active:
            lines.append("  No pins currently in use")
        if pin_name:
            lines.append("")
            lines.extend(self._find_pin_usage(ppins, pin_name))
        gcmd.respond_info("\n".join(lines))

    def _detect_conflicts(self, ppins, mcu_name, resolver):
        conflicts = []
        active = {
            k: v for k, v in ppins.active_pins.items()
            if v.get("chip_name") == mcu_name
        }
        for share_name, params in active.items():
            pin = params["pin"]
            # Check if pin is reserved
            if pin in resolver.reserved:
                reason = resolver.reserved[pin]
                stype = params.get("share_type", None)
                desc = params.get("description", share_name)
                conflicts.append(
                    "Pin %s is in use (%s) but reserved for %s"
                    % (pin, desc or stype or "unknown", reason)
                )
            # Check if an alias points to a reserved pin
            for alias, alias_pin in resolver.aliases.items():
                if alias_pin == pin and pin in resolver.reserved:
                    reason = resolver.reserved[pin]
                    conflicts.append(
                        "Alias %s -> %s conflicts with reservation '%s'"
                        % (alias, pin, reason)
                    )
        return conflicts

    def _find_pin_usage(self, ppins, pin_name):
        lines = ["Pin '%s' usage across all MCUs:" % (pin_name,)]
        found = False
        for share_name, params in sorted(ppins.active_pins.items()):
            p = params.get("pin", "")
            if p == pin_name or share_name.endswith(":" + pin_name):
                chip_name = params.get("chip_name", "?")
                share_type = params.get("share_type", None)
                desc = params.get("description", None)
                parts = ["  %s" % (share_name,)]
                if share_type:
                    parts.append("type=%s" % (share_type,))
                if desc:
                    parts.append("section=%s" % (desc,))
                lines.append(" ".join(parts))
                found = True
        if not found:
            lines.append("  (not currently in use)")
        return lines


def load_config(config):
    return QueryPins(config)
