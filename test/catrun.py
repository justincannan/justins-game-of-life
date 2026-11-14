import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; envs=json.loads(sys.argv[2]); T=int(sys.argv[3]); trials=int(sys.argv[4]); x=json.loads(sys.argv[5]) if len(sys.argv)>5 else {}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env in envs:
        for k in range(trials):
            r=pg.evaluate("""([base,env,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');for(let t=1;t<=T;t++)step();
              let n=0,tl=0;const ca=new Float64Array(8);for(let i=0;i<N;i++){if(!alive[i]||!slen[i])continue;n++;tl+=slen[i];for(let k=0;k<8;k++)ca[k]+=(cat[i]>>(2*k))&3;}
              return {env,n,len:n?+(tl/n).toFixed(1):0,cat:Array.from(ca).map(v=>n?+(v/n).toFixed(2):0),restarts}}""",[base,env,x,T])
            print(json.dumps(r),flush=True)
    print('errors',errs); b.close()
