import sys
from playwright.sync_api import sync_playwright
rich, rate, mu, unit, ticks = sys.argv[2:7]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("""() => { running=false; P.chrich=%s; P.chrate=%s; P.mu=%s; P.chunit=%s; chemCapFill(); reset('organism'); const out=[]; const t0=performance.now();
      for (let t=1;t<=%s;t++){ step(); if (t%%300===0){ census(); const s=series[series.length-1]; const top=[...codes.entries()].filter(([g,c])=>c.count>0).sort((a,b)=>b[1].count-a[1].count).slice(0,3).map(([g,c])=>c.count);
        let n=0,m=0; for(let i=0;i<N;i++) if(alive[i]){n++; m+=costOf(gen[i]);} out.push([t,s.pop,s.distinct,(births/Math.max(1,s.pop)).toFixed(3),starved,top.join('/'),(m/Math.max(1,n)).toFixed(1)]); } }
      return [out, ((performance.now()-t0)/%s).toFixed(1)+' ms/tick']; }""" % (rich, rate, mu, unit, ticks, ticks))
    print(sys.argv[2:6]); [print(x) for x in r[0]]; print(r[1])
    b.save_screenshot = None
    pg.evaluate("() => { running=true; }"); pg.wait_for_timeout(1500); pg.screenshot(path='test/shots/chem_long.png')
    b.close()
