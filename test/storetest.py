import sys, json
from playwright.sync_api import sync_playwright
cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3])
JS="""([x,T])=>{running=false;Object.assign(P,x);P.env='dish';P.dishPop=false;P.autoRestart=false;geoSeed();chemCapFill();reset('organism');const out=[];
let woke=0,still=[0,0],act=[0,0];
for(let t=1;t<=T;t++){const d0=dor.slice(),a0=alive.slice();
 // median sugar among squares holding active cells
 step();
 for(let i=0;i<N;i++){if(!a0[i]||!alive[i])continue;if(d0[i]&&!dor[i])woke++;if(!d0[i]){const k=en[cmap[i]]>x.split?1:0;act[k]++;if(dor[i])still[k]++;}}
 if(t%100===0){let a=0,n=0,L=0;for(let i=0;i<N;i++)if(alive[i]){if(dor[i])n++;else{a++;L+=light[i];}}
  let mot=0;for(let i=0;i<N;i++)if(alive[i]&&((gen[i]>>>16)&3))mot++;let am=0;for(let i=0;i<N;i++)am+=amb[i];out.push({t,motile:mot,ambSum:+am.toFixed(1),active:a,inactive:n,meanStoreActive:+(L/Math.max(1,a)).toFixed(3),woke,goStillRate_lowSugar:+(still[0]/Math.max(1,act[0])).toFixed(4),goStillRate_highSugar:+(still[1]/Math.max(1,act[1])).toFixed(4)});woke=0;still=[0,0];act=[0,0];}}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        pg.evaluate("(b)=>Object.assign(P,JSON.parse(b))",base); print(x); [print('  ',r) for r in pg.evaluate(JS,[x,T])]
    print(errs); b.close()
