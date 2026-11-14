from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/out/rg.html'); pg.wait_for_timeout(500)
    for env in ['pond','vent']:
      print(pg.evaluate("""(env)=>{running=false;P.env=env;geoSeed();chemCapFill();reset('organism');const out=[];for(let t=1;t<=2000;t++){step();if(t%500===0){let n=0,st=0,inC=0,cs=0;for(let i=0;i<N;i++)if(alive[i]){n++;cs+=coat[i];if(coat[i]>=P.coatMin)st++;if(body[i])inC++;}out.push([t,n,st,inC,bodies.size,+(cs/Math.max(1,n)).toFixed(3)]);}}return {env,out,cc:ccStat,panel:ccPanel().replace(/<[^>]+>/g,'')}}""",env))
    print(errs); b.close()
