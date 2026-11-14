import sys
from PIL import Image, ImageDraw
pre=sys.argv[1]; times=sys.argv[2].split(','); labels=sys.argv[3].split('|'); outp=sys.argv[4]
tiles=[]
for T in times:
  for k in range(len(labels)):
    rows=open(f'{pre}{T}_{k}.txt').read().split('\n'); h=len(rows); w=len(rows[0])
    im=Image.new('RGB',(w,h),(18,22,30)); px=im.load()
    for y,r in enumerate(rows):
      for x,c in enumerate(r):
        if c=='#': px[x,y]=(235,200,120)
        elif c=='+': px[x,y]=(120,95,70)
    tiles.append(im.resize((w*2,h*2),Image.NEAREST))
W,H=tiles[0].size; C=len(labels); R=len(times)
out=Image.new('RGB',(C*W+10*C,R*(H+35)),(255,255,255)); d=ImageDraw.Draw(out)
for i,t in enumerate(tiles):
  r,c=divmod(i,C); out.paste(t,(c*(W+10),r*(H+35)+30)); d.text((c*(W+10)+4,r*(H+35)+12),f'{labels[c]} - tick {times[r]}',fill=(0,0,0))
out.save(outp)
