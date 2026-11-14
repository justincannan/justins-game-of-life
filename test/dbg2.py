import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1400,'height':1000}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(1000)
    pg.select_option('#envsel','dish'); pg.click('#reset'); pg.wait_for_timeout(800)
    print(pg.evaluate("()=>[P.env, dishCell&&dishCell.length, N, dishOut(0), W, H, typeof render, img.width, img.height]"))
    print(errs); b.close()
