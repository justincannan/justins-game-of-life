import sys
from playwright.sync_api import sync_playwright
rich, rate, mu, unit, chemon, trials, ticks = sys.argv[2:9]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("""() => { running=false; P.chrich=%s; P.chrate=%s; P.mu=%s; P.chunit=%s; P.chemOn=%s; const out=[];
      for (let k=0;k<%s;k++){ geoSeed(); chemCapFill(); reset('organism'); for(let t=0;t<%s;t++) step(); census(); out.push(series[series.length-1].pop); } return out; }""" % (rich, rate, mu, unit, chemon, trials, ticks))
    print(sys.argv[2:7], r)
    b.close()
