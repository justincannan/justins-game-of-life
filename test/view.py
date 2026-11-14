from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':700,'height':600}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/out/cc.html'); pg.wait_for_timeout(500)
    svg=pg.evaluate("""()=>{running=false;P.env='vent';geoSeed();chemCapFill();reset('organism');for(let t=0;t<1500;t++)step();let i=0;for(;i<N;i++)if(alive[i]&&body[i])break;if(i>=N){i=0;while(!alive[i])i++;}return cellSvg(i)}""")
    pg.set_content('<html><body style="background:#0d0d0d;--ink:#f0efec;--muted:#898781;--accent:#3987e5;--surface:#1a1a19">'+svg+'</body></html>')
    pg.screenshot(path='/home/claude/out/cellview.png'); print(errs, len(svg)); b.close()
