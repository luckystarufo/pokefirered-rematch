#!/usr/bin/env python3
"""Rematch: build overworld sprites for Pokémon that FireRed has no walking sprite for.

FireRed only ships overworld sprites for ~30 Pokémon. Every species does have a
32x32 two-frame menu icon (graphics/pokemon/<name>/icon.png), drawn in the same
pixel style. This script turns those icons into overworld sprites:

  * colors are remapped onto whichever of the four shared NPC palettes fits best
    (FireRed keeps those 4 palettes loaded on every map; a sprite with its own
    palette could only use the single "special" slot, which would clash when
    several Pokémon are on screen),
  * the result goes to graphics/object_events/pics/pokemon/rematch/<name>.png
    (normal build rules turn it into .4bpp),
  * C tables go to src/data/object_events/rematch_mon_sprites*.h and the
    constants to include/constants/rematch_object_events.h.

Run it again after changing SPECIES below:  python3 tools/rematch/make_mon_sprites.py
(from game/). Inputs are the decomp's own graphics; nothing is ripped from a ROM.
"""
import os, re
from PIL import Image

SPECIES = ["arcanine", "onix", "geodude", "starmie", "staryu", "raichu",
           "vileplume", "tangela", "oddish", "weezing", "venomoth", "alakazam",
           "mr_mime", "gengar", "dragonite", "cloyster", "hitmonlee", "blastoise", "lapras",
           "miltank", "tauros", "rapidash", "ninetales", "hitmonchan", "muk"]
# Palette picked by eye where the automatic choice looked wrong (index into NPC_PALS).
PALETTE_OVERRIDE = {"gengar": 0, "venomoth": 0, "oddish": 2, "blastoise": 1, "lapras": 1, "miltank": 1}
FIRST_ID = 152  # first free OBJ_EVENT_GFX id after vanilla (NUM_OBJ_EVENT_GFX)

NPC_PALS = [("NPC_BLUE", "PALSLOT_NPC_1", "npc_blue"), ("NPC_PINK", "PALSLOT_NPC_2", "npc_pink"),
            ("NPC_GREEN", "PALSLOT_NPC_3", "npc_green"), ("NPC_WHITE", "PALSLOT_NPC_4", "npc_white")]

def read_jasc(path):
    lines = open(path).read().split("\n")
    return [tuple(int(v) for v in l.split()) for l in lines[3:19]]

def camel(name):
    return "".join(p.capitalize() for p in name.split("_"))

icon_src = open("src/pokemon_icon.c").read()
pal_idx = {m.group(1).lower(): int(m.group(2))
           for m in re.finditer(r"\[SPECIES_([A-Z0-9_]+)\]\s*=\s*(\d)", icon_src)}
icon_pals = [read_jasc(f"graphics/pokemon/icon_palettes/icon_palette_{i}.pal") for i in range(3)]
npc_pals = [read_jasc(f"graphics/object_events/palettes/{p[2]}.pal") for p in NPC_PALS]

def nearest(c, pal):
    best = min(range(1, 16), key=lambda i: sum((a - b) ** 2 for a, b in zip(c, pal[i])))
    return best, sum((a - b) ** 2 for a, b in zip(c, pal[best]))

os.makedirs("graphics/object_events/pics/pokemon/rematch", exist_ok=True)
consts, decls, entries, body = [], [], [], []
for n, name in enumerate(SPECIES):
    icon = Image.open(f"graphics/pokemon/{name}/icon.png")
    src_pal = icon_pals[pal_idx[name]]
    px = list(icon.getdata())
    used = sorted(set(px) - {0})
    # Pick the NPC palette with the smallest total color error.
    scores = []
    for p, pal in enumerate(npc_pals):
        mapping = {i: nearest(src_pal[i], pal) for i in used}
        scores.append((sum(e for _, e in mapping.values()), p, {i: m for i, (m, _) in mapping.items()}))
    _, p, mapping = min(scores)
    if name in PALETTE_OVERRIDE:
        p = PALETTE_OVERRIDE[name]
        mapping = {i: nearest(src_pal[i], npc_pals[p])[0] for i in used}
    out = Image.new("P", icon.size)
    flat = []
    for c in npc_pals[p]:
        flat += list(c)
    out.putpalette(flat + [0] * (768 - len(flat)))
    out.putdata([0 if v == 0 else mapping[v] for v in px])
    out.save(f"graphics/object_events/pics/pokemon/rematch/{name}.png")

    C = camel(name)
    const = f"OBJ_EVENT_GFX_REMATCH_{name.upper()}"
    consts.append(f"#define {const} {FIRST_ID + n}")
    decls.append(f"const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_Rematch{C};")
    entries.append(f"    [{const}] = &gObjectEventGraphicsInfo_Rematch{C},")
    tag, slot, _ = NPC_PALS[p]
    frames = "\n".join(f"    overworld_frame(gObjectEventPic_Rematch{C}, 4, 4, {f})," for f in (0, 0, 0, 1, 0, 1, 1, 0, 1))
    body.append(f"""const u16 gObjectEventPic_Rematch{C}[] = INCBIN_U16("graphics/object_events/pics/pokemon/rematch/{name}.4bpp");
static const struct SpriteFrameImage sPicTable_Rematch{C}[] = {{
{frames}
}};
const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_Rematch{C} = {{
    .tileTag = TAG_NONE,
    .paletteTag = OBJ_EVENT_PAL_TAG_{tag},
    .reflectionPaletteTag = OBJ_EVENT_PAL_TAG_NONE,
    .size = 512,
    .width = 32,
    .height = 32,
    .paletteSlot = {slot},
    .shadowSize = SHADOW_SIZE_M,
    .inanimate = FALSE,
    .disableReflectionPaletteLoad = FALSE,
    .tracks = TRACKS_FOOT,
    .oam = &gObjectEventBaseOam_32x32,
    .subspriteTables = gObjectEventSpriteOamTables_32x32,
    .anims = sAnimTable_Standard,
    .images = sPicTable_Rematch{C},
    .affineAnims = gDummySpriteAffineAnimTable,
}};
""")
    print(f"{name:10s} -> {tag}")

hdr = "// Generated by tools/rematch/make_mon_sprites.py. Do not edit.\n"
open("include/constants/rematch_object_events.h", "w").write(
    hdr + "#ifndef GUARD_CONSTANTS_REMATCH_OBJECT_EVENTS_H\n#define GUARD_CONSTANTS_REMATCH_OBJECT_EVENTS_H\n\n"
    + "\n".join(consts) + f"\n\n#define NUM_REMATCH_OBJ_EVENT_GFX {len(SPECIES)}\n\n#endif\n")
open("src/data/object_events/rematch_mon_sprites_decls.h", "w").write(hdr + "\n".join(decls) + "\n")
open("src/data/object_events/rematch_mon_sprites_pointers.h", "w").write(hdr + "\n".join(entries) + "\n")
open("src/data/object_events/rematch_mon_sprites.h", "w").write(hdr + "\n".join(body))
