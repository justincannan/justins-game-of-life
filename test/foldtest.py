import sys
from playwright.sync_api import sync_playwright
STATE="""()=>{const ids=new Set();let a=0,i=0,e=0,h=0,m=0,s=0,gsum=0;const win=popWin;
 for(let k=0;k<N;k++){if(alive[k]){if(dor[k])i++;else{a++;e+=light[k];}ids.add(gen[k]+'|'+xg[k]+'|'+(P.seqOn?Array.from(seq.subarray(k*SL,k*SL+slen[k])).join(','):''));}if(husk&&husk[k]>0)h++;}
 for(let q=0;q<chem.length;q++)m+=chem[q];for(let c=0;c<en.length;c++)s+=en[c];
 return {active:a,inactive:i,genotypes:ids.size,energyActive:+e.toFixed(1),remains:h,molecules:+m.toFixed(0),sugar:+s.toFixed(1)}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1400,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(800)
    pg.evaluate('()=>{window._T=600}'); pg.select_option('#envsel','dishpop'); pg.click('#reset'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{running=false;for(let k=0;k<(+window._T||2500);k++)step();}")
    pg.evaluate("""()=>{const L=POP.L,c=(L-1)/2;let best=-1,bd=0;for(let q=0;q<L*L;q++)if(popA[q]+popI[q]>0){const d=Math.hypot(q%L-c,((q/L)|0)-c);if(d>bd){bd=d;best=q;}}
      const {s,ox,oy}=popGeom();window._xy=[Math.floor(ox+(c+(best%L-c)*0.8)*s),Math.floor(oy+(c+(((best/L)|0)-c)*0.8)*s)];inspect(..._xy);}""")
    print('opened         ', pg.evaluate(STATE))
    pg.evaluate("()=>{P.mu*=20;for(let c=0;c<en.length;c++)en[c]*=4;for(let k=0;k<300;k++)step();}")
    before=pg.evaluate(STATE); print('after 300 ticks', before)
    pg.evaluate("()=>popFold()"); pg.evaluate("()=>inspect(..._xy)")
    after=pg.evaluate(STATE); print('reopened       ', after)
    print('genotype table size', pg.evaluate("()=>popGT.length"), 'records', pg.evaluate("()=>popRec.size"))
    print('errors',errs); b.close()
