import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    r=pg.evaluate("""(base)=>{running=false;Object.assign(P,JSON.parse(base));P.env='vent';P.autoRestart=false;P.seed=12;P.domCost=0;reset('organism');const out=[];
      for(let t=1;t<=3060;t++){step();if(t>=3010&&t%3===0){let n=0,inB=0,neg=0,kill=0,wet=0;const bs=new Map();let lsum=0;for(let i=0;i<N;i++){if(!alive[i])continue;n++;lsum+=light[i];if(light[i]<0)neg++;if(VIR.kill&&VIR.kill[i])kill++;if(body[i]){inB++;bs.set(body[i],(bs.get(body[i])||0)+1);}}
        let big=0;for(const v of bs.values())if(v>big)big=v; let w=0;for(let c=0;c<wat.length;c++)w+=wat[c];let co=0;for(let c=0;c<co2.length;c++)co+=co2[c];
        out.push({t,n,light:+(lsum/n).toFixed(2),neg,kill,inBody:inB,bodies:bs.size,biggest:big,wat:+(w/wat.length).toFixed(3),co2:+(co/co2.length).toFixed(3),starved:typeof starved!=='undefined'?starved:-1});}}return out;}""",base)
    for o in r: print(o)
    b.close()
