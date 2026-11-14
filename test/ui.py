import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':900}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    pg.evaluate("() => { P.speed=4; }"); pg.wait_for_timeout(8000)
    pg.evaluate("() => { const el=document.getElementById('chrate'); el.value=.15; el.dispatchEvent(new Event('input')); const m=document.getElementById('mu'); m.value=.03; m.dispatchEvent(new Event('input')); document.getElementById('chemOn').click(); }")
    print('before', pg.evaluate("() => [P.chrate, P.mu, P.chemOn]"))
    pg.evaluate("() => document.querySelector('.resetRules').click()")
    print('after', pg.evaluate("() => [P.chrate, P.mu, P.chemOn]"))
    pg.evaluate("() => { const i=[...Array(N).keys()].find(i=>alive[i]); const x=i%W, y=(i/W)|0; inspect(x,y); document.getElementById('chpanel').scrollIntoView(); }")
    print(pg.evaluate("() => document.getElementById('insp').innerText.slice(0,500)"))
    pg.screenshot(path='test/shots/ui.png')
    pg.evaluate("() => { document.getElementById('insp').scrollIntoView(); }"); pg.screenshot(path='test/shots/ui2.png')
    b.close()
