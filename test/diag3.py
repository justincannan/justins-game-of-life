import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    r=pg.evaluate("""(base)=>{running=false;Object.assign(P,JSON.parse(base));P.env='vent';P.autoRestart=false;P.seed=12;P.domCost=0;reset('organism');const out=[];
      for(let t=1;t<=3040;t++){step();if(t>=3024){let n=0,st=0,cs=0,inB=0,lB=0,lO=0,nO=0,dorm=0,rxa=0;const bs=new Map();for(let i=0;i<N;i++){if(!alive[i])continue;n++;cs+=coat[i];if(!dor[i]&&coat[i]>=P.coatMin)st++;if(dor[i])dorm++;rxa+=rxAct[i];
          if(body[i]){inB++;lB+=light[i];bs.set(body[i],(bs.get(body[i])||0)+1);}else{lO+=light[i];nO++;}}
        let big=0;for(const v of bs.values())if(v>big)big=v;let e=0;for(let c=0;c<en.length;c++)e+=en[c];
        out.push({t,n,sticky:st,coatAvg:+(cs/n).toFixed(3),coatMin:P.coatMin,biggest:big,lightInB:+(lB/Math.max(1,inB)).toFixed(2),lightOut:+(lO/Math.max(1,nO)).toFixed(2),dorm,rxAct:+(rxa/n).toFixed(3),sugar:+e.toFixed(0)});}}return out;}""",base)
    for o in r: print(o)
    b.close()
