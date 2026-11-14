import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2])
JS="""(x)=>{running=false;Object.assign(P,x);P.env='dish';P.autoRestart=false;geoSeed();chemCapFill();reset('organism');const out=[];
for(let t=1;t<=300;t++){
 const was=alive.slice(),L=light.slice();step();
 if(t%30===0){let n=0,iso=0,mot=0,dl=0,dd=0,dorN=0;for(let i=0;i<N;i++){if(was[i]&&!alive[i]){dd++;if(L[i]<.08)dl++;}
  if(!alive[i])continue;n++;if(dor[i])dorN++;if((gen[i]>>>16)&3)mot++;const X=i%W,Y=(i/W)|0;let k=0;for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++)if(a||b)k+=alive[((Y+a+H)%H)*W+(X+b+W)%W];if(!k)iso++;}
  out.push({t,n,iso,mot,dorN,glided,diedThisTick:dd,diedLowLight:dl,births});}}
return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    for r in pg.evaluate(JS,x): print(r)
    print(errs); b.close()
