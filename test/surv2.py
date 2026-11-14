import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':620,'height':460}); pg.goto('file://'+path); pg.wait_for_timeout(300)
    for name,extra in [('all',{}),('quorum only',{'gProd':False,'gSex':False}),('prod only',{'gSex':False}),('sex only',{'gProd':False}),('no ext',{'qmut':0})]:
        r = pg.evaluate("""([extra]) => { running=false; P.env='even'; P.gProd=true; P.gSex=true; P.gPred=false; P.qmut=1; Object.assign(P, extra); let ok=0; const ns=[];
          for (let k=0;k<10;k++){ geoSeed(); chemCapFill(); reset('organism'); for (let t=0;t<300;t++) step(); let n=0; for (let i=0;i<N;i++) if (alive[i]) n++; ns.push(n); if (n>200) ok++; } return [ok, ns]; }""", [extra])
        print(name, r)
    b.close()
