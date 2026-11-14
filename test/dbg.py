from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/out/rx.html'); pg.wait_for_timeout(500)
    print(pg.evaluate("""()=>{running=false;P.rxDom=true;reset('organism');for(let t=0;t<50;t++)step();let nz=0,n=0,i0=-1;for(let i=0;i<N;i++)if(alive[i]&&slen[i]){n++;if(rx[i])nz++;else if(i0<0)i0=i;}
      const g=infold(seq,i0*SL,slen[i0]);return {n,nz,lastRx,dN,len:slen[i0],seq:[...seq.slice(i0*SL,i0*SL+slen[i0])].map(m=>MONO[m]).join(''),rxLen:rx.length,N}}"""))
    print(errs); b.close()
