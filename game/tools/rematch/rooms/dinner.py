# The dinner finale (RematchDinner): the café with every table pushed into one long feast table.
#   - appends a few custom metatiles to gTileset_RestaurantHotel (long-table middles with dishes, chairs facing up);
#     the vanilla CELADON restaurant/hotel maps don't use the new ids. Safe to run again.
#   - writes data/layouts/RematchDinner and data/maps/RematchDinner/map.json (objects: everyone at the table)
import sys, os, json, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import layout, G
os.chdir(G)
TS = 'data/tilesets/secondary/restaurant_hotel'
VANILLA = 112                      # metatiles in the vanilla tileset
VANILLA_TILE_ROWS = 5              # tiles.png is 16 tiles wide, 5 rows (80 tiles) in vanilla
PLATE_T, PLATE_B = 0x280 + 80, 0x280 + 81   # our new tiles: the right half of a plate, without the table's edge,
MUG_T, MUG_B = 0x280 + 82, 0x280 + 83       # ... and the left edge of a drink, which vanilla draws in the table-edge tile,
NIGHT_PANE = 0x280 + 84                     # ... and a window pane showing the night sky (dark, with a few stars),
NEAR_PLATE = [0x280 + 85 + i for i in range(4)]   # ... and a plate / a drink on the NEAR half of the table (the vanilla
NEAR_MUG = [0x280 + 89 + i for i in range(4)]     #     food only sits by the far edge): tiles TL/TR of the table's top
                                                  #     row's lower half, then of its bottom row's upper half
def T(t, h=0, v=0, p=7): return t | (h << 10) | (v << 11) | (p << 12)
FLOOR = [T(0x2a8, p=8)] * 4
def mt(tl, tr, bl, br): return FLOOR + [tl, tr, bl, br]
CUSTOM = [  # (name, entries, attribute)
 ('MID_TOP',      mt(T(0x2b3,1), T(0x2b3), T(0x2c3,1), T(0x2c3)), 0x20000000),
 ('MID_TOP_SALAD',mt(T(0x2b8), T(PLATE_T), T(0x2c8), T(PLATE_B)), 0x20000000),
 ('MID_TOP_SALAD2',mt(T(PLATE_T,1), T(0x2b8,1), T(PLATE_B,1), T(0x2c8,1)), 0x20000000),
 ('MID_TOP_MUG',  mt(T(MUG_T), T(0x2b7), T(MUG_B), T(0x2c7)), 0x20000000),
 ('MID_TOP_MUG2', mt(T(0x2b7,1), T(MUG_T,1), T(0x2c7,1), T(MUG_B,1)), 0x20000000),
 ('MID_BOT',      mt(T(0x2b5,1), T(0x2b5), T(0x2c5,1), T(0x2c5)), 0x20000000),
 ('NEAR_PLATE_TOP', mt(T(0x2b3,1), T(0x2b3), T(NEAR_PLATE[0]), T(NEAR_PLATE[1])), 0x20000000),
 ('NEAR_PLATE_BOT', mt(T(NEAR_PLATE[2]), T(NEAR_PLATE[3]), T(0x2c5,1), T(0x2c5)), 0x20000000),
 ('NEAR_MUG_TOP',   mt(T(0x2b3,1), T(0x2b3), T(NEAR_MUG[0]), T(NEAR_MUG[1])), 0x20000000),
 ('NEAR_MUG_BOT',   mt(T(NEAR_MUG[2]), T(NEAR_MUG[3]), T(0x2c5,1), T(0x2c5)), 0x20000000),
 ('NIGHT_WINDOW', [T(NIGHT_PANE, p=8), T(NIGHT_PANE, 1, 0, 8), T(0x2c0, p=8), T(0x2c0, p=8)] + [0] * 4, 0x0),
 ('CHAIR_UP',     FLOOR + [T(0x2ad,0,1,0), T(0x2ad,1,1,0), T(0x2ac,0,1,0), T(0x2ac,1,1,0)], 0x20000000),
]
ID = {n: 0x280 + VANILLA + i for i, (n, _, _) in enumerate(CUSTOM)}
def write_tiles():
    # The plate in the vanilla tiles sits against the table's right edge (tiles 0x2b8/0x2b9 over 0x2c8/0x2c9).
    # Rebuild its right half on plain table wood so a whole plate can sit in the middle of the long table.
    from PIL import Image
    im = Image.open(f'{TS}/tiles.png'); pal = im.getpalette(); W = im.size[0] // 8
    im = im.crop((0, 0, im.size[0], VANILLA_TILE_ROWS * 8))
    def tile(t):
        i = t - 0x280; return [[im.getpixel(((i % W)*8 + x, (i // W)*8 + y)) for x in range(8)] for y in range(8)]
    def plate_half(edge, wood, top):
        out = [r[:] for r in edge]
        for y in range(8):
            for x in range(8):
                if x >= 6 or out[y][x] == 0 or (top and y < 3): out[y][x] = wood[y][x]
        return out
    def mug_left(edge, wood, top):
        out = [r[:] for r in wood]
        for y in range(8):
            for x in range(4, 8):
                p = edge[y][x]
                if p not in (0, 0xc, 0xd) and not (top and y < 3): out[y][x] = p
        return out
    new = [plate_half(tile(0x2b9), tile(0x2b3), True), plate_half(tile(0x2c9), tile(0x2c3), False),
           mug_left(tile(0x2b6), tile(0x2b3), True), mug_left(tile(0x2c6), tile(0x2c3), False)]
    pane = [r[:] for r in tile(0x2aa)]          # frame 1, glass 4 (white) / 7 (light blue): glass -> 1 (dark slate)
    for y in range(8):
        for x in range(8):
            if pane[y][x] in (4, 7): pane[y][x] = 1
    for (x, y) in ((3, 2), (6, 4), (4, 5)): pane[y][x] = 6     # stars (pale yellow)
    new.append(pane)
    # dishes on the near half: take the whole plate / drink (16x16 over plain wood), drop it 9 pixels lower so it
    # straddles the table's two rows, and cut the four 8x8 tiles it now covers
    def tl(t, h=False):
        p = new[t - 0x280 - 80] if t >= 0x280 + 80 else tile(t)
        return [r[::-1] for r in p] if h else p
    def meta16(a, b, c, d):            # [(tile, hflip)] x4 -> 16x16
        A, B, C, D = (tl(*a), tl(*b), tl(*c), tl(*d))
        return [A[y] + B[y] for y in range(8)] + [C[y] + D[y] for y in range(8)]
    plate = meta16((0x2b8, 0), (PLATE_T, 0), (0x2c8, 0), (PLATE_B, 0))
    mug = meta16((MUG_T, 0), (0x2b7, 0), (MUG_B, 0), (0x2c7, 0))
    base = meta16((0x2b3, 1), (0x2b3, 0), (0x2c3, 1), (0x2c3, 0)) + meta16((0x2b5, 1), (0x2b5, 0), (0x2c5, 1), (0x2c5, 0))
    for dish in (plate, mug):
        canvas = [r[:] for r in base]
        for y in range(3, 16):
            for x in range(16):
                if dish[y][x] not in (0, 0xc): canvas[y + 9][x] = dish[y][x]
        for (y0, x0) in ((8, 0), (8, 8), (16, 0), (16, 8)):
            new.append([canvas[y0 + y][x0:x0 + 8] for y in range(8)])
    out = Image.new('P', (im.size[0], (VANILLA_TILE_ROWS + 1) * 8), 0); out.putpalette(pal); out.paste(im, (0, 0))
    for k, t in enumerate(new):
        for y in range(8):
            for x in range(8): out.putpixel((k*8 + x, VANILLA_TILE_ROWS*8 + y), t[y][x])
    out.save(f'{TS}/tiles.png')

def write_tileset():
    write_tiles()
    m = open(f'{TS}/metatiles.bin', 'rb').read()[:VANILLA * 16]
    a = open(f'{TS}/metatile_attributes.bin', 'rb').read()[:VANILLA * 4]
    for _, e, at in CUSTOM:
        m += struct.pack('<8H', *e); a += struct.pack('<I', at)
    open(f'{TS}/metatiles.bin', 'wb').write(m); open(f'{TS}/metatile_attributes.bin', 'wb').write(a)

COL = 0x400
# Seating (decided 2026-11-18): every seat taken. {PLAYER} and {RIVAL} at the left end, PROF. OAK (and the
# CREATOR, who joins only when it makes the head count even) at the right end, the important faces in the top
# row (facing down, so we see them), everyone else in the bottom row. The table is as long as the rows need.
LEFT_X, ROW_TOP, ROW_BOT = 1, 5, 8     # table on rows 6-7: a clear strip along the top for POKéMON
T1, T2 = ROW_TOP + 1, ROW_TOP + 2
def build_layout(n):
    L = layout('LAYOUT_REMATCH_HALL'); W, H = L['width'], L['height']
    b = struct.unpack(f'<{W*H}H', open(L['blockdata_filepath'], 'rb').read())
    g = [list(b[y*W:(y+1)*W]) for y in range(H)]
    for y in range(3, 12):                       # clear the dining room (the kitchen on the right stays)
        for x in range(1, 17): g[y][x] = 0x2d4
    for x in range(W):                           # it's night: the windows show a dark sky
        if g[1][x] & 0x3ff == 0x2d0: g[1][x] = (g[1][x] & ~0x3ff) | ID['NIGHT_WINDOW']
    g[2][14] = 0x2c5                             # no half-plant on the wall (its pot was in the cleared floor)
    # the camera frames rows 2..11, so the wall with the (night) windows comes down one row into view
    for x in range(1, 17): g[2][x] = g[1][x]
    x0, x1 = LEFT_X + 1, LEFT_X + n              # table columns
    # dishes alternate between the far half (vanilla food) and the near half (ours), so the whole table is laden
    dishes = [('NEAR_PLATE_TOP', 'NEAR_PLATE_BOT'), ('MID_TOP_MUG', 'MID_BOT'), ('NEAR_MUG_TOP', 'NEAR_MUG_BOT'),
              ('MID_TOP_SALAD', 'MID_BOT'), ('NEAR_PLATE_TOP', 'NEAR_PLATE_BOT'), ('MID_TOP_MUG2', 'MID_BOT'),
              ('NEAR_MUG_TOP', 'NEAR_MUG_BOT'), ('MID_TOP_SALAD2', 'MID_BOT')]
    g[T1][x0] = 0x2e8 | COL; g[T1][x1] = 0x2e9 | COL          # ends: a salad on the left, a drink on the right
    g[T2][x0] = 0x2c1 | COL; g[T2][x1] = 0x2c2 | COL
    for k, x in enumerate(range(x0 + 1, x1)):
        top, bot = dishes[k % len(dishes)]
        g[T1][x] = ID[top] | COL; g[T2][x] = ID[bot] | COL
    # no chairs: everyone stands around the table (a mix of seated and standing looked odd)
    for x in range(x0, x1 + 1):
        pass
        # the bottom row sits on the floor side of the table: no chair tiles (a flipped chair showed as a jagged band)

    d = 'data/layouts/RematchDinner'; os.makedirs(d, exist_ok=True)
    open(f'{d}/map.bin', 'wb').write(struct.pack(f'<{W*H}H', *[c for r in g for c in r]))
    open(f'{d}/border.bin', 'wb').write(open(L['border_filepath'], 'rb').read())
    lj = json.load(open('data/layouts/layouts.json')); e = dict(L)
    e.update(id='LAYOUT_REMATCH_DINNER', name='RematchDinner_Layout', border_filepath=f'{d}/border.bin', blockdata_filepath=f'{d}/map.bin')
    lj['layouts'] = [l for l in lj['layouts'] if l.get('id') != 'LAYOUT_REMATCH_DINNER'] + [e]
    json.dump(lj, open('data/layouts/layouts.json', 'w'), indent=2); open('data/layouts/layouts.json', 'a').write('\n')
    return g

TOP = [('MISTY','MISTY'), ('BROCK','BROCK'), ('ERIKA','ERIKA'), ('SURGE','LT_SURGE'), ('KOGA','KOGA'), ('SABRINA','SABRINA'),
       ('BLAINE','BLAINE'), ('LORELEI','LORELEI'), ('BRUNO','BRUNO'), ('AGATHA','AGATHA'), ('LANCE','LANCE')]
BOTTOM = [('GIOVANNI','GIOVANNI'), ('GRUNT_F','ROCKET_F'), ('DAUGHTER','LITTLE_GIRL'), ('GUARD','POLICEMAN'), ('LEX','COOLTRAINER_M'),
          ('NYA','COOLTRAINER_F'), ('JED','MAN'), ('LEA','BEAUTY'), ('GURU','FISHER'), ('BROTHER','FISHER'), ('BIKE_SHOP','MAN')]
guests = 1 + 1 + 1 + len(TOP) + len(BOTTOM)      # {PLAYER}, {RIVAL}, OAK, the rows
WITH_CREATOR = guests % 2 == 1
assert len(TOP) == len(BOTTOM)
N = len(TOP)                                     # seats per row = table length
RIGHT_X = LEFT_X + N + 1
PEOPLE = ([('RIVAL', 'BLUE', LEFT_X, T2, 'RIGHT'), ('OAK', 'PROF_OAK', RIGHT_X, T1, 'LEFT')]
          + ([('CREATOR', 'GBA_KID', RIGHT_X, T2, 'LEFT')] if WITH_CREATOR else [])
          + [(lid, gfx, LEFT_X + 1 + i, ROW_TOP, 'DOWN') for i, (lid, gfx) in enumerate(TOP)]
          + [(lid, gfx, LEFT_X + 1 + i, ROW_BOT, 'UP') for i, (lid, gfx) in enumerate(BOTTOM)]
          # the CHEF and the noodle guy bring the food in from the kitchen and stand together off the right end
          + [('CHEF', 'CHEF', 16, T1, 'LEFT'), ('GRUNT_M', 'ROCKET_M', 16, T2, 'LEFT')]
          # POKéMON around the room, on the floor (not on chairs), looking every which way
          + [('MACHOKE', 'MACHOKE', 2, 3, 'DOWN'), ('CLEFAIRY', 'CLEFAIRY', 6, 3, 'RIGHT'), ('JIGGLYPUFF', 'JIGGLYPUFF', 10, 3, 'DOWN'),
             ('SNORLAX', 'SNORLAX', 14, 4, 'DOWN'),                                  # along the top
             ('PIKACHU', 'PIKACHU', 1, 10, 'UP'), ('MEOWTH', 'MEOWTH', 4, 10, 'RIGHT'), ('PSYDUCK', 'PSYDUCK', 6, 9, 'DOWN'),
             ('LAPRAS', 'LAPRAS', 9, 10, 'DOWN'), ('SLOWPOKE', 'SLOWPOKE', 11, 9, 'LEFT'), ('CHANSEY', 'CHANSEY', 14, 9, 'LEFT')])
PLAYER_SEAT = (LEFT_X, T1)

def write_map():
    objs = [{"local_id": f"LOCALID_DINNER_{lid}", "type": "object", "graphics_id": 'OBJ_EVENT_GFX_' + gfx, "x": x, "y": y,
             "elevation": 3, "movement_type": 'MOVEMENT_TYPE_FACE_' + f, "movement_range_x": 0, "movement_range_y": 0,
             "trainer_type": "TRAINER_TYPE_NONE", "trainer_sight_or_berry_tree_id": "0", "script": "0x0", "flag": "0"}
            for lid, gfx, x, y, f in PEOPLE]
    # OBJECT_EVENTS_COUNT is 40: the player, these, and the scene's camera object must all fit
    assert len(objs) <= 38, len(objs)
    d = 'data/maps/RematchDinner'; os.makedirs(d, exist_ok=True)
    m = {"id": "MAP_REMATCH_DINNER", "name": "RematchDinner", "layout": "LAYOUT_REMATCH_DINNER", "music": "MUS_SS_ANNE",
         "region_map_section": "MAPSEC_SIX_ISLAND", "requires_flash": False, "weather": "WEATHER_NONE", "map_type": "MAP_TYPE_INDOOR",
         "allow_cycling": False, "allow_escaping": False, "allow_running": True, "show_map_name": False, "floor_number": 0,
         "battle_scene": "MAP_BATTLE_SCENE_NORMAL", "connections": None, "object_events": objs,
         "warp_events": [], "coord_events": [], "bg_events": []}
    json.dump(m, open(f'{d}/map.json', 'w'), indent=2); open(f'{d}/map.json', 'a').write('\n')
    mg = json.load(open('data/maps/map_groups.json'))
    for grp, maps in mg.items():
        if isinstance(maps, list) and 'RematchArena' in maps and 'RematchDinner' not in maps: maps.append('RematchDinner')
    json.dump(mg, open('data/maps/map_groups.json', 'w'), indent=2); open('data/maps/map_groups.json', 'a').write('\n')

if __name__ == '__main__':
    write_tileset(); g = build_layout(N); write_map()
    if len(sys.argv) > 1:   # preview with the people marked
        from render import TS as TSet, render_blocks
        ts = TSet('gTileset_Building', 'gTileset_RestaurantHotel')
        render_blocks(ts, [c for r in g for c in r], len(g[0]), len(g), sys.argv[1],
                      marks=[(x, y, lid[:2], (255, 40, 40)) for lid, _, x, y, _ in PEOPLE])
    print('dinner: objects', len(PEOPLE), 'creator' if WITH_CREATOR else 'no creator', 'table', N, 'player seat', PLAYER_SEAT)
