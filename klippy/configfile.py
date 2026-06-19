# Code for reading and writing the Klipper config file
#
# Copyright (C) 2016-2021  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import configparser
import glob
import io
import json
import logging
import os
import pathlib
import re
import sys
import time

from . import mathutil
from .extras.danger_options import get_danger_options

error = configparser.Error


class sentinel:
    pass


PYTHON_SCRIPT_PREFIX = "!"
_INCLUDERE = re.compile(r"!!include (?P<file>.*)")


def _fix_include_path(source_file: str, match: re.Match) -> pathlib.Path:
    new_path = pathlib.Path(source_file).parent.absolute() / match.group("file")
    if not new_path.is_file():
        raise error(f"Attempted to include non-existent file {new_path}")
    return f"!!include {new_path}"


def _json_value_to_string(value):
    """Convert a JSON value to a string suitable for CFG format."""
    if isinstance(value, bool):
        return "True" if value else "False"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        return ", ".join(str(item) for item in value)
    elif isinstance(value, dict):
        raise error("Nested JSON objects not supported in config conversion")
    elif value is None:
        return ""
    return str(value)


def _json_to_cfg(json_data, source_file=""):
    """Convert JSON configuration data to CFG format string.
    
    JSON structure is mapped to CFG as follows:
    - JSON objects become sections
    - JSON key-value pairs become options
    - JSON arrays become comma-separated strings
    - Special key 'include' is handled for file includes
    
    Args:
        json_data: Parsed JSON data (dict)
        source_file: Source file path for include resolution
        
    Returns:
        String in CFG format
    """
    lines = []
    
    # Handle top-level include directive
    if "include" in json_data:
        includes = json_data["include"]
        if isinstance(includes, str):
            includes = [includes]
        for include_path in includes:
            lines.append(f"[include {include_path}]")
        lines.append("")
    
    # Process sections
    for section, values in json_data.items():
        if section == "include":
            continue
        
        if not isinstance(values, dict):
            # Top-level scalar values go to [printer] section
            lines.append("[printer]")
            lines.append(f"{section}: {_json_value_to_string(values)}")
            lines.append("")
            continue
        
        lines.append(f"[{section}]")
        for key, value in values.items():
            if isinstance(value, dict):
                # Nested object - treat as sub-section
                for sub_key, sub_value in value.items():
                    lines.append(
                        f"{key}_{sub_key}: {_json_value_to_string(sub_value)}"
                    )
            else:
                lines.append(f"{key}: {_json_value_to_string(value)}")
        lines.append("")
    
    return "\n".join(lines)


def _read_json_config_file(filename):
    """Read a JSON configuration file and convert to CFG format.
    
    Args:
        filename: Path to JSON config file
        
    Returns:
        Tuple of (cfg_data, json_autosave_path)
        - cfg_data: Configuration in CFG format string
        - json_autosave_path: Path to JSON autosave file (or None)
    """
    try:
        with open(filename, "r") as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"Unable to parse JSON config file {filename}: {e}"
        logging.exception(msg)
        raise error(msg)
    except Exception:
        msg = f"Unable to open config file {filename}"
        logging.exception(msg)
        raise error(msg)
    
    if not isinstance(json_data, dict):
        raise error(f"JSON config file {filename} must contain a JSON object")
    
    # Convert JSON to CFG format
    cfg_data = _json_to_cfg(json_data, filename)
    
    # Determine autosave file path
    json_autosave_path = None
    if filename.endswith(".json"):
        json_autosave_path = filename[:-5] + ".autosave.json"
    
    return cfg_data, json_autosave_path


def cfg_to_json(cfg_data, filename="<string>"):
    """Convert CFG format data to a JSON-serializable dict.
    
    This is the inverse of _json_to_cfg(). Useful for converting
    existing .cfg files to .json format.
    
    Args:
        cfg_data: Configuration in CFG format string
        filename: Source filename for error messages
        
    Returns:
        dict suitable for json.dump()
    """
    fileconfig = configparser.RawConfigParser(
        strict=False,
        inline_comment_prefixes=(";", "#"),
    )
    sbuffer = io.StringIO(cfg_data)
    fileconfig.read_file(sbuffer, filename)
    
    result = {}
    for section in fileconfig.sections():
        section_dict = {}
        for option in fileconfig.options(section):
            value = fileconfig.get(section, option)
            # Try to convert to appropriate type
            if value.lower() in ("true", "yes", "on"):
                section_dict[option] = True
            elif value.lower() in ("false", "no", "off"):
                section_dict[option] = False
            else:
                try:
                    section_dict[option] = int(value)
                except ValueError:
                    try:
                        section_dict[option] = float(value)
                    except ValueError:
                        # Handle comma-separated lists
                        if "," in value:
                            items = [v.strip() for v in value.split(",")]
                            converted = []
                            for item in items:
                                try:
                                    converted.append(int(item))
                                except ValueError:
                                    try:
                                        converted.append(float(item))
                                    except ValueError:
                                        converted.append(item)
                            section_dict[option] = converted
                        else:
                            section_dict[option] = value
        result[section] = section_dict
    
    return result


class SectionInterpolation(configparser.Interpolation):
    """
    variable interpolation replacing ${[section.]option}
    """

    _KEYCRE = re.compile(
        r"(?<!\\)?\$\{(?:(?P<section>[^.:${}]+)[.:])?(?P<option>[^${}]+)\}"
    )

    def __init__(self, access_tracking):
        self.access_tracking = access_tracking

    def before_get(self, parser, section, option, value, defaults):
        if not isinstance(value, str):
            return value
        depth = configparser.MAX_INTERPOLATION_DEPTH
        while depth:
            depth -= 1

            match = self._KEYCRE.search(value)
            if not match:
                break

            sect = match.group("section") or section
            opt = match.group("option")

            const = parser.get(sect, opt)
            self.access_tracking.setdefault((sect, opt), const)

            value = value[: match.start()] + const + value[match.end() :]

        return value.replace("\\${", "${")


class ConfigWrapper:
    error = configparser.Error

    def __init__(self, printer, fileconfig, access_tracking, section):
        self.printer = printer
        self.fileconfig = fileconfig
        self.access_tracking = access_tracking
        self.section = section

    def get_printer(self):
        return self.printer

    def get_name(self):
        return self.section

    def _get_wrapper(
        self,
        parser,
        option,
        default,
        minval=None,
        maxval=None,
        above=None,
        below=None,
        note_valid=True,
    ):
        if not self.fileconfig.has_option(self.section, option):
            if default is not sentinel:
                if note_valid and default is not None:
                    acc_id = (self.section.lower(), option.lower())
                    self.access_tracking[acc_id] = default
                return default
            raise error(
                "Option '%s' in section '%s' must be specified"
                % (option, self.section)
            )
        if parser is float:
            parser = mathutil.safe_float
        try:
            v = parser(self.section, option)
        except self.error as e:
            raise
        except:
            raise error(
                "Unable to parse option '%s' in section '%s'"
                % (option, self.section)
            )
        if note_valid:
            self.access_tracking[(self.section.lower(), option.lower())] = v
        if minval is not None and v < minval:
            raise error(
                "Option '%s' in section '%s' must have minimum of %s"
                % (option, self.section, minval)
            )
        if maxval is not None and v > maxval:
            raise error(
                "Option '%s' in section '%s' must have maximum of %s"
                % (option, self.section, maxval)
            )
        if above is not None and v <= above:
            raise error(
                "Option '%s' in section '%s' must be above %s"
                % (option, self.section, above)
            )
        if below is not None and v >= below:
            raise self.error(
                "Option '%s' in section '%s' must be below %s"
                % (option, self.section, below)
            )
        return v

    def get(self, option, default=sentinel, note_valid=True):
        return self._get_wrapper(
            self.fileconfig.get, option, default, note_valid=note_valid
        )

    def getscript(self, option, default=sentinel, note_valid=True):
        value: str = self.get(option, default, note_valid).strip()

        match = _INCLUDERE.search(value)
        if match:
            file_path = pathlib.Path(match.group("file"))
            if file_path.suffix.lower() == ".py":
                return ("python", file_path.read_text())
            else:
                return ("gcode", file_path.read_text())

        elif value.startswith(PYTHON_SCRIPT_PREFIX):
            return (
                "python",
                "\n".join(
                    line.removeprefix(PYTHON_SCRIPT_PREFIX)
                    for line in value.splitlines()
                ),
            )

        return ("gcode", value)

    def getint(
        self,
        option,
        default=sentinel,
        minval=None,
        maxval=None,
        note_valid=True,
    ):
        return self._get_wrapper(
            self.fileconfig.getint,
            option,
            default,
            minval,
            maxval,
            note_valid=note_valid,
        )

    def getfloat(
        self,
        option,
        default=sentinel,
        minval=None,
        maxval=None,
        above=None,
        below=None,
        note_valid=True,
    ):
        return self._get_wrapper(
            self.fileconfig.getfloat,
            option,
            default,
            minval,
            maxval,
            above,
            below,
            note_valid=note_valid,
        )

    def getboolean(self, option, default=sentinel, note_valid=True):
        return self._get_wrapper(
            self.fileconfig.getboolean, option, default, note_valid=note_valid
        )

    def getchoice(self, option, choices, default=sentinel, note_valid=True):
        if isinstance(choices, list):
            choices = {i: i for i in choices}
        if choices and isinstance(list(choices.keys())[0], int):
            c = self.getint(option, default, note_valid=note_valid)
        else:
            c = self.get(option, default, note_valid=note_valid)
        if c not in choices:
            raise error(
                "Choice '%s' for option '%s' in section '%s'"
                " is not a valid choice" % (c, option, self.section)
            )
        return choices[c]

    def getlists(
        self,
        option,
        default=sentinel,
        seps=(",",),
        count=None,
        parser=str,
        note_valid=True,
    ):
        def lparser(value, pos):
            if len(value.strip()) == 0:
                # Return an empty list instead of [''] for empty string
                parts = []
            else:
                parts = [p.strip() for p in value.split(seps[pos])]
            if pos:
                # Nested list
                return tuple([lparser(p, pos - 1) for p in parts if p])
            res = [parser(p) for p in parts]
            if count is not None and len(res) != count:
                raise error(
                    "Option '%s' in section '%s' must have %d elements"
                    % (option, self.section, count)
                )
            return tuple(res)

        def fcparser(section, option):
            return lparser(self.fileconfig.get(section, option), len(seps) - 1)

        return self._get_wrapper(
            fcparser, option, default, note_valid=note_valid
        )

    def getlist(
        self, option, default=sentinel, sep=",", count=None, note_valid=True
    ):
        return self.getlists(
            option,
            default,
            seps=(sep,),
            count=count,
            parser=str,
            note_valid=note_valid,
        )

    def getintlist(
        self, option, default=sentinel, sep=",", count=None, note_valid=True
    ):
        return self.getlists(
            option,
            default,
            seps=(sep,),
            count=count,
            parser=int,
            note_valid=note_valid,
        )

    def getfloatlist(
        self, option, default=sentinel, sep=",", count=None, note_valid=True
    ):
        return self.getlists(
            option,
            default,
            seps=(sep,),
            count=count,
            parser=mathutil.safe_float,
            note_valid=note_valid,
        )

    def getsection(self, section):
        return ConfigWrapper(
            self.printer, self.fileconfig, self.access_tracking, section
        )

    def has_section(self, section):
        return self.fileconfig.has_section(section)

    def get_prefix_sections(self, prefix):
        return [
            self.getsection(s)
            for s in self.fileconfig.sections()
            if s.startswith(prefix)
        ]

    def get_prefix_options(self, prefix):
        return [
            o
            for o in self.fileconfig.options(self.section)
            if o.startswith(prefix)
        ]

    def deprecate(self, option, value=None):
        if not self.fileconfig.has_option(self.section, option):
            return
        if value is None:
            msg = "Option '%s' in section '%s' is deprecated." % (
                option,
                self.section,
            )
        else:
            msg = "Value '%s' in option '%s' in section '%s' is deprecated." % (
                value,
                option,
                self.section,
            )
        pconfig = self.printer.lookup_object("configfile")
        pconfig.deprecate(self.section, option, value, msg)


AUTOSAVE_HEADER = """
#*# <---------------------- SAVE_CONFIG ---------------------->
#*# DO NOT EDIT THIS BLOCK OR BELOW. The contents are auto-generated.
#*#
"""


class PrinterConfig:
    def __init__(self, printer):
        self.printer = printer
        self.autosave = None
        self.json_autosave_path = None
        self.is_json_config = False
        self.deprecated = {}
        self.runtime_warnings = []
        self.deprecate_warnings = []
        self.status_raw_config = {}
        self.status_save_pending = {}
        self.status_settings = {}
        self.status_warnings = []
        self.unused_sections = []
        self.unused_options = []
        self.save_config_pending = False
        gcode = self.printer.lookup_object("gcode")
        if "SAVE_CONFIG" not in gcode.ready_gcode_handlers:
            gcode.register_command(
                "SAVE_CONFIG",
                self.cmd_SAVE_CONFIG,
                desc=self.cmd_SAVE_CONFIG_help,
            )

    def get_printer(self):
        return self.printer

    def _read_config_file(self, filename):
        # Check if this is a JSON config file
        if filename.endswith(".json"):
            cfg_data, json_autosave_path = _read_json_config_file(filename)
            self.is_json_config = True
            self.json_autosave_path = json_autosave_path
            return cfg_data
        
        # Regular CFG file
        try:
            f = open(filename, "r")
            data = f.read()
            f.close()
        except:
            msg = "Unable to open config file %s" % (filename,)
            logging.exception(msg)
            raise error(msg)
        return data.replace("\r\n", "\n")

    def _find_autosave_data(self, data):
        regular_data = data
        autosave_data = ""
        pos = data.find(AUTOSAVE_HEADER)
        if pos >= 0:
            regular_data = data[:pos]
            autosave_data = data[pos + len(AUTOSAVE_HEADER) :].strip()
        # Check for errors and strip line prefixes
        if "\n#*# " in regular_data:
            logging.warning(
                "Can't read autosave from config file"
                " - autosave state corrupted"
            )
            return data, ""
        out = [""]
        for line in autosave_data.split("\n"):
            if (
                not line.startswith("#*#")
                or (len(line) >= 4 and not line.startswith("#*# "))
            ) and autosave_data:
                logging.warning(
                    "Can't read autosave from config file"
                    " - modifications after header"
                )
                return data, ""
            out.append(line[4:])
        out.append("")
        return regular_data, "\n".join(out)

    comment_r = re.compile("[#;].*$")
    value_r = re.compile("[^A-Za-z0-9_].*$")

    def _strip_duplicates(self, data, config):
        # Comment out fields in 'data' that are defined in 'config'
        lines = data.split("\n")
        section = None
        is_dup_field = False
        for lineno, line in enumerate(lines):
            pruned_line = self.comment_r.sub("", line).rstrip()
            if not pruned_line:
                continue
            if pruned_line[0].isspace():
                if is_dup_field:
                    lines[lineno] = "#" + lines[lineno]
                continue
            is_dup_field = False
            if pruned_line[0] == "[":
                section = pruned_line[1:-1].strip()
                continue
            field = self.value_r.sub("", pruned_line)
            if config.fileconfig.has_option(section, field):
                is_dup_field = True
                lines[lineno] = "#" + lines[lineno]
        return "\n".join(lines)

    def _parse_config_buffer(self, buffer, filename, fileconfig):
        if not buffer:
            return
        data = "\n".join(buffer)
        del buffer[:]
        sbuffer = io.StringIO(data)
        if sys.version_info.major >= 3:
            fileconfig.read_file(sbuffer, filename)
        else:
            fileconfig.readfp(sbuffer, filename)

    def _resolve_include(
        self, source_filename, include_spec, fileconfig, visited
    ):
        dirname = os.path.dirname(source_filename)
        include_spec = include_spec.strip()
        include_glob = os.path.join(dirname, include_spec)
        if sys.version_info >= (3, 5):
            include_filenames = glob.glob(include_glob, recursive=True)
        else:
            include_filenames = glob.glob(include_glob)
        if not include_filenames and not glob.has_magic(include_glob):
            # Empty set is OK if wildcard but not for direct file reference
            raise error("Include file '%s' does not exist" % (include_glob,))
        include_filenames.sort()
        for include_filename in include_filenames:
            include_data = self._read_config_file(include_filename)
            self._parse_config(
                include_data, include_filename, fileconfig, visited
            )
        return include_filenames

    def _parse_config(self, data, filename, fileconfig, visited):
        path = os.path.abspath(filename)
        if path in visited:
            raise error("Recursive include of config file '%s'" % (filename))
        visited.add(path)
        lines = data.split("\n")
        # Buffer lines between includes and parse as a unit so that overrides
        # in includes apply linearly as they do within a single file
        buffer = []
        for line in lines:
            # Strip trailing comment
            pos = line.find("#")
            if pos >= 0:
                line = line[:pos]
            # Process include or buffer line
            mo = configparser.RawConfigParser.SECTCRE.match(line)
            header = mo and mo.group("header")
            if header and header.startswith("include "):
                self._parse_config_buffer(buffer, filename, fileconfig)
                include_spec = header[8:].strip()
                self._resolve_include(
                    filename, include_spec, fileconfig, visited
                )
            else:
                line = _INCLUDERE.sub(
                    lambda match: _fix_include_path(filename, match),
                    line,
                )
                buffer.append(line)
        self._parse_config_buffer(buffer, filename, fileconfig)
        visited.remove(path)

    def _build_config_wrapper(self, data, filename):
        access_tracking = {}
        fileconfig = configparser.RawConfigParser(
            strict=False,
            inline_comment_prefixes=(";", "#"),
            interpolation=SectionInterpolation(access_tracking),
        )

        self._parse_config(data, filename, fileconfig, set())
        return ConfigWrapper(
            self.printer, fileconfig, access_tracking, "printer"
        )

    def _build_config_string(self, config):
        sfile = io.StringIO()
        config.fileconfig.write(sfile)
        return sfile.getvalue().strip()

    def read_config(self, filename):
        return self._build_config_wrapper(
            self._read_config_file(filename), filename
        )

    def read_main_config(self):
        filename = self.printer.get_start_args()["config_file"]
        data = self._read_config_file(filename)
        
        if self.is_json_config:
            # JSON config uses separate autosave file
            autosave_data = self._load_json_autosave()
            regular_config = self._build_config_wrapper(data, filename)
            autosave_data = self._strip_duplicates(autosave_data, regular_config)
            self.autosave = self._build_config_wrapper(autosave_data, filename)
            cfg = self._build_config_wrapper(data + autosave_data, filename)
        else:
            # Traditional CFG config with inline autosave
            regular_data, autosave_data = self._find_autosave_data(data)
            regular_config = self._build_config_wrapper(regular_data, filename)
            autosave_data = self._strip_duplicates(autosave_data, regular_config)
            self.autosave = self._build_config_wrapper(autosave_data, filename)
            cfg = self._build_config_wrapper(regular_data + autosave_data, filename)
        
        return cfg

    def _load_json_autosave(self):
        """Load autosave data from JSON autosave file."""
        if not self.json_autosave_path:
            return ""
        
        if not os.path.exists(self.json_autosave_path):
            return ""
        
        try:
            with open(self.json_autosave_path, "r") as f:
                autosave_json = json.load(f)
        except json.JSONDecodeError as e:
            logging.warning(
                "Can't read JSON autosave file %s: %s",
                self.json_autosave_path, e
            )
            return ""
        except Exception:
            logging.warning(
                "Unable to read JSON autosave file %s",
                self.json_autosave_path
            )
            return ""
        
        if not isinstance(autosave_json, dict):
            logging.warning(
                "JSON autosave file %s must contain a JSON object",
                self.json_autosave_path
            )
            return ""
        
        # Convert JSON autosave to CFG format
        return _json_to_cfg(autosave_json, self.json_autosave_path)

    def check_unused_options(self, config, error_on_unused):
        fileconfig = config.fileconfig
        objects = dict(self.printer.lookup_objects())
        # Determine all the fields that have been accessed
        access_tracking = dict(config.access_tracking)
        for section in self.autosave.fileconfig.sections():
            for option in self.autosave.fileconfig.options(section):
                access_tracking[(section.lower(), option.lower())] = 1
        # Validate that there are no undefined parameters in the config file
        valid_sections = {s for s, o in access_tracking}
        for section_name in fileconfig.sections():
            section = section_name.lower()
            if section not in valid_sections and section not in objects:
                if error_on_unused:
                    raise error(
                        "Section '%s' is not a valid config section"
                        % (section,)
                    )
                else:
                    self.unused_sections.append(section)
            for option in fileconfig.options(section_name):
                option = option.lower()
                if (section, option) not in access_tracking:
                    if error_on_unused and section != "constants":
                        raise error(
                            "Option '%s' is not valid in section '%s'"
                            % (option, section)
                        )
                    else:
                        self.unused_options.append((section, option))
        # Setup get_status()
        self._build_status(config)

    def log_config(self, config):
        lines = [
            "===== Config file =====",
            self._build_config_string(config),
            "=======================",
        ]
        self.printer.set_rollover_info("config", "\n".join(lines))

    # Status reporting
    def runtime_warning(self, msg):
        logging.warning(msg)
        res = {"type": "runtime_warning", "message": msg}
        self.runtime_warnings.append(res)
        self.status_warnings = self.runtime_warnings + self.deprecate_warnings

    def deprecate(self, section, option, value=None, msg=None):
        self.deprecated[(section, option, value)] = msg

    def warn(self, type, msg, section=None, option=None, value=None):
        res = {
            "type": type,
            "message": msg,
        }
        if section is not None:
            res["section"] = section
        if option is not None:
            res["option"] = option
        if value is not None:
            res["value"] = value
        self.status_warnings.append(res)

    def _build_status(self, config):
        self.status_raw_config.clear()
        for section in config.get_prefix_sections(""):
            self.status_raw_config[section.get_name()] = section_status = {}
            for option in section.get_prefix_options(""):
                section_status[option] = section.get(option, note_valid=False)
        self.status_settings = {}
        for (section, option), value in config.access_tracking.items():
            self.status_settings.setdefault(section, {})[option] = value
        for (section, option, value), msg in self.deprecated.items():
            _type = "deprecated_value"
            self.warn(_type, msg, section, option, value)

        for section, option in self.unused_options:
            _type = "unused_option"
            if section == "constants":
                msg = f"Constant '{option}' is unused"
            else:
                msg = f"Option '{option}' in section '{section}' is invalid"
            self.warn(_type, msg, section, option)
        for section in self.unused_sections:
            _type = "unused_section"
            msg = f"Section '{section}' is invalid"
            self.warn(_type, msg, section)

    def get_status(self, eventtime):
        return {
            "config": self.status_raw_config,
            "settings": self.status_settings,
            "warnings": self.status_warnings,
            "save_config_pending": self.save_config_pending,
            "save_config_pending_items": self.status_save_pending,
        }

    # Autosave functions
    def set(self, section, option, value):
        if not self.autosave.fileconfig.has_section(section):
            self.autosave.fileconfig.add_section(section)
        svalue = str(value)
        self.autosave.fileconfig.set(section, option, svalue)
        pending = dict(self.status_save_pending)
        if section not in pending or pending[section] is None:
            pending[section] = {}
        else:
            pending[section] = dict(pending[section])
        pending[section][option] = svalue
        self.status_save_pending = pending
        self.save_config_pending = True
        logging.info("save_config: set [%s] %s = %s", section, option, svalue)

    def remove_section(self, section):
        if self.autosave.fileconfig.has_section(section):
            self.autosave.fileconfig.remove_section(section)
            pending = dict(self.status_save_pending)
            pending[section] = None
            self.status_save_pending = pending
            self.save_config_pending = True
        elif (
            section in self.status_save_pending
            and self.status_save_pending[section] is not None
        ):
            pending = dict(self.status_save_pending)
            del pending[section]
            self.status_save_pending = pending
            self.save_config_pending = True

    def _disallow_include_conflicts(self, regular_data, cfgname, gcode):
        config = self._build_config_wrapper(regular_data, cfgname)
        for section in self.autosave.fileconfig.sections():
            for option in self.autosave.fileconfig.options(section):
                if config.fileconfig.has_option(section, option):
                    # They conflict only if they are not the same value
                    included_value = config.fileconfig.get(section, option)
                    autosave_value = self.autosave.fileconfig.get(
                        section, option
                    )
                    if included_value != autosave_value:
                        msg = (
                            "SAVE_CONFIG section '%s' option '%s' value '%s' conflicts "
                            "with included value '%s' "
                            % (section, option, autosave_value, included_value)
                        )
                        raise gcode.error(msg)

    cmd_SAVE_CONFIG_help = "Overwrite config file and restart"

    def _write_backup(self, cfgpath, cfgdata, gcode):
        printercfg = self.printer.get_start_args()["config_file"]
        configdir = os.path.dirname(printercfg)
        # Define a directory for configuration backups so that include blocks
        # using a wildcard to reference all files in a directory don't throw
        # errors
        backupdir = os.path.join(configdir, "config_backups")
        # Create the backup directory if it doesn't already exist
        if not os.path.exists(backupdir):
            os.mkdir(backupdir)

        # Generate the name of the backup file by stripping the leading path in
        # `cfgpath` and appending to it. Then add it to the config_backups dir
        datestr = time.strftime("-%Y%m%d_%H%M%S")
        cfgname = os.path.basename(cfgpath)
        backup_path = backupdir + "/" + cfgname + datestr
        if cfgpath.endswith(".cfg"):
            backup_path = backupdir + "/" + cfgname[:-4] + datestr + ".cfg"
        logging.info(
            "SAVE_CONFIG to '%s' (backup in '%s')", cfgpath, backup_path
        )
        try:
            # Read the current config into the backup before making changes to
            # the original file
            currentconfig = open(cfgpath, "r")
            backupconfig = open(backup_path, "w")
            backupconfig.write(currentconfig.read())
            backupconfig.close()
            currentconfig.close()
            # With the backup created, write the new data to the original file
            currentconfig = open(cfgpath, "w")
            currentconfig.write(cfgdata)
            currentconfig.close()
        except:
            msg = "Unable to write config file during SAVE_CONFIG"
            logging.exception(msg)
            raise gcode.error(msg)

    def _save_includes(self, cfgpath, data, visitedpaths, gcode):
        # Prevent an infinite loop in the event of configs circularly
        # referencing each other
        if cfgpath in visitedpaths:
            return

        visitedpaths.add(cfgpath)
        dirname = os.path.dirname(cfgpath)
        # Read the data as individual lines so we can find include blocks
        lines = data.split("\n")
        for line in lines:
            # Strip trailing comment
            pos = line.find("#")
            if pos >= 0:
                line = line[:pos]

            mo = configparser.RawConfigParser.SECTCRE.match(line)
            header = mo and mo.group("header")
            if header and header.startswith("include "):
                include_spec = header[8:].strip()
                include_glob = os.path.join(dirname, include_spec)
                # retrieve all filenames associated with the absolute path of
                # the include header
                include_filenames = glob.glob(include_glob)
                if not include_filenames and not glob.has_magic(include_glob):
                    # Empty set is OK if wildcard but not for direct file
                    # reference
                    raise error(
                        "Include file '%s' does not exist" % (include_glob,)
                    )
                include_filenames.sort()
                # Read the include files and check them against autosave data.
                # If autosave data overwites anything we'll update the file
                # and create a backup.
                for include_filename in include_filenames:
                    # Recursively check for includes. No need to check for looping
                    # includes as klipper checks this at startup.
                    include_predata = self._read_config_file(include_filename)
                    self._save_includes(
                        include_filename, include_predata, visitedpaths, gcode
                    )

                    include_postdata = self._strip_duplicates(
                        include_predata, self.autosave
                    )
                    # Only write and backup data that's been changed
                    if include_predata != include_postdata:
                        self._write_backup(
                            include_filename, include_postdata, gcode
                        )

    def cmd_SAVE_CONFIG(self, gcmd):
        if not self.autosave.fileconfig.sections():
            return
        gcode = self.printer.lookup_object("gcode")
        
        if self.is_json_config:
            self._save_json_config(gcmd)
        else:
            self._save_cfg_config(gcmd)

    def _save_json_config(self, gcmd):
        """Save configuration for JSON config files."""
        gcode = self.printer.lookup_object("gcode")
        
        # Build autosave JSON data
        autosave_json = {}
        for section in self.autosave.fileconfig.sections():
            autosave_json[section] = {}
            for option in self.autosave.fileconfig.options(section):
                value = self.autosave.fileconfig.get(section, option)
                autosave_json[section][option] = value
        
        # Write to JSON autosave file
        if not self.json_autosave_path:
            gcode.respond_info("No JSON autosave path configured")
            return
        
        try:
            # Create backup if file exists
            if os.path.exists(self.json_autosave_path):
                self._write_json_backup(self.json_autosave_path, gcode)
            
            # Write new autosave data
            with open(self.json_autosave_path, "w") as f:
                json.dump(autosave_json, f, indent=2)
            
            logging.info(
                "SAVE_CONFIG to '%s'",
                self.json_autosave_path
            )
        except Exception as e:
            msg = f"Unable to write JSON autosave file: {e}"
            logging.exception(msg)
            raise gcode.error(msg)
        
        # If requested restart or no restart just flag config saved
        require_restart = gcmd.get_int("RESTART", 1, minval=0, maxval=1)
        if require_restart:
            gcode.request_restart("restart")
        else:
            self.save_config_pending = False
            gcode.respond_info("Config update without restart successful")

    def _write_json_backup(self, filepath, gcode):
        """Create a backup of a JSON file."""
        configdir = os.path.dirname(filepath)
        backupdir = os.path.join(configdir, "config_backups")
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(backupdir):
            os.mkdir(backupdir)
        
        # Generate backup filename
        datestr = time.strftime("-%Y%m%d_%H%M%S")
        basename = os.path.basename(filepath)
        backup_path = os.path.join(backupdir, basename + datestr)
        
        logging.info(
            "Backup JSON config '%s' to '%s'",
            filepath, backup_path
        )
        
        try:
            # Read current content and write to backup
            with open(filepath, "r") as f:
                current_data = f.read()
            with open(backup_path, "w") as f:
                f.write(current_data)
        except Exception as e:
            logging.warning(
                "Unable to create backup of JSON file %s: %s",
                filepath, e
            )

    def _save_cfg_config(self, gcmd):
        """Save configuration for traditional CFG config files."""
        gcode = self.printer.lookup_object("gcode")
        # Create string containing autosave data
        autosave_data = self._build_config_string(self.autosave)
        lines = [("#*# " + l).strip() for l in autosave_data.split("\n")]
        lines.insert(0, "\n" + AUTOSAVE_HEADER.rstrip())
        lines.append("")
        autosave_data = "\n".join(lines)
        # Read in and validate current config file
        cfgname = self.printer.get_start_args()["config_file"]
        try:
            data = self._read_config_file(cfgname)
            regular_data, old_autosave_data = self._find_autosave_data(data)
            config = self._build_config_wrapper(regular_data, cfgname)
        except error as e:
            msg = "Unable to parse existing config on SAVE_CONFIG"
            logging.exception(msg)
            raise gcode.error(msg)
        regular_data = self._strip_duplicates(regular_data, self.autosave)

        if get_danger_options().autosave_includes:
            self._save_includes(cfgname, data, set(), gcode)

        # NOW we're safe to check for conflicts
        self._disallow_include_conflicts(regular_data, cfgname, gcode)
        data = regular_data.rstrip() + autosave_data
        self._write_backup(cfgname, data, gcode)

        # If requested restart or no restart just flag config saved
        require_restart = gcmd.get_int("RESTART", 1, minval=0, maxval=1)
        if require_restart:
            # Request a restart
            gcode.request_restart("restart")
        else:
            # flag config updated to false since config saved with no restart
            self.save_config_pending = False
            gcode.respond_info("Config update without restart successful")
