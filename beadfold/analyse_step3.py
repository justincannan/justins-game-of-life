"""Task 15, step 3: analyse the folding batches written by run_step3.py (CPU only).

Usage: python analyse_step3.py PREFIX [PREFIX ...] [--dir DIR] [--out JSON]
Per sequence: uniqueness (distinct lowest folds in the runs), thermodynamics by WHAM over the replica ladder (fraction
folded, Tm, heat capacity, Kaya-Chan kappa2, transition width, dG_fold at 300 K), and the native's core and charges.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tertiary as TT  # noqa: E402

RMSD_SAME = 0.30      # nm: two lowest structures are the same fold (a choice; C-alpha folds are usually "the same" under 0.2-0.3 nm)
RMSD_FOLD32 = 0.30    # nm: a snapshot is folded (in the native) within RMSD_FOLD32 * sqrt(L / 32) of the native
                      # (a choice; scaled so that short chains, which are close to any compact shape, are not
                      # counted folded by chance)
TIE_KT = 1.0          # runs within 1 kT of the best energy count as tied lowest
BURIED_N = 4.0        # non-local neighbours for "buried" (the coop sigmoid is past 0.7 there)
TGRID = np.arange(250.0, 480.5, 1.0)
CHARGED = {0: -1, 2: -1, 8: +1, 10: +1}


def kabsch(A, Bm):
    """RMSD between A (N, L, 3) and Bm (L, 3) or (N, L, 3); proper rotations."""
    A = A - A.mean(-2, keepdims=True)
    Bm = Bm - Bm.mean(-2, keepdims=True)
    if Bm.ndim == 2:
        Bm = np.broadcast_to(Bm, A.shape)
    H = np.einsum('nli,nlj->nij', A, Bm)
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(U @ Vt))
    S[:, 2] *= d
    e2 = ((A ** 2).sum((1, 2)) + (Bm ** 2).sum((1, 2)) - 2 * S.sum(1)) / A.shape[1]
    return np.sqrt(np.clip(e2, 0, None))


def cluster(X, E):
    """leader clustering in energy order; returns cluster id per run (0 = the best run's fold)."""
    order = np.argsort(E)
    lab = -np.ones(len(E), int)
    leaders = []
    for i in order:
        for c, j in enumerate(leaders):
            if kabsch(X[i][None].astype(np.float64), X[j].astype(np.float64))[0] <= RMSD_SAME:
                lab[i] = c; break
        else:
            leaders.append(i); lab[i] = len(leaders) - 1
    return lab


def load(prefixes, d):
    seqs = []
    for pre in prefixes:
        for p in sorted(glob.glob(os.path.join(d, pre + '_b*.npz'))):
            z = np.load(p)
            meta = json.loads(str(z['meta']))
            for k in range(meta['n_seq']):
                r = {key[len(f's{k}_'):]: z[key] for key in z.files if key.startswith(f's{k}_')}
                r['meta'] = meta
                r['set'] = pre
                r['name'] = meta.get('names', ['?'] * meta['n_seq'])[k]
                seqs.append(r)
    return seqs


def analyse_one(r):
    meta = r['meta']
    temps = np.array(meta['temps'])
    seq = r['seq'].astype(int)
    L = len(seq)
    E = r['best_e'].astype(float)
    X = r['best_x'].astype(float)
    kT0 = TT.KT0
    lab = cluster(X, E)
    ib = int(np.argmin(E))
    nat = X[ib]
    tied = E <= E[ib] + TIE_KT * kT0
    out = dict(seq=seq.tolist(), L=L, set=r['set'], name=str(r['name']), mode=meta['mode'],
               E_best_kT=float(E[ib] / kT0), E_runs_kT=(E / kT0).round(2).tolist(),
               n_distinct=int(len(set(lab))), n_distinct_tied=int(len(set(lab[tied]))),
               n_tied=int(tied.sum()), frac_same=float((lab == lab[ib]).mean()),
               s_per_seq=meta['s_per_seq'],
               gap_kT=float((E[lab != lab[ib]].min() - E[ib]) / kT0) if (lab != lab[ib]).any() else float('nan'),
               rmsd_best_to_others=[float(kabsch(X[i][None], X[ib])[0]) for i in range(len(E)) if i != ib])
    # thermodynamics: snapshots (nr, K, S, L, 3)
    sx = r['snapX'].astype(np.float64)
    se = r['snapE'].astype(np.float64)
    nr, K, S = se.shape
    rms = kabsch(sx.reshape(-1, L, 3), nat).reshape(nr, K, S)
    Ek = [se[:, k].reshape(-1) for k in range(K)]
    rf = RMSD_FOLD32 * math.sqrt(L / 32.0)
    Fk = [(rms[:, k] <= rf).reshape(-1) for k in range(K)]
    th = TT.thermo(Ek, temps, Fk, TGRID)
    f = th['f']
    # Q: fraction of the native's contacts present (task 02's melting measure), WHAM-averaged
    dab = 0.5 * (TT.DIAM[seq][:, None] + TT.DIAM[seq][None])
    rcut = dab + TT.R_CONTACT_EXTRA
    dn = np.linalg.norm(nat[:, None] - nat[None], axis=-1)
    ci, cj = np.nonzero(np.triu((dn < rcut) & (np.abs(np.arange(L)[:, None] - np.arange(L)[None]) >= 3)))
    if len(ci):
        flat = sx.reshape(-1, L, 3)
        dq = np.linalg.norm(flat[:, ci] - flat[:, cj], axis=-1)
        qv = (dq < 1.2 * rcut[ci, cj]).mean(1).reshape(nr, K, S)
        logw, Ea = TT.wham(Ek, temps)
        qa = np.concatenate([qv[:, k].reshape(-1) for k in range(K)])
        Q = []
        for T in TGRID:
            w = np.exp(logw(T)); w /= w.sum(); Q.append(float((w * qa).sum()))
        Q = np.array(Q)
        out['Q_curve'] = Q[::5].round(4).tolist()
        q0, q1 = Q[0], Q[-1]
        out['Q_lowT'], out['Q_highT'] = float(q0), float(q1)
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
    # Tm: where f crosses 0.5 going up in T
    if f[0] < 0.5:
        Tm = float('-inf')
    elif f[-1] > 0.5:
        Tm = float('inf')
    else:
        j = int(np.argmax(f < 0.5))
        Tm = float(np.interp(0.5, [f[j], f[j - 1]], [TGRID[j], TGRID[j - 1]]))
    out['Tm'] = Tm
    # width: f from 80% to 20% of the way between its low-T and high-T values (task 02's measure, on f not Q)
    flo, fhi = f[0], f[-1]
    if flo - fhi > 0.3:
        a8 = fhi + 0.8 * (flo - fhi); a2 = fhi + 0.2 * (flo - fhi)
        t8 = TGRID[int(np.argmax(f < a8))]; t2 = TGRID[int(np.argmax(f < a2))]
        out['width_K'] = float(t2 - t8)
    else:
        out['width_K'] = float('nan')
    kc = TT.kaya_chan(TGRID, th['C'], th['E'])
    out.update({k: kc[k] for k in ('Tmax', 'k2', 'k2s', 'dHvH', 'dHcal')})
    out['C_curve'] = th['C'][::5].round(4).tolist()
    out['f_curve'] = f[::5].round(4).tolist()
    # the native: burial and core composition
    n = r['best_n'][ib].astype(float)
    out['native_n'] = n.round(2).tolist()
    d = np.linalg.norm(nat[:, None] - nat[None], axis=-1)
    dab = 0.5 * (TT.DIAM[seq][:, None] + TT.DIAM[seq][None])
    con = (d < dab + TT.R_CONTACT_EXTRA) & (np.abs(np.arange(L)[:, None] - np.arange(L)[None]) >= 3)
    out['native_contacts'] = [[int(i), int(j)] for i, j in zip(*np.nonzero(np.triu(con)))]
    out['parts_kT'] = {p: float(v[ib] / kT0) for p, v in ((k[5:], r[k]) for k in r if k.startswith('part_'))}
    buried = n >= BURIED_N
    out['buried'] = buried.astype(int).tolist()
    # charges: buried charged monomers, partnered (contact with an opposite charge) or not
    sb = []
    for i in range(L):
        if int(seq[i]) in CHARGED and buried[i]:
            partners = [j for j in range(L) if con[i, j] and int(seq[j]) in CHARGED
                        and CHARGED[int(seq[j])] * CHARGED[int(seq[i])] < 0]
            sb.append(dict(i=i, m=int(seq[i]), partnered=bool(partners)))
    out['buried_charges'] = sb
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('prefixes', nargs='+')
    ap.add_argument('--dir', default=r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-14\task15_step3')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    rows = [analyse_one(r) for r in load(a.prefixes, a.dir)]
    out = a.out or os.path.join(a.dir, 'analysis_' + '_'.join(a.prefixes) + '.json')
    json.dump(rows, open(out, 'w'))
    for x in rows:
        print(x['set'], x['L'], 'E %.1f' % x['E_best_kT'], 'distinct', x['n_distinct'], 'tied', x['n_tied'],
              x['n_distinct_tied'], 'same %.2f' % x['frac_same'], 'f300 %.2f' % x['f300'], 'dG300 %.1f' % x['dG300_kT'],
              'Tm %.0f' % x['Tm'], 'Tmax %.0f' % x['Tmax'], 'k2 %.2f k2s %.2f' % (x['k2'], x['k2s']),
              'w %.0f' % x['width_K'], 'TmQ', x.get('TmQ'), 'wQ', x.get('widthQ_K'), 'Q0 %.2f' % x.get('Q_lowT', 0), 'fl', np.round(x['f_at_ladder'], 2).tolist())
    print('wrote', out)


if __name__ == '__main__':
    main()
