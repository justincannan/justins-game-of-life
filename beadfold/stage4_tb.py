"""Task 23, stage 4 (cheap): how far page sequences are from foldable ones, and whether foldable sequences are
connected by single mutations (a neutral network). GPU; results analysed with analyse_tb.py.

  walk:    for a few page sequences, a greedy walk in sequence space towards a larger energy gap for the sequence's
           own lowest fold (stage 3), one point mutation at a time (design_tb.energies, decoys = that sequence's
           own stage-3 snapshots); the walk's sequences after 1, 2, 3, 4, 6 and 8 accepted mutations are folded blind.
  neutral: every foldable designed sequence (stage 2), and a sample of its single mutants, folded blind.
Usage: python stage4_tb.py walk|neutral [--n N]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tb as RT  # noqa: E402
import design_tb as D  # noqa: E402
import analyse_step3 as A3  # noqa: E402
import summary_step3 as S3  # noqa: E402

OUT = RT.OUT


def foldable(r):
    return r['f300'] >= S3.FOLD_F300 and r['frac_same'] >= S3.FOLD_SAME


def walk(a):
    rows = json.load(open(os.path.join(OUT, 'analysis_page.json')))
    raw = {r['name'] + str(r['seq'].astype(int).tolist()): r for r in A3.load(['page'], OUT)}
    cand = sorted([r for r in rows if not foldable(r)], key=lambda r: -r['frac_same'])
    pick = cand[:a.n]
    rng = np.random.default_rng(7)
    items = {}
    log = []
    for p in pick:
        rr = raw[p['name'] + str(p['seq'])]
        L = p['L']
        E = rr['best_e'].astype(float); X = rr['best_x'][:, :L].astype(float)
        tgt = X[int(np.argmin(E))]
        dec = D.decoys_from([dict(L=L, snapX=rr['snapX'], best_x=rr['best_x'])], tgt, L, n_snap=400, rng=rng)
        s = np.array(p['seq'])
        allx = np.concatenate([tgt[None], dec], 0)
        g = D.gap(*(lambda e: (e[:, 0], e[:, 1:]))(D.energies([s], allx)))[0]
        path = [(0, s.tolist(), float(g))]
        acc = 0
        for step in range(300):
            props = []
            for _ in range(16):
                t = s.copy(); i = rng.integers(L); t[i] = (t[i] + rng.integers(1, 16)) % 16
                props.append(t)
            e = D.energies(props, allx)
            gp = D.gap(e[:, 0], e[:, 1:])
            k = int(np.argmax(gp))
            if gp[k] > g:
                s, g = props[k], gp[k]; acc += 1
                path.append((acc, s.tolist(), float(g)))
                if acc in (1, 2, 3, 4, 6, 8):
                    items[f"{p['name']}|{p['seq']}|k{acc}"] = s.tolist()
            if acc >= 8:
                break
        items[f"{p['name']}|{p['seq']}|k0"] = p['seq']
        log.append(dict(page=p['seq'], name=p['name'], path=path))
        RT.log('walk', p['seq'], 'accepted', acc, 'gap', round(path[0][2], 1), '->', round(g, 1))
    json.dump(log, open(os.path.join(OUT, 'stage4_walk_paths.json'), 'w'))
    RT.run_set('walk', list(items.items()), 4, 30000, 'coop', OUT, 2400, seed0=1500)


def neutral(a):
    rows = json.load(open(os.path.join(OUT, 'analysis_designs_final.json')))
    good = [r for r in rows if foldable(r)] or sorted(rows, key=lambda r: -r['f300'])[:1]
    rng = np.random.default_rng(9)
    items = []
    for r in good[:2]:
        s = np.array(r['seq']); L = len(s)
        items.append((r['name'] + '|parent', s.tolist()))
        pos = rng.choice(L, min(a.n, L), replace=False)
        for i in pos:
            t = s.copy(); t[i] = (t[i] + rng.integers(1, 16)) % 16
            items.append((r['name'] + f'|m{i}', t.tolist()))
    RT.run_set('neutral', items, 4, 30000, 'coop', OUT, 2400, seed0=1600)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode')
    ap.add_argument('--n', type=int, default=6)
    a = ap.parse_args()
    {'walk': walk, 'neutral': neutral}[a.mode](a)


if __name__ == '__main__':
    main()
