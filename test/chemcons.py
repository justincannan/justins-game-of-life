import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    print(pg.evaluate("""()=>{running=false;P.env='dish';P.dishPop=false;P.autoRestart=false;P.dishSugar=20;geoSeed();chemCapFill();reset('organism');for(let t=0;t<300;t++)step();
      const S=()=>{let g=0;for(let k=0;k<chem.length;k++)g+=chem[k];return g};let wmin=1e9,wmax=0;for(let c=0;c<wat.length;c++){const w=Math.min(1,wat[c]/P.wrain);if(dishSq[c]){wmin=Math.min(wmin,w);wmax=Math.max(wmax,w);}}
      const a=S();for(let k=0;k<50;k++)chemStep();const b=S();
      const wsave=wat.slice();wat.fill(P.wrain*2);const c=S();for(let k=0;k<50;k++)chemStep();const d=S();wat.set(wsave);
      return {rxn:P.rxn,waterFracMin:wmin,waterFracMax:wmax,before:a,after50steps:b,change:(b-a)/a,withUniformWater_change:(d-c)/c}}"""))
    print(errs); b.close()
