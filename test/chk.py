import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    pg.on('pageerror', lambda e: print('pageerror:', str(e)[:400]))
    pg.on('console', lambda m: print('console.'+m.type, m.text[:300]) if m.type in ('error','warning') else None)
    pg.goto('file://' + sys.argv[1]); pg.wait_for_timeout(2500)
    b.close()
