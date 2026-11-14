import sys, json
from playwright.sync_api import sync_playwright
path, env, params, trials, t1 = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
JS = """([env, params, t1, seedk]) => {
  running=false; P.env=env; Object.assign(P, params); geoSeed(); chemCapFill(); reset('organism');
  const BS=6, bw=Math.floor(W/BS), bh=Math.floor(H/BS);
  const bare = () => { const m=new Uint8Array(bw*bh); for (let by=0;by<bh;by++) for (let bx=0;bx<bw;bx++) { let c=0; for (let y=by*BS;y<by*BS+BS&&!c;y++) for (let x=bx*BS;x<bx*BS+BS;x++) if (alive[y*W+x]) { c=1; break; } m[by*bw+bx]=c?0:1; } return m; };
  for (let t=1;t<=t1;t++) step();
  const e1=new Uint8Array(N), g1=new Uint32Array(N); for (let i=0;i<N;i++) if (alive[i]) { g1[i]=gen[i]; const s=strategyAt(i); e1[i]= s==='spore'?1:s==='rhizome'?2:3; }
  const b1=bare(); for (let t=0;t<300;t++) step(); const b2=bare();
  let n1=0, both=0, n2=0; for (let k=0;k<bw*bh;k++) { if (b1[k]) { n1++; if (b2[k]) both++; } if (b2[k]) n2++; }
  let n=0, sp=0, rz=0, rim=0, rimSp=0, rimRz=0, intN=0, intSp=0, intRz=0, scat=0, scatSp=0, scatHop=0, hopAll=0;
  for (let i=0;i<N;i++) { if (!alive[i]) continue; n++; const x=i%W, y=(i/W)|0, g=gen[i], s=strategy(g), hop=((g>>>16)&3)>0; if (s==='spore') sp++; else if (s==='rhizome') rz++; if (hop) hopAll++;
    const bx=Math.min(bw-1,(x/BS)|0), by=Math.min(bh-1,(y/BS)|0); let near=false;
    for (let dy=-1;dy<=1&&!near;dy++) for (let dx=-1;dx<=1;dx++) if (b2[((by+dy+bh)%bh)*bw+((bx+dx+bw)%bw)]) { near=true; break; }
    if (near) { rim++; if (s==='spore') rimSp++; else if (s==='rhizome') rimRz++; } else { intN++; if (s==='spore') intSp++; else if (s==='rhizome') intRz++; }
    let cnt=0; for (let dy=-2;dy<=2;dy++) for (let dx=-2;dx<=2;dx++) { if(!dx&&!dy) continue; if (alive[((y+dy+H)%H)*W+((x+dx+W)%W)]) cnt++; }
    if (cnt<=6) { scat++; if (s==='spore') scatSp++; if (hop) scatHop++; } }
  let gN=0, eN=0, eSp=0, iN=0, iSp=0;
  for (let i=0;i<N;i++) { if (!alive[i]) continue; if (xg[i]&3) gN++; const x=i%W, y=(i/W)|0; let nb=0; for (let dy=-1;dy<=1;dy++) for (let dx=-1;dx<=1;dx++) if ((dx||dy)&&alive[((y+dy+H)%H)*W+((x+dx+W)%W)]) nb++; const sp=strategy(gen[i])==='spore'; if (nb<=3) { eN++; if (sp) eSp++; } else if (nb>=6) { iN++; if (sp) iSp++; } }
  let both2=0, flip=0, gboth=0, gflip=0; for (let i=0;i<N;i++) if (e1[i] && alive[i] && gen[i]===g1[i]) { both2++; const s=strategyAt(i), e= s==='spore'?1:s==='rhizome'?2:3; const f=e!==e1[i]; if (f) flip++; if (xg[i]&3) { gboth++; if (f) gflip++; } }
  const pct = (a,b) => b ? +(a/b).toFixed(3) : null;
  return {occ:pct(n,N), bare:pct(n2,bw*bh), persist:pct(both,n1), spore:pct(sp,n), rhiz:pct(rz,n), rimRz:pct(rimRz,rim), intRz:pct(intRz,intN), rimFrac:pct(rim,n), scatFrac:pct(scat,n), scatSpore:pct(scatSp,scat), scatHop:pct(scatHop,scat), hopAll:pct(hopAll,n), gene:pct(gN,n), edgeSp:pct(eSp,eN), inSp:pct(iSp,iN), iN:iN, flip:pct(flip,both2), gflip:pct(gflip,gboth)};
}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file://'+path); pg.wait_for_timeout(300)
    out=[pg.evaluate(JS, [env, params, t1, k]) for k in range(trials)]
    print(json.dumps({'env':env,'params':params,'res':out,'errs':errs}))
    b.close()
