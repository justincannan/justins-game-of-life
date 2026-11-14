import sys, json
from playwright.sync_api import sync_playwright
path=sys.argv[1]; env=sys.argv[2]; extra=json.loads(sys.argv[3]); T=int(sys.argv[4]); trials=int(sys.argv[5])
JS="""([env,extra,T]) => { running=false; P.env=env; Object.assign(P, extra); geoSeed(); chemCapFill(); reset('organism');
 let est=0; for (let t=1;t<=T;t++){ step(); if(t===200){ let k=0; for(let i=0;i<N;i++) k+=alive[i]; est=k>0?1:0; } }
 let n=0,g=[0,0,0,0,0,0,0,0],mx=[0,0,0,0,0,0,0,0]; for (let i=0;i<N;i++) if (alive[i]) { n++; for (let q=0;q<8;q++){ const e=(xg[i]>>(2*q))&3; if (e) g[q]++; if(e>mx[q]) mx[q]=e; } }
 return {est, occ:+(n/N).toFixed(3), g:g.map(v=>+(v/Math.max(1,n)).toFixed(2)), eaten, bodies:bodies.size, inb:(()=>{let b=0;for(let i=0;i<N;i++) if(alive[i]&&body[i]) b++; return +(b/Math.max(1,n)).toFixed(2)})(), got:enTaken?+(enGot/enTaken).toFixed(2):0}; }"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    res=[pg.evaluate(JS,[env,extra,T]) for _ in range(trials)]
    alive=[r for r in res if r['occ']>0.01]
    m=lambda k:round(sum(r[k] for r in alive)/len(alive),3) if alive else None
    gm=[round(sum(r['g'][q] for r in alive)/len(alive),2) for q in range(8)] if alive else None
    print(json.dumps({'cfg':extra,'env':env,'surv':'%d/%d'%(len(alive),trials),'est':sum(r['est'] for r in res),'survOfEst':'%d/%d'%(sum(1 for r in res if r['est'] and r['occ']>0.01),sum(r['est'] for r in res)),'occ':m('occ'),'genes':gm,'eaten':m('eaten'),'bodies':m('bodies'),'inBody':m('inb'),'errs':errs}))
    b.close()
