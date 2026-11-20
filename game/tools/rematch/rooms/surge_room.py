# LT. SURGE's room: the POWER PLANT's entrance hall with the One Island network machine (the one CELIO
# worked on) moved in. The machine's art is the top layer of 6x5 metatiles in the PokemonCenter tileset; its
# bottom layer (Pokémon Center floor/wall) is swapped for Power Plant floor.
#   python3 surge_room.py mock   -> surge_room.png (mockup)
#   python3 surge_room.py write  -> data/tilesets/secondary/rematch_power_plant + data/layouts/RematchPowerPlant
import sys, os, struct, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import TS, layout, G, render_blocks
from PIL import Image

PP = layout('LAYOUT_POWER_PLANT'); OP = layout('LAYOUT_ONE_ISLAND_POKEMON_CENTER_1F')
pt = TS(PP['primary_tileset'], PP['secondary_tileset']); ot = TS(OP['primary_tileset'], OP['secondary_tileset'])
def blocks(L):
    b = open(f"{G}/{L['blockdata_filepath']}", 'rb').read(); return struct.unpack(f'<{len(b)//2}H', b), L['width']
PB, PW = blocks(PP); OB, OW = blocks(OP)

X0, Y0, W, H = 0, 28, 11, 12                       # the entrance hall (left part of the bottom of the plant)
g = [[PB[(Y0+y)*PW + X0+x] for x in range(W)] for y in range(H)]
FLOOR = PB[32*PW + 3]                             # plain plant floor (0x29f), with its collision/elevation bits
def same(x, y, from_x, from_y): g[y][x] = PB[(Y0+from_y)*PW + X0+from_x]
# one continuous back wall: the band on top, a console row, and its shadow (the original has a corridor gap here)
for x in range(1, 10):
    same(x, 0, 2, 0)          # wall band
    same(x, 1, 2, 1)          # console, upper half
    same(x, 2, 2, 2)          # console, lower half
    same(x, 3, 2, 3)          # shadow under the consoles
same(1, 3, 1, 3)              # shadow's left end
N_SEC_MTS = len(pt.mts) - 640                      # plant secondary metatiles; ours are appended after them
N_SEC_TILES = 80                                   # tiles in power_plant/tiles.png; ours are appended after them
PAL_MAP = {8: 9, 11: 10, 12: 12}                   # Pokémon Center palettes -> free Power Plant slots
CUSTOM = []; NEW_TILES = {}; tmap = {}
def import_mt(m):
    top = []
    for e in ot.mts[m][4:]:
        t, pal = e & 0x3ff, e >> 12
        if t >= 640:
            if t not in tmap:
                tmap[t] = 640 + N_SEC_TILES + len(tmap); NEW_TILES[tmap[t]] = ot.tiles[t]
            t = tmap[t]
        top.append(t | (e & 0x0c00) | (PAL_MAP.get(pal, pal) << 12))
    bottom = list(pt.mts[FLOOR & 0x3ff][:4])
    CUSTOM.append((tuple(bottom + top), ot.attrs[m]))
    return 0x280 + N_SEC_MTS + len(CUSTOM) - 1
MX, MY = 2, 4                                      # machine's top-left corner in the room
for j in range(5):
    for i in range(6):
        m = OB[(1+j)*OW + 12+i] & 0x3ff
        g[MY+j][MX+i] = import_mt(m) | 0x400 | 0x3000          # solid
for (x, y) in ((1, 5), (1, 6), (1, 7), (8, 5), (9, 5), (8, 6), (9, 6), (8, 7), (9, 7), (8, 8), (9, 8)):
    g[y][x] = FLOOR                                # open floor around the machine
g[8][1] = FLOOR                                    # no rubble where RAICHU plays
same(10, 5, 10, 4)                                 # right wall: close the old doorway to the next hall
for (x, y) in ((8, 6), (9, 6), (9, 7)):            # a little rubble left from the repairs
    same(x, y, 8, 6)

# make the hall roomier: 3 more columns just inside the left wall, 5 more rows between the machine and the
# entrance carpet. New columns continue the back wall (band / consoles / shadow) and the floor.
ADD_X, ADD_Y = 3, 5
plain_col = [same_v for same_v in (PB[(Y0+0)*PW+X0+2], PB[(Y0+1)*PW+X0+2], PB[(Y0+2)*PW+X0+2], PB[(Y0+3)*PW+X0+2])]
g = [row[:2] + [plain_col[y] if y < 4 else FLOOR for _ in range(ADD_X)] + row[2:] for y, row in enumerate(g)]
W += ADD_X
open_row = [g[6][0], g[6][1]] + [FLOOR] * (W - 3) + [g[6][W-1]]
g = g[:9] + [open_row[:] for _ in range(ADD_Y)] + g[9:]
H += ADD_Y
for x in range(2, 2 + ADD_X): g[H-1][x] = g[H-1][1]       # bottom wall continues under the new columns
OBJECTS = [  # local id, graphics, x, y, facing
    ('SURGE', 'LT_SURGE', 7, 9, 'FACE_UP'),
    ('AIDE', 'SCIENTIST', 8, 9, 'FACE_UP'),
    ('RAICHU', 'REMATCH_RAICHU', 3, 11, 'FACE_RIGHT'),
    ('VOLTORB', 'VOLTORB', 11, 12, 'FACE_LEFT'),
]

def tileset():
    ts = TS(PP['primary_tileset'], PP['secondary_tileset'])
    for k, (e, a) in enumerate(CUSTOM):
        mid = 0x280 + N_SEC_MTS + k
        while len(ts.mts) <= mid: ts.mts.append((0,)*8); ts.attrs.append(0)
        ts.mts[mid] = e; ts.attrs[mid] = a
    for t, pix in NEW_TILES.items():
        while len(ts.tiles) <= t: ts.tiles.append([[0]*8]*8)
        ts.tiles[t] = pix
    for s, d in PAL_MAP.items(): ts.pals[d] = ot.pals[s]
    return ts

if __name__ == '__main__' and sys.argv[1:] == ['mock']:
    import mock
    render_blocks(tileset(), [c for r in g for c in r], W, H, 'surge_base.png')
    mock.SHEETS['RED'] = ('people/red_normal', 16, 32); mock.SHEETS['SCIENTIST'] = ('people/scientist', 16, 32)
    mock.mock('surge_base.png', [(o[1], o[2], o[3], o[4]) for o in OBJECTS] + [('RED', 9, 15, 'FACE_UP')], 'surge_room.png', scale=3)
