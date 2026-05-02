"""Direct benchmark test."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from kalico_debug_tool.benchmark.engine import BenchmarkEngine, BenchmarkConfig, BenchmarkType
from kalico_debug_tool.protocol.parser import Parser
from kalico_debug_tool.simulator.virtual_mcu import VirtualMCU

parser = Parser()
mcu = VirtualMCU("test")
mcu.start()

def send_fn(data):
    mcu.feed_data(data)
    return True

def recv_fn():
    return []

engine = BenchmarkEngine(parser=parser, send_fn=send_fn, recv_fn=recv_fn,
                          simulator_mode=True, on_progress=print)

print("=== Testing latency ===")
r1 = engine.run_latency(BenchmarkConfig(type=BenchmarkType.LATENCY, latency_sample_count=3))
print(f"  success={r1.success}, samples={len(r1.samples)}, error={r1.error}")

print("=== Testing throughput ===")
r2 = engine.run_throughput(BenchmarkConfig(type=BenchmarkType.THROUGHPUT, throughput_packet_count=20))
print(f"  success={r2.success}, error={r2.error}, samples={len(r2.samples)}")

print("=== Testing clock ===")
r3 = engine.run_clock(BenchmarkConfig(type=BenchmarkType.CLOCK, clock_duration=1.0))
print(f"  success={r3.success}, error={r3.error}")

mcu.stop()
print()
print("ALL BENCHMARK TESTS DONE")
