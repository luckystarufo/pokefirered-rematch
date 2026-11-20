import sys
from PIL import Image, ImageDraw
import os
G=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *(['..']*2)))  # game/
red=Image.open(G+'/graphics/trainers/back_pics/red_back_pic.png'); rp=red.load()
K=(0,0,0); SL=(255,230,180); SS=(222,189,156)
HL=(240,184,100); HM=(212,140,56); HD=(160,96,38); HX=(110,62,26)
GL=(116,128,142); GM=(80,92,108); GD=(52,62,78)
W=H=64
img=[[None]*W for _ in range(H)]
def opaque(x,y): return 0<=x<W and 0<=y<H and rp[x,y]!=0
def edge(x,y): return any(not opaque(x+dx,y+dy) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
torso=Image.new('L',(W,H),0); ImageDraw.Draw(torso).polygon([(23,46),(29,43),(41,43),(47,46),(49,51),(47,57),(42,63),(15,63),(17,53)],fill=255); tk=torso.load()
HAIR=set()
for y in range(H):
    for x in range(W):
        i=rp[x,y]
        if i==0: continue
        if y<=40:
            if y in (27,28,29,30) and x>=51: continue      # the cap's brim sticking past the face: gone
            if y>=31 and x>=46 and i in (4,8): img[y][x]=SS; continue   # ear details stay skin-toned
            if i in (2,3): img[y][x]=SL if i==2 else SS
            elif i==15 and (edge(x,y) or y>=31): img[y][x]=K
            elif y>=31 and i==9: img[y][x]=SL
            else: img[y][x]=HM; HAIR.add((x,y))
        else:
            if i in (2,3): img[y][x]=SL if i==2 else SS
            elif i in (5,6): img[y][x]=GM if i==5 else GD
            elif tk[x,y]: img[y][x]=GM
# small spikes sweeping up/back, plus two forward over the forehead
def spike(a,b,t):
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon([a,b,t],fill=255); mp=m.load()
    for y in range(H):
        for x in range(W):
            if mp[x,y] and img[y][x] in (None,K): img[y][x]=HM; HAIR.add((x,y))
for a,b,t in [((35,17),(40,16),(33,12)),((40,16),(45,16),(41,11)),((45,16),(49,18),(48,12)),((49,18),(52,21),(54,16)),
              ((31,19),(35,17),(28,14)),((29,22),(31,19),(24,18)),((29,26),(29,22),(24,24)),((27,29),(29,26),(23,29)),((49,26),(50,29),(54,27))]:
    spike(a,b,t)
# shading: light from the upper right, darker toward the back and the nape; streaks sweep back
for (x,y) in HAIR:
    v=(x-40)*0.6-(y-20)*1.0
    c=HL if v>5 else HM if v>-6 else HD
    if y>=31: c=HD if (x+y)%5 else HX
    img[y][x]=c
# a few strands sweeping back
d=ImageDraw.Draw(Image.new('L',(1,1)))
def line(x0,y0,x1,y1):
    n=max(abs(x1-x0),abs(y1-y0))
    for k in range(n+1):
        x=round(x0+(x1-x0)*k/n); y=round(y0+(y1-y0)*k/n)
        if (x,y) in HAIR and img[y][x]!=HX: img[y][x]=HD
line(46,14,37,23); line(51,19,41,27); line(41,13,33,20); line(48,23,43,28)
# shirt shading
for y in range(41,H):
    for x in range(W):
        if img[y][x]==GM:
            if x<20+(y-50)//2 or y>60: img[y][x]=GD
            elif y<47: img[y][x]=GL
for y in range(48,57):
    x=33-(y-48)//2
    if img[y][x] in (GM,GL): img[y][x]=GD
# the eye: a clear dark eye with a white glint, and a brow above it
EY=(40,32,56); WH=(255,255,255)
for (x,y),c in {(48,31):EY,(48,32):EY,(48,33):EY,(49,32):EY,(47,32):WH,(47,31):SL,(47,33):SS,(47,30):HD,(48,30):HD,(49,30):HD,(49,31):SS,(49,33):SS}.items():
    img[y][x]=c
# decoration on the back: a small POKé BALL emblem and a lighter collar band
R1=(232,72,64); R2=(176,48,48); BW=(240,240,248)
ball=['..KKK..','.KrrrK.','KrrrrrK','KKKwKKK','KwwwwwK','.KwwwK.','..KKK..']
for dy,row in enumerate(ball):
    for dx,ch in enumerate(row):
        if ch!='.': img[46+dy][30+dx]={'K':K,'r':R1,'w':BW}[ch]
img[47][32]=(255,170,160)
for x in range(29,42):
    if img[43][x] in (GM,GL,GD): img[43][x]=(150,160,172)
out=[r[:] for r in img]
for y in range(H):
    for x in range(W):
        if img[y][x] is None:
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                xx,yy=x+dx,y+dy
                if 0<=xx<W and 0<=yy<H and img[yy][xx] not in (None,K): out[y][x]=K; break
img=out
im=Image.new('RGBA',(W,H),(0,0,0,0)); p=im.load()
for y in range(H):
    for x in range(W):
        if img[y][x]: p[x,y]=img[y][x]+(255,)
im.save(sys.argv[1])
