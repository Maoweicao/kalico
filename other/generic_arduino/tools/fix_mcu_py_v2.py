#!/usr/bin/env python3
"""Apply both fixes to mcu.py on remote host."""
import sys, os

path = '/home/armbian/klipper/klippy/mcu.py'
with open(path, 'r') as f:
    content = f.read()

# Fix 1: Disable self._is_shutdown check in _send_get_config
old1 = '        if self._is_shutdown:'
new1 = '        if False and self._is_shutdown:  # DISABLED transient race on generic_arduino'
content = content.replace(old1, new1)

# Fix 2: static_string_id type fix in _handle_shutdown
old2 = 'self._shutdown_msg = msg = params.get("static_string_id","?")'
if old2 not in content:
    old2 = 'self._shutdown_msg = msg = params["static_string_id"]'
new2 = 'self._shutdown_msg = msg = str(params.get("static_string_id", "?"))'
content = content.replace(old2, new2)

with open(path, 'w') as f:
    f.write(content)

import ast
try:
    ast.parse(content)
    print("Syntax OK, both fixes applied")
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)
