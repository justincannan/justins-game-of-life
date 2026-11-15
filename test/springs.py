import sys, json
from playwright.sync_api import sync_playwright
# springs world: wet share of the ground, cells, share of places occupied, and how cells sit relative to the source
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); seeds=json.loads(sys.argv[4])
JS="""([base,x,T,seed])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env='springs';P.autoRestart=false;geoSeed();chemCapFill();
let s=seed>>>0||1;rng=()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296;};reset(x.mode||'soup');const out=[];
for(let t=1;t<=T;t++){step();if(t%500===0){let n=0,wet=0,occW=0,occD=0,nw=0;const S=cw*chh;
 for(let c=0;c<S;c++)if(wat[c]>=P.wdry)wet++;
 for(let i=0;i<N;i++)if(alive[i]){n++; if(wat[cmap[i]]>=P.wdry)occW++; else occD++;}
 let tt=0;for(let c=0;c<S;c++)tt+=temp[c];
 out.push({t,n,occ:+(n/N).toFixed(3),wet:+(wet/S).toFixed(3),inWet:n?+(occW/n).toFixed(2):0,T:+(tt/S).toFixed(2)});}}
return {x,seed,out};}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        for sd in seeds:
            r=pg.evaluate(JS,[base,x,T,sd]); print(json.dumps(x), sd, [ (o['t'],o['n'],o['occ'],o['wet'],o['inWet'],o['T']) for o in r['out']],flush=True)
    print('errors',errs); b.close()
