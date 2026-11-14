import sys, json
from playwright.sync_api import sync_playwright
cfgs=json.loads(sys.argv[2])
JS="""(x)=>{running=false;Object.assign(P,x);P.env='vent';geoSeed();chemCapFill();reset('soup');for(let t=0;t<200;t++)step();
let src=-1;for(let i=0;i<N;i++)if(alive[i]&&vglow[cmap[i]]>.3){src=i;break;}
// find far places: squares with vglow<.02; plant 12 lone cells and 3 patches of 5x5
const far=[];for(let i=0;i<N;i+=97)if(!alive[i]&&vglow[cmap[i]]<.02)far.push(i);
const plant=i=>{if(alive[i])return;alive[i]=1;gen[i]=gen[src];xg[i]=xg[src];light[i]=.5;changed[i]=1;if(P.seqOn){seqFromGen(i,gen[i]);}};
const lone=far.slice(0,40),patch=far.slice(500,503);lone.forEach(plant);
for(const c of patch){const x0=c%W,y0=(c/W)|0;for(let a=0;a<5;a++)for(let b=0;b<5;b++)plant(((y0+a)%H)*W+(x0+b)%W);}
const out=[];const farCount=()=>{let n=0;for(let i=0;i<N;i++)if(alive[i]&&vglow[cmap[i]]<.02)n++;return n};
out.push([0,farCount(),+light[lone[0]].toFixed(3)]);
for(let t=1;t<=1000;t++){step();if(t%100===0){let lsum=0,ln=0;for(let i=0;i<N;i++)if(alive[i]&&vglow[cmap[i]]<.02){lsum+=light[i];ln++;}out.push([t,farCount(),ln?+(lsum/ln).toFixed(3):0]);}}
let lt=0,n=0;for(let c=0;c<ltc.length;c++)if(vglow[c]<.02){lt+=ltc[c];n++;}
return {farLight:+(lt/n).toFixed(3),cost:ZCOST[0],out}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        pg.evaluate("(b)=>Object.assign(P,JSON.parse(b))",base); r=pg.evaluate(JS,x); print(x, 'far light',r['farLight'],'cost',r['cost']); print('   [tick, cells far from vents, their mean energy]', r['out'])
    print(errs); b.close()
