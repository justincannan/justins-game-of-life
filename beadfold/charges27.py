"""Task 27 (task 26 step 1 completed): the charge-dipole term (Justin's decision of 16 November, about 00:19).

elec='cd' in twobead.py: elec='split' (pairs at eps_pair 20, Born self term at eps_self 4-6) plus a payback of the
Born cost by polar neighbours (side-chain donors/acceptors without charge, and backbone beads), small eps
(eps_cd = eps_self; Sham, Muegge and Warshel 1998). One new constant, MU_CD (effective dipole, e nm).

Part A (CPU, seconds): task 20's benchmarks in the model's own energy, as charges26.py, with the pocket's dipoles:
  a core side chain has K_CORE = 5 side-chain neighbours (the partner and fillers) and N_BB = 6 backbone neighbours
  (measured: median 6.6 backbone and 7.6 side-chain neighbours around buried charges in task 23's random 32-mers),
  all at R_EFF = 0.555 nm (measured: sqrt(count / sum(s / r^2)) around those charges).
  Polar-lined pocket: fillers 4, 6, 12, 14 (donors/acceptors). Oily-lined pocket: fillers 1, 3, 5, 13.
  MU_CD is scanned; the chosen value is the smallest at which benchmark B (pair - isostere, 0-6 kT) holds for 0-8 and
  2-8 with every polar filler at eps_self 5.
Part B (CPU, seconds): the Coulomb energy of task 23's random 32-mers' lowest structures, re-scored (not refolded).
Usage: python charges27.py   (writes results/t27_charge_dipole.json)
"""
import json
import math
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import twobead as TB  # noqa: E402
import saltbridge_tb as SB  # noqa: E402
import charges26 as C26  # noqa: E402

KT = TB.KT0
N_BB, R_EFF = 6, 0.555
POLAR, OILY = (4, 6, 12, 14), (1, 3, 5, 13)


def payback(m, n_dip, mu, eps_self):
    """charge-dipole payback (kJ/mol, >= 0) of monomer m's Born cost with n_dip dipoles at R_EFF."""
    u = TB.born_self(TB.SC['q'][m], TB.SC['d'][m], eps_self)
    if u <= 0:
        return 0.0
    S = TB.COULOMB * abs(TB.SC['q'][m]) * mu / eps_self * n_dip / R_EFF ** 2
    return u * (1 - math.exp(-S / u))


def bench(mu, eps_self, fillers, h_charge='iso', n_bb=N_BB):
    W = TB.pair_tables()
    h = TB.h_table(h_charge)
    dip = TB.DIP_SC

    def us(m, n_sc_dip):
        return TB.born_self(TB.SC['q'][m], TB.SC['d'][m], eps_self) - payback(m, n_sc_dip + n_bb, mu, eps_self)

    def single(a, f):
        return h[a] + us(a, SB.K_CORE * dip[f]) + SB.K_CORE * W[a, f]

    def pair(a, b, f):
        k = SB.K_CORE - 1
        return (h[a] + h[b] + us(a, k * dip[f] + dip[b]) + us(b, k * dip[f] + dip[a]) + W[a, b]
                + C26.elec_pair(a, b, 1.0, TB.EPS_PAIR) + k * (W[a, f] + W[b, f]))

    out = {}
    for name, (a, b) in SB.PAIRS.items():
        rel, bb, lone = [], [], []
        for f in fillers:
            p, iso = pair(a, b, f), pair(SB.ISO[a], SB.ISO[b], f)
            rel.append((single(a, f) + single(b, f) - p) / KT)
            bb.append((p - iso) / KT)
            lone.append((single(a, f) - single(SB.ISO[a], f)) / KT)
        out[name] = dict(relief=[min(rel), max(rel)], pair_minus_iso=[min(bb), max(bb)], lone_minus_iso=[min(lone), max(lone)])
    return out


def random32(mu, eps_self, h_charge='iso'):
    z = np.load(C26.NPZ, allow_pickle=True)
    ns = len([k for k in z.files if k.endswith('_seq')])
    seqs = [z[f's{i}_seq'] for i in range(ns)]
    xs = np.concatenate([z[f's{i}_best_x'] for i in range(ns)])
    idx = np.repeat(np.stack(seqs), 10, 0)
    P = np.repeat(TB.seq_params(seqs, 32)[1], 10, 0)
    m = TB.Model2(idx, P, device='cpu', elec='cd', eps_self=eps_self, h_charge=h_charge, mu_cd=mu)
    with torch.no_grad():
        p = m.energy(torch.as_tensor(xs, dtype=torch.float32), parts=True)
    el, se, cd, tot = (p[k].numpy() / KT for k in ('elec', 'elec_self', 'elec_cd', 'total'))
    best = tot.reshape(ns, 10).argmin(1) + 10 * np.arange(ns)
    return dict(median_coulomb_all_runs=float(np.median(el)), median_coulomb_lowest=float(np.median(el[best])),
                median_self_net=float(np.median(se)), median_cd_payback=float(np.median(cd)),
                median_pairs=float(np.median(el - se)), n_structures=int(len(el)))


def ok_B(b):
    return all(0.0 <= b[k]['pair_minus_iso'][0] and b[k]['pair_minus_iso'][1] <= 6.0 for k in ('0-8', '2-8'))


def main():
    scan = []
    chosen = None
    for mu in np.round(np.arange(0.02, 0.301, 0.005), 3):
        b = bench(mu, 5.0, POLAR)
        scan.append(dict(mu=float(mu), polar=b, oily=bench(mu, 5.0, OILY)))
        if chosen is None and ok_B(b):
            chosen = float(mu)
    print('chosen MU_CD', chosen, 'e nm =', chosen / 0.020819, 'D')
    res = dict(N_BB=N_BB, R_EFF=R_EFF, chosen_mu=chosen, chosen_mu_debye=chosen / 0.020819, scan=scan, at_chosen={})
    for es in (4.0, 5.0, 6.0):
        for hc in ('iso', 'keep'):
            d = dict(polar=bench(chosen, es, POLAR, hc), oily=bench(chosen, es, OILY, hc),
                     oily_no_backbone=bench(chosen, es, OILY, hc, n_bb=0), polar_bb3=bench(chosen, es, POLAR, hc, n_bb=3),
                     oily_bb3=bench(chosen, es, OILY, hc, n_bb=3),
                     random32=random32(chosen, es, hc))
            res['at_chosen'][f'eps{es:g}_{hc}'] = d
            print('eps_self', es, hc)
            for pk in ('polar', 'oily', 'oily_no_backbone', 'polar_bb3', 'oily_bb3'):
                for k, v in d[pk].items():
                    print('  %-16s %-5s relief %6.1f..%6.1f  pair-iso %6.1f..%6.1f  lone-iso %6.1f..%6.1f' % (
                        pk, k, *v['relief'], *v['pair_minus_iso'], *v['lone_minus_iso']))
            print('  random32', {k: round(v, 1) for k, v in d['random32'].items()})
    # mu needed per eps_self (for orientation)
    res['mu_needed'] = {}
    for es in (4.0, 6.0):
        for mu in np.round(np.arange(0.02, 0.401, 0.005), 3):
            if ok_B(bench(mu, es, POLAR)):
                res['mu_needed'][f'eps{es:g}'] = float(mu); break
    print('mu needed at eps 4, 6:', res['mu_needed'])
    json.dump(res, open(os.path.join(HERE, 'results', 't27_charge_dipole.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
