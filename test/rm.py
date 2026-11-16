import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; mode=sys.argv[3]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    r=pg.evaluate("""([base,env,mode])=>{running=false;Object.assign(P,JSON.parse(base));P.env=env;P.autoRestart=false;P.seed=1;reset(mode);const out=[];let m0=0,r0=0,g0=0;
      for(let t=1;t<=3000;t++){step();if(t%500===0){out.push({t,mut:RM.mut-m0,rec:RM.rec-r0,gene:RM.gene-g0,rm:+((RM.rec-r0)/Math.max(1,RM.mut-m0)).toFixed(2),geneRatio:+((RM.gene-g0)/Math.max(1,RM.mut-m0)).toFixed(2),contagion:P.contagion,geneHGT:P.geneHGT});m0=RM.mut;r0=RM.rec;g0=RM.gene;}}return out;}""",[base,env,mode])
    print(env,mode); [print(' ',o) for o in r]; b.close()
