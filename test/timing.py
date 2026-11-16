import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; W0=int(sys.argv[3]); T=int(sys.argv[4])
JS="""([base,env,W0,T])=>{running=false;Object.assign(P,JSON.parse(base));P.env=env;P.autoRestart=false;P.seed=1;reset('soup');
for(let t=0;t<W0;t++)step();
const names=['envStep','chemStep','fieldStep','sigStep','energyStep','rxnStep','xslots','produce','fragStep','virStep','detStep','visitOrder','domReact','seqBirth','seqTransfer','infold','advect','popStep','render','draw','clumpStep','bodyStep','g3Step','airStep','dishStep','speciesStep','statsStep','chartStep'];
const acc={},cnt={};const orig={};
for(const k of names){let f;try{f=eval(k);}catch(e){continue;} if(typeof f!=='function')continue; orig[k]=f; acc[k]=0;cnt[k]=0;
  const w=function(...a){const t0=performance.now();const r=f.apply(this,a);acc[k]+=performance.now()-t0;cnt[k]++;return r;}; try{eval(k+'=w');}catch(e){delete acc[k];}}
let n=0;for(let i=0;i<N;i++)if(alive[i])n++;
const t0=performance.now();for(let t=0;t<T;t++)step();const tot=performance.now()-t0;
for(const k in orig){try{eval(k+'=orig[k]');}catch(e){}}
const out={};for(const k in acc)if(acc[k]>0.5)out[k]=[+(acc[k]/T).toFixed(2),cnt[k]];
return {cells:n,msPerTick:+(tot/T).toFixed(1),parts:out};}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)[:200])); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)"); r=pg.evaluate(JS,[base,env,W0,T]); print(env,json.dumps(r),errs); b.close()
