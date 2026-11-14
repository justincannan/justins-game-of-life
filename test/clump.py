import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cfgs=json.loads(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); pg.goto('file://'+path); pg.wait_for_timeout(300)
    base=pg.evaluate("()=>JSON.stringify(P)")
    for env,x in cfgs:
        r=pg.evaluate("""([base,env,x])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;geoSeed();chemCapFill();reset('organism');for(const k in bstat)bstat[k]=0;
          const tr=[];let md=0,ma=0,fd=0,fa=0;
          for(let t=1;t<=1500;t++){const was=new Int32Array(N);for(let i=0;i<N;i++)was[i]=alive[i]?(body[i]?2:1):0;step();
            if(t>300)for(let i=0;i<N;i++){if(was[i]===2){ma++;if(!alive[i])md++;}else if(was[i]===1){fa++;if(!alive[i])fd++;}}
            if(t%300===0){let n=0,m=0,ad=0;for(let i=0;i<N;i++){if(alive[i]){n++;if(body[i])m++;if((xg[i]>>12)&3)ad++;}}tr.push([t,n,m,bodies.size,+(ad/Math.max(1,n)).toFixed(2)]);if(!n)break;}}
          return {env,x,tr,bstat:{...bstat},deathMember:+(md/Math.max(1,ma)).toFixed(4),deathFree:+(fd/Math.max(1,fa)).toFixed(4)}}""",[base,env,x])
        print(json.dumps(r),flush=True)
    b.close()
