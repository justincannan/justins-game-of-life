import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2])
JS="""(x)=>{running=false;Object.assign(P,x);P.env='pond';P.autoRestart=false;geoSeed();chemCapFill();reset(x.mode||'organism');const out=[];
let st=0,dr=0,ot=0,b=0,d=0;
for(let t=1;t<=(x.T||400);t++){const wa=alive.slice(),L=light.slice();step();b+=births;d+=deaths;
 for(let i=0;i<N;i++)if(wa[i]&&!alive[i]){const c=cmap[i];if(L[i]<0.08)st++;else if(P.rxn&&wat[c]<P.wdry)dr++;else ot++;}
 if(t%25===0){let n=0,ds=0,E=0;for(let i=0;i<N;i++)if(alive[i]){n++;if(dor[i])ds++;E+=light[i];}let lt=0,ac=0;for(let i=0;i<N;i++)if(alive[i]){lt+=ltc[cmap[i]];ac+=amb[i];}
  out.push({t,cells:n,dormant:ds,meanStore:+(E/Math.max(1,n)).toFixed(3),sunAtCells:+(lt/Math.max(1,n)).toFixed(2),ambAtCells:+(ac/Math.max(1,n)).toFixed(3),born:b,died:d,starved:st,dried:dr,other:ot,sun:+envSun.toFixed(2)});b=d=st=dr=ot=0;if(!n)break;}}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    n0=pg.evaluate("()=>{P.env='pond';reset('soup');let n=0;for(let i=0;i<N;i++)n+=alive[i];const s=n;reset('organism');let m=0;for(let i=0;i<N;i++)m+=alive[i];return [s,m,P.cost,ZCOST[0],P.birth]}")
    print('soup start cells, organism start cells, cost, ZCOST, birth:', n0)
    for r in pg.evaluate(JS,x): print(r)
    print(errs); b.close()
