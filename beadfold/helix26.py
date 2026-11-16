"""Task 26 step 2: isolated-helix content of the two-bead model against step 2's Zimm-Bragg predictions (GPU).

Configurations (all in one batch; each chain carries its own local probabilities):
  'v23'          task 23's helix term (step 2's cooperative helix probability x e^3 in the local bias, no coop term);
  'coop_kK'      the cooperative helix term (twobead.py, helix='coop': nucleation EPS_NUC = -kT ln sigma on the helix
                 H-bonds), local bias p_helix = K s / (1 + K s), for a scan of K (the one calibration constant).
Readout: helix content = share of the L - 4 helix H-bonds (i -> i+4) formed (C-alpha distances i, i+3 and i, i+4
within 0.08 nm of the ideal helix, as analyse_tb.py), the analogue of Zimm-Bragg's theta (a residue in state h has
its H-bond formed); WHAM-reweighted to 300 K from the replica ladder. Prediction: step 2's mean helix probability
(secondary.secondary, with its charge corrections) at 300 K, 150 mM.
Usage: python helix26.py [--ks 1 2 4 8] [--nrun 2] [--nsteps 30000] [--elec cd] [--out JSON]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tertiary as TT  # noqa: E402
import twobead as TB  # noqa: E402
import secondary as S  # noqa: E402
import run_step3 as R3  # noqa: E402

TEST = {
    # polar hosts (soluble, as isolated helices are measured): 12 and 6 are strong formers (s 1.3), 14 and 4 weak (1.1)
    '12x12': [12] * 12, '12x16': [12] * 16, '12x20': [12] * 20, '12x24': [12] * 24, '12x32': [12] * 32,
    '6x20': [6] * 20, '14x20': [14] * 20, '4x20': [4] * 20,
    '(0000 8888)x3': ([0] * 4 + [8] * 4) * 3,
    '12 host, 0 every 4th (24)': [0 if i % 4 == 0 else 12 for i in range(24)],
    '12x24, one 15 in the middle': [12] * 12 + [15] + [12] * 11,
    # oily homopolymers (collapse competes with the helix; Zimm-Bragg has no collapse): contrast only
    '7x20 (oily)': [7] * 20, '5x20 (oily)': [5] * 20,
}


def hb_formed(xb, mask):
    r4 = (xb[:, 4:] - xb[:, :-4]).norm(dim=-1); r3 = (xb[:, 3:-1] - xb[:, :-4]).norm(dim=-1)
    f = ((r4 - TB.R_H4).abs() < 0.08) & ((r3 - TB.R_H3).abs() < 0.08)
    m = mask[:, 4:] * mask[:, :-4]
    return (f.float() * m).sum(1) / m.sum(1).clamp_min(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ks', type=float, nargs='*', default=[1.0, 2.0, 4.0, 8.0])
    ap.add_argument('--nrun', type=int, default=2)
    ap.add_argument('--nsteps', type=int, default=30000)
    ap.add_argument('--elec', default='cd')
    ap.add_argument('--no-v23', action='store_true')
    ap.add_argument('--props', type=float, nargs='*', default=None, help="helix='coop2': EPS_PROP values (kT)")
    ap.add_argument('--props-wide', type=float, nargs='*', default=None, help="coop2 with a wider H-bond window")
    ap.add_argument('--w-wide', type=float, default=0.10)
    ap.add_argument('--props-joint', type=float, nargs='*', default=None,
                    help="coop2, narrow window: several EPS_PROP values (kT) in ONE simulation (a per-chain constant)")
    ap.add_argument('--out', default=os.path.join(HERE, 'results', 't26_step2_helix.json'))
    a = ap.parse_args()
    names = list(TEST)
    cfgs = ([] if a.no_v23 else [('v23', None)]) + [(f'coop_k{k:g}', k) for k in a.ks]
    if a.props is not None:
        cfgs += [(f'coop2_p{p:g}', ('p', p)) for p in a.props]
    if a.props_joint is not None:
        cfgs += [(f'coop2_p{p:g}', ('j', p)) for p in a.props_joint]
    if a.props_wide is not None:
        cfgs += [(f'coop2w{a.w_wide:g}_p{p:g}', ('w', p)) for p in a.props_wide]
    seqs, P1, tags = [], [], []
    for cname, k in cfgs:
        for n in names:
            s = TEST[n]
            seqs.append(np.array(s))
            P1.append(TB.local_probs(s) if k is None else TB.local_probs_coop2(s) if isinstance(k, tuple)
                      else TB.local_probs_coop(s, k))
            tags.append((cname, n))
    L = max(len(s) for s in seqs)
    Pm = np.zeros((len(seqs), L, 3)); Pm[:, :, 2] = 1.0
    for i, p in enumerate(P1):
        Pm[i, :len(p)] = p
    # the coop term is a model-wide switch: build two simulations if both kinds are present
    out = dict(test={n: TEST[n] for n in names}, zb={}, configs=[c for c, _ in cfgs], rows=[], nsteps=a.nsteps,
               nrun=a.nrun, elec=a.elec, eps_nuc_kT=TB.EPS_NUC / TB.KT0)
    for n in names:
        out['zb'][n] = float(S.secondary(TEST[n])[:, 0].mean())
    t0 = time.time()
    groups = [('v23', [i for i, (c, _) in enumerate(tags) if c == 'v23'], {}),
              ('coop', [i for i, (c, _) in enumerate(tags) if c.startswith('coop_k')], {})]
    joint = [i for i, (c, _) in enumerate(tags) if isinstance(dict(cfgs)[c], tuple) and dict(cfgs)[c][0] == 'j']
    if joint:
        rep = a.nrun * len(R3.TEMPS)
        ev = np.repeat([dict(cfgs)[tags[i][0]][1] * TB.KT0 for i in joint], rep)
        groups.append(('coop2', joint, dict(eps_prop=ev)))
    for c, k in cfgs:
        if isinstance(k, tuple) and k[0] != 'j':
            ex = dict(eps_prop=k[1] * TB.KT0)
            if k[0] == 'w':
                ex['w_h'] = a.w_wide
            groups.append(('coop2', [i for i, (cc, _) in enumerate(tags) if cc == c], ex))
    for helix, sel, extra in groups:
        if not sel:
            continue
        sq = [seqs[i] for i in sel]
        sim = TB.REMD2(sq, a.nrun, R3.TEMPS, seed=7, P1=Pm[sel], elec=a.elec, h_charge='iso', helix=helix, **extra)
        sim.build(R3.NBLOCK)
        K, ns, nr = sim.K, sim.ns, sim.nr
        nb = a.nsteps // R3.NBLOCK
        every = R3.SNAP // R3.NBLOCK
        burn = int(R3.BURN * nb)
        E, H = [], []
        for b in range(nb):
            sim.run_block(); sim.exchange(b % 2)
            if (b + 1) % every == 0 and b >= burn:
                with torch.no_grad():
                    H.append(hb_formed(sim.x[:, :sim.L], sim.model.maskL).cpu().numpy())
                E.append(sim.e.cpu().numpy().copy())
        E = np.stack(E, 1).reshape(ns, nr, K, -1); H = np.stack(H, 1).reshape(ns, nr, K, -1)
        for j, i in enumerate(sel):
            Ek = [E[j, :, k].reshape(-1).astype(np.float64) for k in range(K)]
            Hk = np.concatenate([H[j, :, k].reshape(-1) for k in range(K)])
            logw, _ = TT.wham(Ek, R3.TEMPS)
            res = {}
            for T in (250.0, 275.0, 300.0, 325.0, 350.0):
                w = np.exp(logw(T)); w /= w.sum()
                res[f'{T:g}'] = float((w * Hk).sum())
            runs300 = []
            for r in range(nr):     # per run, the replica nearest 300 K (no reweighting): spread between runs
                kk = int(np.argmin(np.abs(R3.TEMPS - 300.0)))
                runs300.append(float(H[j, r, kk].mean()))
            c, n = tags[i]
            out['rows'].append(dict(config=c, name=n, L=len(TEST[n]), zb=out['zb'][n], hb_share=res,
                                    hb_share_runs_near300=runs300))
            print('%-10s %-28s ZB %.2f  model(300) %.2f  runs %s' % (c, n, out['zb'][n], res['300'], np.round(runs300, 2)))
        del sim; torch.cuda.empty_cache()
    out['seconds'] = time.time() - t0
    for c, _ in cfgs:
        rr = [r for r in out['rows'] if r['config'] == c]
        rr = [r for r in rr if 'oily' not in r['name']]
        z = np.array([r['zb'] for r in rr]); m = np.array([r['hb_share']['300'] for r in rr])
        out.setdefault('fit', {})[c] = dict(mean_ratio_strong=float(np.mean([r['hb_share']['300'] / r['zb'] for r in rr if r['zb'] > 0.3 and 'oily' not in r['name']])),
                                            rms_diff=float(np.sqrt(np.mean((m - z) ** 2))), corr=float(np.corrcoef(z, m)[0, 1]))
        print(c, out['fit'][c])
    json.dump(out, open(a.out, 'w'), indent=1)
    print('done %.0fs' % out['seconds'])


if __name__ == '__main__':
    main()
