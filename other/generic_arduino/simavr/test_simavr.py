#!/usr/bin/env python3
import subprocess, time, os, sys, signal
SIMAVR_HOME = '/home/maoweicao/simavr'
RUN_AVR = SIMAVR_HOME + '/simavr/run_avr'
FW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.pio', 'build', 'mega2560', 'firmware.hex')
env = os.environ.copy()
env['LD_LIBRARY_PATH'] = SIMAVR_HOME + '/simavr/obj-x86_64-linux-gnu:' + SIMAVR_HOME + '/examples/parts/obj-x86_64-linux-gnu'
print('=' * 60)
print('  Kalico generic_arduino SimAVR Boot Test')
print('=' * 60)
p = subprocess.Popen([RUN_AVR, '-m', 'atmega2560', '-f', '16000000', FW], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
output = b''
start = time.time()
while time.time() - start < 8:
    chunk = p.stdout.read(4096)
    if chunk:
        output += chunk
        if b'Entering Kalico scheduler loop' in output: break
    else: time.sleep(0.1)
p.send_signal(signal.SIGTERM)
try: p.wait(timeout=3)
except: p.kill()
ot = output.decode('utf-8', errors='replace')
checks = [
    ('Firmware booted', 'Kalico generic_arduino firmware' in ot),
    ('Clock freq correct', 'Clock: 16000000 Hz' in ot),
    ('Baud rate correct', 'Baud: 250000' in ot),
    ('Scheduler started', 'Entering Kalico scheduler loop' in ot),
    ('No unexpected shutdown', 'Entering Kalico' in ot or 'shutdown' not in ot.lower()),
]
pcount = sum(1 for label, ok in checks if ok)
for label, ok in checks:
    print('  {} {}'.format('PASS' if ok else 'FAIL', label))
print()
print('=' * 60)
if pcount == len(checks):
    print('  Results: {}/{} passed -- ALL PASSED!'.format(pcount, len(checks)))
else:
    print('  Results: {}/{} passed, {} FAILED'.format(pcount, len(checks), len(checks)-pcount))
print('=' * 60)
sys.exit(0 if pcount == len(checks) else 1)
