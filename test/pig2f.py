import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cases=json.loads(sys.argv[2]); T=int(sys.argv[3])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={'width':620,'height':460})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for env,mode,x,seed in cases:
        pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(400)
        print(env,mode,json.dumps(x),seed,pg.evaluate("""([base,env,mode,x,T,seed])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;P.autoRestart=false;geoSeed();chemCapFill();let s=seed;rng=()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296;};reset(mode);const out=[];
        for(let t=1;t<=T;t++){step(); if(t%250===0){let n=0,pgc=0;for(let i=0;i<N;i++)if(alive[i]){n++;if(coatM&&coatK[i]>=12&&coatM[i]>0)pgc++;}out.push([t,n,pgc]);if(!n)break;}}return out;}""",[base,env,mode,x,T,seed]),flush=True)
    print('errors',errs); b.close()
