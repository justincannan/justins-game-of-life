"""Task 27: random 32-mers refolded with elec='cd' (run_tb.py random --model '{"elec": "cd", "h_charge": "iso"}'):
Coulomb energy of the lowest structures, and the environment of buried charges (CPU).
Usage: python charges27_refold.py DIR PREFIX   (adds 'refolded' to results/t27_charge_dipole.json)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import twobead as TB  # noqa: E402
import analyse_step3 as A3  # noqa: E402
import analyse_tb as AT  # noqa: E402

KT = TB.KT0


def main():
    d, pre = sys.argv[1], sys.argv[2]
    rows = A3.load([pre], d)
    el_all, el_low, self_low, cd_low, bur_low = [], [], [], [], []
    nb, npart, npolar, noily = 0, 0, [], []
    for r in rows:
        E = r['best_e'].astype(float)
        el = r['part_elec'].astype(float) / KT
        el_all.extend(el.tolist())
        ib = int(np.argmin(E))
        el_low.append(el[ib]); self_low.append(float(r['part_elec_self'][ib]) / KT)
        cd_low.append(float(r['part_elec_cd'][ib]) / KT); bur_low.append(float(r['part_burial'][ib]) / KT)
        seq = r['seq'].astype(int); L = len(seq)
        x = r['best_x'][ib].astype(float)
        n = r['best_n'][ib].astype(float)
        con, rc = AT.sc_contacts(x[L:], seq)
        xs, xb = x[L:], x[:L]
        for i in range(L):
            if seq[i] in A3.CHARGED and n[i] >= AT.BURIED_N:
                nb += 1
                part = any(con[i, j] and seq[j] in A3.CHARGED and A3.CHARGED[seq[j]] * A3.CHARGED[seq[i]] < 0 for j in range(L))
                npart += part
                sc_n = [j for j in range(L) if abs(i - j) >= 2 and np.linalg.norm(xs[i] - xs[j]) < rc[i, j]]
                npolar.append(sum(TB.DIP_SC[seq[j]] > 0 for j in sc_n))
                noily.append(sum(seq[j] % 2 == 1 and TB.DIP_SC[seq[j]] == 0 for j in sc_n))
    out = dict(n_seq=len(rows), n_runs=int(len(el_all)), median_coulomb_all_runs=float(np.median(el_all)),
               median_coulomb_lowest=float(np.median(el_low)), median_self_net_lowest=float(np.median(self_low)),
               median_cd_payback_lowest=float(np.median(cd_low)), median_burial_lowest=float(np.median(bur_low)),
               buried_charges=nb, buried_partnered=int(npart),
               polar_sc_neighbours_of_buried_charges=float(np.mean(npolar)) if npolar else None,
               oily_sc_neighbours_of_buried_charges=float(np.mean(noily)) if noily else None)
    print(out)
    p = os.path.join(HERE, 'results', 't27_charge_dipole.json')
    res = json.load(open(p))
    res['refolded'] = out
    json.dump(res, open(p, 'w'), indent=1)


if __name__ == '__main__':
    main()
