import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; seed=int(sys.argv[2]); cost=float(sys.argv[3]); T=int(sys.argv[4]); mode=sys.argv[5] if len(sys.argv)>5 else 'soup'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    r=pg.evaluate("""([base,seed,cost,T,mode])=>{running=false;Object.assign(P,JSON.parse(base));P.env='vent';P.autoRestart=false;P.seed=seed;P.domCost=cost;const MODE=mode;reset(MODE);const out=[];
      for(let t=1;t<=T;t++){step();if(t%500===0){let n=0,L=0,nan=0;for(let i=0;i<N;i++)if(alive[i]){n++;L+=slen[i];if(light[i]!==light[i])nan++;}let mc=0;for(let k=0;k<chem.length;k++)if(chem[k]<mc)mc=chem[k];out.push([t,n,+(L/Math.max(1,n)).toFixed(0),nan,+mc.toFixed(3)]);if(!n)break;}}return out;}""",[base,seed,cost,T,mode])
    print(json.dumps({'seed':seed,'cost':cost,'out':r})); b.close()
