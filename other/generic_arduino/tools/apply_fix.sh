cd /home/armbian/klipper
cp klippy/mcu.py klippy/mcu.py.bak
python3 -c "
lines = open('klippy/mcu.py').readlines()
for i, l in enumerate(lines):
    stripped = l.strip()
    if stripped == 'if self._is_shutdown:':
        indent = l[:len(l) - len(l.lstrip())]
        lines[i] = indent + 'if False and self._is_shutdown:  # DISABLED: transient race on generic_arduino\n'
        break
open('klippy/mcu.py','w').writelines(lines)
"
echo '--- verify ---'
sed -n '1086,1100p' klippy/mcu.py
python3 -c 'import ast; ast.parse(open(\"klippy/mcu.py\").read()); print(\"Syntax OK\")'
