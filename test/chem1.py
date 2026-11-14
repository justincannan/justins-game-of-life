import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300])); pg.on('console', lambda m: print('console', m.text[:200]) if m.type=='error' else None)
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    for t in range(int(sys.argv[2]) if len(sys.argv)>2 else 8):
        pg.wait_for_timeout(4000)
        print(pg.evaluate("() => { const s=series[series.length-1]||{}; return [tick, s.pop, s.distinct, starved, births, deaths, W+'x'+H, [...codes.entries()].filter(([g,c])=>c.count>0).sort((a,b)=>b[1].count-a[1].count).slice(0,3).map(([g,c])=>rule(g)+':'+c.count).join(' | ')] }"))
    pg.screenshot(path='test/shots/chem1.png')
    b.close()
