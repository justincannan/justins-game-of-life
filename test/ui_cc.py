from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1200,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/out/cc.html'); pg.wait_for_timeout(800)
    pg.evaluate("()=>{reset(\"organism\")}");print(pg.evaluate("()=>[P.rxDom,SL]"))
    pg.evaluate("()=>{running=false;for(let t=0;t<1500;t++)step();}")
    print(pg.evaluate("()=>seqPanel().replace(/<[^>]+>/g,'')"))
    print(pg.evaluate("()=>{let i=0;while(!(alive[i]&&slen[i]>20))i++;return seqHtml(i).replace(/<br>/g,'\\n').replace(/<[^>]+>/g,'')}"))
    # check: toggle domOn off and on via checkbox
    pg.evaluate("()=>{const e=document.getElementById('domOn');e.checked=false;e.dispatchEvent(new Event('change'))}")
    print(pg.evaluate("()=>P.domOn"))
    print('errors',errs); b.close()
