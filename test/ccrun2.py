import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); trials=int(sys.argv[4])
JS="""([base,env,x,T])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');let est=0;const cls=i=>{if(!body[i])return 0;const x=i%W,y=(i/W)|0;for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dy)continue;const j=((y+dy+H)%H)*W+((x+dx+W)%W);if(!alive[j]||body[j]!==body[i])return 2;}return 1;};
const bc=[0,0,0];const orig=seqBirth;
for(let t=1;t<=T;t++){if(t===T-1000)seqBirth=function(i,pj,pb,rate){if(pj>=0)bc[cls(pj)]++;return orig(i,pj,pb,rate);};step();if(t===200){let n=0;for(let i=0;i<N;i++)n+=alive[i];est=n>0;}}
seqBirth=orig;const cc=[0,0,0],ca=[0,0,0];for(let i=0;i<N;i++){if(!alive[i])continue;const k=cls(i);cc[k]++;ca[k]+=rxAct[i];}
let n=0,inB=0,st=0;const mem=new Map();for(let i=0;i<N;i++){if(!alive[i])continue;n++;if(coat[i]>=P.coatMin)st++;const b=body[i];if(b){inB++;(mem.get(b)||mem.set(b,[]).get(b)).push(i);}}
let ws=0,wn=0,rs=0,rn=0;const all=[];for(let i=0;i<N;i+=13)if(alive[i]&&slen[i]>2)all.push(i);
for(let k=0;k<400&&all.length>1;k++){rs+=seqSim(all[(rng()*all.length)|0],all[(rng()*all.length)|0]);rn++;}
let sz=0,nb=0;for(const[,m]of mem){if(m.length<4)continue;nb++;sz+=m.length;for(let k=0;k<6;k++){const a=m[(rng()*m.length)|0],b=m[(rng()*m.length)|0];if(a!==b){ws+=seqSim(a,b);wn++;}}}
const w=wn?ws/wn:0,r=rn?rs/rn:0;
return {env,x,est,n,inClumps:+(inB/Math.max(1,n)).toFixed(3),clumps:nb,meanSize:+(sz/Math.max(1,nb)).toFixed(1),sticky:+(st/Math.max(1,n)).toFixed(3),relatedness:wn?+((w-r)/(1-r)).toFixed(2):null,within:+w.toFixed(2),random:+r.toFixed(2),
 formed:ccStat.fromFree,split:ccStat.fromSplit,merged:ccStat.merged,eaten:typeof eaten!=='undefined'?eaten:null,species:specStat.n,cells:{free:cc[0],inner:cc[1],edge:cc[2]},rxActivity:{free:+(ca[0]/Math.max(1,cc[0])).toFixed(2),inner:+(ca[1]/Math.max(1,cc[1])).toFixed(2),edge:+(ca[2]/Math.max(1,cc[2])).toFixed(2)},birthsPerCell1000:{free:+(bc[0]/Math.max(1,cc[0])).toFixed(2),inner:+(bc[1]/Math.max(1,cc[1])).toFixed(2),edge:+(bc[2]/Math.max(1,cc[2])).toFixed(2)}}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        for k in range(trials): print(json.dumps(pg.evaluate(JS,[base,env,x,T])),flush=True)
    print('errors',errs); b.close()
