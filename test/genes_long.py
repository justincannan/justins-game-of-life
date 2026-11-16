import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env,mode,seed,T=sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]); X=json.loads(sys.argv[6]) if len(sys.argv)>6 else {}
JS="""([base,env,mode,T,seed,X])=>{running=false;Object.assign(P,JSON.parse(base),X);P.env=env;P.autoRestart=false;P.seed=seed;
geneDupN=geneDelN=geneHGTN=virIntegN=0;reset(mode);const out=[];const t0=performance.now();let pick=-1;
const ham=(o1,o2,L)=>{let d=0;for(let h=0;h<L;h++)if(seq[o1+h]!==seq[o2+h])d++;return d;};
for(let t=1;t<=T;t++){step(); if(t%1000===0){let n=0,L=0,Lmax=0,G=0,multi=0,gmax=0,mk=0,twins=0,div=0,divRx=0,pairs=0,rxc=0,rx5=0,best=0,oV=0,oO=0;const OG=ORG();
 for(let i=0;i<N;i++){if(!alive[i]||!slen[i])continue;n++;const o=i*SL,Ln=slen[i];L+=Ln;Lmax=Math.max(Lmax,Ln);const k=geneSegs(seq,o,Ln);G+=k;if(k>1)multi++;gmax=Math.max(gmax,k);
  for(let h=0;h<Ln;h++){const v=OG[o+h];if(v===1)oO++;else if(v===2)oV++;}const sg=[];for(let q=0;q<k;q++)sg.push([gSeg[2*q],gSeg[2*q+1]]);let inG=0;for(const [a,b] of sg)inG+=b-a;mk+=Ln-inG;
  if(k>=2&&k>best){best=k;pick=i;}
  for(let r=0;r<4;r++){if((rx[i]>>>(8*r))&255)rxc++;if((rx2[i]>>>(8*r))&255)rxc++;} if(rx2[i])rx5++;
  if(k<2)continue;const rxg=sg.map(([a,b])=>{infoldGene(seq,o+a,b-a);return lastRx>>>0;});
  for(let p=0;p<k;p++)for(let q=p+1;q<k;q++){const la=sg[p][1]-sg[p][0],lb=sg[q][1]-sg[q][0];if(la!==lb||la<3)continue;pairs++;const d=ham(o+sg[p][0],o+sg[q][0],la);
   if(d===0)twins++;else if(d<=Math.max(1,la/4)){div++;if(rxg[p]!==rxg[q])divRx++;}}}
 out.push({t,n,len:+(L/Math.max(1,n)).toFixed(1),Lmax,genes:+(G/Math.max(1,n)).toFixed(2),multi:Math.round(100*multi/Math.max(1,n)),gmax,mark:Math.round(100*mk/Math.max(1,L)),
  samePairs:pairs,twins,diverged:div,divNewRx:divRx,rxPerCell:+(rxc/Math.max(1,n)).toFixed(2),cellsOver4rx:rx5,virusPct:+(100*oV/Math.max(1,L)).toFixed(2),outsidePct:+(100*oO/Math.max(1,L)).toFixed(2),domCost:+domCostSum.toFixed(0),dup:geneDupN,del:geneDelN,hgt:geneHGTN,integ:virIntegN});if(!n)break;}}
let html='';if(pick>=0&&alive[pick])html=geneListHtml(pick);
return {ms:+((performance.now()-t0)/T).toFixed(1),out,html};}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); errs=[]
    pg=b.new_page(viewport={"width":620,"height":460}); pg.on('pageerror',lambda e:errs.append(str(e)[:300])); pg.goto("file://"+path); pg.wait_for_timeout(400)
    base=pg.evaluate("()=>JSON.stringify(P)")
    r=pg.evaluate(JS,[base,env,mode,T,seed,X])
    print(json.dumps({'X':X,'env':env,'mode':mode,'seed':seed,'ms':r['ms'],'out':r['out'],'errors':errs}))
    open(f'/tmp/genehtml_{env}_{seed}_{len(X)}.html','w').write(r['html']); b.close()
