import sys, json
from playwright.sync_api import sync_playwright
path, env, vw, vh, T = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':vw,'height':vh}); pg.goto('file://'+path); pg.wait_for_timeout(300)
    r = pg.evaluate("""([env,T]) => { running=false; P.env=env; geoSeed(); chemCapFill(); reset('organism'); const tr=[];
      for (let t=1;t<=T;t++){ step(); if (t%250===0){ let n=0, sp=0, rz=0; for (let i=0;i<N;i++) if (alive[i]) { n++; const s=strategy(gen[i]); if (s==='spore') sp++; else if (s==='rhizome') rz++; } tr.push([t,n,+(sp/Math.max(1,n)).toFixed(2),+(rz/Math.max(1,n)).toFixed(2)]); } }
      return {W,H,N,tr}; }""", [env,T])
    print(env, json.dumps(r)); b.close()
