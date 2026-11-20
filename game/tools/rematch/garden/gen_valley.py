# Garden v3: Six Island (unchanged) + an eastern valley with two raised terraces.
import sys, struct
sys.path.insert(0,'.')
from render import TS, layout, G, render_blocks
def loadL(lid):
    L=layout(lid); b=open(f"{G}/{L['blockdata_filepath']}",'rb').read()
    return L, struct.unpack(f'<{len(b)//2}H',b)
SL,SB=loadL('LAYOUT_SIX_ISLAND'); SW=SL['width']
W,H=72,30
COL=0x400; E3=0x3000
def mt(m,solid): return m|(COL if solid else E3)
g=[[0]*W for _ in range(H)]
for y in range(H):
    for x in range(SW): g[y][x]=SB[y*SW+x]
def put(x,y,m,solid=True): g[y][x]=mt(m,solid)
def grass(x,y): put(x,y,[[0x8,0x9],[0x10,0x11]][y%2][x%2],False)
def src(x,y): return SB[y*SW+x]
# --- base: mountain above, valley floor, fence + mountain below ---
for x in range(SW,W):
    for y in range(H):
        if y<=5: g[y][x]=src(23,y)
        elif y==6: put(x,y,0x79)                 # upper mountain's south face
        elif y<=20: grass(x,y)
        elif y==21: put(x,y,0xe6)                # fence along the lower mountain
        else: g[y][x]=src(23,y)
grass(23,20); put(23,21,0xe6)                     # tidy the old fence end so the fence runs continuously
for x in (24,25,26):                             # road from town fades into the valley
    g[12][x]=src(23,12); g[13][x]=src(23,13)
def terrace(x0,x1,y_front,stairs,floor):
    """Raised terrace against the upper mountain: floor x0+1..x1-1, rows 7..y_front-1,
    side walls at x0/x1, a cliff front at y_front with stone steps at stairs=(sx,sx+1)."""
    for y in range(7,y_front):
        put(x0,y,0x70); put(x1,y,0x75)
        for x in range(x0+1,x1): floor(x,y)
    put(x0,y_front,0x78); put(x1,y_front,0x7a)
    for x in range(x0+1,x1): put(x,y_front,0x79)
    put(stairs,y_front,0x91,False); put(stairs+1,y_front,0x89,False)
def tree(x,y):                                   # 2x2 pine: crown row y, trunk rows y+1..y+2
    put(x,y,0xe,False); put(x+1,y,0xf,False)
    put(x,y+1,0x1e); put(x+1,y+1,0x1f); put(x,y+2,0x26); put(x+1,y+2,0x27)
def sand(x,y): put(x,y,0x207 if y==7 else 0x349,False)
# --- KOGA: small grassy terrace, cave half-hidden behind a pine ---
terrace(24,31,11,25,grass)              # front edge lines up with the ledge under the Mart's trees
put(27,6,0xa9,False)                             # KOGA's cave mouth (door 27,6)
tree(28,7)                                       # pine screening the cave from the east
# --- a small wooden landing in the fence above the PC, so the cove in the top-left corner can be surfed
put(12,6,0x1bd,False); put(13,6,0x1bf,False)
for (x,y) in ((22,8),(23,8),(22,9),(23,9),(22,10),(23,10),(22,11),(23,11)):
    grass(x,y)                                   # a path beside the MART (pine + ledge removed) up to the strip behind it
# --- the road continues east (open end, for a bigger map later) ---
for x in range(27,W):
    g[12][x]=src(22,12); g[13][x]=src(22,13)
# --- BROCK: through a gap in the fence, steps down into a sunken rocky hollow in the
#     lower mountain; his cave mouth is in the cliff beside the steps ---
HX0,HX1=24,33                                   # hollow floor x range (inclusive)
grass(27,21); grass(28,21)                      # the gap in the fence
for x in range(HX0-1,HX1+2): put(x,22,0x79)     # cliff edge under the valley (faces the hollow)
put(HX0-1,22,0x78); put(HX1+1,22,0x7a)
put(27,22,0x91,False); put(28,22,0x89,False)    # steps down
for y in range(23,28):                          # hollow floor (dirt) with mountain walls
    put(HX0-1,y,0x75); put(HX1+1,y,0x70)
    for x in range(HX0,HX1+1): put(x,y,0x349,False)
for x in range(HX0-1,HX1+2): put(x,28,0x69)     # mountain's lip along the hollow's south side
put(HX0-1,28,0x68); put(HX1+1,28,0x6a)
for (x,y) in ((24,23),(33,27)): put(x,y,0xb7)       # just two rocks, in opposite corners
put(HX0-1,22,0xb2); put(HX1+1,22,0xb3); put(HX0-1,28,0xba); put(HX1+1,28,0xbb)   # corners blend into the mountain
# --- the old sandy terrace, kept as scenery (no cave behind it) ---
terrace(33,39,11,35,sand)                # same front line as KOGA's terrace; the road runs below both
# (no rocks left on the sandy terrace: the two fighters and their POKéMON train there)
# --- valley floor: MISTY's pond (organic shape, built the way Four Island builds its ponds:
#     each water tile picks its edge/corner piece from which neighbours are land) ---
POND_ROWS={15:range(30,33),16:range(29,34),17:range(29,35),18:range(29,35),19:range(31,34)}
def organic_pond(rows):
    wet=lambda x,y: y in rows and x in rows[y]
    for y,xs in rows.items():
        for x in xs:
            t,b,l,r=not wet(x,y-1),not wet(x,y+1),not wet(x-1,y),not wet(x+1,y)
            if t and l: m=0x1a0
            elif t and r: m=0x1a2
            elif b and l: m=0x1b0
            elif b and r: m=0x1b2
            elif t: m=0x1a1
            elif b: m=0x1b1
            elif l: m=0x1a8
            elif r: m=0x1aa
            else: m=0x1a9
            put(x,y,m)
def deep_pond(rows):
    wet=lambda x,y: y in rows and x in rows[y]
    for y,xs in rows.items():
        for x in xs:
            t,l,r=not wet(x,y-1),not wet(x-1,y),not wet(x+1,y)
            if t and l: m=0x1a5
            elif t and r: m=0x1a7
            elif t: m=0x1a6
            elif l: m=0x1ad
            elif r: m=0x1af
            elif not wet(x-1,y-1): m=0x1b4      # inner corners where the top edge steps
            elif not wet(x+1,y-1): m=0x1b3
            else: m=0x1ae
            put(x,y,m)
    for y,xs in rows.items():                    # the bank under the water casts the rim's shadow
        for x in xs:
            if not wet(x,y+1):
                put(x,y+1, 0x134 if wet(x+1,y+1) else 0x132 if wet(x-1,y+1) else 0x133, False)   # walkable bank
deep_pond(POND_ROWS)
tree(35,14)                                         # a pine right at the pond's east end
for (x,y) in ((35,19),(34,20),(35,20)): put(x,y,0xd,False)            # reeds on the south-east bank
for x in range(24,27):                                                  # tall grass, 3 wide x 4 tall, one tile left of MISTY
    for y in range(15,19): put(x,y,0xd,False)
for (x,y) in ((26,19),(27,20),(25,20),(38,19),(37,20),(38,20)): put(x,y,0x4,False)   # flowers in two clusters
# =================== eastern extension (x 40..69) ===================
# --- ERIKA's flower garden, south of the road (wooden fence, opening at the bottom) ---
def fence_box(x0,y0,x1,y1,gaps):
    for x in range(x0+1,x1): put(x,y0,0xe6); put(x,y1,0xe6)
    for y in range(y0,y1+1): put(x0,y,0xf0); put(x1,y,0xf1)
    for x in gaps: grass(x,y1)
# open garden, no fence: a flower bed between two fountains, each fountain ringed by flowers on grass
for y in range(14,20):
    for x in range(43,57): grass(x,y)
for y in range(15,19):
    for x in range(48,52): put(x,y,0x4 if (x+y)%2 else 0xd,False)
for (x,y) in ((43,15),(43,17),(47,15),(47,17),(44,19),(46,19),       # around the west fountain
              (52,15),(52,17),(56,15),(56,17),(53,19),(55,19),       # around the east fountain
              (49,19),(50,14)): put(x,y,0x4,False)
for y in range(14,20):                           # every free cell of the garden: leafy grass
    for x in range(43,57):
        if g[y][x]&0x3ff in (0x8,0x9,0x10,0x11): put(x,y,0xd,False)
# --- LT. SURGE's house, south of the road, with a white-fenced yard ---
def stamp_six(sx,sy,w,h,dx,dy):
    for j in range(h):
        for i in range(w): g[dy+j][dx+i]=SB[(sy+j)*SW+sx+i]
# --- the ELITE FOUR tower on a raised plaza at the east end ---
TL,TB=loadL('LAYOUT_SEVEN_ISLAND_TRAINER_TOWER'); TW=TL['width']
def stamp_t(sx,sy,w,h,dx,dy):
    for j in range(h):
        for i in range(w): g[dy+j][dx+i]=TB[(sy+j)*TW+sx+i]
stamp_t(55,0,7,2, 61,0); stamp_t(54,2,9,5, 60,2); stamp_t(57,7,3,2, 63,7)   # door at (64,7)
for x in range(58,72): put(x,11,0x79)            # the plaza's front edge
put(58,11,0x78); put(71,11,0x7a)
for y in range(7,11): put(58,y,0x70); put(71,y,0x75)   # side walls of the raised plaza
put(64,11,0x91,False); put(65,11,0x89,False)     # stairs up from the road
tree(60,8); tree(68,8)                           # pines flanking the approach
for (x,y) in ((62,10),(63,10),(62,9),(66,9),(66,10),(67,10)): put(x,y,0x4,False)
# --- decorations on the open ground ---
# the meadow east of the garden holds the two couples (x 61..65, rows 15..18): open grass around them,
# a loose ring of flowers, and leafy grass pushed out to the edges
for (x,y) in ((60,14),(66,14),(59,16),(67,16),(60,19),(66,19),(63,20)): put(x,y,0x4,False)
for y in range(14,21):                           # one leafy patch from ERIKA's garden to the couples, flowers in between
    for x in range(43,68):
        if g[y][x]&0x3ff in (0x8,0x9,0x10,0x11): put(x,y,0xd,False)
for (x,y) in ((41,15),(41,18)): put(x,y,0x4,False)
for (x,y) in ((47,18),): pass
# --- the east end closes with pines ---
def forest(x0,y0,x1,y1):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): put(x,y,[[0x1e,0x1f],[0x16,0x17]][(y-y0)%2][(x-x0)%2])
# --- the upper mountain ends after the sandy terrace; a pine forest takes over behind ---
for x in range(40,56):                           # the upper mountain runs on to x=55 (rows 2..11 there are
    for y in range(0,12): put(x,y,0x71)          #  replaced by the Power Plant block copied from Route 10)
def forest_rows(x0,x1,y0,y1):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            in_tower=(y<=1 and 61<=x<=67) or (2<=y<=6 and 60<=x<=68) or (y>=7 and 63<=x<=65)
            clearing=(y<=1 and x==60) or (2<=y<=6 and x==69)   # grass beside the tower instead of half trees
            if clearing: grass(x,y)
            elif not in_tower: put(x,y,[[0x1e,0x1f],[0x16,0x17]][(y+1)%2][x%2])   # row 5 (above the trunks) is a full tree body
forest_rows(60,71,0,5)
for x in list(range(70,72)):                     # tree trunks along the forest's edge
    if False: continue
    put(x,6,[0x24,0x25][x%2])
put(70,6,0x26)
grass(69,6); grass(68,2)
put(68,0,0x1e); put(69,0,0x1f); put(68,1,0x26); put(69,1,0x27)   # trees above the clearing: full body, then trunks
# --- the lower mountain ends after BROCK's hollow; grass runs down to a rocky bank and the sea ---
for y in range(22,30): put(39,y,0x75)            # mountain's east edge
put(39,22,0x6a)
CUT_TREE_X=68                                    # the one gap in the fence holds a small tree you can CUT
for x in range(40,W):
    put(x,21,0xe6)                               # the wooden fence runs on, all the way east
    put(x,22,0x1d6,False)                        # grass gives way to sand
    for y in (23,24): put(x,y,0x115,False)       # beach
    put(x,25,0x11d,False)                        # sand meets the water
    for y in range(26,30): put(x,y,0x12b)        # the sea
grass(CUT_TREE_X,21)
for y in range(25,30):                           # the beach turns south along the mountain: an L-shaped beach
    put(40,y,0x115,False); put(41,y,0x115,False); put(42,y,0x116,False)
put(42,25,0x115,False)
for (x,y) in ((45,27),(58,26),(64,28)):          # rocks in the sea (2x2)
    put(x,y,0x1cb); put(x+1,y,0x1cc); put(x,y+1,0x1d3); put(x+1,y+1,0x1d4)
for (x,y) in ((51,28),(67,26)):                  # small rocks
    put(x,y,0x110); put(x+1,y,0x111); put(x,y+1,0x118); put(x+1,y+1,0x119)
# --- tower base: grass instead of the cliff rock baked into its corner pieces (custom metatiles) ---
_T67=TS(SL['primary_tileset'],SL['secondary_tileset'])
CUSTOM={}; _cache={}
def custom(key,entries,attr):
    if key not in _cache:
        mid=0x280+(len(_T67.mts)-640)+len(CUSTOM); CUSTOM[mid]=(tuple(entries),attr); _cache[key]=mid
    return _cache[key]
CLIFF_BOTTOMS=({0x82,0x83,0x92,0x93},{0xa2,0xa3,0xb2,0xb3})
for y in range(0,9):                             # the tower stands in front of the forest now
    for x in range(60,69):
        v=g[y][x]; m=v&0x3ff; e=_T67.mts[m]
        if {t&0x3ff for t in e[:4]} in CLIFF_BOTTOMS and m>=0x280:
            g[y][x]=(v&~0x3ff)|custom(('grass',m),list(_T67.mts[0x8][:4])+list(e[4:]),_T67.attrs[m])
# --- LT. SURGE's building: Route 10's POWER PLANT, imported. Its metatiles live in Lavender Town's
#     tileset, so they're copied into ours: its 75 tiles go into free tile slots and its three own
#     palettes into the free palette slots 7, 11 and 12 (the shared base palettes need no copying). ---
PLANT_SRC=(0,33,16,10)                           # x, y, w, h on Route 10: the plant with the cliffs around it
PLANT_AT=(40,2)                                  # door ends up at (47,9), two rows of grass, then the road
PAL_MAP={8:7,10:11,11:12}
IMPORT_TILES={}; IMPORT_PALS={}
def import_plant():
    RL,RB=loadL('LAYOUT_ROUTE10'); RW=RL['width']
    lt=TS('gTileset_General','gTileset_LavenderTown')
    used=set()
    for row in g:
        for v in row:
            m=v&0x3ff
            if m<len(_T67.mts):
                for e in _T67.mts[m]: used.add(e&0x3ff)
    for mid,(entries,attr) in CUSTOM.items():
        for e in entries: used.add(e&0x3ff)
    free=[t for t in range(640,1024) if t not in used]
    tmap={}
    for sp,dp in PAL_MAP.items(): IMPORT_PALS[dp]=lt.pals[sp]
    sx,sy,w,h=PLANT_SRC; dx,dy=PLANT_AT
    for j in range(h):
        for i in range(w):
            v=RB[(sy+j)*RW+sx+i]; m=v&0x3ff
            entries=[]
            for e in lt.mts[m]:
                tid=e&0x3ff; pal=e>>12
                if tid>=640:
                    if tid not in tmap:
                        tmap[tid]=free.pop(0); IMPORT_TILES[tmap[tid]]=lt.tiles[tid]
                    tid=tmap[tid]
                entries.append(tid|(e&0x0c00)|(PAL_MAP.get(pal,pal)<<12))
            g[dy+j][dx+i]=(v&~0x3ff)|custom(('plant',m),entries,lt.attrs[m])
import_plant()
_RL,_RB=loadL('LAYOUT_ROUTE10')                  # Route 10's sandy path in front of the plant -> grass
for j in range(PLANT_SRC[3]):
    for i in range(PLANT_SRC[2]):
        if (_RB[(PLANT_SRC[1]+j)*_RL['width']+PLANT_SRC[0]+i]&0x3ff) in (0xd0,0xd1,0xd8,0xd9,0xfe):
            grass(PLANT_AT[0]+i,PLANT_AT[1]+j)
# left: instead of Route 10's 1-tile cliff column, our mountain steps back to the pocket's cliff
for y in range(0,4): put(40,y,0x71)
put(40,4,0x72); put(40,5,0x72); put(40,6,0x7a)   # east wall from the 0x79 face set
for y in range(7,12): grass(40,y)
grass(41,11); grass(41,9); grass(42,9)            # Route 10's ledge stub beside the left pylon
# the mountain continues over x 56..59 and ends there with a proper east edge; the ridge is its spur
for x in range(56,60):
    for y in range(0,6): put(x,y,0x71)
    put(x,6,0x79)
for y in range(0,6): put(59,y,0x75)
put(59,6,0x7a)
for y in range(0,6): put(55,y,0x71)          # no spur wall inside the mountain itself
put(56,6,0x79); put(55,6,0xb3)                 # where the mountain's face meets the spur's east wall
# right: the ridge ends in a proper rounded base one row above the road
put(53,10,0x78); put(54,10,0x79); put(55,10,0x7a)
for x in (53,54,55): grass(x,11)
# the spur is one level with the mountain: solid rock, a west wall, a real east wall
for y in range(3,10): put(54,y,0x71)
for y in range(7,10): put(55,y,0x75)
# one consistent cliff set (east wall 0x75 / west wall 0x73 / face 0x7c / corners 0x7b, 0x7d / inner 0xb2, 0xb3)
for x in range(56,59): put(x,6,0x7c)
put(59,6,0x7d); put(55,6,0xb2)
for y in range(4,10): put(53,y,0x73)
put(53,3,0xb3)
put(53,10,0x7b); put(54,10,0x7c); put(55,10,0x7d)
for y in range(0,11): put(71,y,0x72)          # plaza east wall (0x79 set), running all the way up: no trees east of the tower
for y in range(0,7):
    for x in (69,70): grass(x,y)
for y in (0,1): grass(68,y)
# the tower, its pines and flowers move one tile right: centred between the mountain and the east wall
_tower={(x,y):g[y][x] for y in range(0,9) for x in range(60,69)
        if (y<=1 and 61<=x<=67) or (2<=y<=6 and 60<=x<=68) or (y>=7 and 63<=x<=65)}
for y in range(0,11):
    for x in range(60,71): grass(x,y)
for (x,y),v in _tower.items(): g[y][x+1]=v       # door now at (65,7)
put(64,11,0x79); put(65,11,0x91,False); put(66,11,0x89,False)   # stairs follow the door
tree(61,8); tree(69,8)
for (x,y) in ((63,10),(64,10),(63,9),(67,9),(67,10),(68,10)): put(x,y,0x4,False)
def import_fountain(at_list):
    CL,CB=loadL('LAYOUT_CELADON_CITY'); CW=CL['width']
    ct=TS('gTileset_General','gTileset_CeladonCity')
    used=set(IMPORT_TILES)
    for row in g:
        for v in row:
            m=v&0x3ff
            if m<len(_T67.mts):
                for e in _T67.mts[m]: used.add(e&0x3ff)
    for mid,(entries,attr) in CUSTOM.items():
        for e in entries: used.add(e&0x3ff)
    free=[t for t in range(640,1024) if t not in used]
    pals=list(_T67.pals)
    for k,p in IMPORT_PALS.items(): pals[k]=p
    src=ct.pals[8]
    srcidx=set()
    for m in range(0x2cd,0x2d9):
        for e in ct.mts[m]:
            if e>>12==8:
                for row in ct.tiles[e&0x3ff]: srcidx.update(row)
    def d(a,b): return sum((x-y)**2 for x,y in zip(a,b))
    best=None
    for k in range(13):
        cmap={i:(0 if i==0 else min(range(1,16),key=lambda j:d(src[i],pals[k][j]))) for i in srcidx}
        err=sum(d(src[i],pals[k][cmap[i]]) for i in srcidx if i)
        if best is None or err<best[0]: best=(err,k,cmap)
    _,PK,cmap=best; print('fountain palette ->',PK)
    tmap={}
    for (dx,dy) in at_list:
        for j in range(4):
            for i in range(3):
                v=CB[(18+j)*CW+12+i]; m=v&0x3ff
                entries=[]
                for e in ct.mts[m]:
                    tid=e&0x3ff; pal=e>>12
                    if tid>=640:
                        if tid not in tmap:
                            tmap[tid]=free.pop(0)
                            pix=ct.tiles[tid]
                            IMPORT_TILES[tmap[tid]]=[[cmap.get(c,c) if pal==8 else c for c in row] for row in pix]
                        tid=tmap[tid]
                    entries.append(tid|(e&0x0c00)|((PK if pal==8 else pal)<<12))
                g[dy+j][dx+i]=(v&~0x3ff)|custom(('fountain',m),entries,ct.attrs[m])
import_fountain([(44,15),(53,15)])
# no light road: every path tile becomes plain grass
PATH={0xbd,0xbe,0xc3,0xc4,0xc5,0xc6,0xc7,0xcb,0xcc,0xce,0xcf}
for y in range(H):
    for x in range(W):
        if g[y][x]&0x3ff in PATH: grass(x,y)
# the east edge: the land ends in a rocky shore. Below the plaza, the last two columns are sea; the column
# against the land is water with a rock edge on its left (0x12a), with a rock corner/edge under the plaza
# cliff (0x122, 0x123). These are the General tileset's shore pieces, drawn in the same water as the open
# sea (0x12b) next to them; the Sevii shore pieces use a different water and looked like a different current. A short stand of pines sits
# inland of it, stopping above the gate in the fence so the gate stays reachable.
for y in range(12,22):
    put(70,y,0x12a); put(71,y,0x12b)
put(70,12,0x122); put(71,12,0x123)
for x in (68,69):
    put(x,12,[0xe,0xf][x%2],False)
    for y in range(13,16): put(x,y,[[0x1e,0x1f],[0x16,0x17]][(y-13)%2][x%2])
    put(x,16,[0x26,0x27][x%2])
    for y in range(17,21): grass(x,y)
# the beach ends in sand edges against the water (sand with water above-right / right / below-right)
put(70,22,0x10e,False); put(70,23,0x116,False); put(70,24,0x116,False); put(70,25,0x11e,False)
for y in range(22,26): put(71,y,0x12b)
# three more rows of sea at the bottom, so the ferry can dock below the café (row 29 continues straight down)
ROCKS=set(range(0x1cb,0x1d5))|{0x110,0x111,0x118,0x119}
for _ in range(3): g.append([(v&~0x3ff)|0x12b if v&0x3ff in ROCKS else v for v in g[29]])   # no half-rocks in the new rows
H=len(g)
# the land ends properly at the bottom edge of the map: the lower mountain gets its south cliff face,
# the L-shaped beach its sand edge (water below)
for x in range(16,40): g[H-1][x]=mt(0x7c,True)
g[H-1][16]=mt(0x7b,True); g[H-1][39]=mt(0x7d,True)
g[H-1][40]=mt(0x11d,False); g[H-1][41]=mt(0x11d,False); g[H-1][42]=mt(0x11e,False)
# --- MAP EDGES: the border outside the map is solid rock (build_garden.py), so wherever water reaches the edge
# of the map it gets a rocky shore against that rock instead of running into invisible walls.
SEA_IDS={0x12b,0x273,0x276,0x26f,0x27f,0x274,0x26b}
def is_sea(x,y): return g[y][x]&0x3ff in SEA_IDS
for y in range(len(g)):                          # right edge: water with a rock edge on its right
    if g[y][W-1]&0x3ff in (0x12b,): put(W-1,y,0x12c)
put(W-1,12+0,0x124)                              # top-right corner under the plaza cliff (row 12 is the strip's top)
for x in range(W):                               # bottom edge: a rock lip below the water
    if is_sea(x,len(g)-1) or g[len(g)-1][x]&0x3ff in (0x12c,0x272): put(x,len(g)-1,0x69)
# SIX ISLAND's water (General tileset 0x26x-0x27x) is MB_FAST_WATER: "The current is much too fast!", so it
# can't be surfed. The garden uses copies of those metatiles (same art) with MB_OCEAN_WATER (0x15) instead.
for y in range(len(g)):
    for x in range(W):
        m=g[y][x]&0x3ff
        if m<0x280 and _T67.attrs[m]&0x1ff==0x11:
            g[y][x]=(g[y][x]&~0x3ff)|custom(('calm_sea',m),list(_T67.mts[m]),(_T67.attrs[m]&~0x1ff)|0x15)
# --- 7 more rows at the top (TOP): the mountains run on, the tower keeps rising past the top of the screen, and
# the cove and the grass strips get cliff faces above them. Everything else shifts down by TOP rows.
TOP=5                                            # (cropped to the approved framing: was 7)
tower_rows=[g[0][62:69], g[1][62:69]]   # the tower spans x 62..68            # the tower's two alternating window rows (row 0 = A, row 1 = B)
new=[[mt(0x71,True) for _ in range(W)] for _ in range(TOP)]
for j in range(TOP):
    r=new[j]
    r[59]=mt(0x75,True); r[71]=mt(0x72,True)     # the mountain's east wall and the plaza wall continue up
    r[62:69]=tower_rows[(TOP-j)%2]               # B right above row 0 (A), alternating upwards
for x in list(range(0,16))+[60,61,69,70]:        # cliff faces above the cove and above the grass strips
    new[TOP-1][x]=mt(0x79,True)
new[TOP-1][0]=mt(0x79,True)
g[0:0]=new
H=len(g)
OBJECTS_SHIFT=TOP
# --- OPEN OCEAN to the east and south of the bay: the map grows by R columns and D rows of real, surfable sea.
# The outer band is a strong current (same water art) that carries you back - FireRed's way of ending the sea -
# wide enough that from anywhere you can reach, the screen never shows past the map's edge. The world beyond
# the edge (the border) is open sea again.
R,D=6,5                                          # (cropped to the approved framing: was 11, 9)
BAND_X,BAND_Y,BAND_TOP=8,6,6                    # current band widths: right, bottom, top (above the east sea)
SEA=0x12b
for y in range(12+TOP,len(g)):                    # undo the rocky shore on the old right edge / bottom of the bay
    if g[y][W-1]&0x3ff==0x12c: put(W-1,y,SEA)
put(W-1,12+TOP,0x123)
for x in range(43,W):
    if g[len(g)-1][x]&0x3ff==0x69: put(x,len(g)-1,SEA)
for x in range(16,40): g[len(g)-1][x]=g[len(g)-2][x]   # the lower mountain no longer ends here: it runs on below
oldW,oldH=W,len(g)
for row in g: row.extend([0]*R)
W=oldW+R
for y in range(oldH):                             # east of the plaza cliff: sea, with a rocky edge along the cliff
    for x in range(oldW,W): put(x,y,SEA)
    if y<12+TOP: put(oldW,y,0x12a)
for y in range(oldH,oldH+D):
    g.append([0]*W)
    for x in range(W):
        if x<39: put(x,y,0x71)                   # rock below the harbor and the lower mountain
        elif x==39: put(x,y,0x75)                # the mountain's east wall runs down into the sea
        elif x==40: put(x,y,0x12a)               # water against that wall
        else: put(x,y,SEA)
H=len(g)
def compact_custom():
    # drop custom metatiles that ended up unused (overwritten later) and renumber the rest, so the tileset
    # stays within its 384 secondary metatiles
    global CUSTOM
    used=sorted({c&0x3ff for row in g for c in row} & set(CUSTOM))
    base=0x280+(len(_T67.mts)-640)
    remap={old:base+i for i,old in enumerate(used)}
    for row in g:
        for i,c in enumerate(row):
            if c&0x3ff in remap: row[i]=(c&~0x3ff)|remap[c&0x3ff]
    CUSTOM={remap[o]:CUSTOM[o] for o in used}
    for k in list(_cache):
        if _cache[k] in remap: _cache[k]=remap[_cache[k]]
        else: del _cache[k]
compact_custom()
# --- open sea to the WEST too: LEFT columns prepended, the cove and the harbor flow into it (their rocky left
# shore is undone), the forest becomes a coast. Everything shifts right by LEFT.
LEFT=0                                           # (cropped: the open sea is just beyond the map edge; was 7)
DEEP=0x276                                         # Six Island's water art, so the cove/harbor continue seamlessly
def is_water_cell(c):
    m=c&0x3ff
    if m in CUSTOM: return (CUSTOM[m][1]&0x1ff) in (0x10,0x11,0x12,0x15)
    return m<len(_T67.attrs) and (_T67.attrs[m]&0x1ff) in (0x10,0x11,0x12,0x15)
for y in range(len(g)):                            # undo the old left rocky shore
    m=g[y][0]&0x3ff
    if m in (0x272,): put(0,y,DEEP)
    if m==0x26a: put(0,y,0x26b)
for y in range(len(g)):
    left=[0]*LEFT
    g[y][0:0]=left
W+=LEFT
for y in range(H):
    for x in range(LEFT):
        if y<6: put(x,y,0x71)
        elif y==6: put(x,y,0x79)                   # the cliff above the cove runs on west
        else: put(x,y,DEEP)
    if y>=33+TOP: put(LEFT,y,0x70)                     # the rock below the harbor faces west into the sea
put(LEFT,32+TOP,0x68)                                  # the harbor's bottom lip starts at its west end
# --- the current band: every water tile within a screen of the map edge pushes you back inward (same art as
# the water it replaces), so you never see past the edge. Screen: 7 tiles left/right, 4 up, 5 down of you.
EDGE={'W':7,'E':5,'N':4,'S':3}                     # east/south: 2 tiles narrower so more sea can be surfed
DIRS={'W':0x50,'E':0x51,'N':0x53,'S':0x52}         # band on the west edge flows east, etc.
for y in range(H):
    for x in range(W):
        c=g[y][x]
        if not is_water_cell(c): continue
        d={'W':x,'E':W-1-x,'N':y,'S':H-1-y}
        side=min((k for k in d if d[k]<EDGE[k]), key=lambda k:d[k], default=None)
        if side is None: continue
        m=c&0x3ff
        entries=list(CUSTOM[m][0]) if m in CUSTOM else list(_T67.mts[m])
        attr=CUSTOM[m][1] if m in CUSTOM else _T67.attrs[m]
        g[y][x]=(c&~0x3ff)|custom(('current',DIRS[side],tuple(entries)),entries,(attr&~0x1ff)|DIRS[side])
blocks=[c for row in g for c in row]
# --- BROCK has no cave: he and his POKéMON hang out in the sunken rocky hollow ---
# indoors (step 4): VENOMOTH with KOGA, RAICHU + VOLTORB with LT. SURGE, DRAGONITE with LANCE
OBJECTS=[  # (local id, graphics, x, y, facing)
 ('RIVAL','BLUE',11,18,'FACE_DOWN'),               # the rival, up the path past the stairs above the café's back door
 ('MISTY','MISTY',28,17,'FACE_RIGHT'),         # on the left bank, facing the water
 ('PSYDUCK','PSYDUCK',28,15,'FACE_RIGHT'),      # two tiles above her
 ('STARMIE','REMATCH_STARMIE',31,16,'FACE_LEFT'),   # swimming
 ('STARYU','REMATCH_STARYU',32,18,'FACE_LEFT'),
 ('ERIKA','ERIKA',50,17,'FACE_DOWN'),
 ('VILEPLUME','REMATCH_VILEPLUME',48,16,'FACE_RIGHT'),
 ('ODDISH','REMATCH_ODDISH',51,18,'FACE_LEFT'),
 ('TANGELA','REMATCH_TANGELA',46,19,'FACE_RIGHT'),   # ERIKA's third POKéMON, in the leafy bed
 ('MR_MIME','REMATCH_MR_MIME',18,18,'FACE_DOWN'),   # outside SABRINA's door
 ('CUT_TREE','CUT_TREE',68,21,'FACE_DOWN'),
 ('FERRY','SEAGALLOP',11,31,'FACE_DOWN'),
 ('FISHING_GURU','FISHER',12,6,'FACE_UP'),         # the FISHING GURU (OLD ROD), fishing off the wooden landing
 ('FISHING_BROTHER','FISHER',47,25,'FACE_DOWN'),   # his brother (GOOD ROD), on the beach - a dad now, not fishing
 ('TUBER_BOY','TUBER_M_WATER',55,28,'FACE_LEFT'),  # two kids floating in swim rings in the bay
 ('TUBER_GIRL','TUBER_F',61,30,'FACE_UP'),
 ('BIKE_SHOP','MAN',65,24,'FACE_RIGHT'),          # the CERULEAN bike shop owner, just inside the gate ...
 ('BIKER','BIKER',60,23,'FACE_LEFT'),             # ... and a CYCLING ROAD biker, one row further from the sea
 ('LEX','COOLTRAINER_M',62,16,'FACE_RIGHT'),        # COOL COUPLE LEX & NYA (Sevault Canyon), in the meadow east of the garden ...
 ('NYA','COOLTRAINER_F',62,17,'FACE_RIGHT'),
 ('JED','MAN',64,16,'FACE_LEFT'),                    # ... chatting with YOUNG COUPLE LEA & JED (Route 16)
 ('LEA','BEAUTY',64,17,'FACE_LEFT'),
 ('TAUROS','REMATCH_TAUROS',61,15,'FACE_RIGHT'),   # each POKéMON on the corner behind its trainer, facing the same way
 ('MILTANK','REMATCH_MILTANK',61,18,'FACE_RIGHT'),
 ('RAPIDASH','REMATCH_RAPIDASH',65,15,'FACE_LEFT'),
 ('NINETALES','REMATCH_NINETALES',65,18,'FACE_LEFT'),
 ('MEGA_PUNCH','BLACK_BELT',34,8,'FACE_RIGHT'),   # the MEGA PUNCH / MEGA KICK tutors from Route 4, squared off
 ('MEGA_KICK','BLACK_BELT',38,8,'FACE_LEFT'),     #  three tiles apart on the sandy terrace
 ('HITMONCHAN','REMATCH_HITMONCHAN',34,9,'FACE_RIGHT'),  # below the MEGA PUNCH tutor
 ('HITMONLEE','REMATCH_HITMONLEE',38,9,'FACE_LEFT'),     # below the MEGA KICK tutor
 ('BROCK','BROCK',29,24,'FACE_RIGHT'),        # facing his POKéMON, two tiles away
 ('ONIX','REMATCH_ONIX',31,24,'FACE_LEFT'),
 ('GEODUDE','REMATCH_GEODUDE',31,25,'FACE_LEFT'),  # right below ONIX
]
OBJECTS=[(o[0],o[1],o[2]+LEFT,o[3]+TOP,o[4]) for o in OBJECTS]   # coordinates above are from before the TOP rows
if __name__=='__main__':
    ts=TS(SL['primary_tileset'],SL['secondary_tileset'])
    for mid,(entries,attr) in CUSTOM.items():
        while len(ts.mts)<=mid: ts.mts.append((0,)*8); ts.attrs.append(0)
        ts.mts[mid]=entries; ts.attrs[mid]=attr
    for tid,pix in IMPORT_TILES.items():
        while len(ts.tiles)<=tid: ts.tiles.append([[0]*8]*8)
        ts.tiles[tid]=pix
    for slot,pal in IMPORT_PALS.items(): ts.pals[slot]=pal
    render_blocks(ts,blocks,W,H,'valley.png')
