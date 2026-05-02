# Structured protocol event logging
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Protocol Event Logger
=====================

Records structured protocol events (Tx/Rx messages) as JSON Lines.
Each event captures full context: timestamp, direction, raw bytes,
parsed message, and metadata.

Designed for:
  - Real-time GUI display (event stream)
  - Offline analysis (JSON file)
  - AI Agent consumption (machine-parseable)
"""

import json
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional

from ..protocol.codec import MessageBlock
from ..protocol.parser import ParsedMessage


@dataclass
class ProtocolEvent:
    """A single protocol event (Tx or Rx message)."""

    timestamp: float
    direction: str          # "Tx" or "Rx"
    msg_name: str           # Parsed message name
    seq: int                # Sequence number
    raw_hex: str            # Raw bytes as hex string
    params: Dict[str, Any]  # Decoded parameters
    raw_bytes: bytes        # Raw binary data
    is_parsed: bool = True  # Whether parsing succeeded
    error: str = ""         # Error message if parsing failed
    id: int = 0             # Auto-increment event ID

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict (without raw bytes)."""
        return {
            "id": self.id,
            "ts": round(self.timestamp, 6),
            "direction": self.direction,
            "name": self.msg_name,
            "seq": self.seq,
            "raw": self.raw_hex,
            "params": self.params,
            "is_parsed": self.is_parsed,
            "error": self.error,
        }

    def to_json_line(self) -> str:
        """Serialize to a JSON Lines entry (includes raw hex but not bytes)."""
        data = self.to_dict()
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_parsed(cls, parsed: ParsedMessage, direction: str,
                    event_id: int = 0) -> "ProtocolEvent":
        """Create from a ParsedMessage."""
        return cls(
            timestamp=time.time(),
            direction=direction,
            msg_name=parsed.msg_name,
            seq=parsed.seq,
            raw_hex=parsed.raw_hex,
            params=parsed.params,
            raw_bytes=parsed.block.raw_bytes or parsed.block.encode(),
            is_parsed=True,
            id=event_id,
        )

    @classmethod
    def from_raw(cls, data: bytes, direction: str,
                 msg_name: str = "#raw",
                 error: str = "",
                 event_id: int = 0) -> "ProtocolEvent":
        """Create from raw bytes (unparsed)."""
        return cls(
            timestamp=time.time(),
            direction=direction,
            msg_name=msg_name,
            seq=0,
            raw_hex=data.hex(),
            params={},
            raw_bytes=data,
            is_parsed=not bool(error),
            error=error,
            id=event_id,
        )


class LogEngine:
    """Central log engine for protocol events.

    Maintains an in-memory ring buffer of recent events and
    optionally writes to a JSON Lines file. Thread-safe.
    """

    def __init__(self, max_events: int = 10000):
        self._events: List[ProtocolEvent] = []
        self._max_events = max_events
        self._lock = threading.Lock()
        self._next_id = 1
        self._log_file: Optional[str] = None
        self._file_handle = None

        # Callbacks
        self.on_event: Optional[Callable[[ProtocolEvent], None]] = None

    def start_file_logging(self, filepath: str) -> None:
        """Start writing events to a JSON Lines file."""
        self._log_file = filepath
        self._file_handle = open(filepath, "w", encoding="utf-8")
        header = {
            "type": "log_start",
            "time": time.time(),
            "time_iso": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self._file_handle.write(json.dumps(header) + "\n")
        self._file_handle.flush()

    def stop_file_logging(self) -> None:
        """Stop file logging."""
        if self._file_handle:
            trailer = {
                "type": "log_end",
                "time": time.time(),
                "event_count": self._next_id - 1,
            }
            self._file_handle.write(json.dumps(trailer) + "\n")
            self._file_handle.close()
            self._file_handle = None
            self._log_file = None

    def log_event(self, event: ProtocolEvent) -> None:
        """Record a protocol event."""
        with self._lock:
            event.id = self._next_id
            self._next_id += 1
            self._events.append(event)

            # Write to file if active
            if self._file_handle:
                self._file_handle.write(event.to_json_line() + "\n")
                self._file_handle.flush()

            # Trim ring buffer
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]

        # Fire callback (outside lock)
        if self.on_event:
            try:
                self.on_event(event)
            except Exception as e:
                pass

    def log_message(self, parsed: ParsedMessage,
                    direction: str) -> ProtocolEvent:
        """Convenience: create and log event from ParsedMessage."""
        event = ProtocolEvent.from_parsed(parsed, direction)
        self.log_event(event)
        return event

    def log_raw(self, data: bytes, direction: str,
                msg_name: str = "#raw",
                error: str = "") -> ProtocolEvent:
        """Convenience: create and log event from raw bytes.

        Args:
            data: Raw bytes
            direction: "Tx" or "Rx"
            msg_name: Message name override
            error: Error description if parsing failed
        """
        event = ProtocolEvent.from_raw(data, direction,
                                       msg_name=msg_name, error=error)
        self.log_event(event)
        return event

    def get_events(self, start: int = 0,
                   count: Optional[int] = None) -> List[ProtocolEvent]:
        """Get events from the ring buffer.

        Args:
            start: Starting index (0 = newest? older events)
            count: Number of events to return (None = all)

        Returns:
            List of protocol events (oldest first)
        """
        with self._lock:
            if count is None:
                return list(self._events[start:])
            return list(self._events[start:start + count])

    def get_all_events(self) -> List[ProtocolEvent]:
        """Get all buffered events (oldest first)."""
        with self._lock:
            return list(self._events)

    def clear(self) -> None:
        """Clear all buffered events."""
        with self._lock:
            self._events.clear()

    @property
    def event_count(self) -> int:
        with self._lock:
            return len(self._events)

    @property
    def total_count(self) -> int:
        return self._next_id - 1
