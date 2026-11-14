import sys, json
from playwright.sync_api import sync_playwright
cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3])
JS="""([x,T])=>{running=false;Object.assign(P,x);P.env='springs';geoSeed();chemCapFill();reset(x.mode||'organism');const out=[];
for(let t=1;t<=T;t++){step();if(t%1000===0){const B=[0,.3,.45,.6,.75,2],occ=[0,0,0,0,0],tot=[0,0,0,0,0];
for(let i=0;i<N;i++){const tp=temp[cmap[i]];let k=0;while(k<4&&tp>=B[k+1])k++;tot[k]++;occ[k]+=alive[i];}
let L=0;for(let c=0;c<ltc.length;c++)L+=ltc[c];
out.push({t,cells:occ.reduce((a,b)=>a+b),occupancyByTemp:occ.map((o,k)=>tot[k]?+(o/tot[k]).toFixed(2):null),areaShare:tot.map(v=>+(v/N).toFixed(2)),light:+(L/ltc.length).toFixed(2)});}}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        pg.evaluate("(b)=>Object.assign(P,JSON.parse(b))",base); print(x); [print('  ',r) for r in pg.evaluate(JS,[x,T])]
    print(errs); b.close()
