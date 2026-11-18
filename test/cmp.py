import sys, json
from playwright.sync_api import sync_playwright
env, mode, T = sys.argv[1], sys.argv[2], int(sys.argv[3]); X=json.loads(sys.argv[4])
JS="""([env,mode,T,X])=>{running=false;Object.assign(P,X);P.env=env;P.autoRestart=false;P.seed=1;reset(mode);
const H=a=>{let h=2166136261;for(let i=0;i<a.length;i++){h^=(a[i]*1000)|0;h=Math.imul(h,16777619);}return h>>>0;};
const out=[];for(let t=1;t<=T;t++){step();if(t%100===0){let n=0;for(let i=0;i<N;i++)if(alive[i])n++;out.push([t,n,H(gen),H(light)]);}}return out;}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); R=[]
    for path in ['/tmp/head/base.html','/home/claude/justins-game-of-life/build/justins_game_of_life.html']:
        pg=b.new_page(viewport={"width":620,"height":460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200])); pg.goto("file://"+path); pg.wait_for_timeout(400)
        R.append(pg.evaluate(JS,[env,mode,T,X])); pg.close()
        if errs: print(errs)
    for a,c in zip(*R): print(a[0], 'same' if a==c else 'DIFF', a[1], c[1])
    b.close()
