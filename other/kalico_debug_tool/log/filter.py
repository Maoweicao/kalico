# Protocol event filtering
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Event Filter Module
===================

Provides flexible filtering of protocol events by:
  - Message name (exact match, prefix, regex)
  - Direction (Tx only, Rx only, both)
  - Time range
  - Sequence number
  - Text search within decoded parameters
"""

import re
from typing import List, Optional, Set

from .logger import ProtocolEvent


class EventFilter:
    """Configurable filter for protocol events.

    All criteria are AND-ed together. Set a criterion to None to
    disable that filter dimension.
    """

    def __init__(self):
        self._msg_names: Optional[Set[str]] = None
        self._msg_pattern: Optional[re.Pattern] = None
        self._direction: Optional[str] = None  # "Tx", "Rx", or None
        self._time_start: Optional[float] = None
        self._time_end: Optional[float] = None
        self._seq: Optional[int] = None
        self._text_search: Optional[str] = None
        self._case_sensitive: bool = False
        self._only_errors: bool = False
        self._only_parsed: Optional[bool] = None

    def set_msg_names(self, names: Optional[List[str]]) -> "EventFilter":
        """Filter by exact message name(s)."""
        if names is not None:
            self._msg_names = set(names)
        else:
            self._msg_names = None
        return self

    def set_msg_pattern(self, pattern: Optional[str]) -> "EventFilter":
        """Filter by regex pattern on message name."""
        if pattern is not None:
            self._msg_pattern = re.compile(pattern)
        else:
            self._msg_pattern = None
        return self

    def set_direction(self, direction: Optional[str]) -> "EventFilter":
        """Filter by direction: 'Tx', 'Rx', or None for both."""
        self._direction = direction
        return self

    def set_time_range(self, start: Optional[float] = None,
                       end: Optional[float] = None) -> "EventFilter":
        """Filter by timestamp range (seconds since epoch)."""
        self._time_start = start
        self._time_end = end
        return self

    def set_seq(self, seq: Optional[int]) -> "EventFilter":
        """Filter by sequence number."""
        self._seq = seq
        return self

    def set_text_search(self, text: Optional[str],
                        case_sensitive: bool = False) -> "EventFilter":
        """Filter by text search within decoded params."""
        self._text_search = text
        self._case_sensitive = case_sensitive
        return self

    def set_only_errors(self, only: bool = True) -> "EventFilter":
        """Only show events with parsing errors."""
        self._only_errors = only
        return self

    def set_only_parsed(self, only: bool = True) -> "EventFilter":
        """Only show successfully parsed events."""
        self._only_parsed = only
        return self

    def matches(self, event: ProtocolEvent) -> bool:
        """Check if an event matches all active filter criteria."""
        # Direction
        if self._direction and event.direction != self._direction:
            return False

        # Message name exact
        if self._msg_names and event.msg_name not in self._msg_names:
            return False

        # Message name pattern
        if self._msg_pattern and not self._msg_pattern.search(event.msg_name):
            return False

        # Time range
        if self._time_start is not None and event.timestamp < self._time_start:
            return False
        if self._time_end is not None and event.timestamp > self._time_end:
            return False

        # Sequence number
        if self._seq is not None and event.seq != self._seq:
            return False

        # Parsing status
        if self._only_errors and not event.error:
            return False
        if self._only_parsed is not None:
            if self._only_parsed and not event.is_parsed:
                return False
            if not self._only_parsed and event.is_parsed:
                return False

        # Text search
        if self._text_search:
            text = self._text_search
            if not self._case_sensitive:
                text = text.lower()
                search_in = event.msg_name.lower()
                if text not in search_in:
                    found = False
                    for k, v in event.params.items():
                        k_str = str(k).lower()
                        v_str = str(v).lower()
                        if text in k_str or text in v_str:
                            found = True
                            break
                    if not found:
                        return False
            else:
                search_in = event.msg_name
                if text not in search_in:
                    found = False
                    for k, v in event.params.items():
                        if text in str(k) or text in str(v):
                            found = True
                            break
                    if not found:
                        return False

        return True

    def apply(self, events: List[ProtocolEvent]) -> List[ProtocolEvent]:
        """Filter a list of events."""
        return [e for e in events if self.matches(e)]

    def reset(self) -> None:
        """Clear all filter criteria."""
        self.__init__()

    def is_active(self) -> bool:
        """Check if any filter criterion is set."""
        return any([
            self._msg_names is not None,
            self._msg_pattern is not None,
            self._direction is not None,
            self._time_start is not None,
            self._time_end is not None,
            self._seq is not None,
            self._text_search is not None,
            self._only_errors,
            self._only_parsed is not None,
        ])
