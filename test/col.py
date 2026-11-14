import sys, json
from playwright.sync_api import sync_playwright
name, c, ticks, trials = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("""([c, ticks, trials]) => { running=false; Object.assign(P, c); const res=[];
      for (let k=0;k<trials;k++){ geoSeed(); chemCapFill(); reset('organism'); let bsum=0, bn=0, psum=0;
        for (let t=1;t<=ticks;t++){ step(); if (t>ticks-200){ bsum+=births; bn++; } }
        census(); const pop=series[series.length-1].pop; const L=new Map(); let coh=0;
        for (let i=0;i<N;i++) if (alive[i]) { const l=gen[i]>>>26; L.set(l,(L.get(l)||0)+1);
          const x=i%W,y=(i/W)|0; let same=0,nn=0; for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){ if(!dx&&!dy)continue; const j=idx(x+dx,y+dy); if(alive[j]){nn++; if((gen[j]>>>26)===l) same++;} } if (nn && same*2>=nn) coh++; }
        const big=[...L.values()].filter(v=>v>=2000).length, top=Math.max(0,...L.values());
        res.push({pop, churn:+(bsum/bn/Math.max(1,pop)).toFixed(4), lineages:L.size, big, topshare:+(top/Math.max(1,pop)).toFixed(2), cohesion:+(coh/Math.max(1,pop)).toFixed(2)}); }
      return res; }""", [json.loads(c), ticks, trials])
    print(name, json.dumps(r)); print('errors', errs)
    b.close()
