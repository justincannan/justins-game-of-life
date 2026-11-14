import subprocess, json, sys
from concurrent.futures import ThreadPoolExecutor
F='/home/claude/out/plume.html'
cfgs=[l.rstrip('\n').split('|',1) for l in open('/home/claude/test/s1cfgs.txt') if l.strip()]
def run(c):
    r=subprocess.run(['python3','/home/claude/test/gene2.py',F,c[0],c[1],'2000','6'],capture_output=True,text=True)
    return r.stdout.strip() or r.stderr[-200:]
with ThreadPoolExecutor(2) as ex:
    for o in ex.map(run,cfgs): print(o,flush=True)
print('DONE')
