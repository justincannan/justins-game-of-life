import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; x=json.loads(sys.argv[3]); T=int(sys.argv[4]); trials=int(sys.argv[5])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    for k in range(trials):
        r=pg.evaluate("""([env,x,T])=>{running=false;P.env=env;Object.assign(P,x);geoSeed();chemCapFill();reset('organism');const tr=[];const C0=carbonTotal();
          for(let t=1;t<=T;t++){step();if(t%500===0){let n=0;for(let i=0;i<N;i++)n+=alive[i];tr.push([t,n,+avgF(o2),+avgF(fe),+avgF(en),+(buried/o2.length).toFixed(2),+(enTaken?enAer/enTaken:0).toFixed(2)]);if(!n)break;}}
          return {tr,C:+(carbonTotal()/C0).toFixed(3)}}""",[env,x,T])
        print(json.dumps(r),flush=True)
    print('errors',errs); b.close()
