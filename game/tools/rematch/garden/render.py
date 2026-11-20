# Render a pokefirered layout (or a metatile sheet) to PNG.
import json, struct, sys, os
from PIL import Image
import os
G=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *(['..']*3)))  # game/
def tsdir(sym):
    # gTileset_PokemonCenter -> data/tilesets/secondary/pokemon_center
    import re
    name=re.sub(r'(?<!^)(?=[A-Z][a-z]|(?<=[a-z])[0-9])','_',sym[len('gTileset_'):]).lower()
    for k in ('primary','secondary'):
        p=f'{G}/data/tilesets/{k}/{name}'
        if os.path.isdir(p): return p
    raise SystemExit('no dir for '+sym+' '+name)
def loadpal(d):
    pals=[]
    for i in range(16):
        f=f'{d}/palettes/{i:02}.pal'
        lines=open(f).read().split('\n')[3:19]
        pals.append([tuple(map(int,l.split())) for l in lines])
    return pals
def loadtiles(d):
    im=Image.open(f'{d}/tiles.png')
    w,h=im.size; px=im.load(); tiles=[]
    for ty in range(h//8):
        for tx in range(w//8):
            tiles.append([[px[tx*8+x,ty*8+y] for x in range(8)] for y in range(8)])
    return tiles
class TS:
    def __init__(s,p,sec):
        pd,sd=tsdir(p),tsdir(sec)
        pp,sp=loadpal(pd),loadpal(sd)
        s.pals=pp[:7]+sp[7:]
        s.tiles=loadtiles(pd); s.tiles+= [[[0]*8]*8]*(640-len(s.tiles)); s.tiles+=loadtiles(sd)
        def mt(d):
            b=open(f'{d}/metatiles.bin','rb').read()
            return [struct.unpack('<8H',b[i:i+16]) for i in range(0,len(b),16)]
        def at(d):
            b=open(f'{d}/metatile_attributes.bin','rb').read()
            return [struct.unpack('<I',b[i:i+4])[0] for i in range(0,len(b),4)]
        m=mt(pd); s.npri=len(m); s.mts=m+[(0,)*8]*(640-len(m))+mt(sd)
        a=at(pd); s.attrs=a+[0]*(640-len(a))+at(sd)
    def draw(s,img,mid,ox,oy):
        if mid>=len(s.mts): return
        px=img.load()
        for layer in (0,1):
            for k in range(4):
                e=s.mts[mid][layer*4+k]; t=e&0x3ff; hf=e>>10&1; vf=e>>11&1; pal=e>>12
                if t>=len(s.tiles): continue
                tile=s.tiles[t]
                bx=ox+(k%2)*8; by=oy+(k//2)*8
                for y in range(8):
                    for x in range(8):
                        c=tile[7-y if vf else y][7-x if hf else x]
                        if c==0 and layer==1: continue
                        if c==0 and layer==0: c=0
                        px[bx+x,by+y]=s.pals[pal][c] if pal<13 else (255,0,255)
def layout(lid):
    d=json.load(open(f'{G}/data/layouts/layouts.json'))
    return next(l for l in d['layouts'] if l.get('id')==lid)
def render_blocks(ts,blocks,w,h,out,grid=False,marks=()):
    from PIL import ImageDraw
    img=Image.new('RGB',(w*16,h*16))
    for y in range(h):
        for x in range(w):
            ts.draw(img,blocks[y*w+x]&0x3ff,x*16,y*16)
    dr=ImageDraw.Draw(img)
    if grid:
        for y in range(h):
            for x in range(w):
                if (blocks[y*w+x]>>10)&3: dr.line([x*16,y*16,x*16+15,y*16+15],fill=(255,0,0))
    for (x,y,label,col) in marks:
        dr.rectangle([x*16+2,y*16+2,x*16+13,y*16+13],outline=col)
        dr.text((x*16+1,y*16+1),label,fill=col)
    img.save(out)
if __name__=='__main__':
    if sys.argv[1]=='layout':
        l=layout(sys.argv[2]); ts=TS(l['primary_tileset'],l['secondary_tileset'])
        b=open(f"{G}/{l['blockdata_filepath']}",'rb').read(); blocks=struct.unpack(f'<{len(b)//2}H',b)
        render_blocks(ts,blocks,l['width'],l['height'],sys.argv[3],grid=len(sys.argv)>4)
    else: # sheet primary secondary out
        ts=TS(sys.argv[2],sys.argv[3]); ids=list(range(ts.npri))+list(range(640,len(ts.mts)))
        cols=16; rows=(len(ids)+cols-1)//cols
        from PIL import ImageDraw
        img=Image.new('RGB',(cols*20,rows*20),(40,40,40)); dr=ImageDraw.Draw(img)
        for i,m in enumerate(ids):
            sub=Image.new('RGB',(16,16)); ts.draw(sub,m,0,0); img.paste(sub,((i%cols)*20,(i//cols)*20))
        img.save(sys.argv[4])
        # index file
        open(sys.argv[4]+'.txt','w').write('\n'.join(f'{i//cols},{i%cols}: {m:#x}' for i,m in enumerate(ids)))
