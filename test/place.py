import sys, json
from playwright.sync_api import sync_playwright
# isolation by place: how alike two cells' sequences are, by how far apart they live, and whether they share a habitat (warm or cool water)
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); trials=int(sys.argv[4])
JS="""([base,env,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');for(let t=1;t<=T;t++)step();
specStep();const idx=[];for(let i=0;i<N;i++)if(alive[i]&&slen[i])idx.push(i);const m=Math.min(1000,idx.length);const pick=[];for(let q=0;q<m;q++)pick.push(idx[(rng()*idx.length)|0]);
const sig=new Uint32Array(m*SPH);for(let q=0;q<m;q++)specSig(pick[q],sig,q*SPH);
const tv=pick.map(i=>temp[cmap[i]]);const ts=[...tv].sort((a,b)=>a-b);const med=ts[m>>1];
const B=[4,8,16,32,64,128,1e9],s=new Array(B.length).fill(0),c=new Array(B.length).fill(0),hs=[0,0],hc=[0,0];
for(let k=0;k<40000;k++){const a=(rng()*m)|0,b=(rng()*m)|0;if(a===b)continue;const ia=pick[a],ib=pick[b];
 let dx=Math.abs(ia%W-ib%W),dy=Math.abs(((ia/W)|0)-((ib/W)|0));dx=Math.min(dx,W-dx);dy=Math.min(dy,H-dy);const d=Math.hypot(dx,dy);
 const v=sigSim(sig,a*SPH,sig,b*SPH);let q=0;while(d>=B[q])q++;s[q]+=v;c[q]++;
 if(d>=32){const same=(tv[a]>med)===(tv[b]>med)?0:1;hs[same]+=v;hc[same]++;}}
let n=0;for(let i=0;i<N;i++)n+=alive[i];
return {env,x,n,species:specStat.n,eff:+specStat.div.toFixed(1),hgtFail:hgtTried?+(hgtFailed/hgtTried).toFixed(2):0,
 byDist:B.map((b,q)=>[b<1e8?b:'far',c[q]?+(s[q]/c[q]).toFixed(3):null,c[q]]),
 far_sameHabitat:hc[0]?+(hs[0]/hc[0]).toFixed(3):null,far_otherHabitat:hc[1]?+(hs[1]/hc[1]).toFixed(3):null,tempSpread:+(ts[(m*.9)|0]-ts[(m*.1)|0]).toFixed(3)}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        for k in range(trials):
            print(json.dumps(pg.evaluate(JS,[base,env,x,T])),flush=True)
    print('errors',errs); b.close()
