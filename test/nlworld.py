import sys, json
from playwright.sync_api import sync_playwright
cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3])
JS="""([x,T])=>{running=false;Object.assign(P,x);geoSeed();chemCapFill();reset(x.mode||'soup');const out=[];
for(let t=1;t<=T;t++){step();if(t%250===0){let n=0,l=0,iso=0;const lin=new Set();for(let i=0;i<N;i++)if(alive[i]){n++;l+=light[i];lin.add(gen[i]>>>28);}
out.push([t,n,+(l/Math.max(1,n)).toFixed(2),births,deaths,lin.size]);if(!n)break;}}return {N,out}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        pg.evaluate("(b)=>Object.assign(P,JSON.parse(b))",base)
        r=pg.evaluate(JS,[x,T]); print(x, 'N',r['N']); [print('  ',row) for row in r['out']]
    print(errs); b.close()
