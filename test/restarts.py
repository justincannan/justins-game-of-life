import sys, json
from playwright.sync_api import sync_playwright
worlds=json.loads(sys.argv[2]); S=int(sys.argv[3]); T=int(sys.argv[4])
JS="""([w,seed,T])=>{running=false;P.env=w;P.autoRestart=true;P.seed=seed;geoSeed();chemCapFill();restarts=0;reset('organism');const tr=[];let dead=-1;
for(let t=1;t<=T;t++){step();if(t%50===0||t===10){let n=0;for(let i=0;i<N;i++)n+=alive[i];if(t%250===0)tr.push(n);if(!n&&dead<0){dead=t;break;}}}
return {restarts,deadAt:dead,at250s:tr}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for w in worlds:
        for s in range(S):
            pg.evaluate("(b)=>Object.assign(P,JSON.parse(b))",base)
            pg.evaluate("(a)=>{let x=(a*2654435761)>>>0;rng=()=>{x^=x<<13;x>>>=0;x^=x>>>17;x^=x<<5;x>>>=0;return x/4294967296};return 0}",s+1)
            print(w,s,json.dumps(pg.evaluate(JS,[w,s+1,T])),flush=True)
    print('errors',errs); b.close()
