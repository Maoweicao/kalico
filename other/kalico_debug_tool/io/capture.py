# Real-time data capture for Kalico protocol debugging
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Data Capture Module
===================

Captures raw serial data streams in real-time, writing them to
log files with timestamps for later analysis and replay.

Capture format: timestamped JSON Lines (.jsonl)
Each line: {"ts": float, "direction": "Tx"|"Rx", "data": [int bytes...]}
"""

import json
import os
import threading
import time
from typing import Optional, TextIO, Union


class CaptureSession:
    """Manages a real-time data capture session.

    Captures both Tx and Rx data with precise timestamps.
    Thread-safe: can be called from serial read thread and main thread.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._file: Optional[TextIO] = None
        self._lock = threading.Lock()
        self._start_time: float = 0.0
        self._packet_count = 0
        self._open()

    def _open(self) -> None:
        """Open the capture file and write header."""
        self._file = open(self.filepath, "w", encoding="utf-8")
        self._start_time = time.time()
        header = {
            "type": "capture_header",
            "start_time": self._start_time,
            "start_iso": time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.localtime(self._start_time)
            ),
        }
        self._file.write(json.dumps(header) + "\n")
        self._file.flush()

    def record(self, direction: str, data: Union[bytes, bytearray]) -> None:
        """Record a data event.

        Args:
            direction: "Tx" for transmitted, "Rx" for received
            data: raw bytes
        """
        entry = {
            "ts": time.time() - self._start_time,
            "direction": direction,
            "data": list(bytes(data)),
        }
        with self._lock:
            if self._file:
                self._file.write(json.dumps(entry) + "\n")
                self._file.flush()
                self._packet_count += 1

    def close(self) -> None:
        """Close the capture file."""
        with self._lock:
            if self._file:
                duration = time.time() - self._start_time
                trailer = {
                    "type": "capture_trailer",
                    "end_time": time.time(),
                    "duration": round(duration, 3),
                    "packet_count": self._packet_count,
                }
                self._file.write(json.dumps(trailer) + "\n")
                self._file.close()
                self._file = None

    @property
    def packet_count(self) -> int:
        return self._packet_count

    @property
    def elapsed(self) -> float:
        return time.time() - self._start_time


class CaptureManager:
    """Manages multiple capture sessions with start/stop control."""

    def __init__(self, capture_dir: Optional[str] = None):
        self.capture_dir = capture_dir or "captures"
        self._session: Optional[CaptureSession] = None
        self._lock = threading.Lock()

    def start(self, name: Optional[str] = None) -> str:
        """Start a new capture session.

        Args:
            name: Optional filename (without extension)

        Returns:
            Path to the capture file
        """
        if not os.path.exists(self.capture_dir):
            os.makedirs(self.capture_dir, exist_ok=True)
        if name is None:
            name = time.strftime("capture_%Y%m%d_%H%M%S")
        filepath = os.path.join(self.capture_dir, f"{name}.jsonl")
        with self._lock:
            if self._session:
                self._session.close()
            self._session = CaptureSession(filepath)
        return filepath

    def record(self, direction: str, data: Union[bytes, bytearray]) -> None:
        """Record data to the active session."""
        with self._lock:
            if self._session:
                self._session.record(direction, data)

    def stop(self) -> Optional[str]:
        """Stop the current capture session.

        Returns:
            Path to the capture file, or None if no session
        """
        with self._lock:
            if self._session:
                path = self._session.filepath
                self._session.close()
                self._session = None
                return path
        return None

    @property
    def is_capturing(self) -> bool:
        with self._lock:
            return self._session is not None

    @property
    def session(self) -> Optional[CaptureSession]:
        with self._lock:
            return self._session


def load_capture(filepath: str) -> list:
    """Load a capture file into a list of events.

    Returns list of dicts with keys: ts, direction, data
    """
    events = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("type") in ("capture_header", "capture_trailer"):
                events.append(entry)
            else:
                entry["data"] = bytes(entry["data"])
                events.append(entry)
    return events
