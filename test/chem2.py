import sys
from playwright.sync_api import sync_playwright
chem = sys.argv[2]=='1'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    pg.evaluate("(c) => { P.chemOn = c; %s reset('organism'); }" % (sys.argv[3] if len(sys.argv)>3 else ''), chem)
    for t in range(6):
        pg.wait_for_timeout(3000)
        print(pg.evaluate("() => { const s=series[series.length-1]||{}; return [tick, s.pop, s.distinct, starved, births, deaths] }"))
    b.close()
