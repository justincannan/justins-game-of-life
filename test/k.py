import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required','--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(3000)
    print(pg.evaluate("() => [W,H,N,cam.s,fitScale()]"))
    pg.click('#musicBtn'); r0 = pg.evaluate("() => P.root")
    for k in ['ArrowRight','ArrowRight','ArrowUp','ArrowUp','ArrowUp','ArrowLeft']: pg.keyboard.press(k)
    print(r0, pg.evaluate("() => [P.root, P.oct, document.getElementById('mroot').value, document.getElementById('moct').value]"))
    for i in range(6): pg.click('#zout')
    pg.wait_for_timeout(300); pg.screenshot(path='test/shots/h.png' if False else '/home/claude/test/shots/h.png')
    pg.wait_for_timeout(6000); print(pg.evaluate("() => [SY.state(), M.stepN, document.getElementById('minfo').textContent.slice(0,40)]"))
    fps = pg.evaluate("() => new Promise(r => { let n=0; const t=performance.now(); (function f(){ n++; if (performance.now()-t>3000) r(n/3); else requestAnimationFrame(f); })(); })"); print('fps', fps)
    b.close()
