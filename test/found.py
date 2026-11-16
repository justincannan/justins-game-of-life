import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); errs=[]
    pg=b.new_page(viewport={"width":620,"height":460}); pg.on('pageerror',lambda e:errs.append(str(e)[:200])); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    d=pg.evaluate("""(base)=>{const out=[];for(let sd=1;sd<=12;sd++){running=false;Object.assign(P,JSON.parse(base));P.env='dish';P.autoRestart=false;P.seed=sd;reset('organism');
      let i=-1;for(let k=0;k<N;k++)if(alive[k]&&slen[k]){i=k;break;} if(i<0){out.push([sd,'none']);continue;}
      const k=geneSegs(seq,i*SL,slen[i]);out.push([sd,Array.from(seq.slice(i*SL,i*SL+slen[i])).join(' '),k,(rx[i]>>>0).toString(16)]);}return out;}""",base)
    for r in d: print('dish',r)
    v=pg.evaluate("""(base)=>{const out=[];for(let sd=11;sd<=30;sd++){running=false;Object.assign(P,JSON.parse(base));P.env='vent';P.autoRestart=false;P.seed=sd;reset('organism');
      const g=CHF.gene;let n=0;for(let t=0;t<400;t++){step();} for(let k=0;k<N;k++)if(alive[k])n++;out.push([sd,g,n]);}return out;}""",base)
    for r in v: print('vent',r)
    print('founded',sum(1 for r in v if r[2]>100),'of',len(v),errs); b.close()
