import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); trials=int(sys.argv[4])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        for k in range(trials):
            r=pg.evaluate("""([base,env,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');for(let t=1;t<=T;t++)step();
              specStep();const idx=[];for(let i=0;i<N;i++)if(alive[i]&&slen[i])idx.push(i);const m=Math.min(600,idx.length);const pick=[];for(let q=0;q<m;q++)pick.push(idx[(rng()*idx.length)|0]);
              const sig=new Uint32Array(m*SPH);for(let q=0;q<m;q++)specSig(pick[q],sig,q*SPH);const nn=new Array(11).fill(0),rp=new Array(11).fill(0);
              for(let q=0;q<m;q++){let mx=0;for(let r=0;r<m;r++)if(r!==q){const s=sigSim(sig,q*SPH,sig,r*SPH);if(s>mx)mx=s;}nn[Math.round(mx*10)]++;const r=(rng()*m)|0;if(r!==q)rp[Math.round(sigSim(sig,q*SPH,sig,r*SPH)*10)]++;}
              let n=0;for(let i=0;i<N;i++)n+=alive[i];
              return {env,x,n,species:specStat.n,eff:+specStat.div.toFixed(1),within:+specStat.within.toFixed(2),between:+specStat.between.toFixed(2),niches:specStat.niches,refused:mateTried?+(mateRefused/mateTried).toFixed(2):0,hgtFail:hgtTried?+(hgtFailed/hgtTried).toFixed(2):0,nearest:nn,random:rp}}""",[base,env,x,T])
            print(json.dumps(r),flush=True)
    print('errors',errs); b.close()
