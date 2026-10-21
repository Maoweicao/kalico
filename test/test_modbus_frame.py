# Tests for the shared Modbus RTU frame helpers
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from klippy.extras.rs485.modbus_frame import (
    FC_READ_HOLDING_REGISTERS,
    FC_WRITE_MULTIPLE_REGISTERS,
    FC_WRITE_SINGLE_REGISTER,
    build_read_request,
    build_write_multiple_request,
    build_write_single_request,
    calc_crc16,
    check_crc,
    decode_read_response,
    exception_message,
    is_exception,
)

######################################################################
# CRC16
######################################################################


def test_calc_crc16_matches_the_canonical_vector():
    # The well known Modbus RTU example: the read request
    # "01 03 00 00 00 01" carries the CRC bytes 84 0A
    assert calc_crc16(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x01])) == 0x0A84


def test_calc_crc16_matches_an_independent_implementation():
    def reference(data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    for data in (b"", b"\x01", b"\x01\x03", bytes(range(32))):
        assert calc_crc16(data) == reference(data)


def test_calc_crc16_of_an_empty_frame():
    assert calc_crc16(b"") == 0xFFFF


def test_calc_crc16_is_order_dependent():
    assert calc_crc16(b"\x01\x03") != calc_crc16(b"\x03\x01")


def test_check_crc_accepts_a_valid_frame():
    frame = build_read_request(1, 0, 1)
    assert check_crc(frame) is True


def test_check_crc_rejects_a_short_frame():
    assert check_crc(b"\x01") is False
    assert check_crc(b"") is False


def test_check_crc_rejects_a_flipped_bit():
    frame = bytearray(build_read_request(1, 0, 1))
    frame[3] ^= 0x01
    assert check_crc(bytes(frame)) is False


def test_check_crc_rejects_a_flipped_crc_bit():
    frame = bytearray(build_read_request(1, 0, 1))
    frame[-1] ^= 0x01
    assert check_crc(bytes(frame)) is False


######################################################################
# Exception helpers
######################################################################


def test_is_exception():
    assert is_exception(0x83) is True
    assert is_exception(0x90) is True
    assert is_exception(0x03) is False
    assert is_exception(0x10) is False


def test_exception_message_of_a_known_code():
    assert exception_message(0x02) == "Illegal Data Address"
    assert exception_message(0x01) == "Illegal Function"


def test_exception_message_of_an_unknown_code():
    assert exception_message(0x99).startswith("Unknown")


######################################################################
# Request builders
######################################################################


def test_build_read_request():
    request = build_read_request(1, 0x6041, 1)
    assert request[0] == 1
    assert request[1] == FC_READ_HOLDING_REGISTERS
    assert request[2:4] == b"\x60\x41"
    assert request[4:6] == b"\x00\x01"
    assert len(request) == 8
    assert check_crc(request) is True


def test_build_read_request_appends_the_crc_little_endian():
    request = build_read_request(1, 0, 1)
    crc = calc_crc16(request[:-2])
    assert request[-2:] == crc.to_bytes(2, "little")


def test_build_write_single_request():
    request = build_write_single_request(2, 0x607A, 0x1234)
    assert request[0] == 2
    assert request[1] == FC_WRITE_SINGLE_REGISTER
    assert request[2:4] == b"\x60\x7a"
    assert request[4:6] == b"\x12\x34"
    assert check_crc(request) is True


def test_build_write_single_request_masks_the_value():
    request = build_write_single_request(1, 0x6040, 0x1FFFF)
    assert request[4:6] == b"\xff\xff"


def test_build_write_multiple_request():
    request = build_write_multiple_request(1, 0x6064, [0x1111, 0x2222])
    assert request[0] == 1
    assert request[1] == FC_WRITE_MULTIPLE_REGISTERS
    assert request[2:4] == b"\x60\x64"
    assert request[4:6] == b"\x00\x02"
    assert request[6] == 4
    assert request[7:9] == b"\x11\x11"
    assert request[9:11] == b"\x22\x22"
    assert check_crc(request) is True


def test_build_write_multiple_request_with_one_value():
    request = build_write_multiple_request(1, 0x6064, [0x1111])
    assert request[6] == 2
    assert len(request) == 11


######################################################################
# Response decoding
######################################################################


def _read_response(slave_id=1, values=(0x1234,)):
    body = bytearray([slave_id, FC_READ_HOLDING_REGISTERS])
    body.append(len(values) * 2)
    for value in values:
        body += value.to_bytes(2, "big")
    return bytes(body) + calc_crc16(bytes(body)).to_bytes(2, "little")


def test_decode_read_response():
    assert decode_read_response(_read_response(values=[0x1234]), 1, 1) == [
        0x1234
    ]


def test_decode_read_response_of_several_registers():
    response = _read_response(values=[0x0001, 0x0002, 0x0003])
    assert decode_read_response(response, 1, 3) == [1, 2, 3]


def test_decode_read_response_rejects_a_wrong_length():
    assert decode_read_response(_read_response(values=[0x1234]), 1, 2) is None


def test_decode_read_response_rejects_a_wrong_slave():
    assert decode_read_response(_read_response(slave_id=2), 1, 1) is None


def test_decode_read_response_rejects_an_exception():
    body = bytes([1, FC_READ_HOLDING_REGISTERS | 0x80, 0x02])
    response = body + calc_crc16(body).to_bytes(2, "little")
    assert decode_read_response(response, 1, 1) is None


def test_decode_read_response_rejects_a_wrong_byte_count():
    response = bytearray(_read_response(values=[0x1234]))
    response[2] = 4
    body = bytes(response[:-2])
    response = body + calc_crc16(body).to_bytes(2, "little")
    assert decode_read_response(bytes(response), 1, 1) is None


def test_decode_read_response_rejects_a_broken_crc():
    response = bytearray(_read_response(values=[0x1234]))
    response[-1] ^= 0xFF
    assert decode_read_response(bytes(response), 1, 1) is None
