from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1200,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/out/hom.html'); pg.wait_for_timeout(800)
    for id_,v in [('mateThr','0.4'),('hgtHom','3')]:
        pg.evaluate(f"()=>{{const e=document.getElementById('{id_}');e.value='{v}';e.dispatchEvent(new Event('input'))}}")
    print(pg.evaluate("()=>[P.mateThr,P.hgtHom]"))
    pg.evaluate("()=>{running=false;for(let t=0;t<300;t++)step();specStep();}")
    print(pg.evaluate("()=>specPanel().replace(/<[^>]+>/g,'')"))
    print('errors',errs); b.close()
