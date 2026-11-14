import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; T=int(sys.argv[3]); cfgs=json.loads(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    for env,x in cfgs:
        r=pg.evaluate("""([env,x,T])=>{running=false;P.env=env;Object.assign(P,x);geoSeed();chemCapFill();reset('organism');let D=0,dB=0,dF=0,Dr=0,drySq=0,samp=0,popMin=1e9;
          for(let t=1;t<=T;t++){step();D+=dried;Dr+=drifted;if(t%50===0){samp++;let d=0;for(let c=0;c<wat.length;c++)if(wat[c]<P.wdry)d++;drySq+=d/wat.length;let n=0;for(let i=0;i<N;i++)n+=alive[i];if(t>300&&n<popMin)popMin=n;}}
          let n=0;for(let i=0;i<N;i++)n+=alive[i];return {env,x,pop:n,popMin,driedTotal:D,drifted:Dr,meanDryShare:+(drySq/samp).toFixed(3)}}""",[env,x,T])
        print(json.dumps(r),flush=True)
    print('errors',errs); b.close()
