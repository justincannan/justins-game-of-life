import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    r=pg.evaluate("""(base)=>{running=false;Object.assign(P,JSON.parse(base));P.env='vent';P.autoRestart=false;P.seed=12;P.domCost=0;reset('organism');
      for(let t=1;t<3034;t++)step();
      const was=new Uint8Array(N);for(let i=0;i<N;i++)was[i]=alive[i]&&body[i]?1:0;
      const L0=light.slice(),D0=dor.slice(),T0=temp.slice(),W0=wat.slice(),G0=gen.slice(),K0=VIR.kill?VIR.kill.slice():null;
      const c0={dried,heated:typeof heated!=='undefined'?heated:0,deaths,eaten:typeof eaten!=='undefined'?eaten:0};
      step();
      const c1={dried,heated:typeof heated!=='undefined'?heated:0,deaths,eaten:typeof eaten!=='undefined'?eaten:0};
      let died=0,neg=0,kill=0,dorm=0,hot=0,thf=0,dry=0;let samp=[];
      for(let i=0;i<N;i++){if(!was[i]||alive[i])continue;died++;if(L0[i]<0)neg++;if(K0&&K0[i])kill++;if(D0[i])dorm++;const tf=thermFit(G0[i],T0[cmap[i]]);thf+=tf;if(W0[cmap[i]]<P.wdry)dry++;if(samp.length<5)samp.push([i,L0[i].toFixed(2),tf.toFixed(3),W0[cmap[i]].toFixed(2),T0[cmap[i]].toFixed(2)]);}
      return {died,neg,kill,dorm,meanThermFit:+(thf/Math.max(1,died)).toFixed(3),inDry:dry,c0,c1,heatHarm:P.heatHarm,wdry:P.wdry,samp,tick,dryHarm:P.dryHarm};}""",base)
    print(json.dumps(r,indent=0)); b.close()
