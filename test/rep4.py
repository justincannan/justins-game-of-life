import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; T=int(sys.argv[3]); waits=json.loads(sys.argv[4])
JS="""([base,env,T,seed])=>{running=false;Object.assign(P,JSON.parse(base));P.env=env;P.autoRestart=false;P.seed=seed;
reset('soup');const hs=[];const H=a=>{let h=2166136261;for(let i=0;i<a.length;i++){h^=a[i]*1000|0;h=Math.imul(h,16777619);}return h>>>0;};
for(let t=1;t<=T;t++){step(); if(t%100===0){let n=0;for(let i=0;i<N;i++)if(alive[i])n++;hs.push([t,n,H(gen),H(light)]);}}
return hs;}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    res=[]
    for w in waits:
        pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(w)
        base=pg.evaluate("()=>JSON.stringify(P)")
        res.append((w,pg.evaluate(JS,[base,env,T,1]))); pg.close()
    b.close()
for k in range(len(res[0][1])):
    row=[r[1][k] for r in res]; same=all(x==row[0] for x in row)
    print(row[0][0], 'same' if same else 'DIFF', [x[1:] for x in row] if not same else row[0][1])
    if not same: break
