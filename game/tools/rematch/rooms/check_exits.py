# For every Rematch map: list each warp and the behaviour of the tile it sits on. A warp only fires if its
# tile is a door / arrow-warp / stairs / regular warp; on a plain floor tile the player is stuck inside.
import sys, os, json, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import TS, G
os.chdir(G)
B = {}
for l in open('include/constants/metatile_behaviors.h'):
    p = l.split()
    if len(p) >= 3 and p[0] == '#define' and p[1].startswith('MB_'):
        try: B[int(p[2], 16)] = p[1]
        except ValueError: pass
lj = {l.get('id'): l for l in json.load(open('data/layouts/layouts.json'))['layouts']}
for name in sorted(os.listdir('data/maps')):
    if not name.startswith('Rematch'): continue
    m = json.load(open(f'data/maps/{name}/map.json')); L = lj[m['layout']]
    ts = TS(L['primary_tileset'], L['secondary_tileset'])
    b = open(L['blockdata_filepath'], 'rb').read(); blk = struct.unpack(f'<{len(b)//2}H', b)
    for i, w in enumerate(m['warp_events']):
        v = blk[w['y']*L['width'] + w['x']]; mid = v & 0x3ff
        a = ts.attrs[mid] if mid < len(ts.attrs) else None
        print(f"{name:22} warp {i} ({w['x']},{w['y']}) -> {w['dest_map']} {w['dest_warp_id']}: mt {mid:#x} {B.get(a & 0x1ff, a) if a is not None else '??'}")
