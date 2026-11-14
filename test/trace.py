import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; x=json.loads(sys.argv[3]); trials=int(sys.argv[4])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); pg.goto('file://'+path); pg.wait_for_timeout(300)
    for k in range(trials):
        r=pg.evaluate("""([env,x])=>{running=false;P.env=env;Object.assign(P,x);geoSeed();chemCapFill();reset('organism');const tr=[];let D=0,C=0,Hh=0,S=0;
          for(let t=1;t<=1500;t++){step();D+=dried;C+=carbonless;Hh+=heated;S+=starved;if(t%100===0){let n=0;for(let i=0;i<N;i++)n+=alive[i];tr.push(n);if(!n)break;}}
          return {tr,dried:D,noC:C,heat:Hh,chem:S-C,sea:+rxSeason.toFixed(2),w:avgF(wat),co2:avgF(co2)}}""",[env,x])
        print(json.dumps(r),flush=True)
    b.close()
