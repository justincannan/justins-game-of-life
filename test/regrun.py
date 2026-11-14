import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); trials=int(sys.argv[4])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        for k in range(trials):
            r=pg.evaluate("""([base,env,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');const tr=[];
              const meas=()=>{let nb=0,rb=0,sk=0,rbs=0;for(const bo of bodies.values()){nb++;sk+=BG(bo.code);if((bo.code>>>26)&1){rb++;rbs+=BG(bo.code);}}let n=0;for(let i=0;i<N;i++)n+=alive[i];return [n,nb,nb?+(rb/nb).toFixed(2):null,nb?+(sk/nb).toFixed(2):null,somaN,regN];};
              for(let t=1;t<=T;t++){step();if(t%(T/5)===0)tr.push([t].concat(meas()));}return {env,x,tr,restarts}}""",[base,env,x,T])
            print(json.dumps(r),flush=True)
    print('errors',errs); b.close()
