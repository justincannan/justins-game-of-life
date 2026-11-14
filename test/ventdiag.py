import sys, json
from playwright.sync_api import sync_playwright
cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3])
JS="""([x,T])=>{running=false;Object.assign(P,x);P.env='vent';P.autoRestart=false;geoSeed();chemCapFill();reset(x.mode||'soup');const out=[];let st0=0,cb0=0;
for(let t=1;t<=T;t++){step();if(t%500===0){const occ=[0,0,0],tot=[0,0,0];let L=0,n=0,rx=0;for(let i=0;i<N;i++){const g=vglow[cmap[i]],k=g>.3?0:g>.05?1:2;tot[k]++;if(alive[i]){occ[k]++;n++;L+=light[i];if(rxAct[i]>0)rx++;}}
out.push({t,cells:n,near:+(occ[0]/tot[0]).toFixed(3),mid:+(occ[1]/tot[1]).toFixed(3),meanEnergy:+(L/Math.max(1,n)).toFixed(3),reacting:+(rx/Math.max(1,n)).toFixed(2),births,deaths,blockedForMolecules:starved-st0,blockedForCarbon:(typeof carbonless!=='undefined'?carbonless:0)-cb0,rxGain:+rxGain.toFixed(1),rxCost:+rxCost.toFixed(1)});st0=starved;cb0=(typeof carbonless!=='undefined'?carbonless:0);rxGain=0;rxCost=0;if(!n)break;}}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        pg.evaluate("(b)=>Object.assign(P,JSON.parse(b))",base); print(x); [print('  ',r) for r in pg.evaluate(JS,[x,T])]
    print(errs); b.close()
