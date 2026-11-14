import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    pg.on('pageerror', lambda e: print('pageerror:', str(e)[:400]))
    pg.goto('file://' + sys.argv[1]); pg.wait_for_timeout(2000)
    pg.click('#musicBtn')
    pg.evaluate("() => { window.__pk = 0; setInterval(() => { window.__pk = Math.max(window.__pk, SY.level()); }, 30); }")
    pg.wait_for_timeout(15000)
    print('peak sim music', pg.evaluate("() => window.__pk"))
    # per zone solo peaks: mute all but one
    for z in range(6):
        pg.evaluate(f"() => {{ for (let k=0;k<6;k++) SY.mute(k, k!=={z}); window.__pk=0; }}")
        pg.wait_for_timeout(5000)
        print('zone', z, pg.evaluate(f"() => [SY.chan({z}).n, window.__pk]"))
    b.close()
