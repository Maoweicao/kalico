#!/usr/bin/env python3
"""End-to-end klippy+simavr test."""
import subprocess, time, os, signal, sys

SIMAVR = '/mnt/f/kalico/other/generic_arduino/simavr/simavr_runner'
FW = '/mnt/f/kalico/other/generic_arduino/.pio/build/mega2560/firmware.hex'
KLIPPY_PY = '/mnt/f/kalico/klippy/klippy.py'
CFG_TMPL = '/mnt/f/kalico/other/generic_arduino/simavr/klippy_test.cfg'

env = os.environ.copy()
env['LD_LIBRARY_PATH'] = '/usr/local/lib'

subprocess.run(['pkill', '-9', 'simavr_runner'], capture_output=True)
subprocess.run(['rm', '-f', '/tmp/simavr-uart*', '/tmp/klippy_test.*'])

print('=' * 60)
print('  Kalico E2E Test: klippy + simavr + generic_arduino')
print('=' * 60)

print('\n[1] Starting simavr...')
p_mcu = subprocess.Popen([SIMAVR, FW], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
time.sleep(2)
pty = os.readlink('/tmp/simavr-uart1')
print('    UART1 =', pty)

with open(CFG_TMPL) as f:
    cfg = f.read().replace('REPLACE_WITH_PTY_PATH', pty)
with open('/tmp/klippy_test.cfg', 'w') as f:
    f.write(cfg)

print('\n[2] Starting klippy...')
sys.path.insert(0, '/mnt/f/kalico')
p_kp = subprocess.Popen(
    ['python3', KLIPPY_PY, '/tmp/klippy_test.cfg', '-l', '/tmp/klippy_test.log', '-v'],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, cwd='/mnt/f/kalico'
)

print('\n[3] Monitoring (30s)...')
output = b''
start = time.time()
success = False
while time.time() - start < 30:
    try:
        chunk = p_kp.stdout.read(4096)
        if chunk:
            output += chunk
            text = chunk.decode('utf-8', errors='replace')
            for line in text.split('\n'):
                if line.strip():
                    print('   ', line.strip()[:130])
                if 'Klipper host software' in line or 'Starting printer' in line:
                    success = True
    except:
        time.sleep(0.1)
    if p_kp.poll() is not None:
        break

print('\n[4] Log:')
try:
    with open('/tmp/klippy_test.log') as f:
        for line in f:
            if any(k in line.lower() for k in ['connect', 'mcu', 'identify', 'config', 'loaded', 'shutdown', 'error', 'serial', 'timeout']):
                print('   ', line.strip()[:130])
except Exception as e:
    print('    error:', e)

try: p_kp.terminate(); p_kp.wait(timeout=3)
except: p_kp.kill()
p_mcu.terminate()
try: p_mcu.wait(timeout=3)
except: p_mcu.kill()

print('\n' + '=' * 60)
print('  Result:', 'SUCCESS' if success else 'CHECK /tmp/klippy_test.log')
print('=' * 60)
sys.exit(0 if success else 1)
