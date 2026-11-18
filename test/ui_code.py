import re
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
    pg.goto("file:///home/claude/justins-game-of-life/build/justins_game_of_life.html"); pg.wait_for_timeout(400)
    r=pg.evaluate("""()=>{running=false;P.env='vent';P.seed=11;reset('organism');for(let t=0;t<800;t++)step();
      let pick=-1;for(let i=0;i<N;i++)if(alive[i]&&slen[i]&&ctabD[i]&&geneSegs(seq,i*SL,slen[i])>1){pick=i;break;} if(pick<0)for(let i=0;i<N;i++)if(alive[i]&&slen[i]&&geneSegs(seq,i*SL,slen[i])>1){pick=i;break;}
      const g=geneListHtml(pick);const sm=seqPanel();return {g:g.replace(/<br>/g,'\\n').replace(/<div>/g,'\\n').replace(/<[^>]+>/g,''),sm:sm.replace(/<[^>]+>/g,'').match(/the code:[^·]*/)};}""")
    print(r['g'][:1400]); print(r['sm']); print(errs); b.close()
