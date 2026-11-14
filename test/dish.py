import sys, json
from playwright.sync_api import sync_playwright
# the dish: one seed in the centre, little light, food laid once; measure the colony's shape and save a picture of it
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); shot=sys.argv[4] if len(sys.argv)>4 else ''
JS="""([base,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env='dish';geoSeed();chemCapFill();P.autoRestart=false;reset("organism");const ser=[];
for(let t=1;t<=T;t++){step();if(t%250===0){let n=0;for(let i=0;i<N;i++)n+=alive[i];ser.push([t,n,glided]);if(!n)break;}}
const occ=new Uint8Array(N);let n=0,cx=W/2,cy=H/2,rmax=0,peri=0;for(let i=0;i<N;i++)if(alive[i]){occ[i]=1;n++;const dx=Math.min(Math.abs(i%W-cx),W-Math.abs(i%W-cx)),dy=Math.min(Math.abs(((i/W)|0)-cy),H-Math.abs(((i/W)|0)-cy));rmax=Math.max(rmax,Math.hypot(dx,dy));}
for(let i=0;i<N;i++)if(occ[i]){const x=i%W,y=(i/W)|0;let e=0;for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){const j=((y+dy+H)%H)*W+((x+dx+W)%W);if(!occ[j])e++;}peri+=e;}
const bc=[];for(const s of [2,4,8,16,32]){const seen=new Set();for(let i=0;i<N;i++)if(occ[i])seen.add(((((i/W)|0)/s)|0)*1000+(((i%W)/s)|0));bc.push(seen.size);}
let fd=null;if(bc[0]>0&&bc[4]>0)fd=+(-(Math.log(bc[4])-Math.log(bc[0]))/(Math.log(32)-Math.log(2))).toFixed(2);
const fill=rmax>0?+(n/(Math.PI*rmax*rmax)).toFixed(3):0;let pfood=0;for(let c=0;c<cw*chh;c++)pfood+=chem[(c<<4)+15];
const hk=k=>husk&&husk[k]>0;const img=[];for(let y=0;y<H;y+=2){let r='';for(let x=0;x<W;x+=2)r+=(occ[y*W+x]||occ[y*W+x+1]||occ[(y+1)*W+x])?'#':(hk(y*W+x)||hk(y*W+x+1)||hk((y+1)*W+x))?'+':'.';img.push(r);}
let outN=0;for(let i=0;i<N;i++)if(alive[i]&&dishOut(i))outN++;let es=0;for(let c=0;c<en.length;c++)es+=en[c];let hN=0;if(husk)for(let i=0;i<N;i++)if(husk[i]>0)hN++;let dN=0;for(let i=0;i<N;i++)if(alive[i]&&dor[i])dN++;return {x,remains:hN,inactive:dN,outN,sugarTotal:+es.toFixed(0),n,radius:+rmax.toFixed(1),fillOfDisc:fill,perimeterPerCell:n?+(peri/n).toFixed(2):0,boxDim:fd,foodLeft:+(pfood/(cw*chh*P.dishFood*P.chrich*ABUND[15]*.6+1e-9)).toFixed(2),series:ser,img}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for k,x in enumerate(cfgs):
        r=pg.evaluate(JS,[base,x,T]); img=r.pop('img'); print(json.dumps(r),flush=True)
        if shot: open(f'{shot}_{k}.txt','w').write('\n'.join(img))
    print('errors',errs); b.close()
