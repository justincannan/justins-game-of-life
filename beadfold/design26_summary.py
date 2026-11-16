"""Task 26 step 3: summarise design26.py's design_state.json into results/t26_design_summary.json and the figure
comms/from_gpu/26_design.png (PIL). Usage: python design26_summary.py [STATE.json]"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import summary_step3 as S3  # noqa: E402

COL = [(31, 119, 180), (214, 39, 40), (44, 160, 44), (148, 103, 189), (255, 127, 14)]
D = r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-16\task26\design\design_state.json'


def main():
    st = json.load(open(sys.argv[1] if len(sys.argv) > 1 else D))
    names = list(dict.fromkeys(r['target'] for rd in st['rounds'] for r in rd['rows']))
    out = dict(timing=st['timing'], args=st['args'], model=st['model'], rounds=[])
    for rd in st['rounds']:
        per = {}
        for n in names:
            rr = [r for r in rd['rows'] if r['target'] == n]
            ok = [r for r in rr if abs(r['target_minus_fold_kT']) < 500]
            per[n] = dict(n=len(rr), gap_full_max=max(r['gap_full_kT'] for r in rr),
                          gap_full_median=float(np.median([r['gap_full_kT'] for r in rr])),
                          target_minus_fold_min=min(r['target_minus_fold_kT'] for r in rr),
                          target_minus_fold_median=float(np.median([r['target_minus_fold_kT'] for r in ok])) if ok else None,
                          rmsd_best_min=min(r['rmsd_best_to_target'] for r in rr),
                          frac_same_max=max(r['frac_same'] for r in rr),
                          target_lower=sum(r['target_minus_fold_kT'] < 0 for r in rr),
                          gap_positive=sum(r['gap_full_kT'] > 0 for r in rr),
                          drift_max=max(r['target_drift_nm'] for r in rr),
                          n_blowups=len(rr) - len(ok))
        out['rounds'].append(dict(round=rd['round'], mc_s=rd['mc_s'], fold_s=rd['fold_s'], pool=rd['pool'], per_target=per))
    n_seq = sum(len(rd['rows']) for rd in st['rounds'])
    out['cost'] = dict(total_s=st['timing']['total_s'], candidates=n_seq, s_per_candidate=st['timing']['total_s'] / n_seq,
                       relax_s=st['timing']['relax_s'], n_relaxed=st['timing']['n_relaxed'],
                       ms_per_relaxation=1000 * st['timing']['relax_s'] / st['timing']['n_relaxed'])
    json.dump(out, open(os.path.join(HERE, 'results', 't26_design_summary.json'), 'w'), indent=1)
    for rd in out['rounds']:
        print('round', rd['round'], 'mc %.0fs fold %.0fs' % (rd['mc_s'], rd['fold_s']))
        for n, v in rd['per_target'].items():
            print('  %-20s' % n, {k: (round(x, 2) if isinstance(x, float) else x) for k, x in v.items()})
    print(out['cost'])
    # figure: per round, best full gap and best (target - blind fold) per target
    img = Image.new('RGB', (1500, 520), 'white')
    R = len(out['rounds'])
    p1 = S3.Panel(img, (80, 50, 680, 430), (-0.5, R - 0.5), (-60, 40), 'relaxed gap (softmin decoys - target), best per round',
                  'round', 'kT')
    p2 = S3.Panel(img, (800, 50, 1400, 430), (-0.5, R - 0.5), (-40, 100), 'relaxed target - lowest blind fold, best per round',
                  'round', 'kT')
    p1.line([-0.5, R - 0.5], [0, 0], (180, 180, 180), 1)
    p2.line([-0.5, R - 0.5], [0, 0], (180, 180, 180), 1)
    for k, n in enumerate(names):
        g = [rd['per_target'][n]['gap_full_max'] for rd in out['rounds']]
        t = [rd['per_target'][n]['target_minus_fold_min'] for rd in out['rounds']]
        xs = np.arange(R) + 0.05 * (k - 2)
        p1.line(xs, np.clip(g, -60, 40), COL[k], 2); p1.dots(xs, np.clip(g, -60, 40), COL[k], 4)
        p2.line(xs, np.clip(t, -40, 100), COL[k], 2); p2.dots(xs, np.clip(t, -40, 100), COL[k], 4)
    p1.legend([(n.replace('design_', ''), COL[k]) for k, n in enumerate(names)])
    img.save(os.path.join(HERE, '..', 'comms', 'from_gpu', '26_design.png'))


if __name__ == '__main__':
    main()
