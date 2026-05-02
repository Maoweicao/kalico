# Offline data replay for Kalico protocol debugging
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Data Replay Module
==================

Replays previously captured data streams for offline analysis.
Supports variable speed playback, step-by-step mode, and
callback-driven event delivery.

This is useful for:
  - Debugging protocol issues offline
  - Testing the parser without a real MCU
  - Regression testing after protocol changes
"""

import threading
import time
from typing import Callable, List, Optional, Tuple

from .capture import load_capture


class ReplayPlayback:
    """Controls playback of a captured data stream.

    Events are delivered via callbacks, simulating real-time
    serial communication.
    """

    STATE_IDLE = "idle"
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_FINISHED = "finished"

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.events = load_capture(filepath)
        self._state = self.STATE_IDLE
        self._speed = 1.0
        self._current_index = 0
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

        # Callbacks
        self.on_tx: Optional[Callable[[bytes], None]] = None
        self.on_rx: Optional[Callable[[bytes], None]] = None
        self.on_complete: Optional[Callable] = None
        self.on_progress: Optional[Callable[[int, int], None]] = None

    @property
    def state(self) -> str:
        return self._state

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = max(0.1, min(1000.0, value))

    @property
    def total_events(self) -> int:
        return len(self.events)

    @property
    def current_position(self) -> int:
        return self._current_index

    def _is_data_event(self, event: dict) -> bool:
        return "direction" in event and "data" in event

    def play(self) -> None:
        """Start or resume playback."""
        if self._state == self.STATE_PLAYING:
            return
        if self._state == self.STATE_PAUSED:
            self._pause_event.clear()
            self._state = self.STATE_PLAYING
            return
        self._state = self.STATE_PLAYING
        self._stop_event.clear()
        self._pause_event.clear()
        self._thread = threading.Thread(
            target=self._playback_loop, daemon=True,
            name="replay-thread"
        )
        self._thread.start()

    def pause(self) -> None:
        """Pause playback."""
        if self._state == self.STATE_PLAYING:
            self._state = self.STATE_PAUSED
            self._pause_event.set()

    def stop(self) -> None:
        """Stop playback and reset to beginning."""
        self._state = self.STATE_IDLE
        self._stop_event.set()
        self._current_index = 0

    def step(self) -> bool:
        """Advance one event (step mode).

        Returns:
            True if there was a next event
        """
        if self._current_index >= len(self.events):
            return False
        event = self.events[self._current_index]
        self._current_index += 1
        if self._is_data_event(event):
            self._dispatch_event(event)
        return True

    def seek(self, index: int) -> None:
        """Jump to a specific event index."""
        self._current_index = max(0, min(index, len(self.events)))

    def _dispatch_event(self, event: dict) -> None:
        """Dispatch a single data event to the appropriate callback."""
        direction = event["direction"]
        data = event["data"]
        if isinstance(data, bytes):
            raw = data
        else:
            raw = bytes(data) if data else b""

        if direction == "Tx" and self.on_tx:
            self.on_tx(raw)
        elif direction == "Rx" and self.on_rx:
            self.on_rx(raw)

    def _playback_loop(self) -> None:
        """Background playback thread."""
        data_events = [
            (i, e) for i, e in enumerate(self.events)
            if self._is_data_event(e)
        ]
        if not data_events:
            self._state = self.STATE_FINISHED
            if self.on_complete:
                self.on_complete()
            return

        # Find header for base timestamp
        base_ts = 0.0
        for e in self.events:
            if e.get("type") == "capture_header":
                base_ts = e.get("start_time", 0.0)
                break
        if not base_ts:
            base_ts = data_events[0][1].get("ts", 0.0)

        first_real_ts = time.time()
        first_event_ts = data_events[0][1].get("ts", 0.0)

        for idx, event in data_events:
            if self._stop_event.is_set():
                break

            # Pause handling
            while self._pause_event.is_set():
                if self._stop_event.is_set():
                    break
                time.sleep(0.05)

            # Timing: replay at specified speed
            event_ts = event.get("ts", 0.0)
            elapsed = event_ts - first_event_ts
            target_time = first_real_ts + (elapsed / self._speed)
            now = time.time()
            if target_time > now:
                wait = target_time - now
                if wait > 0.005:
                    self._stop_event.wait(min(wait, 1.0))
                    if self._stop_event.is_set():
                        break

            self._current_index = idx
            self._dispatch_event(event)

            if self.on_progress:
                self.on_progress(idx + 1, len(data_events))

        if not self._stop_event.is_set():
            self._state = self.STATE_FINISHED
            if self.on_complete:
                self.on_complete()
