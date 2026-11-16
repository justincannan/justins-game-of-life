import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cases=json.loads(sys.argv[2]); T=int(sys.argv[3])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); errs=[]
    for env,mode,x,seed in cases:
        pg=b.new_page(viewport={"width":620,"height":460}); pg.on('pageerror',lambda e:errs.append(str(e)[:300])); pg.goto("file://"+path); pg.wait_for_timeout(400)
        base=pg.evaluate("()=>JSON.stringify(P)")
        r=pg.evaluate("""([base,env,mode,x,T,seed])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;P.autoRestart=false;geoSeed();chemCapFill();let s=seed;rng=()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296;};reset(mode);const out=[];
        for(let t=1;t<=T;t++){step(); if(t%500===0){let n=0,pgc=0,het=0,phO=0;for(let i=0;i<N;i++)if(alive[i]){n++;const pgm=coatM&&coatK[i]>=12&&coatM[i]>0;if(pgm)pgc++;const h=(xg[i]>>10)&3;if(h)het++;if(!pgm&&h)phO++;}
        let D=0;if(DET.a)for(let c=0;c<DET.a.length;c++)D+=DET.a[c];
        out.push({t,n,pig:+(pgc/Math.max(1,n)).toFixed(2),het:+(het/Math.max(1,n)).toFixed(2),hetOnly:+(phO/Math.max(1,n)).toFixed(2),detMade:Math.round(DET.made),toSugar:Math.round(DET.toSugar),det:Math.round(D)});if(!n)break;}}return out;}""",[base,env,mode,x,T,seed])
        print(env,mode,json.dumps(x),seed,[(o['t'],o['n'],o['pig'],o['hetOnly'],o['detMade'],o['toSugar'],o['det']) for o in r],flush=True); pg.close()
    print('errors',errs); b.close()
