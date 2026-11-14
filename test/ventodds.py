import sys, json
from playwright.sync_api import sync_playwright
S=int(sys.argv[2]); T=int(sys.argv[3]); x=json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for s in range(S):
        pg.evaluate("(b)=>Object.assign(P,JSON.parse(b))",base)
        r=pg.evaluate("""([s,T,x])=>{let z=(s*2654435761+12345)>>>0;rng=()=>{z^=z<<13;z>>>=0;z^=z>>>17;z^=z<<5;z>>>=0;return z/4294967296};running=false;Object.assign(P,x);P.env='vent';geoSeed();chemCapFill();reset('soup');const tr=[];
          for(let t=1;t<=T;t++){step();if(t%100===0){let n=0;for(let i=0;i<N;i++)n+=alive[i];tr.push(n);if(!n)break;}}return tr}""",[s+1,T,x])
        print('seed',s+1,r,flush=True)
    b.close()
