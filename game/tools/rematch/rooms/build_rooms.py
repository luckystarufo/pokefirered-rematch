# Writes the three leader rooms into the game (approved from mockups, 2026-11-17):
#   RematchPowerPlant  LT. SURGE + an aide at CELIO's network machine (own tileset gTileset_RematchPowerPlant)
#   RematchSabrina     the SAFFRON GYM's entrance room + the leader's pink cushions (gTileset_SaffronGym)
#   RematchKogaCave    FIVE ISLAND's Lost Cave entrance, dark until FLASH (gTileset_Cave)
import sys, os, json, struct, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import surge_room as S
from render import layout, G
from PIL import Image
os.chdir(G)

def region(lid, x0, y0, w, h):
    L = layout(lid); b = open(L['blockdata_filepath'], 'rb').read(); B = struct.unpack(f'<{len(b)//2}H', b)
    return L, [[B[(y0+y)*L['width'] + x0+x] for x in range(w)] for y in range(h)]

def write_layout(name, src, g, secondary=None):
    lid = 'LAYOUT_' + ''.join('_'+c if c.isupper() else c.upper() for c in name).lstrip('_')
    d = f'data/layouts/{name}'; os.makedirs(d, exist_ok=True)
    open(f'{d}/map.bin', 'wb').write(struct.pack(f'<{len(g)*len(g[0])}H', *[c for r in g for c in r]))
    shutil.copy(src['border_filepath'], f'{d}/border.bin')
    lj = json.load(open('data/layouts/layouts.json'))
    e = dict(src); e.update(id=lid, name=f'{name}_Layout', width=len(g[0]), height=len(g),
                            border_filepath=f'{d}/border.bin', blockdata_filepath=f'{d}/map.bin')
    if secondary: e['secondary_tileset'] = secondary
    lj['layouts'] = [l for l in lj['layouts'] if l.get('id') != lid] + [e]
    json.dump(lj, open('data/layouts/layouts.json', 'w'), indent=2); open('data/layouts/layouts.json', 'a').write('\n')
    return lid

def obj(prefix, lid, gfx, x, y, move, rx=1, ry=1, script=None):
    return {"local_id": f"LOCALID_{prefix}_{lid}", "type": "object", "graphics_id": 'OBJ_EVENT_GFX_' + gfx, "x": x, "y": y,
            "elevation": 3, "movement_type": move, "movement_range_x": rx, "movement_range_y": ry,
            "trainer_type": "TRAINER_TYPE_NONE", "trainer_sight_or_berry_tree_id": "0",
            "script": script or f"Rematch_{prefix.title().replace('_','')}_EventScript_{''.join(p.capitalize() for p in lid.split('_'))}", "flag": "0"}

def write_map(name, lid, music, mtype, mapsec, objs, warps, bgs=(), flash=False):
    d = f'data/maps/{name}'; os.makedirs(d, exist_ok=True)
    m = {"id": 'MAP_' + lid[len('LAYOUT_'):], "name": name, "layout": lid, "music": music, "region_map_section": mapsec,
         "requires_flash": flash, "weather": "WEATHER_NONE", "map_type": mtype, "allow_cycling": False,
         "allow_escaping": False, "allow_running": True, "show_map_name": False, "floor_number": 0,
         "battle_scene": "MAP_BATTLE_SCENE_NORMAL", "connections": None, "object_events": objs,
         "warp_events": [{"x": x, "y": y, "elevation": 0, "dest_map": "MAP_REMATCH_GARDEN", "dest_warp_id": str(w)} for x, y, w in warps],
         "coord_events": [], "bg_events": list(bgs)}
    json.dump(m, open(f'{d}/map.json', 'w'), indent=2); open(f'{d}/map.json', 'a').write('\n')
    mg = json.load(open('data/maps/map_groups.json'))
    for grp, maps in mg.items():
        if isinstance(maps, list) and 'RematchArena' in maps and name not in maps: maps.append(name)
    json.dump(mg, open('data/maps/map_groups.json', 'w'), indent=2); open('data/maps/map_groups.json', 'a').write('\n')

WANDER = 'MOVEMENT_TYPE_WANDER_AROUND'
# ------------------------------------------------------------ LT. SURGE: tileset + layout + map (garden warp 4)
SRC = 'data/tilesets/secondary/power_plant'; DST = 'data/tilesets/secondary/rematch_power_plant'
os.makedirs(DST + '/palettes', exist_ok=True)
im = Image.open(SRC + '/tiles.png'); tw = im.size[0] // 8
need = S.N_SEC_TILES + len(S.NEW_TILES); rows = (need + tw - 1) // tw
out = Image.new('P', (im.size[0], rows * 8)); out.putpalette(im.getpalette()); out.paste(im, (0, 0)); px = out.load()
for t, pix in S.NEW_TILES.items():
    i = t - 640
    for y in range(8):
        for x in range(8): px[(i % tw)*8 + x, (i // tw)*8 + y] = pix[y][x]
out.save(DST + '/tiles.png')
for i in range(16):
    if i in S.PAL_MAP.values():
        src_slot = [k for k, v in S.PAL_MAP.items() if v == i][0]
        with open(f'{DST}/palettes/{i:02}.pal', 'w', newline='\r\n') as f:
            f.write('JASC-PAL\n0100\n16\n' + ''.join(f'{r} {g_} {b}\n' for r, g_, b in S.ot.pals[src_slot]))
    else:
        shutil.copy(f'{SRC}/palettes/{i:02}.pal', f'{DST}/palettes/{i:02}.pal')
mts = open(SRC + '/metatiles.bin', 'rb').read(); ats = open(SRC + '/metatile_attributes.bin', 'rb').read()
assert len(mts) // 16 == S.N_SEC_MTS
for e, a in S.CUSTOM: mts += struct.pack('<8H', *e); ats += struct.pack('<I', a)
open(DST + '/metatiles.bin', 'wb').write(mts); open(DST + '/metatile_attributes.bin', 'wb').write(ats)
lid = write_layout('RematchPowerPlant', S.PP, S.g, 'gTileset_RematchPowerPlant')
objs = [obj('SURGE_ROOM', 'SURGE', 'LT_SURGE', 7, 9, 'MOVEMENT_TYPE_FACE_UP', script='Rematch_PowerPlant_EventScript_Surge'),
        obj('SURGE_ROOM', 'AIDE', 'SCIENTIST', 8, 9, 'MOVEMENT_TYPE_FACE_UP', script='Rematch_PowerPlant_EventScript_Aide'),
        obj('SURGE_ROOM', 'RAICHU', 'REMATCH_RAICHU', 3, 11, WANDER, 2, 2, 'Rematch_PowerPlant_EventScript_Raichu'),
        obj('SURGE_ROOM', 'VOLTORB', 'VOLTORB', 11, 12, WANDER, 2, 2, 'Rematch_PowerPlant_EventScript_Voltorb')]
bg_machine = [{"type": "sign", "x": x, "y": 8, "elevation": 0, "player_facing_dir": "BG_EVENT_PLAYER_FACING_NORTH",
               "script": "Rematch_PowerPlant_EventScript_Machine"} for x in range(5, 11)]
write_map('RematchPowerPlant', lid, 'MUS_POKE_MANSION', 'MAP_TYPE_INDOOR', 'MAPSEC_SIX_ISLAND', objs,
          [(7, 16, 4), (8, 15, 4), (9, 16, 4)], bg_machine)
print('surge: tiles', need, 'metatiles +', len(S.CUSTOM))

# ------------------------------------------------------------ SABRINA (garden warp 5)
L, g = region('LAYOUT_SAFFRON_CITY_GYM', 9, 16, 11, 8)
_, rug = region('LAYOUT_SAFFRON_CITY_GYM', 12, 10, 5, 3)
for j in range(3):                                 # her old leader's cushion, all 5x3 of it, against the back
    for i in range(5): g[2+j][3+i] = rug[j][i]     # wall as in SAFFRON (its top row is part of the wall strip)
_, orig = region('LAYOUT_SAFFRON_CITY_GYM', 9, 16, 11, 8)
statue_top, statue_base = orig[3][3], orig[4][3]
for x in (2, 8): g[3][x] = statue_top; g[4][x] = statue_base   # the statues step aside to frame the cushion
lid = write_layout('RematchSabrina', L, g)
objs = [obj('SABRINA_ROOM', 'SABRINA', 'SABRINA', 5, 3, 'MOVEMENT_TYPE_FACE_DOWN', script='Rematch_Sabrina_EventScript_Sabrina'),
        obj('SABRINA_ROOM', 'ALAKAZAM', 'REMATCH_ALAKAZAM', 2, 6, WANDER, 1, 1, 'Rematch_Sabrina_EventScript_Alakazam')]
write_map('RematchSabrina', lid, 'MUS_LAVENDER', 'MAP_TYPE_INDOOR', 'MAPSEC_SIX_ISLAND', objs, [(4, 7, 5), (5, 7, 5), (6, 7, 5)])

# ------------------------------------------------------------ KOGA (garden warp 6)
L, g = region('LAYOUT_FIVE_ISLAND_LOST_CAVE_ENTRANCE', 0, 0, 11, 11)
g[5][5] = g[4][5]                                  # floor instead of the hole down
lid = write_layout('RematchKogaCave', L, g)
objs = [obj('KOGA_ROOM', 'KOGA', 'KOGA', 5, 3, 'MOVEMENT_TYPE_FACE_DOWN', script='Rematch_KogaCave_EventScript_Koga'),
        obj('KOGA_ROOM', 'WEEZING', 'REMATCH_WEEZING', 3, 4, WANDER, 1, 1, 'Rematch_KogaCave_EventScript_Weezing'),
        obj('KOGA_ROOM', 'MUK', 'REMATCH_MUK', 7, 4, WANDER, 1, 1, 'Rematch_KogaCave_EventScript_Muk')]
write_map('RematchKogaCave', lid, 'MUS_SEVII_CAVE', 'MAP_TYPE_UNDERGROUND', 'MAPSEC_SIX_ISLAND', objs, [(5, 8, 6)], flash=True)
print('done')
