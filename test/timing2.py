import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]
JS="""([base,env])=>{running=false;Object.assign(P,JSON.parse(base));P.env=env;P.autoRestart=false;P.seed=1;reset('soup');
for(let t=0;t<1000;t++)step();
let t0=performance.now();for(let t=0;t<60;t++)step();const a=(performance.now()-t0)/60;
const L=light.slice(),C=chem.slice();const ids=[];for(let i=0;i<N;i++)if(alive[i]&&rx[i]&&!dor[i])ids.push(i);
t0=performance.now();for(let r=0;r<20;r++)for(const i of ids)domReact(i);const d=(performance.now()-t0)/20;light.set(L);chem.set(C);
return {msPerTick:+a.toFixed(1),domReactPerTick:+d.toFixed(1),cellsWithRx:ids.length};}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460})
    pg.goto("file://"+path); pg.wait_for_timeout(400); base=pg.evaluate("()=>JSON.stringify(P)"); print(env,pg.evaluate(JS,[base,env])); b.close()
