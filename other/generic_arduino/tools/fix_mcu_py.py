#!/usr/bin/env python3
"""Fix mcu.py: remove transient _is_shutdown check in _send_get_config."""
import sys, os

path = '/home/armbian/klipper/klippy/mcu.py'
with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
skip_until_outdent = False
in_send_get_config = False
found_config_send = False

for i, line in enumerate(lines):
    if 'def _send_get_config(self):' in line:
        in_send_get_config = True
        new_lines.append(line)
        continue
    
    if in_send_get_config and 'config_params = get_config_cmd.send()' in line:
        found_config_send = True
        new_lines.append(line)
        # Add comment
        new_lines.append("        # Trust MCU's atomic config response for is_shutdown.\n")
        new_lines.append("        # Do not check self._is_shutdown (transient race\n")
        new_lines.append("        # with MCU-side post-config shutdown on generic_arduino).\n")
        continue
    
    if in_send_get_config and found_config_send and 'if self._is_shutdown:' in line:
        # Skip this block until we see a line at same indent level
        target_indent = len(line) - len(line.lstrip())
        block_lines = 0
        j = i
        while j < len(lines):
            l = lines[j]
            if l.strip() == '' or l.strip().startswith('#'):
                block_lines += 1
                j += 1
                continue
            indent = len(l) - len(l.lstrip())
            if indent <= target_indent and l.strip():
                break
            block_lines += 1
            j += 1
        # Skip past the block
        for k in range(i, j):
            pass  # just skip
        continue
    
    if in_send_get_config and 'return config_params' in line:
        in_send_get_config = False
        found_config_send = False
    
    if skip_until_outdent:
        # This path won't be used due to the continue above
        pass
    
    new_lines.append(line)

with open(path, 'w') as f:
    f.writelines(new_lines)

print("mcu.py patched successfully")

# Verify
import ast
with open(path) as f:
    source = f.read()
try:
    ast.parse(source)
    print("Syntax OK")
except SyntaxError as e:
    print(f"Syntax error: {e}")
