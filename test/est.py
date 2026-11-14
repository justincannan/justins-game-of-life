import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); trials=int(sys.argv[3])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':900,'height':600}); pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        ok=0
        for k in range(trials):
            ok+=pg.evaluate("""([base,x])=>{running=false;Object.assign(P,JSON.parse(base),x);geoSeed();chemCapFill();reset('organism');for(let t=1;t<=200;t++)step();let n=0;for(let i=0;i<N;i++)n+=alive[i];return n>0?1:0}""",[base,x])
        print(json.dumps(x), '%d/%d established'%(ok,trials), flush=True)
    b.close()
