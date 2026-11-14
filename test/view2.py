import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    print(pg.evaluate("() => { running=false; P.env='pond'; geoSeed(); chemCapFill(); reset('organism'); for (let t=0;t<1100;t++) step(); let n=0; for (let i=0;i<N;i++) if (alive[i]) n++; return n; }"))
    for v in ['normal','ir','strat']:
        pg.evaluate("(v) => { P.view=v; document.getElementById('viewsel').value=v; render(); }", v)
        pg.screenshot(path=f'test/shots/live_{v}.png', clip={'x':0,'y':0,'width':900,'height':800})
    print('errors', errs); b.close()
