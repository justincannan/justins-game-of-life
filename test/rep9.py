import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]
JS="""([base,env])=>{running=false;Object.assign(P,JSON.parse(base));P.env=env;P.autoRestart=false;P.seed=1;
const H=a=>{if(!a||a.length===undefined)return 'z';let nz=false;for(let i=0;i<a.length;i++)if(a[i]){nz=true;break;}if(!nz)return 'z';let h=2166136261;for(let i=0;i<a.length;i++){h^=(a[i]*1000)|0;h=Math.imul(h,16777619);}return (h>>>0)+':'+a.length;};
const names=['alive', 'amb', 'bmark', 'body', 'cH', 'cat', 'ccId', 'changed', 'cmap', 'co2', 'coat', 'coatK', 'coatM', 'coatS', 'dens', 'dishCell', 'dishSq', 'divT', 'divTgt', 'dor', 'en', 'fe', 'folded', 'fp', 'fp2', 'fps', 'frAmt', 'frLen', 'frLig', 'frRx', 'frStr', 'fsrc', 'fu2', 'fv2', 'fvx', 'fvy', 'fw', 'fx', 'fy', 'gen', 'hopm', 'husk', 'huskG', 'lamp', 'light', 'ltc', 'nalive', 'nbody', 'nchanged', 'ndor', 'ngen', 'nrsv', 'nxg', 'o2', 'regd', 'rsv', 'rx', 'rx2', 'rxAct', 'rxStr', 'rxStr2', 'sdiv', 'sig', 'slen', 'soma', 'tamb', 'temp', 'tlin', 'tstr', 'tsurf', 'ux', 'uy', 'vglow', 'vhot', 'wat', 'wup', 'xg', 'zmap', 'seq', 'chem'];
const snap=()=>{const o={};for(const k of names){try{const v=eval(k);o[k]=(typeof v==='number'||typeof v==='string')?v:H(v);}catch(e){o[k]='x';}}return o;};
reset('organism');const out=[snap()];for(let t=0;t<3;t++){step();out.push(snap());}return out;}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); R=[]
    for w in [400,1500]:
        pg=b.new_page(viewport={"width":620,"height":460}); pg.goto("file://"+path); pg.wait_for_timeout(w)
        base=pg.evaluate("()=>JSON.stringify(P)"); R.append(pg.evaluate(JS,[base,env])); pg.close()
    for t in range(len(R[0])):
        d=[k for k in R[0][t] if R[0][t][k]!=R[1][t][k] and k not in ('VORD','VPOOL','nalive','ngen','geneDupN','geneHGTN','hgtTried','sameCompN')]
        print(t,d)
    else: print('no diff in 60')
    b.close()
