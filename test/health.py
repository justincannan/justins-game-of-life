import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2]); T=int(sys.argv[3])
JS="""([x,T])=>{running=false;Object.assign(P,x);P.autoRestart=false;geoSeed();chemCapFill();reset(x.mode||'soup');const out=[];let B=0,D=0;
for(let t=1;t<=T;t++){step();B+=births;D+=deaths;if(t%1000===0){let n=0,act=0,L=0,sl=0,rxn=0;const comp=new Set(),ln=new Set(),cc=new Map();
 for(let i=0;i<N;i++)if(alive[i]){n++;if(!dor[i]){act++;L+=light[i];}comp.add(gen[i]);ln.add(gen[i]>>>28);if(P.seqOn)sl+=slen[i];if(rxAct&&rxAct[i]>0)rxn++;if(ccId&&ccId[i]>0)cc.set(ccId[i],(cc.get(ccId[i])||0)+1);}
 let clumps=0;for(const v of cc.values())if(v>=P.clumpMin)clumps++;
 out.push({t,cells:n,active:act,birthsPer1000:B,deathsPer1000:D,meanStore:+(L/Math.max(1,act)).toFixed(3),compounds:comp.size,meanSeqLen:+(sl/Math.max(1,n)).toFixed(1),species:specStat.n,established:specStat.est,niches:specStat.niches,clumps,reacting:+(rxn/Math.max(1,n)).toFixed(2),chainKinds:fragCount(),longestChain:FRS.longest});B=0;D=0;if(!n)break;}}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    print(json.dumps(x)); [print('  ',json.dumps(r)) for r in pg.evaluate(JS,[x,T])]
    print('errors',errs); b.close()
