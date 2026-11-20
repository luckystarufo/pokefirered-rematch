# The creator's room reuses the HALL OF FAME tileset, whose floor metatiles have the ICE behaviour
# (the player slides). Nothing in Rematch visits the vanilla HALL OF FAME or UNION ROOM maps, so the
# floor is made normal ground in place. Safe to run again.
import struct
G = __file__.rsplit('/tools/', 1)[0]
MB = {}
for l in open(G + '/include/constants/metatile_behaviors.h'):
    p = l.split()
    if len(p) >= 3 and p[0] == '#define' and p[1].startswith('MB_'):
        try: MB[p[1]] = int(p[2], 16)
        except ValueError: pass
path = G + '/data/tilesets/secondary/hall_of_fame/metatile_attributes.bin'
a = list(struct.unpack('<%dI' % (len(open(path, 'rb').read()) // 4), open(path, 'rb').read()))
n = 0
for i, v in enumerate(a):
    if v & 0x1ff == MB['MB_ICE']:
        a[i] = (v & ~0x1ff) | MB['MB_NORMAL']; n += 1
open(path, 'wb').write(struct.pack('<%dI' % len(a), *a))
print('ice -> normal:', n)
