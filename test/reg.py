import sys
from playwright.sync_api import sync_playwright
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox'])
    ctxb = b.new_context(viewport={'width': 1280, 'height': 800}); pg = ctxb.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    pg.goto('file://' + sys.argv[1]); pg.wait_for_timeout(2000)
    pg.click('#musicBtn')
    pg.select_option('#mtune', '24'); pg.select_option('#mscale', 'Every step'); pg.wait_for_timeout(1500)
    pg.keyboard.press('4'); box = pg.locator('#view').bounding_box(); cx, cy = box['x']+box['width']/2, box['y']+box['height']/2
    pg.mouse.move(cx-100, cy); pg.mouse.down(); pg.mouse.move(cx+100, cy+40, steps=8); pg.mouse.up()
    print('lamps', pg.evaluate("() => lampCount"))
    pg.click('#reset'); pg.wait_for_timeout(500)
    print('after reset lamps', pg.evaluate("() => [lampCount, W, H]"))
    pg.select_option('#zlayout', '2'); pg.wait_for_timeout(500)
    print('3x3', pg.evaluate("() => [Z.n, document.querySelectorAll('.zrow').length]"))
    pg.select_option('#zlayout', '5'); pg.wait_for_timeout(300)
    pg.click('#zreroll'); pg.uncheck('#zdistinct'); pg.wait_for_timeout(500)
    # instrument change
    pg.select_option('#zlayout', '0'); pg.wait_for_timeout(300)
    pg.select_option('.zrow[data-z="1"] .zi', label='Choir'); pg.wait_for_timeout(300)
    print('chan1', pg.evaluate("() => SY.chan(1)"))
    # inspector shows zone
    pg.keyboard.press('1'); pg.mouse.click(cx, cy); pg.wait_for_timeout(300)
    print('insp', pg.evaluate("() => document.getElementById('insp').innerText.slice(0,140)"))
    # reload: loops persist?
    pg.click('#recBtn'); pg.select_option('#reclen','s4'); pg.wait_for_timeout(100)
    pg.wait_for_timeout(300)
    b.close()
print('errors', errs)
