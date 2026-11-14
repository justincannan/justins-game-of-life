import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required','--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(1500)
    print(pg.evaluate("() => [W,H,N, document.querySelector('#view').width]"))
    pg.click('#musicBtn')
    pg.evaluate("""() => { const o = SY.play; window.__n=0; window.__d=0; window.__byc={}; SY.play = function(c,...a){ window.__n++; const r = o.call(SY,c,...a); if(!r){window.__d++; window.__byc[c]=(window.__byc[c]||0)+1;} return r; };
       window.__f=0; (function f(){ window.__f++; requestAnimationFrame(f); })(); }""")
    pg.wait_for_timeout(15000)
    print(pg.evaluate("() => ({n:__n, dropped:__d, byc:__byc, fps:__f/15, tick, pop: series[series.length-1].pop})"))
    b.close()
