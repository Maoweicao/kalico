"""Debug test for benchmark throughput."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.getcwd())

from kalico_debug_tool.benchmark.engine import (
    BenchmarkEngine, BenchmarkConfig, BenchmarkType,
)
from kalico_debug_tool.protocol.parser import Parser
from kalico_debug_tool.simulator.virtual_mcu import VirtualMCU

parser = Parser()
mcu = VirtualMCU("test-bm")
mcu.start()

def send_fn(data):
    mcu.feed_data(data)
    return True

def recv_fn():
    return []

engine = BenchmarkEngine(parser=parser, send_fn=send_fn, recv_fn=recv_fn,
                          simulator_mode=True)

# Test identify encode
payload = parser.encode_message("identify", offset=0, count=40)
print(f"identify payload: {payload.hex() if payload else 'None'}")

# Test sending directly
print("Testing direct send...")
success = send_fn(payload)
print(f"Direct send: {success}")

# Now manually test the while loop from run_throughput
cfg = BenchmarkConfig(type=BenchmarkType.THROUGHPUT, throughput_packet_count=5)
total_sent = 0
batch_size = 5

print(f"engine._running before loop: {engine._running}")

import time
start_time = time.monotonic()
while total_sent < cfg.throughput_packet_count:
    print(f"  loop iteration: total_sent={total_sent}, _running={engine._running}")
    if not engine._running:
        print("  -> would raise InterruptedError")
        break
    batch = min(batch_size, cfg.throughput_packet_count - total_sent)
    for _ in range(batch):
        engine.send_fn(payload)
    total_sent += batch
    print(f"  sent batch of {batch}, total={total_sent}")

elapsed = time.monotonic() - start_time
print(f"Total: {total_sent} packets in {elapsed:.3f}s")
rate = (total_sent * len(payload)) / elapsed if elapsed > 0 else 0
print(f"Rate: {rate:.0f} bytes/s ({rate/1024:.1f} KB/s)")

mcu.stop()
print("DONE")
