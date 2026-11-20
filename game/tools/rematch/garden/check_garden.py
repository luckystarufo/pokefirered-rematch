# Garden checks: every calm water tile reachable (walking + SURF), no FAST water left, and no tile you can stand
# on whose screen (7 left/right, 4 up, 5 down) reaches past the map edge. Current tiles push you off, so you
# can't stand on them.
import struct, sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import TS, G
from collections import Counter
os.chdir(G)
ts = TS('gTileset_General', 'gTileset_RematchGarden')
L = [l for l in json.load(open('data/layouts/layouts.json'))['layouts'] if l.get('id') == 'LAYOUT_REMATCH_GARDEN'][0]; W, H = L['width'], L['height']
b = open('data/layouts/RematchGarden/map.bin', 'rb').read(); B = struct.unpack(f'<{len(b)//2}H', b)
CURRENT = {0x50, 0x51, 0x52, 0x53}; CALM = {0x10, 0x12, 0x15, 0x1a}
def info(x, y): v = B[y*W + x]; m = v & 0x3ff; return m, ts.attrs[m] & 0x1ff, (v >> 10) & 3, v >> 12
def standable(x, y):
    m, beh, col, el = info(x, y)
    return col == 0 and beh not in CURRENT and beh != 0x11
mj = json.load(open('data/maps/RematchGarden/map.json')); w0 = mj['warp_events'][0]; start = (w0['x'], w0['y'] + 1)
seen = {start}; q = [start]
while q:
    x, y = q.pop()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (x + dx, y + dy)
        if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and standable(*n): seen.add(n); q.append(n)
calm = {(x, y) for y in range(H) for x in range(W) if info(x, y)[1] in CALM and info(x, y)[2] == 0}   # solid = sea rocks
fast = sum(1 for y in range(H) for x in range(W) if info(x, y)[1] == 0x11)
bad = [(x, y) for (x, y) in seen if x - 7 < 0 or x + 7 >= W or y - 4 < 0 or y + 5 >= H]
print(f'map {W}x{H}; calm water {len(calm)}, unreachable {len(calm - seen)}; fast water {fast}; '
      f'standable tiles seeing past the edge {len(bad)}', Counter(('L' if x < 7 else '') + ('R' if x + 7 >= W else '') + ('T' if y < 4 else '') + ('B' if y + 5 >= H else '') for x, y in bad))
if bad: print(sorted(bad)[:12])
