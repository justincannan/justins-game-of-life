import sys, json
from playwright.sync_api import sync_playwright
JS="""([env,T])=>{running=false;P.rxDom=true;P.env=env;geoSeed();chemCapFill();reset('organism');for(let t=1;t<=T;t++)step();
const vs=[];for(let c=0;c<cw*chh;c++)vs.push(vglow[c]);const so=[...vs].sort((a,b)=>a-b);const hi=so[(so.length*.9)|0];
const r={near:{cells:0,down:0},far:{cells:0,down:0}};let dens={near:0,far:0},sq={near:0,far:0};
for(let c=0;c<cw*chh;c++){const k=vglow[c]>=hi&&hi>0?'near':'far';sq[k]++;}
for(let i=0;i<N;i++){if(!alive[i])continue;const k=vglow[cmap[i]]>=hi&&hi>0?'near':'far';r[k].cells++;const x=rx[i];let d=0;for(let q=0;q<4;q++){const b=(x>>>(8*q))&255;if(!b)break;if(RXE[b>>4]>RXE[b&15]+.3)d=1;}r[k].down+=d;}
return {env,hi:+hi.toFixed(3),near:{perSquare:+(r.near.cells/Math.max(1,sq.near)).toFixed(1),strongDownhill:+(r.near.down/Math.max(1,r.near.cells)).toFixed(2)},far:{perSquare:+(r.far.cells/Math.max(1,sq.far)).toFixed(1),strongDownhill:+(r.far.down/Math.max(1,r.far.cells)).toFixed(2)}}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/out/rx2.html'); pg.wait_for_timeout(500)
    for env in ['vent','springs']: print(json.dumps(pg.evaluate(JS,[env,2500])),flush=True)
    print(errs); b.close()
