import sys, json
from playwright.sync_api import sync_playwright
# why do about half of the one-organism starts die out? Trace each start's first 400 ticks with no restart
path=sys.argv[1]; env=sys.argv[2]; trials=int(sys.argv[3]); x=json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
JS="""([base,env,x])=>{running=false;Object.assign(P,JSON.parse(base),x,{autoRestart:false});P.env=env;geoSeed();chemCapFill();reset('organism');
const cnt=()=>{let n=0;for(let i=0;i<N;i++)n+=alive[i];return n};const tr=[];let n0=cnt(),g0=new Set();
for(let i=0;i<N;i++)if(alive[i])g0.add(gen[i]>>>0);
const marks=[1,2,5,10,20,50,100,200,400];let mi=0,births=0,prev=new Uint8Array(N);
for(let t=1;t<=400;t++){prev.set(alive);step();let b=0,n=0;for(let i=0;i<N;i++){if(alive[i]){n++;if(!prev[i])b++;}}births+=b;
 if(t===marks[mi]){const gs=new Set();let cop=0;for(let i=0;i<N;i++)if(alive[i]){gs.add(gen[i]>>>0);}
  tr.push([t,n,b,gs.size]);mi++;}
 if(n===0){tr.push(['dead',t]);break;}}
return {n0,trace:tr,births}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for k in range(trials): print(json.dumps(pg.evaluate(JS,[base,env,x])),flush=True)
    print('errors',errs); b.close()
