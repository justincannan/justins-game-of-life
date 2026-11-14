import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    print(pg.evaluate("""()=>{running=false;P.env='dish';P.lifeRule=false;P.autoRestart=false;geoSeed();chemCapFill();reset('organism');
    const r=[[P.o2air,P.dishAir,o2[0],en[0],fe[0],o2.length,en.length]];for(let t=0;t<4;t++){step();let bad=0;for(let c=0;c<o2.length;c++)if(!isFinite(o2[c]))bad++;let be=0;for(let c=0;c<en.length;c++)if(!isFinite(en[c]))be++;r.push([t,o2[0],en[0],bad,be]);}return r}"""))
    print(errs); b.close()
