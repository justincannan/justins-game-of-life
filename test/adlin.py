import sys, json
from playwright.sync_api import sync_playwright
# how long does each changed reading code last? Follow every code hash: when it first appears, when it was last seen,
# how many cells carried it at most, and the mean sequence length and enzyme count of its carriers when first seen
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); trials=int(sys.argv[4])
JS="""([base,env,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');
const C=new Map();
for(let t=1;t<=T;t++){step();if(t%50)continue;const now=new Map();
 for(let i=0;i<N;i++){if(!alive[i]||!cH[i])continue;let r=now.get(cH[i]);if(!r){r={n:0,L:0,E:0,s:0};now.set(cH[i],r);}r.n++;if(r.s<8){infold(seq,i*SL,slen[i]);r.L+=slen[i];r.E+=dN-lastAd;r.s++;}}
 for(const[h,r]of now){let c=C.get(h);if(!c){c={b:t,l:t,max:r.n,L:r.L/r.s,E:r.E/r.s};C.set(h,c);}c.l=t;if(r.n>c.max)c.max=r.n;}}
const recs=[...C.values()].filter(c=>c.b<T-500);
const bucket=(arr,key,edges)=>edges.map((e,k)=>{const lo=k?edges[k-1]:-1,s=arr.filter(c=>c[key]>lo&&c[key]<=e);const lt=s.map(c=>c.l-c.b+50).sort((a,b)=>a-b);
 return {upTo:e,codes:s.length,medianLife:lt.length?lt[lt.length>>1]:null,meanLife:lt.length?Math.round(lt.reduce((a,b)=>a+b,0)/lt.length):null,over500:s.filter(c=>c.l-c.b>=500).length,bigMax:s.filter(c=>c.max>=50).length};});
let n=0;for(let i=0;i<N;i++)n+=alive[i];
return {env,x,n,codesSeen:C.size,byLength:bucket(recs,'L',[16,24,32,48,128]),byEnzymes:bucket(recs,'E',[0.5,1.5,2.5,4,20])}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        for k in range(trials): print(json.dumps(pg.evaluate(JS,[base,env,x,T])),flush=True)
    print('errors',errs); b.close()
