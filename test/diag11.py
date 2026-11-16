import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    r=pg.evaluate("""(base)=>{running=false;Object.assign(P,JSON.parse(base));P.env='vent';P.autoRestart=false;P.seed=12;P.domCost=0;reset('organism');
      const mn=()=>{let m=0,at=-1;for(let k=0;k<chem.length;k++)if(chem[k]<m){m=chem[k];at=k;}return [m,at];};
      let T=-1;for(let t=1;t<3034;t++){step();const [m]=mn();if(m<-1e-4){T=t;break;}}
      if(T<0)return {none:true};
      // replay to T-1 then find the function
      P.seed=12;reset('organism');for(let t=1;t<T;t++)step();
      const names=['envStep','chemStep','fieldStep','sigStep','energyStep','rxnStep','xslots','produce','fragStep','virStep','detStep','domReact','seqBirth','seqTransfer','virBorn','detDie','driftPass','coatReturn','burn','payChem','swapChem','releaseChem','cellClumpCensus','virIntegrate','geneTransfer','advect','fragRelease','fragReturn','fragInsert','virSpill','pigBorn','olfStep'];
      const hits=[],orig={};
      for(const k of names){let f;try{f=eval(k);}catch(e){continue;}if(typeof f!=='function')continue;orig[k]=f;
        const w=function(...a){const [m0]=mn();const r=f.apply(this,a);const [m1,at]=mn();if(m1<m0-1e-6&&m1<-1e-4&&hits.length<10)hits.push({fn:k,args:a.slice(0,3).map(x=>typeof x==='number'?x:typeof x),m0,m1,sq:at>>4,k:at&15});return r;};try{eval(k+'=w');}catch(e){}}
      step();for(const k in orig){try{eval(k+'=orig[k]');}catch(e){}}
      return {T,hits};}""",base)
    print(json.dumps(r)); b.close()
