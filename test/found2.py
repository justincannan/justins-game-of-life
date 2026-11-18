import sys, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); errs=[]
    pg=b.new_page(viewport={"width":620,"height":460}); pg.on('pageerror',lambda e:errs.append(str(e)[:200])); pg.goto("file:///home/claude/justins-game-of-life/build/justins_game_of_life.html"); pg.wait_for_timeout(400)
    r=pg.evaluate("""()=>{const out={};for(const env of ['pond','vent','dish','springs'])for(const on of [false,true]){let f=0,tot=0;const ns=[];
      for(let sd=21;sd<=28;sd++){running=false;P.codeOn=on;P.env=env;P.autoRestart=false;P.seed=sd;reset('organism');for(let t=0;t<400;t++)step();let n=0;for(let i=0;i<N;i++)if(alive[i])n++;ns.push(n);tot++;if(n>100)f++;}
      out[env+(on?'_code':'_direct')]=f+' of '+tot+'  ('+ns.join(',')+')';}return out;}""")
    for k,v in r.items(): print(k,v)
    print(errs); b.close()
