import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required','--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    print(pg.evaluate("() => [document.getElementById('seedmode').value, codes.size, (()=>{let n=0;for(let i=0;i<N;i++)n+=alive[i];return n})()]"))
    pg.wait_for_timeout(15000)
    print(pg.evaluate("() => [tick, series[series.length-1].pop, codes.size]"))
    pg.screenshot(path='/home/claude/test/shots/o.png')
    for i in range(8): pg.click('#zout')
    pg.wait_for_timeout(300); print(pg.evaluate("() => [cam.s, fitScale()]")); pg.screenshot(path='/home/claude/test/shots/o2.png')
    for sh in ['cross','band']:
        pg.select_option('#soupshape', sh); pg.select_option('#seedmode','soup'); pg.click('#reset'); pg.wait_for_timeout(300)
        print(sh, pg.evaluate("() => { let n=0; for (let i=0;i<N;i++) n+=alive[i]; return n }"))
    b.close()
