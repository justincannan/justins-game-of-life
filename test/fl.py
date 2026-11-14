import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1200,'height':700}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/out/fluid.html'); pg.wait_for_timeout(500)
    for env in ['vent','pond']:
        r=pg.evaluate("""([env,x])=>{running=false;P.env=env;Object.assign(P,x);geoSeed();chemCapFill();reset('organism');const t0=performance.now();for(let t=0;t<600;t++)step();const ms=(performance.now()-t0)/600;let mx=0,me=0;for(let c=0;c<fx.length;c++){const m=Math.hypot(fx[c],fy[c]);me+=m;if(m>mx)mx=m;}
          const t1=performance.now();for(let k=0;k<20;k++)fluidStep(P.current,0,.05);return {env,ms:+ms.toFixed(1),fluidMs:+((performance.now()-t1)/20).toFixed(1),squares:fx.length,mean:+(me/fx.length).toFixed(3),max:+mx.toFixed(2)}}""",[env,x])
        print(r)
        pg.select_option('#topview','c:flow'); pg.wait_for_timeout(300); pg.screenshot(path=f'/home/claude/test/shots/flow_{env}.png')
        pg.select_option('#topview','v:ir'); pg.wait_for_timeout(300); pg.screenshot(path=f'/home/claude/test/shots/ir_{env}.png')
    print('errors',errs); b.close()
