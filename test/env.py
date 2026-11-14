import sys, json
from playwright.sync_api import sync_playwright
env, trials, ticks = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
extra = sys.argv[5] if len(sys.argv)>5 else '{}'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("""([env, trials, ticks, extra]) => { running=false; P.env=env; Object.assign(P, extra); const res=[]; const t0=performance.now();
      for (let k=0;k<trials;k++){ geoSeed(); chemCapFill(); reset('organism'); const track=[];
        for (let t=1;t<=ticks;t++){ step(); if (t%%300===0){ census(); track.push(series[series.length-1].pop); } }
        let n=0, th=[0,0,0,0], tsum=0; for (let i=0;i<N;i++) if (alive[i]) { n++; th[(gen[i]>>>26)&3]++; tsum+=temp[cmap[i]]; }
        res.push({track, thermo: th.map(v=>+(v/Math.max(1,n)).toFixed(2)), meanT:+(tsum/Math.max(1,n)).toFixed(2), heated, churn:+(births/Math.max(1,n)).toFixed(3)}); }
      return {res, ms:((performance.now()-t0)/(trials*ticks)).toFixed(1)}; }""".replace('%%','%'), [env, trials, ticks, json.loads(extra)])
    print(env, json.dumps(r)); print('errors', errs)
    b.close()
