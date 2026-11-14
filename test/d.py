import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required','--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(1500)
    print(pg.title(), pg.evaluate("() => [P.showLight, P.showForms, P.bodiesOn, ['showLight','showForms','bodiesOn'].map(i=>document.getElementById(i).checked), document.querySelector('h1').textContent]"))
    cnt = "() => { let n=0; for (let i=0;i<N;i++) n+=alive[i]; return n }"
    for mode in ['organism','soup']:
        pg.select_option('#seedmode', mode)
        for v in ['5','20','80']:
            pg.evaluate(f"() => {{ const e=document.getElementById('soupsize'); e.value={v}; e.dispatchEvent(new Event('input')) }}"); pg.click('#reset'); print(mode, v, pg.evaluate(cnt))
    pg.screenshot(path='/home/claude/test/shots/s.png'); b.close()
