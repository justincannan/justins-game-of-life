import sys, json
from playwright.sync_api import sync_playwright
# how lopsided is the dish colony? centroid offset (in plate radii) and the spread of cells over 8 sectors, per setting
path=sys.argv[1]; cfgs=json.loads(sys.argv[2]); T=int(sys.argv[3]); seeds=json.loads(sys.argv[4])
JS="""([base,x,T,seed])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env='dish';geoSeed();chemCapFill();P.autoRestart=false;if(x.H4&&H%4){allocWorld(W,H-H%4,false);geoSeed();chemCapFill();}
let s=seed>>>0||1;rng=()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296;};reset("organism");const out=[];
let fxs=0;for(let c=0;c<(typeof fx!=='undefined'&&fx?fx.length:0);c++)fxs+=Math.abs(fx[c])+Math.abs(fy[c]);
for(let t=1;t<=T;t++){step();if(t%250===0){let n=0,sx=0,sy=0;const sec=new Array(8).fill(0);const cx=W/2,cy=H/2;
 for(let i=0;i<N;i++)if(alive[i]){const x=i%W-cx+.5,y=((i/W)|0)-cy+.5;n++;sx+=x;sy+=y;sec[((Math.atan2(y,x)+Math.PI)/(2*Math.PI)*8|0)%8]++;}
 const R=W/2*P.dishR,mx=n?Math.max(...sec)/(n/8):0,mn=n?Math.min(...sec)/(n/8):0;
 out.push({t,n,cx:+(sx/n/R).toFixed(3),cy:+(sy/n/R).toFixed(3),secMax:+mx.toFixed(2),secMin:+mn.toFixed(2),drifted:typeof drifted!=='undefined'?drifted:null});}}
return {x,seed,WH:[W,H,cw,chh],flowSum:+fxs.toFixed(2),out};}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file://'+path); pg.wait_for_timeout(500); base=pg.evaluate("()=>JSON.stringify(P)")
    for x in cfgs:
        for sd in seeds: print(json.dumps(pg.evaluate(JS,[base,x,T,sd])),flush=True)
    print('errors',errs); b.close()
