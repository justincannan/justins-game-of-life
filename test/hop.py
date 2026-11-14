import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    for t in range(6):
        pg.wait_for_timeout(5000)
        print(pg.evaluate("() => [tick, series[series.length-1].pop, motileN, document.getElementById('hopinfo').textContent]"))
    pg.screenshot(path='/home/claude/test/shots/hop.png')
    # soup mode: half motile at start
    pg.select_option('#seedmode','soup'); pg.click('#reset'); pg.wait_for_timeout(8000)
    print(pg.evaluate("() => [tick, series[series.length-1].pop, motileN]"))
    b.close()
