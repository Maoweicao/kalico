# CANopen EDS/DCF device description file parser (CiA 306 INI format)
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import configparser
import logging
import os
import re


# CiA 301 data types
DATA_TYPES = {
    0x0001: "BOOLEAN",
    0x0002: "INTEGER8",
    0x0003: "INTEGER16",
    0x0004: "INTEGER32",
    0x0005: "UNSIGNED8",
    0x0006: "UNSIGNED16",
    0x0007: "UNSIGNED32",
    0x0008: "REAL32",
    0x0009: "VISIBLE_STRING",
    0x000A: "OCTET_STRING",
    0x000B: "UNICODE_STRING",
    0x000C: "TIME_OF_DAY",
    0x000D: "TIME_DIFFERENCE",
    0x000F: "DOMAIN",
    0x0010: "INTEGER24",
    0x0011: "REAL64",
    0x0012: "INTEGER40",
    0x0013: "INTEGER48",
    0x0014: "INTEGER56",
    0x0015: "INTEGER64",
    0x0016: "UNSIGNED24",
    0x0018: "UNSIGNED40",
    0x0019: "UNSIGNED48",
    0x001A: "UNSIGNED56",
    0x001B: "UNSIGNED64",
}

# Data type sizes in bytes (None = variable)
DATA_TYPE_SIZES = {
    0x0001: 1,   # BOOLEAN
    0x0002: 1,   # INTEGER8
    0x0003: 2,   # INTEGER16
    0x0004: 4,   # INTEGER32
    0x0005: 1,   # UNSIGNED8
    0x0006: 2,   # UNSIGNED16
    0x0007: 4,   # UNSIGNED32
    0x0008: 4,   # REAL32
    0x0010: 3,   # INTEGER24
    0x0011: 8,   # REAL64
    0x0012: 5,   # INTEGER40
    0x0013: 6,   # INTEGER48
    0x0014: 7,   # INTEGER56
    0x0015: 8,   # INTEGER64
    0x0016: 3,   # UNSIGNED24
    0x0018: 5,   # UNSIGNED40
    0x0019: 6,   # UNSIGNED48
    0x001A: 7,   # UNSIGNED56
    0x001B: 8,   # UNSIGNED64
}

# CiA 402 operating modes (0x6060 values)
OPERATING_MODES = {
    1: "PP",     # Profile Position
    3: "PV",     # Profile Velocity
    4: "PT",     # Profile Torque
    6: "HOMING", # Homing
    7: "IP",     # Interpolated Position
    8: "CSP",    # Cyclic Synchronous Position
    9: "CSV",    # Cyclic Synchronous Velocity
    10: "CST",   # Cyclic Synchronous Torque
    11: "CSTCA", # Cyclic Synchronous Torque with Commutation Angle
}

# Well-known CiA 402 object indices
CIA402_OBJECTS = {
    0x6040: "Controlword",
    0x6041: "Statusword",
    0x6060: "Modes of Operation",
    0x6061: "Modes of Operation Display",
    0x607A: "Target Position",
    0x6064: "Position Actual Value",
    0x60FF: "Target Velocity",
    0x606C: "Velocity Actual Value",
    0x6071: "Target Torque",
    0x6077: "Torque Actual Value",
    0x60FE: "Digital Outputs",
    0x60FD: "Digital Inputs",
    0x6098: "Homing Method",
    0x6099: "Homing Speeds",
    0x607F: "Max Profile Velocity",
    0x6083: "Profile Acceleration",
    0x6084: "Profile Deceleration",
    0x6085: "Quick Stop Deceleration",
    0x60C5: "Max Acceleration",
    0x60C6: "Max Deceleration",
}


class ObjectEntry:
    """A single object dictionary entry."""

    def __init__(self, index, subindex=0, name="", data_type=0x0005,
                 access="rw", default_value=0, pdo_mapping=False):
        self.index = index
        self.subindex = subindex
        self.name = name
        self.data_type = data_type
        self.access = access
        self.default_value = default_value
        self.pdo_mapping = pdo_mapping

    def get_data_type_name(self):
        return DATA_TYPES.get(self.data_type, "UNKNOWN(0x%04X)" % self.data_type)

    def get_data_type_size(self):
        return DATA_TYPE_SIZES.get(self.data_type)

    def is_readable(self):
        return "r" in self.access

    def is_writable(self):
        return "w" in self.access

    def __repr__(self):
        return (
            "ObjectEntry(0x%04X:%02X '%s' type=0x%04X(%s) access=%s"
            " default=0x%X pdo=%s)"
            % (
                self.index, self.subindex, self.name,
                self.data_type, self.get_data_type_name(),
                self.access, self.default_value, self.pdo_mapping,
            )
        )


class EDSFile:
    """Parsed CANopen EDS/DCF device description file."""

    def __init__(self, filepath):
        self.filepath = os.path.abspath(filepath)
        self.device_info = {}
        self.device_comissioning = {}
        self.objects = {}  # (index, subindex) -> ObjectEntry
        self._parse(filepath)

    def _parse(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError("EDS file not found: %s" % filepath)

        config = configparser.RawConfigParser()
        config.read(filepath)

        # Parse [DeviceInfo]
        if config.has_section("DeviceInfo"):
            for key, value in config.items("DeviceInfo"):
                self.device_info[key] = value

        # Parse [DeviceComissioning] (note: CiA spec has this typo)
        if config.has_section("DeviceComissioning"):
            for key, value in config.items("DeviceComissioning"):
                self.device_comissioning[key] = value

        # Build index list from [Objects] section
        index_map = {}
        if config.has_section("Objects"):
            for key, value in config.items("Objects"):
                try:
                    count = int(value)
                    index_map[key] = count
                except ValueError:
                    pass

        # Parse each object section
        object_sections = {}
        for section in config.sections():
            # Match hex index like "1000", "1000sub1", "1600"
            m = re.match(r'^([0-9A-Fa-f]{4})(?:sub(\d+))?$', section)
            if m:
                index = int(m.group(1), 16)
                subindex = int(m.group(2)) if m.group(2) else 0
                object_sections[(index, subindex)] = section

        # Parse object entries
        for (index, subindex), section in sorted(object_sections.items()):
            params = dict(config.items(section))
            obj = self._parse_object(index, subindex, params)
            if obj is not None:
                self.objects[(index, subindex)] = obj

        logging.info(
            "Loaded EDS '%s': %d objects, Vendor=%s Product=0x%s",
            os.path.basename(filepath),
            len(self.objects),
            self.device_info.get("VendorName", "Unknown"),
            self.device_info.get("ProductCode", "0"),
        )

    def _parse_object(self, index, subindex, params):
        """Parse a single object entry from EDS section parameters."""
        name = params.get("parametername", "")
        if not name:
            name = params.get("name", "")

        # Parse data type
        data_type_str = params.get("datatype", params.get("data_type", "0x0005"))
        try:
            data_type = int(data_type_str, 0)
        except (ValueError, TypeError):
            data_type = 0x0005  # UNSIGNED8 default

        # Parse access type
        access_str = params.get("accesstype", params.get("access", "rw"))
        access_str = access_str.lower().strip()
        # Normalize access types
        if access_str in ("rw", "rww", "rw*"):
            access = "rw"
        elif access_str in ("ro", "const"):
            access = "ro"
        elif access_str == "wo":
            access = "wo"
        else:
            access = "rw"

        # Parse default value
        default_str = params.get("defaultvalue",
                                 params.get("default_value", "0"))
        try:
            default_value = int(default_str, 0)
        except (ValueError, TypeError):
            default_value = 0

        # Parse PDO mapping flag
        pdo_mapping_str = params.get("pdomapping", params.get("pdo_mapping", "0"))
        try:
            pdo_mapping = int(pdo_mapping_str, 0) != 0
        except (ValueError, TypeError):
            pdo_mapping = False

        return ObjectEntry(
            index=index,
            subindex=subindex,
            name=name,
            data_type=data_type,
            access=access,
            default_value=default_value,
            pdo_mapping=pdo_mapping,
        )

    def get_object(self, index, subindex=0):
        """Get an object entry by index and subindex."""
        return self.objects.get((index, subindex))

    def get_object_default(self, index, subindex=0, default=None):
        """Get an object's default value, or default if not found."""
        obj = self.objects.get((index, subindex))
        if obj is not None:
            return obj.default_value
        return default

    def get_supported_modes(self):
        """Return list of supported operating mode names from 0x6502.

        Bit positions per CiA 402:
          bit 1: PP, bit 2: PV, bit 4: PT, bit 5: HOMING
          bit 6: IP, bit 7: CSP, bit 8: CSV, bit 9: CST
        """
        modes = []
        obj = self.get_object(0x6502)
        if obj is not None:
            val = obj.default_value
            if val & (1 << 1):
                modes.append("PP")
            if val & (1 << 2):
                modes.append("PV")
            if val & (1 << 4):
                modes.append("PT")
            if val & (1 << 5):
                modes.append("HOMING")
            if val & (1 << 6):
                modes.append("IP")
            if val & (1 << 7):
                modes.append("CSP")
            if val & (1 << 8):
                modes.append("CSV")
            if val & (1 << 9):
                modes.append("CST")
        return modes

    def get_pdo_mappable_objects(self):
        """Return list of (index, subindex, entry) for PDO-mappable objects."""
        return [
            (idx, sub, entry)
            for (idx, sub), entry in sorted(self.objects.items())
            if entry.pdo_mapping
        ]

    def find_objects_by_range(self, low_index, high_index):
        """Find all objects within an index range."""
        return [
            ((idx, sub), entry)
            for (idx, sub), entry in sorted(self.objects.items())
            if low_index <= idx <= high_index
        ]

    def get_identity(self):
        """Return device identity dict from 0x1018."""
        return {
            "vendor_id": self.get_object_default(0x1018, 1, 0),
            "product_code": self.get_object_default(0x1018, 2, 0),
            "revision_number": self.get_object_default(0x1018, 3, 0),
            "serial_number": self.get_object_default(0x1018, 4, 0),
        }

    def dump_summary(self):
        """Log a summary of the EDS file."""
        logging.info("EDS Summary: %s", self.filepath)
        logging.info("  Vendor: %s", self.device_info.get("VendorName", "?"))
        logging.info("  Product: %s", self.device_info.get("ProductName", "?"))
        identity = self.get_identity()
        logging.info("  VendorID: 0x%08X", identity["vendor_id"])
        logging.info("  ProductCode: 0x%08X", identity["product_code"])
        modes = self.get_supported_modes()
        if modes:
            logging.info("  Supported Modes: %s", ", ".join(modes))
        logging.info("  Total Objects: %d", len(self.objects))
        mappable = self.get_pdo_mappable_objects()
        logging.info("  PDO Mappable: %d", len(mappable))
