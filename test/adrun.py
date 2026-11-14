import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); trials=int(sys.argv[4])
JS="""([base,env,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');
const orig=seqBirth;const byLen=[[0,0],[0,0],[0,0],[0,0]];const series=[];let ch=0,bn=0;
seqBirth=function(i,pj,pb,rate){const pc=pj>=0?cH[pj]:0,pl=pj>=0?slen[pj]:0;const g=orig(i,pj,pb,rate);if(pj>=0){const b=pl<16?0:pl<32?1:pl<48?2:3;byLen[b][1]++;if(cH[i]!==pc)byLen[b][0]++;bn++;if(cH[i]!==pc)ch++;}return g;};
for(let t=1;t<=T;t++){step();if(t%500===0){let n=0,wc=0,ad=0,en=0;const codes=new Map();for(let i=0;i<N;i+=3){if(!alive[i]||!slen[i])continue;n++;if(cH[i]){wc++;codes.set(cH[i],(codes.get(cH[i])||0)+1);}infold(seq,i*SL,slen[i]);ad+=lastAd;en+=dN-lastAd;}
 series.push({t,cells:n*3,withCode:+(wc/Math.max(1,n)).toFixed(3),codes:codes.size,topShare:+(Math.max(0,...codes.values())/Math.max(1,n)).toFixed(3),adaptorsPerCell:+(ad/Math.max(1,n)).toFixed(2),enzymesPerCell:+(en/Math.max(1,n)).toFixed(2),codeChangePerBirth:+(ch/Math.max(1,bn)).toFixed(4)});ch=0;bn=0;}}
seqBirth=orig;return {env,x,series,changeByParentLength:byLen.map(([a,b],k)=>[['<16','16-31','32-47','48+'][k],b?+(a/b).toFixed(4):null,b])}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        for k in range(trials): print(json.dumps(pg.evaluate(JS,[base,env,x,T])),flush=True)
    print('errors',errs); b.close()
