import sys
from playwright.sync_api import sync_playwright
rich, rate, dur = sys.argv[2], sys.argv[3], int(sys.argv[4])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    pg.evaluate("() => { P.chrich=%s; P.chrate=%s; P.speed=4; chemCapFill(); reset('organism'); }" % (rich, rate))
    for t in range(dur):
        pg.wait_for_timeout(4000)
        print(pg.evaluate("() => { const s=series[series.length-1]||{}; const top=[...codes.entries()].filter(([g,c])=>c.count>0).sort((a,b)=>b[1].count-a[1].count)[0]; return [tick, s.pop, s.distinct, starved, births, deaths, top?rule(top[0])+':'+top[1].count:''] }"))
    b.close()
