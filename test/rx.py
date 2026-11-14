import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; extra=json.loads(sys.argv[3]); T=int(sys.argv[4])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    r=pg.evaluate("""([env,extra,T])=>{running=false;P.env=env;Object.assign(P,extra);geoSeed();chemCapFill();reset('organism');const t0=performance.now();const tr=[];const C0=carbonTotal();
      for(let t=1;t<=T;t++){step();if(t%250===0){let n=0;for(let i=0;i<N;i++)n+=alive[i];tr.push({t,n,C:+(carbonTotal()/C0).toFixed(4),o2:+avgF(o2),co2:+avgF(co2),w:+avgF(wat),sug:+avgF(en),aer:enTaken?+(enAer/enTaken).toFixed(2):0,dried,carbonless});}}
      return {ms:+((performance.now()-t0)/T).toFixed(1),tr}}""",[env,extra,T])
    print(json.dumps(r)); print('errors',errs); b.close()
