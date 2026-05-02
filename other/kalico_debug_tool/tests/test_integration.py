"""Integration test for Kalico Debug Tool."""
import sys
import os

# Add workspace root to path
SRC = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, SRC)
os.chdir(SRC)

print("=== Kalico Debug Tool - Integration Test ===")
print()

# 1. Version
from kalico_debug_tool import __version__
print(f"1. Version: {__version__}")

# 2. Codec
from kalico_debug_tool.protocol.codec import (
    MessageBlock, VLQEncoder, VLQDecoder, build_message_packet,
)
# Build a proper identify command: msgid=1, offset=0, count=40
msgid_vlq = VLQEncoder.encode_uint32(1)
offset_vlq = VLQEncoder.encode_uint32(0)
count_vlq = VLQEncoder.encode_byte(40)
content = bytes(msgid_vlq + offset_vlq + count_vlq)
block = MessageBlock(seq=0, content=content)
packet = block.encode()
decoded = MessageBlock.decode(packet)
assert decoded.seq == 0
assert decoded.content == content
print(f"2. Codec roundtrip: {packet.hex()}")

# 3. Dictionary
from kalico_debug_tool.protocol.dictionary import MessageDictionary
d = MessageDictionary()
d.add_default_messages()
print(f"3. Dictionary: {len(d.messages)} msgs")

# 4. Parser
from kalico_debug_tool.protocol.parser import Parser
p = Parser()
parsed = p.parse_block(decoded)
print(f"4. Parser: {parsed.msg_name}")

# 5. VirtualMCU
from kalico_debug_tool.simulator.virtual_mcu import VirtualMCU
mcu = VirtualMCU("test")
mcu.start()
msg = mcu.feed_data(packet)
mcu.stop()
print(f"5. VirtualMCU: state={mcu.state}, msgs={len(msg)}")

# 6. LogEngine
from kalico_debug_tool.log.logger import LogEngine
log = LogEngine()
log.log_message(parsed, "Rx")
log.log_raw(packet, "Tx")
print(f"6. LogEngine: {log.event_count} events")

# 7. Exporter
from kalico_debug_tool.log.export import Exporter
csv = Exporter.to_csv(log.get_all_events())
print(f"7. Exporter: csv={len(csv)} chars")

# 8. CLICommands
from kalico_debug_tool.cli.commands import CLICommands
cmds = CLICommands()
status = cmds.cmd_get_status()
print(f"8. CLICommands: ok={status.get('ok')}")

# 9. AIBridge
from kalico_debug_tool.cli.ai_bridge import AIBridge
bridge = AIBridge()
line = '{"id":"1","cmd":"get_status","params":{}}'
resp = bridge.process_line(line)
has_ok = '"ok": true' in resp
print(f"9. AIBridge: ok={has_ok}")

print()
print("ALL INTEGRATION TESTS PASSED")
