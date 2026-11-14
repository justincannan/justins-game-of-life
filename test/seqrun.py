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
              const meas=()=>{let n=0,tl=0,top=0;const ss=new Set(),gs=new Map();for(let i=0;i<N;i++){if(!alive[i])continue;n++;if(!slen[i])continue;const o=i*SL,L=slen[i];tl+=L;let h=2166136261;for(let q=0;q<L;q++)h=Math.imul(h^seq[o+q],16777619);ss.add((h^L)>>>0);gs.set(gen[i],(gs.get(gen[i])||0)+1);}
                for(const v of gs.values())if(v>top)top=v;return [n,n?+(tl/n).toFixed(1):0,ss.size,gs.size,n?+(top/n).toFixed(2):0,seqMut?+(seqNeutral/seqMut).toFixed(2):0];};
              for(let t=1;t<=T;t++){step();if(t%(T/6)===0)tr.push([t].concat(meas()));}return {env,x,tr,restarts}}""",[base,env,x,T])
            print(json.dumps(r),flush=True)
    print('errors',errs); b.close()
