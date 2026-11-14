import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; extra=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    r = pg.evaluate("""([env,extra]) => { running=false; P.env=env; Object.assign(P, extra); geoSeed(); chemCapFill(); reset('organism'); const tr=[]; const t0=performance.now();
      for (let t=1;t<=2500;t++){ step(); if (t%500===0){ let n=0, q=[0,0,0,0], sg=0; for (let i=0;i<N;i++) if (alive[i]) { n++; q[xg[i]&3]++; } let hi=0; for (let c=0;c<sig.length;c++) if (sig[c]>=P.qthr) hi++; tr.push({t, n, q:q.map(v=>+(v/Math.max(1,n)).toFixed(3)), crowdSq:+(hi/sig.length).toFixed(3), sigMax:+Math.max(...sig).toFixed(2)}); } }
      chemPanel(); return {ms:((performance.now()-t0)/2500).toFixed(1), tr, panel: document.getElementById('chpanel').innerText.slice(0,330)}; }""", [env, extra])
    print(json.dumps(r, indent=0)[:1800]); print('errors', errs); b.close()
