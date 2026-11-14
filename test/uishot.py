import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1400,'height':1000}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(1500)
    pg.screenshot(path=sys.argv[2])
    print(pg.evaluate("()=>[...document.querySelectorAll('.side > *')].map(e=>e.className==='grp'?'## '+e.textContent:e.tagName==='DETAILS'?(e.open?'[open] ':'')+e.querySelector('summary').textContent:e.tagName).join(' | ')"))
    pg.select_option('#envsel','dish'); pg.click('#reset'); pg.wait_for_timeout(1500)
    pg.screenshot(path=sys.argv[2].replace('.png','_dish.png'))
    print('errors',errs); b.close()
