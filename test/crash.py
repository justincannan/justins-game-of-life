import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required','--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800})
    pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.on('console', lambda m: print('console', m.type, m.text[:200]) if m.type=='error' else None)
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(1500)
    pg.click('#musicBtn')
    pg.evaluate("() => { window.__pk=0; setInterval(()=>{window.__pk=Math.max(window.__pk,SY.level())},30) }")
    for i in range(12):
        pg.wait_for_timeout(5000)
        print(i*5+5, pg.evaluate("() => { const r=[SY.state(), +window.__pk.toFixed(3), M.stepN, M.ac.currentTime.toFixed(1), (M.next-M.ac.currentTime).toFixed(2)]; window.__pk=0; return r }"))
    b.close()
