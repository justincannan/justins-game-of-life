import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; cases=json.loads(sys.argv[2]); T=int(sys.argv[3])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); errs=[]
    for env,mode,x,seed in cases:
        pg=b.new_page(viewport={"width":620,"height":460}); pg.on('pageerror',lambda e:errs.append(str(e)[:300])); pg.goto("file://"+path); pg.wait_for_timeout(400)
        base=pg.evaluate("()=>JSON.stringify(P)")
        r=pg.evaluate("""([base,env,mode,x,T,seed])=>{running=false;Object.assign(P,JSON.parse(base),x);P.env=env;P.autoRestart=false;geoSeed();chemCapFill();let s=seed;rng=()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296;};
        geneDupN=geneDelN=geneHGTN=virIntegN=0;reset(mode);const out=[];const t0=performance.now();
        for(let t=1;t<=T;t++){step(); if(t%500===0){let n=0,L=0,Lmax=0,g1=0,g2=0,g3=0,r5=0;for(let i=0;i<N;i++)if(alive[i]&&slen[i]){n++;L+=slen[i];Lmax=Math.max(Lmax,slen[i]);const k=geneSegs(seq,i*SL,slen[i]);if(k<=1)g1++;else if(k===2)g2++;else g3++; if(rx2[i])r5++;}
        out.push({t,n,L:+(L/Math.max(1,n)).toFixed(1),Lmax,g1,g2,g3,r5,dup:geneDupN,del:geneDelN,hgt:geneHGTN,integ:virIntegN});if(!n)break;}}
        return {ms:+((performance.now()-t0)/T).toFixed(1),out};}""",[base,env,mode,x,T,seed])
        print(env,mode,json.dumps(x),seed,r['ms'],'ms/tick'); [print('  ',o) for o in r['out']]; pg.close()
    print('errors',errs); b.close()
