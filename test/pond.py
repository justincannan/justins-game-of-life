import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); seeds=json.loads(sys.argv[4])
JS="""([base,x,T,seed])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env='pond';P.autoRestart=false;geoSeed();chemCapFill();
let s=seed>>>0||1;rng=()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296;};reset(x.mode||'organism');const out=[];
for(let t=1;t<=T;t++){step();if(t%250===0){let n=0,h=0;for(let i=0;i<N;i++)if(alive[i]){n++;if((xg[i]>>10)&3)h++;}out.push([t,n,h,+(PIN.got||0).toFixed(0)]);if(!n)break;}}
return out;}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        for sd in seeds: print(json.dumps(x), sd, pg.evaluate(JS,[base,x,T,sd]),flush=True)
    print('errors',errs); b.close()
