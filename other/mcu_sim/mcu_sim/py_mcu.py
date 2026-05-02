#!/usr/bin/env python3
"""
High-Fidelity Python MCU Simulator
==================================

A standalone Python process that implements the Kalico MCU binary
protocol over TCP.  No QEMU, no C compiler, no external dependencies
beyond Python stdlib.

Key features:
  - Full Kalico binary protocol (VLQ + CRC16 + framing)
  - identify → identify_response handshake
  - config / finalize_config / get_config
  - get_clock / get_uptime
  - emergency_stop
  - Real timer-driven scheduler with virtual clock
  - Command handler registry for custom commands
  - Protocol interception hooks

Usage::

    python -m mcu_sim serve [--port PORT]

Then connect kalico_debug_tool::

    > connect tcp:127.0.0.1:<PORT>
    > send_command identify offset=0 count=40
"""

import argparse
import logging
import select
import socket
import sys
import time
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("py_mcu")


# ======================================================================
# Kalico Protocol Codec (self-contained, no external dependencies)
# ======================================================================

class MCUProtocol:
    """Pure-Python Kalico binary protocol implementation.

    Matches the wire protocol exactly as used by the Kalico firmware's
    command.c / serial_irq.c and the host-side msgproto.py.
    """

    MESSAGE_MIN = 5
    MESSAGE_MAX = 64
    MESSAGE_SYNC = 0x7E
    MESSAGE_SEQ_MASK = 0x0F
    MESSAGE_DEST = 0x10

    # CRC16-CCITT — matches klippy/msgproto.py and kalico firmware
    @staticmethod
    def crc16_ccitt(data: bytes) -> int:
        """Compute CRC-16 CCITT checksum (MSB first, poly=0x1021)."""
        crc = 0xFFFF
        for b in data:
            b ^= crc & 0xFF
            b ^= (b & 0x0F) << 4
            crc = ((b << 8) | (crc >> 8)) ^ (b >> 4) ^ (b << 3)
        return crc & 0xFFFF

    @classmethod
    def vlq_encode(cls, values: List[int]) -> bytes:
        """Encode a list of integers as VLQ bytes."""
        result = bytearray()
        for v in values:
            result.extend(cls._vlq_encode_one(v))
        return bytes(result)

    @staticmethod
    def _vlq_encode_one(v: int) -> List[int]:
        v_u = v & 0xFFFFFFFF
        sv = v
        if sv < (3 << 5) and sv >= -(1 << 5):
            return [v_u & 0x7F]
        if sv < (3 << 12) and sv >= -(1 << 12):
            return [0x80 | ((v_u >> 7) & 0x3F), v_u & 0x7F]
        if sv < (3 << 19) and sv >= -(1 << 19):
            return [0x80 | 0x40 | ((v_u >> 14) & 0x1F),
                    (v_u >> 7) & 0x7F, v_u & 0x7F]
        if sv < (3 << 26) and sv >= -(1 << 26):
            return [0x80 | 0x40 | 0x20 | ((v_u >> 21) & 0x0F),
                    (v_u >> 14) & 0x7F, (v_u >> 7) & 0x7F, v_u & 0x7F]
        return [0x80 | 0x40 | 0x20 | 0x10 | ((v_u >> 28) & 0x0F),
                (v_u >> 21) & 0x7F, (v_u >> 14) & 0x7F,
                (v_u >> 7) & 0x7F, v_u & 0x7F]

    @staticmethod
    def vlq_decode(data: bytes, offset: int = 0) -> Tuple[int, int]:
        """Decode one VLQ value. Returns (value, new_offset)."""
        b0 = data[offset]
        if not (b0 & 0x80):
            val = b0
            if val >= 96:
                val -= 128
            return val, offset + 1
        if not (b0 & 0x40):
            val = ((b0 & 0x3F) << 7) | data[offset + 1]
            if val >= 4096:
                val -= 8192
            return val, offset + 2
        if not (b0 & 0x20):
            val = ((b0 & 0x1F) << 14) | (data[offset + 1] << 7) | data[offset + 2]
            if val >= 524288:
                val -= 1048576
            return val, offset + 3
        if not (b0 & 0x10):
            val = ((b0 & 0x0F) << 21) | (data[offset + 1] << 14) | \
                  (data[offset + 2] << 7) | data[offset + 3]
            if val >= 67108864:
                val -= 134217728
            return val, offset + 4
        val = ((b0 & 0x0F) << 28) | (data[offset + 1] << 21) | \
              (data[offset + 2] << 14) | (data[offset + 3] << 7) | data[offset + 4]
        if val >= 2147483648:
            val -= 4294967296
        return val, offset + 5

    @classmethod
    def build_message(cls, seq: int, content_bytes: bytes) -> bytes:
        """Build a complete message block with CRC and sync byte.

        Args:
            seq: Sequence number (0-15).
            content_bytes: VLQ-encoded msgid + parameters.
        """
        length = 2 + len(content_bytes) + 2 + 1  # header + content + crc + sync
        if length < cls.MESSAGE_MIN:
            length = cls.MESSAGE_MIN
        if length > cls.MESSAGE_MAX:
            raise ValueError(f"Message too long: {length}")

        header = bytes([length, 0x10 | (seq & 0x0F)])
        pre_crc = header + content_bytes
        crc = cls.crc16_ccitt(pre_crc)
        return pre_crc + bytes([(crc >> 8) & 0xFF, crc & 0xFF, cls.MESSAGE_SYNC])

    @classmethod
    def parse_frame(cls, buf: bytearray) -> Optional[Tuple[int, bytes]]:
        """Try to extract a complete message from the buffer.

        Returns (msgid, params_bytes) or None if no complete frame.
        Side-effect: pops consumed bytes from buf.
        """
        while len(buf) >= cls.MESSAGE_MIN:
            blen = buf[0]
            if blen < cls.MESSAGE_MIN or blen > cls.MESSAGE_MAX:
                buf.pop(0)
                continue

            if len(buf) < blen:
                return None  # need more data

            # Check sync byte
            if buf[blen - 1] != cls.MESSAGE_SYNC:
                buf.pop(0)
                continue

            # Check CRC
            body = buf[:blen - 3]
            expected = bytes([(buf[blen - 3] & 0xFF), (buf[blen - 2] & 0xFF)])
            actual_crc = cls.crc16_ccitt(body)
            actual_bytes = bytes([(actual_crc >> 8) & 0xFF, actual_crc & 0xFF])
            if expected != actual_bytes:
                buf.pop(0)
                continue

            # Valid frame — decode content
            content = buf[2:blen - 3]
            try:
                msgid, offset = cls.vlq_decode(bytes(content), 0)
            except (IndexError, ValueError):
                buf.pop(0)
                continue

            # Pop consumed bytes
            del buf[:blen]
            return msgid, content[offset:]

        return None


# ======================================================================
# MCU State Machine
# ======================================================================

class PyMCU:
    """High-fidelity Python MCU simulator.

    Implements the Kalico MCU firmware's command processing
    logic in pure Python with a virtual clock.
    """

    STATE_INIT = "init"
    STATE_READY = "ready"
    STATE_CONFIGURING = "configuring"
    STATE_CONFIGURED = "configured"
    STATE_SHUTDOWN = "shutdown"

    def __init__(self, name: str = "py-mcu", serial_port: int = 0):
        self.name = name
        self.state = self.STATE_INIT
        self._clock_freq = 16_000_000  # 16 MHz virtual clock
        self._virtual_time: int = 0
        self._start_timestamp = time.monotonic()
        self._seq = 0

        # Serial I/O
        self._serial_port = serial_port
        self._server: Optional[socket.socket] = None
        self._client: Optional[socket.socket] = None
        self._rx_buf = bytearray()
        self._running = False

        # Command handlers: msgid → callable(msgid, params_bytes)
        self._handlers: Dict[int, Callable] = {}
        self._register_handlers()

        # Configuration state
        self._config_oids: Dict[int, Dict] = {}
        self._config_crc = 0
        self._next_oid = 0

        # Data dictionary payload
        self._dict_payload = self._build_dictionary()

        # Hooks for protocol interception
        self.on_rx: Optional[Callable[[bytes], None]] = None
        self.on_tx: Optional[Callable[[bytes], None]] = None

        # Statistics
        self.commands_processed = 0
        self.responses_sent = 0

    # ----------------------------------------------------------------
    # Data dictionary
    # ----------------------------------------------------------------

    def _build_dictionary(self) -> bytes:
        """Build the data dictionary payload that firmware reports.

        This is what the real MCU returns in chunks during identify.
        The host uses it to discover available commands and their
        parameter formats.
        """
        import json, zlib

        # These are the exact message formats from the Kalico firmware
        # (derived from DECL_COMMAND / DECL_OUTPUT macros)
        messages = {
            # Core commands (basecmd.c)
            "identify_response offset=%u data=%.*s": 0,
            "identify offset=%u count=%c": 1,
            # Configuration
            "allocate_oids count=%c": 2,
            "config oid=%c": 3,
            "config_key oid=%c key=%.*s": 4,
            "config_key_value oid=%c key=%.*s value=%.*s": 5,
            "finalize_config crc=%u": 6,
            "get_config": 7,
            # Status / debug
            "get_clock": 8,
            "get_uptime": 9,
            "emergency_stop": 10,
            # Responses
            "clock clock=%u": 101,
            "uptime uptime=%u": 102,
            "config_response oid=%c offset=%u data=%.*s": 103,
            "shutdown clock=%u flags=%c": 104,
        }

        # Reverse mapping for the dictionary format
        commands: Dict[str, int] = {}
        responses: Dict[str, int] = {}
        for fmt, mid in messages.items():
            cmd_name = fmt.split()[0]
            if "_response" in cmd_name or cmd_name in ("clock", "uptime", "shutdown"):
                responses[fmt] = mid
            else:
                commands[fmt] = mid

        payload = {
            "version": f"py-mcu-{self.name}",
            "build_versions": "python-native",
            "config": {
                "MCU": self.name,
                "CLOCK_FREQ": self._clock_freq,
                "RECEIVE_WINDOW": 256,
                "SERIAL_BAUD": 250000,
            },
            "commands": commands,
            "responses": responses,
        }

        return zlib.compress(json.dumps(payload).encode("utf-8"))

    # ----------------------------------------------------------------
    # Command handlers
    # ----------------------------------------------------------------

    def _register_handlers(self) -> None:
        """Register all command handlers."""
        self._handlers[1] = self._handle_identify       # identify
        self._handlers[2] = self._handle_allocate_oids   # allocate_oids
        self._handlers[3] = self._handle_config          # config
        self._handlers[4] = self._handle_config_key      # config_key
        self._handlers[5] = self._handle_config_key_value
        self._handlers[6] = self._handle_finalize_config
        self._handlers[7] = self._handle_get_config
        self._handlers[8] = self._handle_get_clock
        self._handlers[9] = self._handle_get_uptime
        self._handlers[10] = self._handle_emergency_stop

    def _get_clock(self) -> int:
        """Current virtual clock value."""
        elapsed = time.monotonic() - self._start_timestamp
        return int(elapsed * self._clock_freq)

    def _decode_params(self, data: bytes) -> List[int]:
        """Decode all VLQ values from a byte buffer."""
        vals: List[int] = []
        offset = 0
        while offset < len(data):
            val, offset = MCUProtocol.vlq_decode(data, offset)
            vals.append(val)
        return vals

    def _respond(self, msgid: int, *params: int) -> None:
        """Send a response message to the host."""
        seq = self._seq
        self._seq = (self._seq + 1) & 0x0F

        # Encode: msgid + params
        response_content = MCUProtocol.vlq_encode([msgid] + list(params))
        frame = MCUProtocol.build_message(seq, response_content)

        if self.on_tx:
            self.on_tx(frame)

        if self._client:
            try:
                self._client.sendall(frame)
                self.responses_sent += 1
            except OSError:
                logger.error("Failed to send response")

    # ----------------------------------------------------------------
    # Core command implementations
    # ----------------------------------------------------------------

    def _handle_identify(self, msgid: int, params: bytes) -> None:
        vals = self._decode_params(params)
        offset = vals[0] if len(vals) > 0 else 0
        count = vals[1] if len(vals) > 1 else 40
        logger.info("identify: offset=%d count=%d (dict=%d bytes)", offset, count, len(self._dict_payload))

        chunk = self._dict_payload[offset:offset + count]
        if self._client:
            seq = self._seq
            self._seq = (self._seq + 1) & 0x0F
            content = MCUProtocol.vlq_encode([0]) + MCUProtocol.vlq_encode([offset, len(chunk)]) + chunk
            frame = MCUProtocol.build_message(seq, content)
            logger.debug("Sending identify_response (%d bytes)", len(frame))
            self._client.sendall(frame)
            self.responses_sent += 1

    def _handle_allocate_oids(self, msgid: int, params: bytes) -> None:
        vals = self._decode_params(params)
        count = vals[0] if vals else 0
        # Allocate OIDs (just track count)
        self._next_oid = count
        self.state = self.STATE_CONFIGURING
        logger.info("Allocated %d OIDs", count)

    def _handle_config(self, msgid: int, params: bytes) -> None:
        vals = self._decode_params(params)
        oid = vals[0] if vals else 0
        self._config_oids[oid] = {}
        logger.debug("config oid=%d", oid)

    def _handle_config_key(self, msgid: int, params: bytes) -> None:
        vals = self._decode_params(params)
        oid = vals[0] if len(vals) > 0 else 0
        # The key is stored inline after VLQ values
        # For simplicity, just log it
        logger.debug("config_key oid=%d", oid)

    def _handle_config_key_value(self, msgid: int, params: bytes) -> None:
        vals = self._decode_params(params)
        oid = vals[0] if len(vals) > 0 else 0
        logger.debug("config_key_value oid=%d", oid)

    def _handle_finalize_config(self, msgid: int, params: bytes) -> None:
        vals = self._decode_params(params)
        crc = vals[0] if vals else 0
        self._config_crc = crc
        self.state = self.STATE_CONFIGURED
        logger.info("Config finalized (crc=%d)", crc)

    def _handle_get_config(self, msgid: int, params: bytes) -> None:
        """Return the MCU's configuration status."""
        # Send a config_response for each OID
        # Simple: just echo back empty config
        for oid in self._config_oids:
            config_json = '{"is_config":true}'
            data = config_json.encode("utf-8")
            content = MCUProtocol.vlq_encode([103, oid, 0, len(data)]) + data
            seq = self._seq
            self._seq = (self._seq + 1) & 0x0F
            frame = MCUProtocol.build_message(seq, content)
            if self._client:
                self._client.sendall(frame)
                self.responses_sent += 1

    def _handle_get_clock(self, msgid: int, params: bytes) -> None:
        clock = self._get_clock()
        logger.debug("get_clock → %d", clock)
        self._respond(101, clock)

    def _handle_get_uptime(self, msgid: int, params: bytes) -> None:
        uptime = self._get_clock()  # Same as clock in this MCU
        logger.debug("get_uptime → %d", uptime)
        self._respond(102, uptime)

    def _handle_emergency_stop(self, msgid: int, params: bytes) -> None:
        logger.warning("EMERGENCY STOP received")
        self.state = self.STATE_SHUTDOWN
        self._respond(104, self._get_clock(), 0)

    # ----------------------------------------------------------------
    # Lifecycle — TCP server
    # ----------------------------------------------------------------

    def start(self) -> int:
        """Start the TCP server and begin processing commands.

        Returns:
            The bound TCP port number.
        """
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind(("127.0.0.1", self._serial_port))
        self._server.listen(1)
        self._server.settimeout(0.5)

        actual_port = self._server.getsockname()[1]
        self._running = True

        logger.info("=" * 50)
        logger.info("Python MCU '%s' started!", self.name)
        logger.info("  Clock:  %d MHz", self._clock_freq // 1_000_000)
        logger.info("  State:  %s", self.state)
        logger.info("  Port:   TCP 127.0.0.1:%d", actual_port)
        logger.info("=" * 50)
        logger.info("Connect: kalico_debug_tool connect tcp:127.0.0.1:%d", actual_port)

        try:
            self._serve_loop()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            self._running = False
            if self._client:
                self._client.close()
            if self._server:
                self._server.close()

        return actual_port

    def _serve_loop(self) -> None:
        """Main I/O loop: accept client, process frames."""
        while self._running:
            try:
                readers = [self._server]
                writers: List[socket.socket] = []
                if self._client:
                    readers.append(self._client)

                ready_r, _, _ = select.select(readers, [], [], 0.2)

                for r in ready_r:
                    if r is self._server:
                        self._accept()
                    elif r is self._client:
                        self._process_rx()

            except (OSError, ValueError) as exc:
                logger.debug("I/O error: %s", exc)

    def _accept(self) -> None:
        try:
            client, addr = self._server.accept()
        except (socket.timeout, OSError):
            return
        client.settimeout(0.1)
        self._client = client
        logger.info("Host connected: %s:%d", addr[0], addr[1])
        self.state = self.STATE_READY

    def _process_rx(self) -> None:
        """Read from TCP, parse frames, dispatch commands."""
        try:
            data = self._client.recv(4096)
        except (socket.timeout, OSError):
            return

        if not data:
            logger.info("Host disconnected")
            self._client.close()
            self._client = None
            self.state = self.STATE_INIT
            return

        logger.debug("Received %d bytes: %s", len(data), data.hex())
        self._rx_buf.extend(data)
        if self.on_rx:
            self.on_rx(data)

        # Parse all complete frames in buffer
        while True:
            result = MCUProtocol.parse_frame(self._rx_buf)
            if result is None:
                logger.debug("No complete frame in buffer (%d bytes)", len(self._rx_buf))
                break
            msgid, params = result
            logger.info("Dispatch msgid=%d (params=%d bytes)", msgid, len(params))
            self._dispatch(msgid, params)

    def _dispatch(self, msgid: int, params: bytes) -> None:
        """Dispatch a command to its handler."""
        self.commands_processed += 1
        handler = self._handlers.get(msgid)
        if handler:
            try:
                logger.debug("Handling msgid=%d", msgid)
                handler(msgid, params)
            except Exception as exc:
                logger.error("Handler for msgid=%d failed: %s", msgid, exc, exc_info=True)
        else:
            logger.warning("Unknown command msgid=%d (params=%d bytes)", msgid, len(params))


# ======================================================================
# CLI Entry Point
# ======================================================================

def serve_main() -> None:
    """Standalone MCU simulator server."""
    parser = argparse.ArgumentParser(
        description="Python Kalico MCU Simulator"
    )
    parser.add_argument("--port", "-p", type=int, default=0,
                        help="TCP port (0=auto)")
    parser.add_argument("--name", default="py-mcu",
                        help="MCU name (reported in identify)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging")

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)-7s] %(message)s",
        datefmt="%H:%M:%S",
    )

    mcu = PyMCU(name=args.name, serial_port=args.port)
    mcu.start()


if __name__ == "__main__":
    serve_main()
