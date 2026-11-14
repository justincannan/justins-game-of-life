import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; extra=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}; T=int(sys.argv[4]) if len(sys.argv)>4 else 2000
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    r = pg.evaluate("""([env,extra,T]) => { running=false; P.env=env; Object.assign(P, extra); geoSeed(); chemCapFill(); reset('organism'); const tr=[]; const t0=performance.now();
      for (let t=1;t<=T;t++){ step(); if (t%500===0){ let n=0, g=[0,0,0,0]; for (let i=0;i<N;i++) if (alive[i]) { n++; for (let q=0;q<4;q++) if ((xg[i]>>(2*q))&3) g[q]++; } tr.push({t, n, g:g.map(v=>+(v/Math.max(1,n)).toFixed(2)), eaten}); } }
      return {ms:((performance.now()-t0)/T).toFixed(1), tr}; }""", [env, extra, T])
    print(json.dumps(r)); print('errors', errs); b.close()
