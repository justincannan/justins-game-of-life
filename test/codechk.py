import sys, json
from playwright.sync_api import sync_playwright
env, mode, T = sys.argv[1], sys.argv[2], int(sys.argv[3]); seeds=json.loads(sys.argv[4])
JS="""([env,mode,T,seed,on])=>{running=false;P.codeOn=on;P.env=env;P.autoRestart=false;P.seed=seed;reset(mode);const t0=performance.now();
for(let t=1;t<=T;t++)step();const ms=(performance.now()-t0)/T;let n=0,bad=0,chk=0,drift=0;
for(let i=0;i<N;i++){if(!alive[i])continue;n++;if(!on||!slen[i])continue;chk++;if(ctabD[i])drift++;const o=i*SL;for(let h=0;h<slen[i];h++)if(codTr(i,cod[o+h])!==seq[o+h]){bad++;break;}}
return {on,seed,n,ms:+ms.toFixed(1),cellsChecked:chk,cellsBad:bad,drifted:drift,silent:codSilent,sense:codSense,tabMut:codTabMut,mutLetters:RM.mut};}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    for sd in seeds:
        for on in [False, True]:
            pg=b.new_page(viewport={"width":620,"height":460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200])); pg.goto("file:///home/claude/justins-game-of-life/build/justins_game_of_life.html"); pg.wait_for_timeout(400)
            print(env,mode,pg.evaluate(JS,[env,mode,T,sd,on]),errs); pg.close()
    b.close()
