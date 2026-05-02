"""Test benchmark engine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.getcwd())

from kalico_debug_tool.benchmark.engine import (
    BenchmarkEngine, BenchmarkConfig, BenchmarkType, format_result_summary,
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
print(f"engine._running before: {engine._running}")
engine._running = True
print(f"engine._running after: {engine._running}")

# Test identify encode
payload = parser.encode_message("identify", offset=0, count=40)
print(f"identify payload: {payload.hex() if payload else 'None'}")

# Throughput
cfg = BenchmarkConfig(type=BenchmarkType.THROUGHPUT, throughput_packet_count=50)
cfg = BenchmarkConfig(type=BenchmarkType.THROUGHPUT, throughput_packet_count=50)
result = engine.run_throughput(cfg)
s = result.summary()
print(f"Throughput: success={s['success']}, samples={len(result.samples)}")
assert s["success"], f"Throughput failed: {s['error']}"

# Clean up
mcu.stop()
print("ALL THROUGHPUT BENCHMARK TESTS PASSED")
