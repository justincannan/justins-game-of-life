import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; x=json.loads(sys.argv[2]); T=int(sys.argv[3])
JS="""([x,T])=>{running=false;Object.assign(P,x);P.env='dish';geoSeed();chemCapFill();reset('organism');const out=[];
for(let t=1;t<=T;t++){step();if(t%25===0){let n=0,l=0,b=0;for(let i=0;i<N;i++)if(alive[i]){n++;l+=light[i];}
let lt=0;for(let c=0;c<ltc.length;c++)lt+=ltc[c];let et=0;for(let c=0;c<en.length;c++)et+=en[c];let hz=0;for(let i=0;i<N;i++)if(alive[i]&&((xg[i]>>10)&3))hz++;out.push([t,n,+et.toFixed(0),hz,+enTaken.toFixed(1),+(l/n).toFixed(3),births,deaths,starved,+(lt/ltc.length).toFixed(3)]);if(!n)break;}}
return {chemOn:P.chemOn,floor:P.floor,birth:P.birth,cost:P.cost,ZB:ZBIRTH[0],ZC:ZCOST[0],ZRG:ZRG[0],dishLight:P.dishLight,seqCost:P.seqCost,out}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    r=pg.evaluate(JS,[x,T]); o=r.pop('out'); print(r)
    for row in o: print(row)
    print('errors',errs); b.close()
