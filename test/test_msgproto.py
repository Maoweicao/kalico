# Tests for the firmware message protocol
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# The wire format of the MCU protocol is the most critical part of the
# host code - a silent break of the framing or the CRC would brick every
# printer.  The tests below pin the format down and check that a broken
# frame is always rejected.
import pytest

from klippy.msgproto import (
    MESSAGE_DEST,
    MESSAGE_MAX,
    MESSAGE_MIN,
    MESSAGE_SEQ_MASK,
    MESSAGE_SYNC,
    Enumeration,
    MessageFormat,
    MessageParser,
    PT_byte,
    PT_int16,
    PT_int32,
    PT_string,
    PT_uint16,
    PT_uint32,
    convert_msg_format,
    crc16_ccitt,
    error,
    lookup_output_params,
    lookup_params,
)

pytestmark = pytest.mark.proto

######################################################################
# CRC
######################################################################


def test_crc16_ccitt_of_an_empty_buffer():
    assert crc16_ccitt(b"") == [0xFF, 0xFF]


def test_crc16_ccitt_is_deterministic():
    assert crc16_ccitt(b"hello") == crc16_ccitt(b"hello")


def test_crc16_ccitt_changes_with_the_input():
    assert crc16_ccitt(b"hello") != crc16_ccitt(b"hellp")


def test_crc16_ccitt_returns_two_bytes():
    crc = crc16_ccitt(b"\x01\x02\x03")
    assert len(crc) == 2
    assert all(0 <= b <= 0xFF for b in crc)


######################################################################
# Variable length integers
######################################################################


@pytest.mark.parametrize(
    "value",
    [0, 1, 0x3F, 0x40, 0x1FFF, 0x2000, 0xFFFFFF, 0x1000000, 0xFFFFFFFF],
)
def test_uint32_round_trip(value):
    out = []
    PT_uint32().encode(out, value)
    assert len(out) <= PT_uint32.max_length
    parsed, pos = PT_uint32().parse(out, 0)
    assert parsed == value
    assert pos == len(out)


@pytest.mark.parametrize("value", [0, 1, -1, 0x7FFF, -0x8000, 0x7FFFFFFF])
def test_int32_round_trip(value):
    out = []
    PT_int32().encode(out, value)
    parsed, pos = PT_int32().parse(out, 0)
    assert parsed == value


@pytest.mark.parametrize("value", [0, 1, 0xFFFF])
def test_uint16_round_trip(value):
    out = []
    PT_uint16().encode(out, value)
    assert len(out) <= PT_uint16.max_length
    parsed, pos = PT_uint16().parse(out, 0)
    assert parsed == value


@pytest.mark.parametrize("value", [0, 1, -1, 0x7FFF, -0x8000])
def test_int16_round_trip(value):
    out = []
    PT_int16().encode(out, value)
    assert len(out) <= PT_int16.max_length
    parsed, pos = PT_int16().parse(out, 0)
    assert parsed == value


@pytest.mark.parametrize("value", [0, 1, 0xFF])
def test_byte_round_trip(value):
    out = []
    PT_byte().encode(out, value)
    assert len(out) <= PT_byte.max_length
    parsed, pos = PT_byte().parse(out, 0)
    assert parsed == value


def test_a_large_uint32_uses_the_maximum_length():
    out = []
    PT_uint32().encode(out, 0xFFFFFFFF)
    assert len(out) == PT_uint32.max_length


def test_a_small_uint32_uses_a_single_byte():
    out = []
    PT_uint32().encode(out, 1)
    assert len(out) == 1


def test_string_round_trip():
    out = []
    PT_string().encode(out, b"abc")
    assert out[0] == 3
    parsed, pos = PT_string().parse(out, 0)
    assert parsed == b"abc"
    assert pos == 4


def test_an_empty_string_round_trip():
    out = []
    PT_string().encode(out, b"")
    parsed, pos = PT_string().parse(out, 0)
    assert parsed == b""
    assert pos == 1


######################################################################
# Enumerations
######################################################################


def test_enumeration_round_trip():
    enum = Enumeration(PT_byte(), "pin", {"PA1": 1, "PA2": 2})
    out = []
    enum.encode(out, "PA2")
    parsed, pos = enum.parse(out, 0)
    assert parsed == "PA2"


def test_an_unknown_enumeration_value_raises():
    enum = Enumeration(PT_byte(), "pin", {"PA1": 1})
    with pytest.raises(error):
        enum.encode([], "PB1")


def test_an_unknown_enumeration_code_parses_to_a_placeholder():
    enum = Enumeration(PT_byte(), "pin", {"PA1": 1})
    parsed, pos = enum.parse([0x55], 0)
    assert parsed == "?85"


######################################################################
# Format lookup
######################################################################


def test_lookup_params():
    params = lookup_params("stepper_x enable=%u")
    assert params[0][0] == "enable"
    assert isinstance(params[0][1], PT_uint32)


def test_lookup_params_applies_an_enumeration():
    params = lookup_params("stepper_x pin=%u", {"pin": {"PA1": 1, "PA2": 2}})
    assert isinstance(params[0][1], Enumeration)


def test_lookup_params_matches_a_suffixed_enumeration():
    params = lookup_params("stepper_x endstop_pin=%u", {"pin": {"PA1": 1}})
    assert isinstance(params[0][1], Enumeration)


def test_lookup_output_params():
    types = lookup_output_params("%u %c")
    assert len(types) == 2
    assert isinstance(types[0], PT_uint32)
    assert isinstance(types[1], PT_byte)


def test_lookup_output_params_of_an_invalid_format():
    with pytest.raises(error):
        lookup_output_params("%q")


def test_convert_msg_format():
    assert convert_msg_format("cmd %u") == "cmd %s"
    assert convert_msg_format("cmd %hu") == "cmd %s"
    assert convert_msg_format("cmd %.*s") == "cmd %s"


######################################################################
# Message framing
######################################################################


def _make_parser():
    parser = MessageParser()
    parser.fill_enumerations({})
    return parser


def test_encode_msgblock_builds_a_valid_frame():
    parser = _make_parser()
    frame = parser.encode_msgblock(3, [0x01, 0x00])
    assert frame[0] == MESSAGE_MIN + 2
    assert frame[1] == (3 & MESSAGE_SEQ_MASK) | MESSAGE_DEST
    assert frame[-1] == MESSAGE_SYNC
    assert parser.check_packet(frame) == len(frame)


def test_the_sequence_number_is_masked():
    parser = _make_parser()
    frame = parser.encode_msgblock(0xFF, [])
    assert frame[1] == (0x0F & MESSAGE_SEQ_MASK) | MESSAGE_DEST


def test_check_packet_needs_more_data():
    parser = _make_parser()
    frame = parser.encode_msgblock(1, [0x01])
    assert parser.check_packet(frame[:2]) == 0
    assert parser.check_packet(frame[:-1]) == 0


def test_check_packet_accepts_a_valid_frame():
    parser = _make_parser()
    frame = parser.encode_msgblock(1, [0x01, 0x02])
    assert parser.check_packet(frame) == len(frame)


def test_check_packet_rejects_a_broken_crc():
    parser = _make_parser()
    frame = parser.encode_msgblock(1, [0x01, 0x02])
    frame[-3] ^= 0xFF
    assert parser.check_packet(frame) == -1


def test_check_packet_rejects_a_flipped_payload_bit():
    parser = _make_parser()
    frame = parser.encode_msgblock(1, [0x01, 0x02])
    frame[2] ^= 0xFF
    assert parser.check_packet(frame) == -1


def test_check_packet_rejects_a_broken_sync_byte():
    parser = _make_parser()
    frame = parser.encode_msgblock(1, [0x01, 0x02])
    frame[-1] ^= 0xFF
    assert parser.check_packet(frame) == -1


def test_check_packet_rejects_a_wrong_destination():
    parser = _make_parser()
    frame = parser.encode_msgblock(1, [0x01, 0x02])
    frame[1] = (frame[1] & ~MESSAGE_DEST) | 0x20
    assert parser.check_packet(frame) == -1


def test_check_packet_rejects_an_impossible_length():
    parser = _make_parser()
    frame = parser.encode_msgblock(1, [0x01])
    frame[0] = MESSAGE_MAX + 1
    assert parser.check_packet(frame) == -1
    frame[0] = MESSAGE_MIN - 1
    assert parser.check_packet(frame) == -1


def test_a_frame_round_trips_through_the_parser():
    parser = _make_parser()
    parser._init_messages({"test_cmd value=%u": 20})
    frame = parser.encode_msgblock(
        2, parser.messages_by_name["test_cmd"].encode([0x1234])
    )
    assert parser.check_packet(frame) == len(frame)
    params = parser.parse(frame)
    assert params["value"] == 0x1234
    assert params["#name"] == "test_cmd"


def test_parse_rejects_extra_data():
    parser = _make_parser()
    parser._init_messages({"test_cmd value=%u": 20})
    frame = parser.encode_msgblock(
        2, parser.messages_by_name["test_cmd"].encode([0x1234])
    )
    frame.insert(-1, 0x00)
    frame[0] += 1
    with pytest.raises(error):
        parser.parse(frame)


######################################################################
# Command lookup
######################################################################


def test_lookup_command():
    parser = _make_parser()
    parser._init_messages({"test_cmd value=%u": 20})
    mp = parser.lookup_command("test_cmd value=%u")
    assert mp.name == "test_cmd"


def test_lookup_command_of_an_unknown_command():
    parser = _make_parser()
    with pytest.raises(error):
        parser.lookup_command("nope value=%u")


def test_lookup_command_with_a_mismatched_format():
    parser = _make_parser()
    parser._init_messages({"test_cmd value=%u": 20})
    with pytest.raises(error):
        parser.lookup_command("test_cmd value=%c")


def test_create_command_encodes_a_command():
    parser = _make_parser()
    parser._init_messages({"test_cmd value=%u": 20})
    out = parser.create_command("test_cmd value=4660")
    assert out[0] == 20
    # 0x1234 is encoded as a two byte variable length integer
    assert out[1:] == [0xA4, 0x34]


def test_create_command_of_an_unknown_command():
    parser = _make_parser()
    with pytest.raises(error):
        parser.create_command("nope value=1")


def test_create_command_of_an_empty_message():
    parser = _make_parser()
    assert parser.create_command("") == ""


######################################################################
# Message formats
######################################################################


def test_message_format_encode_and_parse():
    mf = MessageFormat([0x10], "test_cmd value=%u")
    out = mf.encode([0x1234])
    assert out[0] == 0x10
    params, pos = mf.parse(out, 0)
    assert params["value"] == 0x1234


def test_message_format_encode_by_name():
    mf = MessageFormat([0x10], "test_cmd value=%u")
    out = mf.encode_by_name(value=0x1234)
    assert out[0] == 0x10


def test_message_format_formats_the_parameters():
    mf = MessageFormat([0x10], "test_cmd value=%u")
    assert mf.format_params({"value": 5}) == "test_cmd value=5"


def test_message_format_repr_of_a_string_parameter():
    mf = MessageFormat([0x10], "test_cmd data=%.*s")
    text = mf.format_params({"data": b"ab"})
    assert "'ab'" in text
