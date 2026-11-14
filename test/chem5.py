import sys
from playwright.sync_api import sync_playwright
rich, rate, mu, unit, dur = sys.argv[2:7]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    pg.evaluate("() => { P.chrich=%s; P.chrate=%s; P.mu=%s; P.chunit=%s; P.speed=8; chemCapFill(); reset('organism'); }" % (rich, rate, mu, unit))
    for t in range(int(dur)):
        pg.wait_for_timeout(6000)
    r = pg.evaluate("() => { const s=series[series.length-1]||{}; const top=[...codes.entries()].filter(([g,c])=>c.count>0).sort((a,b)=>b[1].count-a[1].count).slice(0,3).map(([g,c])=>c.count); let m=0,n=0; for(let i=0;i<N;i++) if(alive[i]){n++; m+=costOf(gen[i]);} return {cfg:'%s %s %s %s', tick, pop:s.pop, distinct:s.distinct, churn:(births/Math.max(1,s.pop)).toFixed(3), starved, top, avgcost:(m/Math.max(1,n)).toFixed(1)} }" % (rich, rate, mu, unit))
    print(r)
    b.close()
