from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':620,'height':460}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/out/sc.html'); pg.wait_for_timeout(500)
    print(pg.evaluate("""()=>{running=false;P.env='pond';P.sugarKeep=.05;geoSeed();chemCapFill();reset('organism');const out=[];for(let t=1;t<=3000;t++){step();if(t%500===0){let st=0,s1=0,s3=0,n=0,lt=0,coatRx=0;
     for(let i=0;i<N;i++){if(!alive[i])continue;n++;lt+=light[i];const r=rx[i];for(let q=0;q<4;q++){const v=(r>>>(8*q))&255;if(!v)break;if((v&15)===((v>>4)^8)){coatRx++;break;}}
       if(coat[i]<P.coatMin)continue;st++;const x=i%W,y=(i/W)|0;let k=0;for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dy)continue;const j=((y+dy+H)%H)*W+((x+dx+W)%W);if(alive[j]&&coat[j]>=P.coatMin)k++;}if(k>=1)s1++;if(k>=3)s3++;}
     out.push({t,n,meanLight:+(lt/n).toFixed(2),coatFold:+(coatRx/n).toFixed(3),sticky:st,withStickyNbr:s1,with3:s3,clumps:bodies.size});}}return out}"""))
    print(errs); b.close()
