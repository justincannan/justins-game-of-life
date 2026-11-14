import sys, time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1400,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(800)
    pg.select_option('#envsel','dishpop'); pg.click('#reset'); pg.wait_for_timeout(300)
    t=time.time(); pg.evaluate("()=>{running=false;for(let k=0;k<3000;k++)step();running=true}"); print('3000 population ticks: %.1fs'%(time.time()-t))
    pg.wait_for_timeout(1200); pg.screenshot(path=sys.argv[2]+'_plate.png'); print(pg.evaluate("()=>document.getElementById('hud').textContent"))
    # open a patch at the colony's edge
    r=pg.evaluate("""()=>{const L=POP.L;let best=-1,bd=0;const c=(L-1)/2;for(let q=0;q<L*L;q++){if(popA[q]+popI[q]>0){const d=Math.hypot(q%L-c,((q/L)|0)-c);if(d>bd){bd=d;best=q;}}}
      const {s,ox,oy}=popGeom();const x=Math.floor(ox+((best%L)-bd*0.15*Math.sign((best%L)-c))*s),y=Math.floor(oy+(((best/L)|0))*s);inspect(x,y);
      let n=0,dn=0;for(let i=0;i<N;i++)if(alive[i]){n++;if(dor[i])dn++;}return {edgeRadius:bd,cells:n,inactive:dn,win:popWin}}""")
    print('opened',r); pg.wait_for_timeout(800); pg.screenshot(path=sys.argv[2]+'_open0.png')
    pg.evaluate("()=>{running=false;for(let k=0;k<400;k++)step();running=true}"); pg.wait_for_timeout(800); pg.screenshot(path=sys.argv[2]+'_open400.png')
    print(pg.evaluate("()=>{let n=0,dn=0;for(let i=0;i<N;i++)if(alive[i]){n++;if(dor[i])dn++;}return {cells:n,inactive:dn,births,deaths}}"))
    pg.click('#popFold'); pg.wait_for_timeout(600); print(pg.evaluate("()=>document.getElementById('hud').textContent"))
    pg.evaluate("()=>{running=false;for(let k=0;k<500;k++)step();running=true}"); pg.wait_for_timeout(800); pg.screenshot(path=sys.argv[2]+'_folded.png')
    print('errors',errs); b.close()
