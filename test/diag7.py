import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; seed=int(sys.argv[2]); T=int(sys.argv[3])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    r=pg.evaluate("""([base,seed,T])=>{running=false;Object.assign(P,JSON.parse(base));P.env='vent';P.autoRestart=false;P.seed=seed;P.domCost=0;reset('organism');
      for(let t=1;t<T;t++)step();
      const hits=[];const nanCount=()=>{let c=0,f=-1;for(let i=0;i<N;i++)if(light[i]!==light[i]){c++;if(f<0)f=i;}return [c,f];};
      const names=['envStep','chemStep','fieldStep','sigStep','energyStep','rxnStep','xslots','produce','fragStep','virStep','detStep','domReact','seqBirth','seqTransfer','pigBorn','virBorn','detDie','driftPass','coatReturn','burn','payChem','swapChem','releaseChem','cellClumpCensus','clumpStep','virIntegrate','geneTransfer','chemoFounder','hopPass'];
      const orig={};
      for(const k of names){let f;try{f=eval(k);}catch(e){continue;}if(typeof f!=='function')continue;orig[k]=f;
        const w=function(...a){const [c0]=nanCount();const r=f.apply(this,a);const [c1,fi]=nanCount();if(c1>c0&&hits.length<20)hits.push({fn:k,args:a.slice(0,3).map(x=>typeof x==='number'?x:typeof x),before:c0,after:c1,first:fi,coat:fi>=0?coat[fi]:null,coatM:fi>=0&&coatM?coatM[fi]:null,coatK:fi>=0&&coatK?coatK[fi]:null});return r;};try{eval(k+'=w');}catch(e){}}
      const [b0]=nanCount();step();const [b1]=nanCount();
      for(const k in orig){try{eval(k+'=orig[k]');}catch(e){}}
      return {b0,b1,hits};}""",[base,seed,T])
    print(json.dumps(r)); b.close()
