import sys, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':620,'height':460}); pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("""() => { running=false; P.env='even'; geoSeed(); chemCapFill(); reset('organism'); const out={};
      for (const T of [1000,2500]) { while (tick<T) step(); const a=Array.from(sig).sort((x,y)=>x-y); const q=f=>+a[Math.floor(f*(a.length-1))].toFixed(2); out[T]={p50:q(.5),p75:q(.75),p90:q(.9),p95:q(.95),p99:q(.99),mx:q(1)}; } return out; }""")
    print(json.dumps(r)); b.close()
