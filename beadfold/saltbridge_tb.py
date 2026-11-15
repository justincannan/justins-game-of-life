"""Task 23, stage 1: the two-bead model's terms against their targets, in the model's own energy (CPU, seconds).

A side chain in a packed core has K_CORE side-chain neighbours (and backbone ones), so its burial factor is ~1.
Energies are against the same monomers fully exposed and apart (0). In kT at 300 K.
  Salt bridges (task 20; Hendsch and Tidor 1994; Waldburger et al. 1995):
    A. a buried unpartnered charge far worse than a partnered pair (relief by the partner > 3 kT);
    B. a buried partnered pair 0-6 kT worse than its oily isostere pair (target about 6 kT, Hendsch-Tidor's mean).
    eps_core is scanned; eps_w / eps_core <= 17 (Lehninger's factor, the upper bound).
  Packing (Eriksson et al. 1992, T4 lysozyme Leu -> Ala): a large -> tiny oily mutation in a core costs a constant
    (transfer-like) part plus a part that grows with the cavity; the cavity part is read here as the packing term's
    loss, target about 2-5 kT (proposal, from a slope of order 20-30 cal/mol per cubic angstrom over cavities of
    50-150 cubic angstroms; the slope is as usually quoted, not re-read).
Usage: python saltbridge_tb.py [--eps-core X] [--eps-vdw X]   (writes results/tb_stage1_terms.json)
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import twobead as TB  # noqa: E402

KT = TB.KT0
K_CORE = 5                       # side-chain neighbours of a core side chain
FILLERS = (1, 3, 5, 13)
PAIRS = {'0-8': (0, 8), '2-8': (2, 8), '0-10': (0, 10), '2-10': (2, 10)}
ISO = {0: 13, 2: 3, 8: 3, 10: 3}


def contact_r(a, b):
    d = 0.5 * (TB.SC['d'][a] + TB.SC['d'][b])
    return 1.122 * TB.SC_SC_F * d          # where the WCA wall ends


def elec(a, b, G, eps_core):
    qa, qb = TB.SC['q'][a], TB.SC['q'][b]
    if qa == 0 or qb == 0:
        return 0.0
    r = max(contact_r(a, b), 0.35)
    return TB.COULOMB * qa * qb / r * ((1 - G) * math.exp(-r / TB.LAMBDA_D) / TB.EPS_W + G / eps_core)


def single(a, f, W):
    return TB.SC['h'][a] + K_CORE * W[a, f]


def pair(a, b, f, W, eps_core):
    return TB.SC['h'][a] + TB.SC['h'][b] + W[a, b] + elec(a, b, 1.0, eps_core) + (K_CORE - 1) * (W[a, f] + W[b, f])


def benchmarks(eps_core, eps_vdw):
    W = TB.pair_tables(eps_vdw=eps_vdw)
    rows = []
    for name, (a, b) in PAIRS.items():
        for f in FILLERS:
            p = pair(a, b, f, W, eps_core)
            u = single(a, f, W) + single(b, f, W)
            iso = pair(ISO[a], ISO[b], f, W, eps_core)
            rows.append(dict(pair=name, filler=f, pair_kT=p / KT, two_unpartnered_kT=u / KT,
                             relief_kT=(u - p) / KT, iso_kT=iso / KT, pair_minus_iso_kT=(p - iso) / KT,
                             exposed_pair_elec_kT=elec(a, b, 0.0, eps_core) / KT))
    pk = []
    for f in FILLERS:
        pk.append(dict(filler=f, large_to_tiny_pack_kT=K_CORE * (W[9, f] - W[1, f]) / KT,
                       large_to_tiny_burial_kT=(TB.SC['h'][9] - TB.SC['h'][1]) / KT))
    return rows, pk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eps-core', type=float, default=TB.EPS_CORE)
    ap.add_argument('--eps-vdw', type=float, default=TB.EPS_VDW / KT)
    a = ap.parse_args()
    out = dict(K_core=K_CORE, eps_w=TB.EPS_W, eps_core_bound=TB.EPS_W / 17, scan=[])
    for ec in (TB.EPS_W / 17, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 40.0, TB.EPS_W):
        rows, pk = benchmarks(ec, a.eps_vdw * KT)
        d = np.array([r['pair_minus_iso_kT'] for r in rows]); rl = np.array([r['relief_kT'] for r in rows])
        out['scan'].append(dict(eps_core=ec, pair_minus_iso_mean=d.mean(), pair_minus_iso_range=[d.min(), d.max()],
                                relief_mean=rl.mean(), relief_range=[rl.min(), rl.max()]))
        print('eps_core %5.1f  pair-iso %5.1f (%5.1f..%5.1f)  relief %5.1f' % (ec, d.mean(), d.min(), d.max(), rl.mean()))
    rows, pk = benchmarks(a.eps_core, a.eps_vdw * KT)
    out.update(chosen=dict(eps_core=a.eps_core, eps_vdw_kT=a.eps_vdw), rows=rows, packing=pk)
    for r in rows:
        if r['filler'] == 5:
            print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    for r in pk:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    json.dump(out, open(os.path.join(HERE, 'results', 'tb_stage1_terms.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
