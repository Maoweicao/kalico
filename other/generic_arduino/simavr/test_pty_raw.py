#!/usr/bin/env python3
"""Test PTY output from simavr using raw os.read instead of pyserial."""
import subprocess, time, os, signal, fcntl

env = os.environ.copy()
env['LD_LIBRARY_PATH'] = '/home/maoweicao/simavr/simavr/obj-x86_64-linux-gnu:/home/maoweicao/simavr/examples/parts/obj-x86_64-linux-gnu'

print("Starting simavr...")
p = subprocess.Popen([
    '/mnt/f/kalico/other/generic_arduino/simavr/simavr_runner',
    '/mnt/f/kalico/other/generic_arduino/.pio/build/mega2560/firmware.elf'
], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True)

time.sleep(2)

# Read UART0 PTY using raw fd (non-blocking)
uart0_link = '/tmp/simavr-uart0'
uart1_link = '/tmp/simavr-uart1'

for label, link in [('UART0', uart0_link), ('UART1', uart1_link)]:
    if os.path.exists(link):
        pty_path = os.readlink(link)
        print(f"\n{label}: opening {pty_path}...")
        try:
            fd = os.open(pty_path, os.O_RDONLY | os.O_NONBLOCK)
            data = b''
            for _ in range(40):  # 4 seconds of polling
                try:
                    chunk = os.read(fd, 256)
                    if chunk:
                        data += chunk
                except BlockingIOError:
                    pass
                time.sleep(0.1)
            os.close(fd)
            print(f"{label}: {len(data)} bytes read")
            print(f"  hex: {data[:80].hex() if data else '(empty)'}" )
            print(f"  raw: {repr(data[:100])}")
        except Exception as e:
            print(f"{label}: Error: {e}")
    else:
        print(f"{label}: PTY link not found")

p.terminate()
try:
    p.wait(timeout=3)
except:
    p.kill()
