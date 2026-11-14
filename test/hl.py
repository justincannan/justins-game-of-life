import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("""() => { running=false; P.env='even'; reset('soup'); for (let t=0;t<250;t++) step(); census();
      const cs = comps.filter(c=>c.size>=8&&c.size<=60).sort((a,b)=>b.size-a.size);
      if (!cs.length) return 'no comps '+comps.length; const c=cs[Math.floor(cs.length/2)];
      let at=-1; for (let y=c.y;y<c.y+c.hh&&at<0;y++) for (let x=c.x;x<c.x+c.w;x++) if (alive[idx(x,y)]) { at=idx(x,y); break; }
      P.showForms=true; cam.s=12; cam.x=c.x+c.w/2; cam.y=c.y+c.hh/2; inspect(at%W,(at/W)|0); render();
      const same = comps.filter(k=>k.h===c.h).length;
      return {size:c.size, sel: sel && {n:sel.n}, same, text: document.getElementById('insp').innerText.slice(-260)}; }""")
    print(r)
    pg.screenshot(path='test/shots/hl.png', clip={'x':0,'y':0,'width':900,'height':800})
    # click again on empty ground clears; step and track
    print(pg.evaluate("""() => { for (let t=0;t<30;t++) step(); census(); render(); const s1 = !!sel; inspect(0,0); const e=[...Array(N).keys()].find(i=>!alive[i]); inspect(e%W,(e/W)|0); return [s1, sel]; }"""))
    print('errors', errs); b.close()
