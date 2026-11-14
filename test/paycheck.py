import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    print(pg.evaluate("""(x)=>{running=false;Object.assign(P,x);P.env='dish';P.dishPop=false;P.autoRestart=false;geoSeed();chemCapFill();reset('organism');for(let t=0;t<150;t++)step();
      const mol=g=>{let s=0;for(let k=0;k<16;k++)s+=((g>>>(2*k))&3);return s*P.chunit};
      let paid=0,calls=0,paidMol=0;const op=payChem;payChem=function(c,g,m,bid){const r=op(c,g,m,bid);if(r){calls++;paid+=mol(g)*m;paidMol+=mol(g);}return r};
      let rel=0;const orl=releaseChem;releaseChem=function(c,g,bid){rel+=mol(g)*P.chrecyc;return orl(c,g,bid)};
      let got=0,newborn=0,changedLive=0,diffLive=0;
      for(let t=0;t<50;t++){const wa=alive.slice(),wg=gen.slice();step();
        for(let i=0;i<N;i++){if(alive[i]&&!wa[i]){newborn++;got+=mol(gen[i]);} else if(alive[i]&&wa[i]&&gen[i]!==wg[i]){changedLive++;diffLive+=mol(gen[i])-mol(wg[i]);}}}
      return {births:newborn,payCalls:calls,paidWithExtra:+paid.toFixed(0),paidCompoundAtPayment:paidMol,compoundNewbornsHave:got,livingCellsWhoseCompoundChanged:changedLive,netChangeInThoseCompounds:diffLive,released:+rel.toFixed(0)}}""",x))
    print(errs); b.close()
