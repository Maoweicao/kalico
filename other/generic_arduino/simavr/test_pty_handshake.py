#!/usr/bin/env python3
"""Full identify handshake + data dictionary validation."""
import os, time, zlib, json

def crc16(data):
    crc = 0xffff
    for b in data:
        x = b ^ (crc & 0xff); x ^= (x << 4) & 0xff
        crc = (((x << 8) | (crc >> 8)) ^ (x >> 4) ^ (x << 3)) & 0xffff
    return crc

def e(v):
    if -(1<<5) <= v < (3<<5): return bytes([v & 0x7f])
    if -(1<<12) <= v < (3<<12): return bytes([((v>>7)&0x7f)|0x80, v&0x7f])
    if -(1<<19) <= v < (3<<19): return bytes([((v>>14)&0x7f)|0x80, ((v>>7)&0x7f)|0x80, v&0x7f])
    return bytes([((v>>21)&0x7f)|0x80, ((v>>14)&0x7f)|0x80, ((v>>7)&0x7f)|0x80, v&0x7f])

def b(msgid, payload=b''):
    body = bytes([msgid]) + payload if msgid < 0x80 else bytes([(msgid>>7)|0x80, msgid&0x7f]) + payload
    ml = 2 + len(body) + 3
    crc = crc16(bytes([ml, 0x10]) + body)
    return bytes([ml, 0x10]) + body + bytes([(crc>>8)&0xff, crc&0xff, 0x7e])

pty1 = os.readlink('/tmp/simavr-uart1')
print('UART1 =', pty1)
fd = os.open(pty1, os.O_RDWR | os.O_NONBLOCK)
time.sleep(0.5)
while True:
    try: os.read(fd, 4096)
    except: break

all_data = b''
offset = 0

for chunk_num in range(20):
    os.write(fd, b(1, e(offset) + e(50)))

    time.sleep(0.3)
    buf = b''
    for _ in range(30):
        try:
            d = os.read(fd, 4096)
            if d: buf += d
        except: pass
        time.sleep(0.02)

    # Find identify_response (msgid=0)
    found = False
    i = 0
    while i + 5 <= len(buf):
        ml = buf[i]
        if ml < 5 or ml > 64 or i+ml > len(buf) or buf[i+ml-1] != 0x7e:
            i += 1; continue
        body = buf[i+2:i+ml-3]
        if len(body) < 1:
            i += ml; continue
        msgid = body[0] & 0x7f
        if body[0] & 0x80 and len(body) > 1:
            msgid = ((body[0]&0x7f)<<7) | body[1]
        if msgid == 0:
            hdr = 1 if body[0] < 0x80 else 2
            dlen = body[hdr+1] if len(body) > hdr+1 else 0
            chunk = body[hdr+2:hdr+2+dlen] if dlen > 0 else b''
            all_data += chunk
            offset += dlen
            found = True
            print('  Chunk {}: offset={} len={} total={}'.format(chunk_num, body[hdr], dlen, len(all_data)))
            if dlen == 0:
                break
        i += ml
    if not found or (found and offset > 0):
        break

os.close(fd)

if all_data:
    try:
        info = json.loads(zlib.decompress(all_data))
        print('\nData dictionary ({}B compressed):'.format(len(all_data)))
        print('  Commands ({}):'.format(len(info.get('commands',{}))))
        for k, v in sorted(info.get('commands',{}).items(), key=lambda x: x[1]):
            print('    msgid={}: {}'.format(v, k))
        print('  Responses ({}):'.format(len(info.get('responses',{}))))
        for k, v in sorted(info.get('responses',{}).items(), key=lambda x: x[1]):
            print('    msgid={}: {}'.format(v, k))
    except Exception as e:
        print('Error:', e)
        print('Raw:', all_data[:200].hex())
