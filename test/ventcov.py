import sys, json
from playwright.sync_api import sync_playwright
cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3])
JS="""([x,T])=>{running=false;Object.assign(P,x);P.env='vent';geoSeed();chemCapFill();reset(x.mode||'soup');const out=[];let rxE=0;
for(let t=1;t<=T;t++){step();if(t%500===0){const occ=[0,0,0],tot=[0,0,0];for(let i=0;i<N;i++){const g=vglow[cmap[i]],k=g>.3?0:g>.05?1:2;tot[k]++;occ[k]+=alive[i];}
let wmax=0,wpos=0;for(let c=0;c<wup.length;c++){wmax=Math.max(wmax,wup[c]);if(wup[c]>.005)wpos++;}
out.push({t,cells:occ.reduce((a,b)=>a+b),nearVent:+(occ[0]/tot[0]).toFixed(3),mid:+(occ[1]/tot[1]).toFixed(3),far:+(occ[2]/tot[2]).toFixed(3),
 lifted:airStat.lifted,settled:airStat.settled,aloft:air.length,g3:(typeof G3==='object'?G3.state:'-'),wupMax:+wmax.toFixed(4),sqRising:wpos,broth:+(()=>{let s=0;for(let c=0;c<chem.length;c++)s+=chem[c];return s/chem.length})().toFixed(2)});}}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        pg.evaluate("(b)=>Object.assign(P,JSON.parse(b))",base)
        print(x); [print('  ',r) for r in pg.evaluate(JS,[x,T])]
    print(errs); b.close()
