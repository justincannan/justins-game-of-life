import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    for hc in ['0.25']:
        pg.evaluate(f"() => {{ const e=document.getElementById('hopcost'); e.value={hc}; e.dispatchEvent(new Event('input')); }}")
        pg.select_option('#seedmode','soup'); pg.click('#reset')
        for t in range(5):
            pg.wait_for_timeout(5000)
            print(hc, pg.evaluate("() => [tick, document.getElementById('hopinfo').textContent]"))
    b.close()
