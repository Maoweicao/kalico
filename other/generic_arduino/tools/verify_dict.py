import re, zlib, json
with open('/mnt/f/kalico/other/generic_arduino/src/compile_time_request.c') as f:
    c = f.read()
hexes = re.findall(r'0x([0-9a-fA-F]{2})', c[c.find('command_identify_data'):][:8000])
data = bytes(int(h,16) for h in hexes)
d = json.loads(zlib.decompress(data))
print('MCU:', d['config'].get('MCU','NOT FOUND'))
print('app:', d.get('app','NOT FOUND'))
print('version:', d.get('version','NOT FOUND')[:60])
print('config keys:', sorted(d['config'].keys()))
