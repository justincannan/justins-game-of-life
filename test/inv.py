import sys, json
from playwright.sync_api import sync_playwright
cfgs = json.loads(sys.argv[2])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    for name, c in cfgs.items():
        r = pg.evaluate("""(c) => { running=false; Object.assign(P, c); P.mu=0; P.speed=1; const res=[];
          for (let trial=0; trial<4; trial++) {
            geoSeed(); chemCapFill(); reset('blank'); chem.fill(0); chem.set(chemCap); 
            const cx=Math.round(W*.35), cy=H>>1, LA=(LIFE|(5<<26))>>>0, EX=(0x555F|(9<<26))>>>0;
            for (let y=-40;y<=40;y++) for (let x=-40;x<=40;x++) if (x*x+y*y<=1600 && rng()<.35) { const i=idx(cx+x,cy+y); alive[i]=1; gen[i]=LA; }
            changed.fill(1);
            for (let t=0;t<150;t++) step();
            let a0=0; for (let i=0;i<N;i++) if (alive[i] && (gen[i]>>>26)===5) a0++;
            for (let y=-5;y<=5;y++) for (let x=-5;x<=5;x++) if (x*x+y*y<=25 && rng()<.5) { const i=idx(cx+44+x,cy+y); alive[i]=1; gen[i]=EX; }
            changed.fill(1);
            for (let t=0;t<400;t++) step();
            let a=0,bb=0; for (let i=0;i<N;i++) if (alive[i]) { if ((gen[i]>>>26)===5) a++; else if ((gen[i]>>>26)===9) bb++; }
            res.push([a0,a,bb]);
          } return res; }""", c)
        print(name, r)
    print('errors', errs)
    b.close()
