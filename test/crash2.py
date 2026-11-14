import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required','--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800})
    pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.on('console', lambda m: print('console', m.type, m.text[:200]) if m.type in('error','warning') else None)
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(1500)
    pg.click('#musicBtn'); pg.keyboard.press('s'); pg.wait_for_timeout(1000)
    fr = pg.frames[1]
    for k in 'qwertyuiop': pg.keyboard.press(k); pg.wait_for_timeout(120)
    fr.click('#banks button:nth-child(3)'); pg.wait_for_timeout(300)
    for k in 'asdfghj': pg.keyboard.down(k); pg.wait_for_timeout(200); pg.keyboard.up(k)
    pg.wait_for_timeout(500)
    print(pg.evaluate("() => [SY.state(), M.stepN, SY.level()]"))
    pg.wait_for_timeout(4000)
    print(pg.evaluate("() => [SY.state(), M.stepN, SY.level()]"))
    b.close()
