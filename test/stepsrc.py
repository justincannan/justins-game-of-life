import sys,re
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    pg=b.new_page(); pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(500)
    s=pg.evaluate("()=>step.toString()"); 
    for m in re.finditer(r'[^\n]{0,90}chem[A-Za-z]*\[[^\n]{0,60}', s): print('>>', m.group(0)[:170])
    print(len(s)); b.close()
