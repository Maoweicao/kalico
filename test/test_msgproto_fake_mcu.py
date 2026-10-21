# Cross checks between the host protocol and the MCU simulators
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# The MCU simulators reimplement the wire protocol of the firmware.  A
# divergence between the two implementations silently breaks the
# simulator - the cross checks below pin them together.
import importlib.util
import pathlib

import pytest

from klippy.msgproto import (
    MESSAGE_DEST,
    MESSAGE_SEQ_MASK,
    MESSAGE_SYNC,
    PT_byte,
    PT_int32,
    crc16_ccitt,
)

pytestmark = pytest.mark.proto

REPO = pathlib.Path(__file__).parent.parent

VALUES = [
    0,
    1,
    0x1F,
    0x20,
    0x3F,
    0x40,
    0x5F,
    0x60,
    0x7F,
    0x80,
    0x1FF,
    0x3FF,
    0x1000,
    0x2FFF,
    0x3000,
    0x1234,
    0xFFFF,
    0x10000,
    0x17FFFF,
    0x180000,
    0x1234567,
    0x1FFFFFF,
    0x7FFFFFFF,
    -1,
    -32,
    -33,
    -1000,
    -0x80000,
    -0x4000000,
]


def _load_module(name, relative_path):
    path = REPO / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mcu_sim():
    return _load_module("mcu_sim_py_mcu", "other/mcu_sim/mcu_sim/py_mcu.py")


@pytest.fixture(scope="module")
def debug_tool():
    return _load_module(
        "kalico_debug_codec", "other/kalico_debug_tool/protocol/codec.py"
    )


######################################################################
# CRC
######################################################################


def test_the_crc_of_the_simulator_matches(mcu_sim):
    for data in (b"", b"\x01", b"\x01\x02\x03", bytes(range(32))):
        expected = crc16_ccitt(data)
        assert mcu_sim.MCUProtocol.crc16_ccitt(data) == (
            (expected[0] << 8) | expected[1]
        )


def test_the_crc_of_the_debug_tool_matches(debug_tool):
    for data in (b"", b"\x01", b"\x01\x02\x03", bytes(range(32))):
        assert debug_tool.crc16_ccitt(data) == crc16_ccitt(data)
        assert debug_tool.crc16_ccitt_int(data) == (
            (crc16_ccitt(data)[0] << 8) | crc16_ccitt(data)[1]
        )


@pytest.mark.parametrize("value", VALUES)
def test_the_variable_length_encoding_of_the_debug_tool_matches(
    debug_tool, value
):
    expected = []
    PT_int32().encode(expected, value)
    assert debug_tool.VLQEncoder.encode_int32(value) == expected
    assert debug_tool.VLQEncoder.encode_uint32(value) == expected


@pytest.mark.parametrize("value", [0, 1, 0x5F, 0x60, 0x7F, 0xFF])
def test_the_byte_encoding_of_the_debug_tool_matches(debug_tool, value):
    expected = []
    PT_byte().encode(expected, value)
    assert debug_tool.VLQEncoder.encode_byte(value) == expected


######################################################################
# Variable length integers
######################################################################


@pytest.mark.parametrize("value", VALUES)
def test_the_variable_length_encoding_matches(mcu_sim, value):
    expected = []
    PT_int32().encode(expected, value)
    assert mcu_sim.MCUProtocol.vlq_encode([value]) == bytes(expected)


@pytest.mark.parametrize("value", VALUES)
def test_the_simulator_decodes_its_own_encoding(mcu_sim, value):
    encoded = mcu_sim.MCUProtocol.vlq_encode([value])
    decoded, offset = mcu_sim.MCUProtocol.vlq_decode(encoded, 0)
    assert decoded == value
    assert offset == len(encoded)


@pytest.mark.parametrize("value", VALUES)
def test_the_simulator_decodes_the_host_encoding(mcu_sim, value):
    expected = []
    PT_int32().encode(expected, value)
    decoded, offset = mcu_sim.MCUProtocol.vlq_decode(bytes(expected), 0)
    assert decoded == value
    assert offset == len(expected)


######################################################################
# Message framing
######################################################################


def test_the_message_frame_matches(mcu_sim):
    from klippy.msgproto import MessageParser

    parser = MessageParser()
    content = bytes([0x01, 0x02, 0x03])
    expected = parser.encode_msgblock(5, list(content))
    assert mcu_sim.MCUProtocol.build_message(5, content) == bytes(expected)


def test_the_message_frame_has_the_expected_layout(mcu_sim):
    frame = mcu_sim.MCUProtocol.build_message(5, bytes([0x01]))
    assert frame[0] == 5 + len([0x01])
    assert frame[1] == (5 & MESSAGE_SEQ_MASK) | MESSAGE_DEST
    assert frame[-1] == MESSAGE_SYNC


def test_the_simulator_parses_a_host_frame(mcu_sim):
    from klippy.msgproto import MessageParser

    parser = MessageParser()
    # The first byte of the content is the message id
    frame = bytes(parser.encode_msgblock(3, [0x01, 0x02]))
    msgid, content = mcu_sim.MCUProtocol.parse_frame(bytearray(frame))
    assert msgid == 1
    assert bytes(content) == b"\x02"
