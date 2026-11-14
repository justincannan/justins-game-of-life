import sys
from playwright.sync_api import sync_playwright
errs=[]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required','--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(2000)
    print(pg.title(), pg.evaluate("() => [W,H,Z.n,document.querySelector('h1').textContent, document.querySelectorAll('.zi').length]"))
    pg.click('#musicBtn'); pg.evaluate("() => { window.__pk=0; setInterval(()=>{window.__pk=Math.max(window.__pk,SY.level())},30) }")
    pg.select_option('.zi', label='Choir'); pg.wait_for_timeout(6000)
    print('peak', pg.evaluate("() => [window.__pk, SY.chan(0).n, M.stepN]"))
    pg.click('#recBtn'); pg.wait_for_timeout(300); pg.select_option('#reclen','s4') if False else None
    pg.click('#recBtn'); pg.select_option('#reclen','s4'); pg.click('#recBtn'); pg.wait_for_timeout(7000)
    print(pg.evaluate("() => document.getElementById('recmsg').textContent"))
    pg.screenshot(path='shots/f.png'); b.close()
print(errs)
