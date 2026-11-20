# Writes the garden designed in gen_valley.py into the game:
#   data/tilesets/secondary/rematch_garden/  (copy of sevii_islands_67 + imported tiles/palettes + custom metatiles)
#   data/layouts/RematchGarden/{map.bin,border.bin}  and  data/maps/RematchGarden/map.json (objects/warps/signs)
import sys, os, json, struct, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_valley as v
from PIL import Image
G = v.G
SRC = f'{G}/data/tilesets/secondary/sevii_islands_67'
DST = f'{G}/data/tilesets/secondary/rematch_garden'
os.makedirs(DST + '/palettes', exist_ok=True)

# --- tileset ---
im = Image.open(SRC + '/tiles.png').copy(); px = im.load(); tw = im.size[0] // 8
for tid, pix in v.IMPORT_TILES.items():
    i = tid - 640; tx, ty = i % tw, i // tw
    assert ty < im.size[1] // 8, tid
    for y in range(8):
        for x in range(8): px[tx*8+x, ty*8+y] = pix[y][x]
im.save(DST + '/tiles.png')
for i in range(16):
    if i in v.IMPORT_PALS:
        with open(f'{DST}/palettes/{i:02}.pal', 'w', newline='\r\n') as f:
            f.write('JASC-PAL\n0100\n16\n' + ''.join(f'{r} {g_} {b}\n' for r, g_, b in v.IMPORT_PALS[i]))
    else:
        shutil.copy(f'{SRC}/palettes/{i:02}.pal', f'{DST}/palettes/{i:02}.pal')
mts = open(SRC + '/metatiles.bin', 'rb').read(); ats = open(SRC + '/metatile_attributes.bin', 'rb').read()
n = len(mts) // 16
for k, mid in enumerate(sorted(v.CUSTOM)):
    assert mid == 0x280 + n + k, (hex(mid), n, k)
    e, a = v.CUSTOM[mid]
    mts += struct.pack('<8H', *e); ats += struct.pack('<I', a)
open(DST + '/metatiles.bin', 'wb').write(mts); open(DST + '/metatile_attributes.bin', 'wb').write(ats)
print('metatiles', n, '+', len(v.CUSTOM), '=', len(mts)//16, ' imported tiles', len(v.IMPORT_TILES))

# --- layout ---
g = [row[:] for row in v.g]
COL = 0x400
WARPS = [((11, 23), 'MAP_REMATCH_HALL', '3'),      # 0: the café's back door (harbor building)
         ((65, 7), 'MAP_REMATCH_ARENA', '0'),      # 1: the ELITE FOUR tower
         ((11, 11), 'MAP_REMATCH_POKEMON_CENTER', '0'),  # 2: POKéMON CENTER
         ((20, 11), 'MAP_REMATCH_MART', '0'),      # 3: POKé MART
         ((47, 9), 'MAP_REMATCH_POWER_PLANT', '1'),  # 4: LT. SURGE (arrive on the middle of the mat)
         ((16, 17), 'MAP_REMATCH_SABRINA', '1'),   # 5: SABRINA
         ((27, 6), 'MAP_REMATCH_KOGA_CAVE', '0')]  # 6: KOGA
WARPS = [((x + v.LEFT, y + v.TOP), m, w) for (x, y), m, w in WARPS]
CLOSED = {}   # every door now leads somewhere   # interiors come in step 4
for (x, y) in CLOSED: g[y][x] |= COL
# open water (the bay and MISTY's pond): no collision bit, elevation 1, like FireRed's own sea. The player
# (elevation 3) still can't walk onto it; swimmers and water POKéMON (elevation 1) can move across it.
# Every tile that behaves as water - ours and SIX ISLAND's own (which vanilla marks solid: its cove and harbor
# were scenery) - is made surfable this way, so all the water on the map can be reached with SURF.
MB = {}
for l in open(f'{G}/include/constants/metatile_behaviors.h'):
    p_ = l.split()
    if len(p_) >= 3 and p_[0] == '#define' and p_[1].startswith('MB_'):
        try: MB[p_[1]] = int(p_[2], 16)
        except ValueError: pass
SURFABLE = {MB[n] for n in ('MB_POND_WATER', 'MB_FAST_WATER', 'MB_DEEP_WATER', 'MB_OCEAN_WATER', 'MB_UNUSED_WATER',
                            'MB_CYCLING_ROAD_WATER', 'MB_EASTWARD_CURRENT', 'MB_WESTWARD_CURRENT',
                            'MB_NORTHWARD_CURRENT', 'MB_SOUTHWARD_CURRENT') if n in MB}
def behaviour(m):
    if m in v.CUSTOM: return v.CUSTOM[m][1] & 0x1ff
    return v._T67.attrs[m] & 0x1ff if m < len(v._T67.attrs) else 0
SEA_ROCKS = set(range(0x1cb, 0x1d5)) | {0x110, 0x111, 0x118, 0x119}     # rocks standing in the sea: they block SURF
for row in g:
    for i, c in enumerate(row):
        if c & 0x3ff in SEA_ROCKS: row[i] = (c & 0x3ff) | 0x400 | 0x1000
        elif behaviour(c & 0x3ff) in SURFABLE: row[i] = (c & 0x3ff) | 0x1000
os.makedirs(f'{G}/data/layouts/RematchGarden', exist_ok=True)
open(f'{G}/data/layouts/RematchGarden/map.bin', 'wb').write(struct.pack(f'<{v.W*v.H}H', *[c for row in g for c in row]))
open(f'{G}/data/layouts/RematchGarden/border.bin', 'wb').write(struct.pack('<4H', *[0x12b] * 4))   # open sea beyond the edges
LJ = f'{G}/data/layouts/layouts.json'; lj = json.load(open(LJ))
entry = {"id": "LAYOUT_REMATCH_GARDEN", "name": "RematchGarden_Layout", "width": v.W, "height": v.H,
         "border_width": 2, "border_height": 2, "primary_tileset": "gTileset_General",
         "secondary_tileset": "gTileset_RematchGarden",
         "border_filepath": "data/layouts/RematchGarden/border.bin",
         "blockdata_filepath": "data/layouts/RematchGarden/map.bin"}
lj['layouts'] = [l for l in lj['layouts'] if l.get('id') != 'LAYOUT_REMATCH_GARDEN'] + [entry]
json.dump(lj, open(LJ, 'w'), indent=2); open(LJ, 'a').write('\n')

# --- map.json ---
GFX = {'REMATCH_': 'OBJ_EVENT_GFX_REMATCH_'}
def gfx(name):
    return 'OBJ_EVENT_GFX_' + name
def camel(s): return ''.join(p.capitalize() for p in s.split('_'))
WATER = {'STARMIE', 'STARYU', 'TUBER_BOY', 'TUBER_GIRL', 'FERRY'}
# who moves: (movement type, range x, range y). A WALK_SEQUENCE type starts at the bottom-left corner and
# traces a square whose side is the range (up, right, down, left).
MOVES = {  # the BIKER is parked now: he rides up to you (Rematch_Garden_EventScript_BikerRollsUp)
         'TUBER_BOY': ('MOVEMENT_TYPE_WALK_SEQUENCE_UP_RIGHT_DOWN_LEFT', 2, 2),
         'TUBER_GIRL': ('MOVEMENT_TYPE_WALK_SEQUENCE_UP_RIGHT_DOWN_LEFT', 2, 2),
         'STARMIE': ('MOVEMENT_TYPE_WANDER_AROUND', 1, 1),
         'STARYU': ('MOVEMENT_TYPE_WANDER_AROUND', 1, 1),
         'MR_MIME': ('MOVEMENT_TYPE_WANDER_AROUND', 1, 1),
         # the couples' POKéMON roam behind their trainers, each in its own way and with random pauses
         'TAUROS': ('MOVEMENT_TYPE_WANDER_AROUND', 1, 1),          # trots around
         'MILTANK': ('MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', 1, 0),  # ambles side to side
         'RAPIDASH': ('MOVEMENT_TYPE_WANDER_AROUND', 1, 1),        # prances around
         'NINETALES': ('MOVEMENT_TYPE_WANDER_UP_AND_DOWN', 0, 1),  # drifts up and down
         'VILEPLUME': ('MOVEMENT_TYPE_WANDER_AROUND', 2, 1),     # ERIKA's POKéMON roam the flower beds
         'ODDISH': ('MOVEMENT_TYPE_WANDER_AROUND', 2, 1),
         'TANGELA': ('MOVEMENT_TYPE_WANDER_AROUND', 2, 1)}
objs = []
for lid, gname, x, y, face in v.OBJECTS:
    o = {"local_id": f"LOCALID_GARDEN_{lid}", "type": "object", "graphics_id": gfx(gname), "x": x, "y": y,
         "elevation": 1 if lid in WATER else 3, "movement_type": MOVES[lid][0] if lid in MOVES else f"MOVEMENT_TYPE_{face}",
         "movement_range_x": MOVES.get(lid, (None, 1, 1))[1], "movement_range_y": MOVES.get(lid, (None, 1, 1))[2], "trainer_type": "TRAINER_TYPE_NONE",
         "trainer_sight_or_berry_tree_id": "0",
         "script": "0x0" if lid == 'FERRY' else f"Rematch_Garden_EventScript_{camel(lid)}",
         "flag": "FLAG_REMATCH_GARDEN_CUT_TREE" if lid == 'CUT_TREE' else "0"}
    objs.append(o)
MJ = f'{G}/data/maps/RematchGarden/map.json'; mj = json.load(open(MJ))
mj['layout'] = 'LAYOUT_REMATCH_GARDEN'
mj['region_map_section'] = 'MAPSEC_SIX_ISLAND'
mj['object_events'] = objs
mj['warp_events'] = [{"x": x, "y": y, "elevation": 0, "dest_map": m, "dest_warp_id": w} for (x, y), m, w in WARPS]
# walk-ups (scripts in data/maps/RematchGarden/scripts.pory): BROCK at the stairs into his hollow, the BIKER on the beach
mj['coord_events'] = [{"type": "trigger", "x": x, "y": y, "elevation": 3, "var": v, "var_value": "0", "script": sc} for x, y, v, sc in [
    (27, 27, 'VAR_TEMP_2', 'Rematch_Garden_EventScript_BrockAtStairs'), (28, 27, 'VAR_TEMP_2', 'Rematch_Garden_EventScript_BrockAtStairs'),
    (68, 27, 'VAR_TEMP_3', 'Rematch_Garden_EventScript_BikerRollsUp'), (40, 30, 'VAR_TEMP_3', 'Rematch_Garden_EventScript_BikerRollsUp'),
    (41, 30, 'VAR_TEMP_3', 'Rematch_Garden_EventScript_BikerRollsUp'), (42, 30, 'VAR_TEMP_3', 'Rematch_Garden_EventScript_BikerRollsUp')]]
signs = [((9 + v.LEFT, 17 + v.TOP), 'GardenSign'), ((46 + v.LEFT, 11 + v.TOP), 'PowerPlantSign')] + [(xy, s) for xy, s in CLOSED.items()]
mj['bg_events'] = [{"type": "sign", "x": x, "y": y, "elevation": 0, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                    "script": f"Rematch_Garden_EventScript_{s}"} for (x, y), s in signs]
json.dump(mj, open(MJ, 'w'), indent=2); open(MJ, 'a').write('\n')
print('objects', len(objs), [o['local_id'][15:] for o in objs])
