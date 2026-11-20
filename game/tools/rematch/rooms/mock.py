# mock.py: composite real overworld sprites onto a rendered map (for approval mockups)
from PIL import Image
import os
G=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *(['..']*3)))  # game/
SHEETS={'BLUE':('people/blue',16,32),'PIDGEOT':('pokemon/pidgeot',16,16),'NURSE':('people/nurse',16,32),
 'CHANSEY':('pokemon/chansey',16,16),'CLERK':('people/clerk',16,32),'PROF_OAK':('people/prof_oak',16,32),
 'BLAINE':('people/blaine',16,32),'STRENGTH_BOULDER':('misc/strength_boulder',16,16),'ERIKA':('people/erika',16,32),'MISTY':('people/misty',16,32),'KOGA':('people/koga',16,32),'LT_SURGE':('people/lt_surge',16,32),'SABRINA':('people/sabrina',16,32),'BROCK':('people/brock',16,32),'PSYDUCK':('pokemon/psyduck',16,16),'VOLTORB':('pokemon/voltorb',16,16),'CHEF':('people/chef',16,32),'WOMAN_2':('people/woman_2',16,32),'RED':('people/red_normal',16,32)}
FACE={'FACE_DOWN':0,'FACE_UP':1,'FACE_LEFT':2,'FACE_RIGHT':3}
def sprite(gfx,face):
    if gfx.startswith('REMATCH_'):
        path,fw,fh=('pokemon/rematch/'+gfx[8:].lower(),32,32); fr=0
    else:
        path,fw,fh=SHEETS[gfx]; fr=FACE.get(face,0)
    s=Image.open(f'{G}/graphics/object_events/pics/{path}.png'); pal=s.getpalette()
    flip = fr==3
    if flip: fr=2
    if fh==16 and s.size[0]<=fw*fr: fr=0
    f=s.crop((fr*fw,0,fr*fw+fw,fh)); out=Image.new('RGBA',(fw,fh),(0,0,0,0)); px=f.load(); o=out.load()
    for y in range(fh):
        for x in range(fw):
            v=px[x,y]
            if v: o[x,y]=tuple(pal[v*3:v*3+3])+(255,)
    if gfx.startswith('REMATCH_') and face=='FACE_RIGHT' or flip: out=out.transpose(Image.FLIP_LEFT_RIGHT)
    return out
def mock(base_png, objs, out, scale=3):
    im=Image.open(base_png).convert('RGBA')
    for gfx,x,y,face in sorted(objs,key=lambda o:o[2]):
        s=sprite(gfx,face); w,h=s.size
        im.alpha_composite(s,(x*16+8-w//2, y*16+16-h))
    im.convert('RGB').resize((im.width*scale,im.height*scale),Image.NEAREST).save(out)
