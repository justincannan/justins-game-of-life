import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); trials=int(sys.argv[4])
JS="""([base,env,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');
let est=0;for(let t=1;t<=T;t++){step();if(t===200){let n=0;for(let i=0;i<N;i++)n+=alive[i];est=n>0;}}
specStep();let n=0,m=0,L=0,dn=0,dsz=0,dmul=0,hid=0,prs=0;const ca=new Array(8).fill(0);const P0=P.domOn;P.domOn=true;
for(let i=0;i<N;i++){if(!alive[i])continue;n++;if(!slen[i]||i%5)continue;m++;L+=slen[i];infold(seq,i*SL,slen[i]);dn+=dN;hid+=dHidden;prs+=dPairs;for(let d=0;d<dN;d++){dsz+=dB[d]-dA[d]+1;if(dS[d]>1)dmul++;}for(let k=0;k<8;k++)ca[k]+=CA(i,k);}
P.domOn=P0;return {env,x,est,n,len:+(L/Math.max(1,m)).toFixed(1),domPerCell:+(dn/Math.max(1,m)).toFixed(2),domSize:+(dsz/Math.max(1,dn)).toFixed(2),firmer:+(dmul/Math.max(1,dn)).toFixed(3),hidden:+(hid/Math.max(1,prs)).toFixed(3),
 enz:ca.map(v=>+(v/Math.max(1,m)).toFixed(2)),species:specStat.n,eff:+specStat.div.toFixed(1)}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        for k in range(trials): print(json.dumps(pg.evaluate(JS,[base,env,x,T])),flush=True)
    print('errors',errs); b.close()
