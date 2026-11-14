import sys, json
from playwright.sync_api import sync_playwright
# is the lengthening of sequences driven or passive? Length quantiles over time (McShea's minimum and skew tests), and a Price-style split
# of each interval's change: selection (parents against the living) and transmission (child against parent)
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); every=int(sys.argv[4])
JS="""([base,env,x,T,every])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');
const orig=seqBirth;let pS=0,pN=0,dS=0,lS=0,lN=0,fS=0,fN=0,flS=0,flN=0,fU=0,fD=0;
seqBirth=function(i,pj,pb,rate){const lp=slen[pj]||0;const g=orig(i,pj,pb,rate);if(lp){pS+=lp;pN++;dS+=slen[i]-lp;if(lp>=16){fS+=lp;fN++;}}return g;};
const out=[];
for(let t=1;t<=T;t++){step();
 if(t%10===0){for(let i=0;i<N;i+=7)if(alive[i]&&slen[i]){lS+=slen[i];lN++;if(slen[i]>=16){flS+=slen[i];flN++;}}}
 if(t%every===0){const L=[];for(let i=0;i<N;i++)if(alive[i]&&slen[i])L.push(slen[i]);L.sort((a,b)=>a-b);const n=L.length;
  const q=f=>n?L[Math.min(n-1,(f*n)|0)]:0;let m=0;for(const v of L)m+=v;m/=Math.max(1,n);let m3=0,m2=0;for(const v of L){m2+=(v-m)**2;m3+=(v-m)**3;}m2/=Math.max(1,n);m3/=Math.max(1,n);
  out.push({t,n,mean:+m.toFixed(2),min:q(0),p10:q(.1),med:q(.5),p90:q(.9),max:n?L[n-1]:0,skew:m2>0?+(m3/m2**1.5).toFixed(2):0,atCap:+(L.filter(v=>v>=SL-3).length/Math.max(1,n)).toFixed(3),
   selection:lN&&pN?+(pS/pN-lS/lN).toFixed(2):null,transmission:pN?+(dS/pN).toFixed(3):null,births:pN,selFar:fN&&flN?+(fS/fN-flS/flN).toFixed(2):null});pS=pN=dS=lS=lN=fS=fN=flS=flN=0;}}
seqBirth=orig;return {env,x,series:out};}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        print(json.dumps(pg.evaluate(JS,[base,env,x,T,every])),flush=True)
    print('errors',errs); b.close()
