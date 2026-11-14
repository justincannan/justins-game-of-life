import sys, json
from playwright.sync_api import sync_playwright
x=json.loads(sys.argv[2]); T=int(sys.argv[3])
JS="""([x,T])=>{running=false;Object.assign(P,x);geoSeed();chemCapFill();reset(x.mode||'soup');const out=[];
for(let t=1;t<=T;t++){step();if(t%500===0){let n=0;for(let i=0;i<N;i++)n+=alive[i];let kinds=new Set(),amt=0,cat=0;if(frAmt)for(let q=0;q<frAmt.length;q++)if(frAmt[q]>=.5){amt+=frAmt[q];kinds.add(Array.from(frSeq.subarray(q*FL,q*FL+frLen[q])).join(''));if(frRx[q])cat++;}
const agg=new Map();if(frAmt)for(let q=0;q<frAmt.length;q++)if(frAmt[q]>=.5){const k=Array.from(frSeq.subarray(q*FL,q*FL+frLen[q])).map(v=>MONO[v]).join('');const r=agg.get(k)||{a:0,sq:0};r.a+=frAmt[q];r.sq++;agg.set(k,r);}const top=[...agg.entries()].sort((u,v)=>v[1].a-u[1].a).slice(0,3).map(([k,r])=>k+' x'+r.a.toFixed(0)+' in '+r.sq);let tot=0;for(const r of agg.values())tot+=r.a;
out.push({t,cells:n,topShare:+(agg.size?[...agg.values()].reduce((m,r)=>Math.max(m,r.a),0)/tot:0).toFixed(3),top,longestNow:(()=>{let m=0;if(frAmt)for(let q=0;q<frAmt.length;q++)if(frAmt[q]>=.5)m=Math.max(m,frLen[q]);return m})(),meanLen:(()=>{let s=0,w=0;if(frAmt)for(let q=0;q<frAmt.length;q++)if(frAmt[q]>=.5){s+=frLen[q]*frAmt[q];w+=frAmt[q];}return +(s/Math.max(1,w)).toFixed(2)})(),ligaseSlots:(()=>{let k=0;if(frAmt)for(let q=0;q<frAmt.length;q++)if(frAmt[q]>=.5&&frLig[q])k++;return k})(),fragmentSlots:fragCount(),distinctSequences:kinds.size,copies:+amt.toFixed(0),slotsThatCatalyse:cat,...Object.fromEntries(Object.entries(FRS).map(([k,v])=>[k,+v.toFixed(0)]))});}}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    for r in pg.evaluate(JS,[x,T]): print(r)
    print(pg.evaluate("()=>document.getElementById('hud').textContent.slice(0,200)"))
    print(errs); b.close()
