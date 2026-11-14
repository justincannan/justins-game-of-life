import sys, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("""([T1, T2]) => { running=false; geoSeed(); chemCapFill(); reset('organism');
      for (let t=0;t<T1;t++) step();
      // label empty components (4-neighbour)
      const lab = new Int32Array(N).fill(-1), comps=[]; const q=[];
      for (let s=0;s<N;s++){ if (alive[s]||lab[s]>=0) continue; const id=comps.length; const cells=[s]; lab[s]=id;
        for (let h=0;h<cells.length;h++){ const i=cells[h], x=i%W, y=(i/W)|0; for (const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){ const j=idx(x+dx,y+dy); if(!alive[j]&&lab[j]<0){lab[j]=id;cells.push(j);} } }
        comps.push(cells); }
      const holes = comps.filter(c=>c.length>=120 && c.length<20000);
      const area = holes.reduce((a,c)=>a+c.length,0);
      // diagnose boundary squares
      const why={interior:0, light:0, noparent:0, chem:0, other:0}; let bsq=0;
      for (const c of holes) for (const i of c){ const x=i%W,y=(i/W)|0; let n=0; const nb=[]; for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){ if(!dx&&!dy)continue; const j=idx(x+dx,y+dy); nb.push(j); n+=alive[j]; }
        if (n===0){ why.interior++; continue; } bsq++;
        if (light[i] < ZCOST[0]) { why.light++; continue; }
        let par=[]; for (const j of nb) if (alive[j] && ((B(gen[j])>>n)&1)) par.push(j);
        if (!par.length) { why.noparent++; continue; }
        let ok=false; const c0=cmap[i]<<4; for (const j of par){ const g=gen[j]; let can=true; for(let k=0;k<16;k++){ const e=(g>>>(2*k))&3; if(e && chem[c0+k] < e*P.chunit){can=false;break;} } if(can){ok=true;break;} }
        if (!ok) why.chem++; else why.other++; }
      const snap = new Uint8Array(N); for (const c of holes) for (const i of c) snap[i]=1;
      for (let t=0;t<T2;t++) step();
      let still=0; for (let i=0;i<N;i++) if (snap[i] && !alive[i]) still++;
      return {tick, pop:series[series.length-1].pop, holes:holes.length, area, sizes:holes.map(c=>c.length).sort((a,b)=>b-a).slice(0,6), boundarySquares:bsq, why, stillEmptyAfter:still, filledFrac:+(1-still/Math.max(1,area)).toFixed(2)}; }""", [int(sys.argv[2]), int(sys.argv[3])])
    print(json.dumps(r)); print('errors', errs)
    b.close()
