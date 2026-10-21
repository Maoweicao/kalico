# Tests for the stepper driver register codec
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import pytest

from klippy.extras.lyx9231 import Fields as LYXFields
from klippy.extras.lyx9231 import SignedFields as LYXSignedFields
from klippy.extras.tmc import FieldHelper, ffs
from klippy.extras.tmc2130 import Fields as TMC2130Fields
from klippy.extras.tmc2208 import Fields as TMC2208Fields
from klippy.extras.tmc2209 import Fields as TMC2209Fields
from klippy.extras.tmc2240 import Fields as TMC2240Fields
from klippy.extras.tmc2660 import Fields as TMC2660Fields
from klippy.extras.tmc5160 import Fields as TMC5160Fields

pytestmark = pytest.mark.unit
DRIVERS = [
    ("tmc2130", TMC2130Fields, []),
    ("tmc2208", TMC2208Fields, []),
    ("tmc2209", TMC2209Fields, []),
    ("tmc2240", TMC2240Fields, []),
    ("tmc2660", TMC2660Fields, []),
    ("tmc5160", TMC5160Fields, []),
    ("lyx9231", LYXFields, LYXSignedFields),
]


######################################################################
# ffs
######################################################################


def test_ffs_of_a_single_bit():
    assert ffs(0x01) == 0
    assert ffs(0x02) == 1
    assert ffs(0x80) == 7
    assert ffs(0x8000) == 15


def test_ffs_of_a_multi_bit_mask():
    assert ffs(0x03) == 0
    assert ffs(0x06) == 1
    assert ffs(0x18) == 3


def test_ffs_of_a_full_mask():
    assert ffs(0xFFFFFFFF) == 0


######################################################################
# The field tables
######################################################################


@pytest.mark.parametrize(
    "name,fields,signed", DRIVERS, ids=[d[0] for d in DRIVERS]
)
def test_every_field_is_in_a_register(name, fields, signed):
    for reg_name, reg_fields in fields.items():
        assert reg_fields, "%s has no fields" % reg_name
        for field_name, mask in reg_fields.items():
            assert mask != 0, "%s.%s has an empty mask" % (
                reg_name,
                field_name,
            )
            # The mask has to fit into a register
            assert mask >> ffs(mask) <= 0xFFFFFFFF


@pytest.mark.parametrize(
    "name,fields,signed", DRIVERS, ids=[d[0] for d in DRIVERS]
)
def test_the_fields_of_a_register_do_not_overlap(name, fields, signed):
    for reg_name, reg_fields in fields.items():
        used = 0
        for field_name, mask in reg_fields.items():
            assert used & mask == 0, "%s.%s overlaps another field" % (
                reg_name,
                field_name,
            )
            used |= mask


@pytest.mark.parametrize(
    "name,fields,signed", DRIVERS, ids=[d[0] for d in DRIVERS]
)
def test_the_signed_fields_exist(name, fields, signed):
    for field_name in signed:
        assert any(
            field_name in reg_fields for reg_fields in fields.values()
        ), "%s is not a known field" % field_name


######################################################################
# The field helper
######################################################################


def _make_helper(fields, signed_fields=None):
    return FieldHelper(fields, signed_fields=signed_fields or [])


def test_get_field_of_an_unsigned_field():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF, "intpol": 0x100}})
    assert helper.get_field("mres", 0x0012, "CHOPCONF") == 0x12
    assert helper.get_field("intpol", 0x0100, "CHOPCONF") == 1


def test_get_field_of_a_signed_field():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF}}, signed_fields=["mres"])
    # 0xFF is -1 in a signed 8 bit field
    assert helper.get_field("mres", 0x00FF, "CHOPCONF") == -1
    assert helper.get_field("mres", 0x007F, "CHOPCONF") == 127


def test_set_field_keeps_the_other_fields():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF, "intpol": 0x100}})
    res = helper.set_field("intpol", 1, 0x0012, "CHOPCONF")
    assert res == 0x0112
    # The other field is unchanged
    assert helper.get_field("mres", res, "CHOPCONF") == 0x12


def test_set_field_and_get_field_round_trip():
    helper = _make_helper(
        {"CHOPCONF": {"mres": 0xFF, "intpol": 0x100}},
        signed_fields=["mres"],
    )
    for value in (0, 1, 127, -1, -128):
        reg = helper.set_field("mres", value, 0, "CHOPCONF")
        assert helper.get_field("mres", reg, "CHOPCONF") == value


def test_set_field_stores_the_register():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF}})
    helper.set_field("mres", 0x12, 0, "CHOPCONF")
    assert helper.registers["CHOPCONF"] == 0x12


def test_get_field_uses_the_stored_register():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF}})
    helper.set_field("mres", 0x34)
    assert helper.get_field("mres") == 0x34


def test_lookup_register():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF}})
    assert helper.lookup_register("mres") == "CHOPCONF"
    assert helper.lookup_register("nope") is None


def test_get_reg_fields():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF, "intpol": 0x100}})
    fields = helper.get_reg_fields("CHOPCONF", 0x0112)
    assert fields["mres"] == 0x12
    assert fields["intpol"] == 1


def test_pretty_format():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF}})
    text = helper.pretty_format("CHOPCONF", 0x12)
    assert "CHOPCONF" in text
    assert "00000012" in text
    assert "mres=18" in text


def test_pretty_format_uses_the_field_formatters():
    helper = FieldHelper(
        {"CHOPCONF": {"mres": 0xFF}},
        field_formatters={"mres": lambda v: "0x%02x" % v},
    )
    assert "mres=0x12" in helper.pretty_format("CHOPCONF", 0x12)


def test_pretty_format_of_an_unknown_register():
    helper = _make_helper({"CHOPCONF": {"mres": 0xFF}})
    assert "nope" in helper.pretty_format("nope", 0)


######################################################################
# The real driver tables
######################################################################


@pytest.mark.parametrize(
    "name,fields,signed", DRIVERS, ids=[d[0] for d in DRIVERS]
)
def test_the_driver_tables_can_be_decoded(name, fields, signed):
    helper = _make_helper(fields, signed)
    for reg_name, reg_fields in fields.items():
        reg_value = 0xFFFFFFFF
        decoded = helper.get_reg_fields(reg_name, reg_value)
        assert set(decoded) == set(reg_fields)


@pytest.mark.parametrize(
    "name,fields,signed", DRIVERS, ids=[d[0] for d in DRIVERS]
)
def test_the_driver_tables_can_be_encoded(name, fields, signed):
    helper = _make_helper(fields, signed)
    for reg_name, reg_fields in fields.items():
        reg_value = 0
        for field_name in reg_fields:
            reg_value = helper.set_field(field_name, 1, reg_value, reg_name)
        decoded = helper.get_reg_fields(reg_name, reg_value)
        for field_name in reg_fields:
            assert decoded[field_name] == 1
