# Tests for the CANopen EDS parser
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import pathlib

import pytest

from klippy.extras.canopen.eds_parser import (
    CIA402_OBJECTS,
    DATA_TYPES,
    EDSFile,
    ObjectEntry,
)

pytestmark = pytest.mark.proto

EDS_PATH = (
    pathlib.Path(__file__).parent / "test_configs" / "canopen" / "servo_x.eds"
)


@pytest.fixture(scope="module")
def eds():
    return EDSFile(str(EDS_PATH))


######################################################################
# The device info
######################################################################


def test_the_device_info_is_parsed(eds):
    # The raw config parser lower cases the option names
    assert eds.device_info["vendorname"] == "TestServo"
    assert eds.device_info["productname"] == "ServoX"


def test_the_device_info_values_are_strings(eds):
    # The raw config parser keeps the values as strings
    assert eds.device_info["vendornumber"] == "0x12345678"
    assert eds.device_info["productcode"] == "0x00010001"


def test_the_commissioning_section_is_parsed(eds):
    assert eds.device_comissioning["nodeid"] == "1"
    assert eds.device_comissioning["nodename"] == "ServoX"


######################################################################
# The object dictionary
######################################################################


def test_the_objects_are_parsed(eds):
    assert len(eds.objects) > 0
    obj = eds.get_object(0x6040)
    assert obj is not None
    assert obj.index == 0x6040


def test_the_sub_indices_are_parsed(eds):
    # 0x1018 has four sub indices
    for sub in range(1, 5):
        assert eds.get_object(0x1018, sub) is not None


def test_an_unknown_object_is_none(eds):
    assert eds.get_object(0xDEAD) is None


def test_get_object_default(eds):
    assert eds.get_object_default(0xDEAD, 0, 42) == 42


def test_the_object_data_type_is_parsed(eds):
    obj = eds.get_object(0x1018, 1)
    assert obj.data_type in DATA_TYPES


def test_the_object_access_type_is_normalized(eds):
    for (index, sub), obj in eds.objects.items():
        assert obj.access in ("rw", "ro", "wo")
        assert obj.is_readable() or obj.is_writable()


def test_the_pdo_mapping_flag_is_parsed(eds):
    # The drive profile objects are PDO mappable
    assert eds.get_object(0x6040).pdo_mapping


def test_find_objects_by_range(eds):
    found = eds.find_objects_by_range(0x6000, 0x60FF)
    assert found
    for (index, sub), entry in found:
        assert 0x6000 <= index <= 0x60FF


def test_find_objects_by_an_empty_range(eds):
    assert eds.find_objects_by_range(0xA000, 0xAFFF) == []


######################################################################
# The supported modes
######################################################################


def test_the_supported_modes_are_parsed(eds):
    modes = eds.get_supported_modes()
    assert "PP" in modes
    assert "CSP" in modes


def test_the_supported_modes_of_a_device_without_0x6502():
    class _Empty(EDSFile):
        def __init__(self):
            self.objects = {}

    assert _Empty().get_supported_modes() == []


######################################################################
# The device identity
######################################################################


def test_the_identity_is_parsed(eds):
    identity = eds.get_identity()
    assert set(identity) == {
        "vendor_id",
        "product_code",
        "revision_number",
        "serial_number",
    }


######################################################################
# The pdo mappable objects
######################################################################


def test_the_pdo_mappable_objects_are_listed(eds):
    entries = eds.get_pdo_mappable_objects()
    assert entries
    for index, sub, entry in entries:
        assert entry.pdo_mapping


######################################################################
# The object entry
######################################################################


def test_the_data_type_size():
    entry = ObjectEntry(0x2000, 0, "test", data_type=0x0007)
    assert entry.get_data_type_size() == 4
    assert entry.get_data_type_name()


def test_the_data_type_size_of_an_unknown_type():
    entry = ObjectEntry(0x2000, 0, "test", data_type=0x0099)
    assert entry.get_data_type_size() is None
    assert entry.get_data_type_name().startswith("UNKNOWN")


def test_the_read_and_write_flags():
    entry = ObjectEntry(0x2000, 0, "test", access="rw")
    assert entry.is_readable()
    assert entry.is_writable()
    entry = ObjectEntry(0x2000, 0, "test", access="ro")
    assert entry.is_readable()
    assert not entry.is_writable()
    entry = ObjectEntry(0x2000, 0, "test", access="wo")
    assert not entry.is_readable()
    assert entry.is_writable()


def test_the_object_repr():
    entry = ObjectEntry(0x2000, 1, "test")
    assert "2000" in repr(entry)


######################################################################
# The drive profile objects
######################################################################


def test_the_cia402_objects_are_known():
    for index in (0x6040, 0x6041, 0x6060, 0x6061, 0x607A, 0x6064):
        assert index in CIA402_OBJECTS
