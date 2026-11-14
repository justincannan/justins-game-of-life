import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2])
JS="""(x)=>{running=false;Object.assign(P,x);P.env='dish';P.dishPop=false;P.autoRestart=false;geoSeed();chemCapFill();reset('organism');for(let t=0;t<(x.warm||150);t++)step();
const molE=g=>{let s=0;for(let k=0;k<16;k++)s+=((g>>>(2*k))&3)*RXE[k];return s*P.chunit};
const E=()=>{let l=0,r=0,s=0,m=0,c=0,h=0,co=0,p=0;for(let i=0;i<N;i++){l+=light[i];r+=rsv[i]/P.rconv;if(alive[i])c+=molE(gen[i]);if(huskG&&huskG[i])h+=molE(huskG[i]);if(coatM)co+=coatM[i]*RXE[coatK[i]]+coatS[i];}
 for(let k=0;k<en.length;k++)s+=en[k];for(let q=0;q<chem.length;q++)m+=chem[q]*RXE[q&15];if(typeof mxPool!=='undefined')for(const v of mxPool.values())for(let k=0;k<16;k++)p+=v[k]*RXE[k];
 return {light:l,reserve:r,sugar:s,groundMol:m,cellMol:c,remainsMol:h,coat:co,pools:p,total:l+r+s+m+c+h+co+p}};
const fns={};const names=['chemStep','energyStep','produce','glidePass','hopPass','sporePass','dishTick','cellClumpCensus','rxnStep','sigStep','envStep'].filter(f=>typeof window[f]==='function');for(const f of names){const o=window[f];fns[f]=0;window[f]=function(...a){const s=E().total;const r=o.apply(this,a);fns[f]+=E().total-s;return r}}
rxGain=0;rxCost=0;const a=E();let up=0,worst=0;for(let t=0;t<(x.T||40);t++){const b=E().total;step();const d=E().total-b;if(d>0){up++;worst=Math.max(worst,d);}}
const z=E();const ins={};for(const [k,v] of Object.entries(fns))if(v>1e-6)ins[k]=+v.toFixed(3);
return {rxGainInLight:+rxGain.toFixed(2),rxCostInLight:+rxCost.toFixed(2),start:Object.fromEntries(Object.entries(a).map(([k,v])=>[k,+v.toFixed(1)])),end:Object.fromEntries(Object.entries(z).map(([k,v])=>[k,+v.toFixed(1)])),stepsWhereTotalRose:up,largestRise:+worst.toFixed(3),functionsThatAddEnergy:ins}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    r=pg.evaluate(JS,x)
    for k,v in r.items(): print(k, v)
    print(errs); b.close()
