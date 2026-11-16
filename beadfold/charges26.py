"""Task 26, step 1: charges split into a Born-like self term (eps_self 4-6) and charge-charge interactions at
eps_pair about 20 (Justin's decision of 15 November; Schutz and Warshel 2001). Constants are proposals.

Part A (CPU, seconds): task 20's benchmarks in the model's own energy, as saltbridge_tb.py, for
  elec 'v23' (task 23: one eps_core = 6) and elec 'split' with eps_self in 4, 5, 6 and the burial table either kept
  ('keep': charged monomers keep their burial h, the Born term is added) or with charged monomers given their oily
  isostere's h ('iso': the charge's desolvation is counted once, by the Born term).
Part B (CPU, seconds): the Coulomb energy (pairs + self) of task 23's random 32-mers' lowest structures (10 runs x 20
  sequences, results/2026-11-15/task23/random32_b00.npz), re-evaluated without refolding, before and after.
Usage: python charges26.py   (writes results/t26_step1_charges.json)
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

KT = TB.KT0
NPZ = r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23\random32_b00.npz'


def elec_pair(a, b, G, eps_in):
    qa, qb = TB.SC['q'][a], TB.SC['q'][b]
    if qa == 0 or qb == 0:
        return 0.0
    r = max(SB.contact_r(a, b), 0.35)
    return TB.COULOMB * qa * qb / r * ((1 - G) * math.exp(-r / TB.LAMBDA_D) / TB.EPS_W + G / eps_in)


def benchmarks(cfg):
    W = TB.pair_tables()
    h = TB.h_table(cfg['h_charge'])
    split = cfg['elec'] == 'split'
    eps_in = TB.EPS_PAIR if split else TB.EPS_CORE
    us = (lambda m: TB.born_self(TB.SC['q'][m], TB.SC['d'][m], cfg['eps_self'])) if split else (lambda m: 0.0)

    def single(a, f):
        return h[a] + us(a) + SB.K_CORE * W[a, f]

    def pair(a, b, f):
        return h[a] + h[b] + us(a) + us(b) + W[a, b] + elec_pair(a, b, 1.0, eps_in) + (SB.K_CORE - 1) * (W[a, f] + W[b, f])

    rows = []
    for name, (a, b) in SB.PAIRS.items():
        for f in SB.FILLERS:
            p, u, iso = pair(a, b, f), single(a, f) + single(b, f), pair(SB.ISO[a], SB.ISO[b], f)
            rows.append(dict(pair=name, filler=f, relief_kT=(u - p) / KT, pair_minus_iso_kT=(p - iso) / KT,
                             lone_minus_iso_kT=(single(a, f) - single(SB.ISO[a], f)) / KT))
    out = {}
    for name in SB.PAIRS:
        rr = [r for r in rows if r['pair'] == name]
        out[name] = dict(relief=[min(r['relief_kT'] for r in rr), max(r['relief_kT'] for r in rr)],
                         pair_minus_iso=[min(r['pair_minus_iso_kT'] for r in rr), max(r['pair_minus_iso_kT'] for r in rr)],
                         lone_minus_iso=[min(r['lone_minus_iso_kT'] for r in rr), max(r['lone_minus_iso_kT'] for r in rr)])
    return out


def random32(cfg):
    z = np.load(NPZ, allow_pickle=True)
    ns = len([k for k in z.files if k.endswith('_seq')])
    seqs = [z[f's{i}_seq'] for i in range(ns)]
    xs = np.concatenate([z[f's{i}_best_x'] for i in range(ns)])          # (ns*10, 64, 3)
    idx = np.repeat(np.stack(seqs), 10, 0)
    P = np.repeat(TB.seq_params(seqs, 32)[1], 10, 0)
    kw = dict(elec=cfg['elec'], eps_self=cfg['eps_self'], h_charge=cfg['h_charge'])
    m = TB.Model2(idx, P, device='cpu', **kw)
    with torch.no_grad():
        p = m.energy(torch.as_tensor(xs, dtype=torch.float32), parts=True)
    el, se, bu, tot = (p[k].numpy() / KT for k in ('elec', 'elec_self', 'burial', 'total'))
    best = tot.reshape(ns, 10).argmin(1) + 10 * np.arange(ns)            # each sequence's lowest run, this energy
    return dict(median_coulomb_all_runs=float(np.median(el)), median_coulomb_lowest=float(np.median(el[best])),
                median_self=float(np.median(se)), median_pairs=float(np.median(el - se)),
                median_burial=float(np.median(bu)), n_structures=int(len(el)))


def main():
    cfgs = [dict(elec='v23', eps_self=None, h_charge='keep')]
    for hc in ('keep', 'iso'):
        for es in (4.0, 5.0, 6.0):
            cfgs.append(dict(elec='split', eps_self=es, h_charge=hc))
    res = []
    for c in cfgs:
        c2 = dict(c, eps_self=c['eps_self'] or TB.EPS_SELF)
        r = dict(cfg=c, born_kT={m: TB.born_self(TB.SC['q'][m], TB.SC['d'][m], c2['eps_self']) / KT for m in (0, 2, 8, 10)}
                 if c['elec'] == 'split' else None, bench=benchmarks(c2), random32=random32(c2))
        res.append(r)
        print(c)
        for k, v in r['bench'].items():
            print('  %-5s relief %6.1f..%6.1f  pair-iso %6.1f..%6.1f  lone-iso %6.1f..%6.1f' % (k, *v['relief'], *v['pair_minus_iso'], *v['lone_minus_iso']))
        print('  random32:', {k: round(v, 1) for k, v in r['random32'].items()})
    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    json.dump(dict(eps_pair=TB.EPS_PAIR, born_f=TB.BORN_F, eps_w=TB.EPS_W, results=res),
              open(os.path.join(HERE, 'results', 't26_step1_charges.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
