import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required','--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(4000)
    pg.screenshot(path='shots/g1.png')
    for i in range(5): pg.click('#zout')
    pg.wait_for_timeout(300); print(pg.evaluate("() => [cam.s, fitScale()]")); pg.screenshot(path='shots/g2.png')
    pg.keyboard.press('s'); pg.wait_for_timeout(800); pg.screenshot(path='shots/g3.png'); b.close()
