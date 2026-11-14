"""Merge the page dumps (dump_seq.js outputs, one JSON per seed) into fold3d/data/page_seqs.json.
Usage: python make_page_seqs.py DUMPDIR"""
import glob
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = sys.argv[1]
worlds = {}
meta = []
for f in sorted(glob.glob(str(Path(d) / '*.json'))):
    r = json.load(open(f, encoding='utf-8'))
    for w, v in r['worlds'].items():
        meta.append(dict(file=Path(f).name, world=w, tick=v['tick'], live=v['live'], distinct=v['distinct'], restarts=v['restarts']))
        acc = worlds.setdefault(w, {})
        for s in v['seqs']:
            acc[s['seq']] = acc.get(s['seq'], 0) + s['n']
out = dict(runs=meta, worlds={w: [dict(seq=q, n=c) for q, c in sorted(a.items(), key=lambda t: -t[1])] for w, a in worlds.items()})
(HERE / 'data').mkdir(exist_ok=True)
(HERE / 'data' / 'page_seqs.json').write_text(json.dumps(out), encoding='utf-8')
for w, lst in out['worlds'].items():
    print(w, len(lst), 'distinct sequences;', sum(len(s['seq']) >= 12 for s in lst), 'of length >= 12')
