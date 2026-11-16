"""Task 26 step 3 check: each designed sequence's target relaxed by plain capped gradient descent (tertiary.minimise,
3,000 steps, as task 23's relax_targets_tb.py), against design26's Adam relaxation (250 steps) and the sequence's
lowest blind-fold structure. Catches targets whose Adam relaxation failed (ideal side chains placed on top of each
other). GPU, about two minutes. Writes results/t26_target_relax.json."""
import json
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tertiary as TT  # noqa: E402
import twobead as TB  # noqa: E402
import analyse_step3 as A3  # noqa: E402
import design26 as D26  # noqa: E402

ST = r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-16\task26\design\design_state.json'


def main():
    st = json.load(open(sys.argv[1] if len(sys.argv) > 1 else ST))
    D26.MK.clear(); D26.MK.update(st['model'])
    T = json.load(open(os.path.join(HERE, 'results', 'tb_targets.json')))
    rows = [r for rd in st['rounds'] for r in rd['rows']]
    Lmax = max(len(r['seq']) for r in rows)
    seqs = [np.array(r['seq']) for r in rows]
    xs = [D26.ideal_target(r['seq'], np.array(T[r['target']]['x'])) for r in rows]
    idx, P, X = D26.pad_batch(seqs, xs, Lmax)
    m = TB.Model2(idx, P, device='cuda', **D26.MK)
    x, e = TT.minimise(m, X, iters=3000)
    e = e.double().cpu().numpy() / TB.KT0
    out = []
    for k, r in enumerate(rows):
        L = len(r['seq'])
        xr = x[k, :L].cpu().numpy().astype(np.float64)
        drift = float(A3.kabsch(xr[None], np.array(T[r['target']]['x']))[0])
        out.append(dict(target=r['target'], round=r['round'], seq=r['seq'], E_target_gd_kT=float(e[k]),
                        E_target_adam_kT=r['E_target_relaxed_kT'], E_fold_best_kT=r['E_fold_best_kT'],
                        target_minus_fold_gd_kT=float(e[k]) - r['E_fold_best_kT'], drift_gd_nm=drift,
                        rmsd_best_to_target=r['rmsd_best_to_target']))
        print('%-20s r%d  adam %8.1f  gd %8.1f  fold %8.1f  target-fold(gd) %7.1f  drift %.2f' % (
            r['target'], r['round'], r['E_target_relaxed_kT'], e[k], r['E_fold_best_kT'], out[-1]['target_minus_fold_gd_kT'], drift))
    json.dump(out, open(os.path.join(HERE, 'results', 't26_target_relax.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
