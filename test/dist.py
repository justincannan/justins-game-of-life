import sys, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':620,'height':460}); pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("""() => { running=false; P.env='even'; geoSeed(); chemCapFill(); reset('organism'); const out={};
      for (const T of [800,2500]) { while (tick<T) step();
        const minb=new Array(10).fill(0), nb=new Array(10).fill(0), has=new Array(9).fill(0); let n=0, surv1=0;
        for (let i=0;i<N;i++) if (alive[i]) { n++; const bt=B(gen[i]); let lo=0, c=0; for (let k=1;k<=8;k++) if (bt>>k&1) { if(!lo) lo=k; c++; has[k]++; } minb[lo]++; nb[c]++; }
        out[T]={n, minBirth:minb.map(v=>+(v/n).toFixed(3)), nBirthBits:nb.map(v=>+(v/n).toFixed(3)), hasBirthAt:has.map(v=>+(v/n).toFixed(3))}; }
      return out; }""")
    print(json.dumps(r)); b.close()
