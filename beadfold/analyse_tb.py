"""Task 23: analyse two-bead folding batches (run_tb.py), with step 3's readouts (analyse_step3.py), CPU only.

Usage: python analyse_tb.py PREFIX [PREFIX ...] [--dir DIR] [--out JSON] [--target-file JSON]
Same readouts and thresholds as step 3: folds compared by backbone RMSD (proper rotations), Q from the native's
side-chain contacts, buried = at least BURIED_N neighbours of the side chain (two-bead count, see twobead.py).
With --target-file, each sequence's lowest fold is also compared with its design target (backbone RMSD).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tertiary as TT  # noqa: E402
import twobead as TB  # noqa: E402
import analyse_step3 as A3  # noqa: E402

RMSD_SAME, RMSD_FOLD32, TIE_KT = A3.RMSD_SAME, A3.RMSD_FOLD32, A3.TIE_KT
BURIED_N = 6.5        # two-bead neighbour count at which the coop burial factor is about 0.65 (half at 6)
TGRID = A3.TGRID
CHARGED = A3.CHARGED


def sc_contacts(xs, seq):
    L = len(seq)
    d = np.linalg.norm(xs[:, None] - xs[None], axis=-1)
    dm = TB.SC['d'][seq]
    rc = 0.5 * (dm[:, None] + dm[None]) + TB.R_EXTRA
    sep = np.abs(np.arange(L)[:, None] - np.arange(L)[None])
    return (d < rc) & (sep >= 3), rc


def analyse_one(r, targets=None, natives=None):
    meta = r['meta']
    temps = np.array(meta['temps'])
    seq = r['seq'].astype(int)
    L = len(seq)
    E = r['best_e'].astype(float)
    X = r['best_x'].astype(float)          # (nr, 2L, 3)
    XB = X[:, :L]
    kT0 = TT.KT0
    lab = A3.cluster(XB, E)
    ib = int(np.argmin(E))
    nat = X[ib]
    key = str(r['name']).split('@')[0].split('__')[0]
    if natives is not None and key in natives:                   # Go check: the native is the given structure
        nat = np.array(natives[key]['x'], float)
    tied = E <= E[ib] + TIE_KT * kT0
    out = dict(seq=seq.tolist(), L=L, set=r['set'], name=str(r['name']), mode=meta['mode'],
               E_best_kT=float(E[ib] / kT0), E_runs_kT=(E / kT0).round(2).tolist(),
               n_distinct=int(len(set(lab))), n_distinct_tied=int(len(set(lab[tied]))),
               n_tied=int(tied.sum()), frac_same=float((lab == lab[ib]).mean()),
               s_per_seq=meta['s_per_seq'], s_per_run=meta['s_per_run'],
               gap_kT=float((E[lab != lab[ib]].min() - E[ib]) / kT0) if (lab != lab[ib]).any() else float('nan'),
               rmsd_best_to_others=[float(A3.kabsch(XB[i][None], XB[ib])[0]) for i in range(len(E)) if i != ib])
    if targets is not None and key in targets:
        tx = np.array(targets[key]['x'], float)[:L]
        out['rmsd_to_target'] = float(A3.kabsch(XB[ib][None], tx)[0])
        out['rmsd_runs_to_target'] = A3.kabsch(XB, tx).round(3).tolist()
    sx = r['snapX'].astype(np.float64)
    se = r['snapE'].astype(np.float64)
    nr, K, S = se.shape
    sb = sx[..., :L, :].reshape(-1, L, 3)
    rms = A3.kabsch(sb, nat[:L]).reshape(nr, K, S)
    Ek = [se[:, k].reshape(-1) for k in range(K)]
    rf = RMSD_FOLD32 * math.sqrt(L / 32.0)
    Fk = [(rms[:, k] <= rf).reshape(-1) for k in range(K)]
    logw, Ea = TT.wham(Ek, temps)
    th = TT.thermo(Ek, temps, Fk, TGRID)
    f = th['f']
    con, rcut = sc_contacts(nat[L:], seq)
    ci, cj = np.nonzero(np.triu(con))
    if len(ci):
        ss = sx[..., L:, :].reshape(-1, L, 3)
        dq = np.linalg.norm(ss[:, ci] - ss[:, cj], axis=-1)
        qv = (dq < 1.2 * rcut[ci, cj]).mean(1).reshape(nr, K, S)
        qa = np.concatenate([qv[:, k].reshape(-1) for k in range(K)])
        Q = []
        for T in TGRID:
            w = np.exp(logw(T)); w /= w.sum(); Q.append(float((w * qa).sum()))
        Q = np.array(Q)
        out['Q_curve'] = Q[::5].round(4).tolist()
        q0, q1 = Q[0], Q[-1]
        out['Q_lowT'], out['Q_highT'] = float(q0), float(q1)
        out['Q300'] = float(np.interp(300.0, TGRID, Q))
        j = np.argmax(Q < 0.5 * q0)
        out['TmQ'] = float(TGRID[j]) if Q[-1] < 0.5 * q0 else float('inf')
        if q0 - q1 > 0.05:
            a8 = q1 + 0.8 * (q0 - q1); a2 = q1 + 0.2 * (q0 - q1)
            out['widthQ_K'] = float(TGRID[int(np.argmax(Q < a2))] - TGRID[int(np.argmax(Q < a8))])
        else:
            out['widthQ_K'] = float('nan')
    out['n_native_contacts'] = int(len(ci))
    out['f_at_ladder'] = [float(np.mean(x)) for x in Fk]
    out['f300'] = float(np.interp(300.0, TGRID, f))
    out['dG300_kT'] = float(np.interp(300.0, TGRID, th['dG']))
    if f[0] < 0.5:
        Tm = float('-inf')
    elif f[-1] > 0.5:
        Tm = float('inf')
    else:
        j = int(np.argmax(f < 0.5))
        Tm = float(np.interp(0.5, [f[j], f[j - 1]], [TGRID[j], TGRID[j - 1]]))
    out['Tm'] = Tm
    flo, fhi = f[0], f[-1]
    if flo - fhi > 0.3:
        a8 = fhi + 0.8 * (flo - fhi); a2 = fhi + 0.2 * (flo - fhi)
        out['width_K'] = float(TGRID[int(np.argmax(f < a2))] - TGRID[int(np.argmax(f < a8))])
    else:
        out['width_K'] = float('nan')
    kc = TT.kaya_chan(TGRID, th['C'], th['E'])
    out.update({k: kc[k] for k in ('Tmax', 'k2', 'k2s', 'dHvH', 'dHcal')})
    out['C_curve'] = th['C'][::5].round(4).tolist()
    out['f_curve'] = f[::5].round(4).tolist()
    n = r['best_n'][ib].astype(float)
    out['native_n'] = n.round(2).tolist()
    out['native_contacts'] = [[int(i), int(j)] for i, j in zip(ci, cj)]
    out['parts_kT'] = {p: float(v[ib] / kT0) for p, v in ((k[5:], r[k]) for k in r if k.startswith('part_'))}
    buried = n >= BURIED_N
    out['buried'] = buried.astype(int).tolist()
    sbr = []
    for i in range(L):
        if int(seq[i]) in CHARGED and buried[i]:
            partners = [j for j in range(L) if con[i, j] and int(seq[j]) in CHARGED
                        and CHARGED[int(seq[j])] * CHARGED[int(seq[i])] < 0]
            sbr.append(dict(i=i, m=int(seq[i]), partnered=bool(partners)))
    out['buried_charges'] = sbr
    # helix content of the native (backbone H-bonds i -> i+4 formed) and strand pairing
    xb = nat[:L]
    if L > 4:
        r4 = np.linalg.norm(xb[4:] - xb[:-4], axis=1); r3 = np.linalg.norm(xb[3:-1] - xb[:-4], axis=1)
        out['helix_hb_share'] = float(np.mean((np.abs(r4 - TB.R_H4) < 0.08) & (np.abs(r3 - TB.R_H3) < 0.08)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('prefixes', nargs='+')
    ap.add_argument('--dir', default=r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23')
    ap.add_argument('--out', default=None)
    ap.add_argument('--target-file', default=None)
    ap.add_argument('--native-file', default=None, help='Go check: measure f and Q against these structures')
    a = ap.parse_args()
    targets = json.load(open(a.target_file)) if a.target_file else None
    natives = json.load(open(a.native_file)) if a.native_file else None
    rows = [analyse_one(r, targets, natives) for r in A3.load(a.prefixes, a.dir)]
    out = a.out or os.path.join(a.dir, 'analysis_' + '_'.join(a.prefixes) + '.json')
    json.dump(rows, open(out, 'w'))
    for x in rows:
        print(x['name'][:18], x['L'], 'E %.1f' % x['E_best_kT'], 'dist', x['n_distinct'], 'tied', x['n_distinct_tied'],
              'same %.2f' % x['frac_same'], 'f300 %.2f' % x['f300'], 'Q0 %.2f' % x.get('Q_lowT', 0),
              'TmQ', x.get('TmQ'), 'Tmax %.0f' % x['Tmax'], 'k2s %.2f' % x['k2s'],
              'rmsdT %.2f' % x.get('rmsd_to_target', -1), 'hx %.2f' % x.get('helix_hb_share', 0))
    print('wrote', out)


if __name__ == '__main__':
    main()
