import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    print(pg.evaluate("""(x)=>{running=false;Object.assign(P,x);P.env='dish';P.dishPop=false;P.autoRestart=false;geoSeed();chemCapFill();reset('organism');for(let t=0;t<200;t++)step();
      const G=()=>{let g=0;for(let k=0;k<chem.length;k++)g+=chem[k];return g};const mol=g=>{let s=0;for(let k=0;k<16;k++)s+=((g>>>(2*k))&3);return s*P.chunit};
      let paid=0,rel=0,cs=0,cs2=0;const op=payChem;payChem=function(c,g,m,bid){const a=G();const r=op(c,g,m,bid);paid+=a-G();return r};
      const orl=releaseChem;releaseChem=function(c,g,bid){const a=G();orl(c,g,bid);rel+=G()-a};
      const ocs=chemStep;chemStep=function(){const a=G();ocs();cs+=G()-a};
      const fns={};const names=Object.keys(window).filter(f=>{try{return typeof window[f]==='function'&&/chem\b|chem\[/.test(window[f].toString())&&!['payChem','releaseChem','chemStep','step','G','mol'].includes(f)}catch(e){return false}});for(const f of names)if(typeof window[f]==='function'&&!/^[A-Z]/.test(f)){const o=window[f];fns[f]=0;window[f]=function(...a){const s=G();const r=o.apply(this,a);fns[f]+=G()-s;return r}}
      const a=G();for(let t=0;t<30;t++)step();const total=G()-a;
      return {groundChange:+total.toFixed(1),paidAtBirth:+(-paid).toFixed(1),releasedAtDeath:+rel.toFixed(1),groundStep:+cs.toFixed(1),byFunction:Object.fromEntries(Object.entries(fns).filter(([k,v])=>Math.abs(v)>1).map(([k,v])=>[k,+v.toFixed(1)])),
        unexplained:+(total+paid-rel-cs-Object.values(fns).reduce((p,q)=>p+q,0)).toFixed(1)}}""",x))
    print(errs); b.close()
