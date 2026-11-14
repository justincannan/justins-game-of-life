import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2])
JS="""(x)=>{running=false;Object.assign(P,x);P.env='dish';P.dishPop=false;P.autoRestart=false;geoSeed();chemCapFill();reset('organism');
const mol=g=>{let s=0;for(let k=0;k<16;k++)s+=((g>>>(2*k))&3);return s*P.chunit};
let made=0;const orl=releaseChem;releaseChem=function(c,g,b){made+=P.ebody;return orl(c,g,b)};
const M=()=>{let g=0,c=0,p=0,h=0,cm=0,cs=0,e=0,co=0;for(let k=0;k<chem.length;k++)g+=chem[k];
 for(let i=0;i<N;i++){if(alive[i])c+=mol(gen[i]);if(huskG&&huskG[i])h+=mol(huskG[i]);if(coatM){cm+=coatM[i];cs+=coatS[i];}}
 if(typeof mxPool!=='undefined')for(const v of mxPool.values())for(let k=0;k<16;k++)p+=v[k];
 for(let k=0;k<en.length;k++){e+=en[k];co+=co2[k];}
 let fr=0;if(frAmt)for(let q=0;q<frAmt.length;q++)fr+=frAmt[q]*frLen[q]*P.chunit;return {inFragments:+fr.toFixed(0),molecules:+(g+c+p+h+cm+fr).toFixed(0),carbon:+(e+co+cs).toFixed(0),sugarMadeAtDeaths:+made.toFixed(0),all:+(g+c+p+h+cm+fr+e+co+cs-made).toFixed(0),cells:c?undefined:0}};
const out=[{t:0,...M()}];for(let t=1;t<=(x.T||600);t++){step();if(t%100===0)out.push({t,...M()});}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    for r in pg.evaluate(JS,x): print(r)
    print(errs); b.close()
