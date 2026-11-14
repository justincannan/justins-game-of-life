import sys
from playwright.sync_api import sync_playwright
rich, rate, mu, dur = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    pg.evaluate("() => { P.chrich=%s; P.chrate=%s; P.mu=%s; P.speed=4; chemCapFill(); reset('organism'); }" % (rich, rate, mu))
    out=[]
    for t in range(dur):
        pg.wait_for_timeout(4000)
        out.append(pg.evaluate("() => { const s=series[series.length-1]||{}; return [tick, s.pop, s.distinct, starved] }"))
    print(rich, rate, mu, out)
    b.close()
