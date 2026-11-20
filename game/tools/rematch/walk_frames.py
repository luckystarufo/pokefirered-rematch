# Rematch: make FireRed-style walking frames (used for MOM, BROCK, SABRINA, who never walked in vanilla).
# Usage: python3 tools/rematch/walk_frames.py <3-frame sheet> <9-frame output>
# Make FireRed-style walking frames from the 3 standing frames (down, up, left) of a 16x32 NPC sheet.
# Like the game's own walk cycles: the body bobs up 1 pixel while one foot stays planted (looks like a step).
import sys
from PIL import Image
def frames(im):
    return [[[im.getpixel((f*16+x, y)) for x in range(16)] for y in range(32)] for f in range(3)]
def step(fr, planted):           # planted: which columns keep their feet down ('left' / 'right')
    out = [[0]*16 for _ in range(32)]
    for y in range(31):          # bob up 1px
        out[y] = fr[y+1][:]
    LEG = 25                     # rows from here down are legs/feet
    for y in range(LEG, 32):
        for x in range(16):
            mine = (x < 8) if planted == 'left' else (x >= 8)
            if mine:
                out[y][x] = fr[y][x] if y < 32 else 0
    # tidy: a planted foot keeps its outline row; the lifted foot's last row is empty already
    return out
def build(src):
    im = Image.open(src); f = frames(im)
    d, u, l = f
    seq = [d, u, l, step(d, 'left'), step(d, 'right'), step(u, 'left'), step(u, 'right'), step(l, 'left'), step(l, 'right')]
    out = Image.new('P', (16*9, 32), 0); out.putpalette(im.getpalette())
    for k, fr in enumerate(seq):
        for y in range(32):
            for x in range(16): out.putpixel((k*16+x, y), fr[y][x])
    return out
if __name__ == '__main__':
    build(sys.argv[1]).save(sys.argv[2])
