import subprocess, sys, json
from concurrent.futures import ThreadPoolExecutor
cfgs=[l.rstrip('\n').split('|',1) for l in open('/home/claude/test/configs.txt') if l.strip()]
def run(c):
    e,p=c
    r=subprocess.run(['python3','/home/claude/test/sweep.py','/home/claude/out/sweep_build.html',e,p,'4','2500'],capture_output=True,text=True)
    with open('/home/claude/test/sweep_out.jsonl','a') as f: f.write((r.stdout.strip() or json.dumps({'env':e,'params':json.loads(p),'res':[],'errs':[r.stderr[-200:]]}))+'\n')
open('/home/claude/test/sweep_out.jsonl','w').close()
with ThreadPoolExecutor(2) as ex: list(ex.map(run,cfgs))
open('/home/claude/test/sweep_out.jsonl','a').write('DONE\n')
