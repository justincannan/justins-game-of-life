"""Task 23, stage 2 check: is the target the lowest structure for its designed sequence? Each design's target
backbone (side chains ideal) is minimised with the full model (3,000 gradient steps; it may drift) and its energy is
compared with the lowest structure found by the blind fold (analysis_designs_final.json). GPU, about a minute.
Writes results/tb_target_relax.json."""
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

D = r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23'
T = json.load(open(os.path.join(HERE, 'results', 'tb_targets.json')))
rows = json.load(open(os.path.join(D, 'analysis_designs_final.json')))
out = []
Lmax = max(r['L'] for r in rows)
seqs = [r['seq'] for r in rows]
idx, P = TB.seq_params(seqs, Lmax)
m = TB.Model2(idx, P)
xb = np.zeros((len(rows), Lmax, 3))
for k, r in enumerate(rows):
    t = np.array(T[r['name'].split('__')[0]]['x'])
    xb[k, :r['L']] = t
    xb[k, r['L']:] = 100.0 + 0.3 * np.arange(Lmax - r['L'])[:, None] * np.array([1, 0.2, 0.1])
x = TB.place_sc(m, torch.tensor(xb, dtype=torch.float32, device='cuda'))
x, e = TT.minimise(m, x, iters=3000)
for k, r in enumerate(rows):
    L = r['L']
    xr = x[k, :L].cpu().numpy()
    drift = float(A3.kabsch(xr[None].astype(float), np.array(T[r['name'].split('__')[0]]['x']))[0])
    out.append(dict(name=r['name'], E_target_relaxed_kT=float(e[k]) / TB.KT0, E_fold_best_kT=r['E_best_kT'],
                    drift_nm=drift, target_lower=bool(float(e[k]) / TB.KT0 < r['E_best_kT'])))
    print(r['name'][:24].ljust(24), 'target relaxed %.1f  blind best %.1f  drift %.2f nm' % (out[-1]['E_target_relaxed_kT'], r['E_best_kT'], drift))
json.dump(out, open(os.path.join(HERE, 'results', 'tb_target_relax.json'), 'w'), indent=1)
