"""Run a set of configurations, several runs each, two at a time.
usage: python3 test/runset.py BUILD.html CONFIGS.txt [ticks=1500] [runs=6]
CONFIGS.txt: one line per configuration, "world|{json of P overrides}", e.g.  pond|{"rxn":false}
Prints one JSON line per configuration (from gene2.py): survival, survival among colonies established by tick 200,
mean occupancy, share of cells carrying each extension gene, clumps, share of cells in clumps."""
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__))
build = os.path.abspath(sys.argv[1]); cfgs = [l.rstrip('\n').split('|', 1) for l in open(sys.argv[2]) if l.strip()]
T = sys.argv[3] if len(sys.argv) > 3 else '1500'; R = sys.argv[4] if len(sys.argv) > 4 else '6'
def run(c):
    r = subprocess.run([sys.executable, os.path.join(here, 'gene2.py'), build, c[0], c[1], T, R], capture_output=True, text=True)
    return r.stdout.strip() or r.stderr[-300:]
with ThreadPoolExecutor(2) as ex:
    for o in ex.map(run, cfgs): print(o, flush=True)
