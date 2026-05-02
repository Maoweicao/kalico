# Virtual MCU command handler framework
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Command Handler Framework
=========================

Provides a flexible command registration and dispatch system
for the virtual MCU simulator. Handlers can be registered for
specific command message names and can produce responses.

Each handler is a callable that receives decoded parameters
and returns response parameters.
"""

import logging
from typing import Any, Callable, Dict, Optional

# Handler type: receives (params_dict, virtual_mcu) and returns response dict
CommandHandler = Callable[[Dict[str, Any], "VirtualMCU"], Optional[Dict[str, Any]]]  # noqa


class CommandRegistry:
    """Registry mapping command names to handler functions."""

    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}
        self._default_handler: Optional[CommandHandler] = None

    def register(self, cmd_name: str, handler: CommandHandler) -> None:
        """Register a handler for a specific command."""
        self._handlers[cmd_name] = handler
        logging.debug(f"Registered command handler: {cmd_name}")

    def unregister(self, cmd_name: str) -> None:
        """Remove a command handler."""
        self._handlers.pop(cmd_name, None)

    def set_default(self, handler: CommandHandler) -> None:
        """Set a default handler for unregistered commands."""
        self._default_handler = handler

    def dispatch(self, cmd_name: str, params: Dict[str, Any],
                 mcu: "VirtualMCU") -> Optional[Dict[str, Any]]:
        """Dispatch a command to its registered handler.

        Args:
            cmd_name: Command name (e.g., "identify", "config")
            params: Decoded command parameters
            mcu: The VirtualMCU instance (passed to handler)

        Returns:
            Response parameters dict, or None if no response needed
        """
        handler = self._handlers.get(cmd_name)
        if handler is not None:
            return handler(params, mcu)
        if self._default_handler is not None:
            return self._default_handler(params, mcu)
        logging.warning(f"No handler for command: {cmd_name}")
        return None

    def has_handler(self, cmd_name: str) -> bool:
        return cmd_name in self._handlers

    def list_commands(self) -> list:
        return sorted(self._handlers.keys())


# Import here to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .virtual_mcu import VirtualMCU
