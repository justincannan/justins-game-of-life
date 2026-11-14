import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2])
JS="""(x)=>{running=false;Object.assign(P,x);P.env='dish';P.dishPop=false;P.autoRestart=false;geoSeed();chemCapFill();reset('organism');
const M=()=>{let g=0,c=0,p=0,cells=0,mp=0;for(let k=0;k<chem.length;k++)g+=chem[k];
 for(let i=0;i<N;i++)if(alive[i]){cells++;const gg=gen[i];for(let k=0;k<16;k++)c+=((gg>>>(2*k))&3)*P.chunit;}
 if(typeof mxPool!=='undefined')for(const v of mxPool.values())for(let k=0;k<16;k++)mp+=v[k];
 let e=0;for(let k=0;k<en.length;k++)e+=en[k];let l=0,co=0;for(let i=0;i<N;i++)if(alive[i]){l+=light[i];co+=coat[i];}
 return {ground:+g.toFixed(0),inCells:c,inPools:+mp.toFixed(0),total:+(g+c+mp).toFixed(0),cells,sugar:+e.toFixed(0),cellEnergy:+l.toFixed(0),coat:+co.toFixed(1)}};
const out=[{t:0,...M()}];let D=0,B=0,W=0;
for(let t=1;t<=(x.T||600);t++){step();D+=deaths;B+=births;W+=(typeof writes!=='undefined'?0:0);if(t%100===0)out.push({t,...M(),deathsSoFar:D,birthsSoFar:B});}
return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    for r in pg.evaluate(JS,x): print(r)
    print(errs); b.close()
