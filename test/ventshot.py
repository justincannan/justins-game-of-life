import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1400,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(800)
    pg.select_option('#envsel','vent'); pg.click('#reset'); pg.evaluate("()=>{running=false;for(let t=0;t<800;t++)step();running=true}"); pg.click('#zfit'); pg.wait_for_timeout(1500)
    pg.screenshot(path=sys.argv[2]); print(pg.evaluate("()=>document.getElementById('hud').textContent.slice(0,160)")); print(errs); b.close()
