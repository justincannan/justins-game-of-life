"""Task 26 step 3: the design loop with a relaxed target and relaxed decoys (Justin's decision of 15 November,
about 21:26; proposal 3 of report 23). GPU.

Differences from task 23's design_tb.py (which placed side chains ideally on unrelaxed backbones, used thermal
snapshots as decoys and ran two rounds):
  - every energy in the gap is a RELAXED energy: the structure (backbone and side chains, side chains free) is
    minimised with the trial sequence before it is scored (decoys: Adam, cosine-decayed step; the target: capped
    gradient descent from ideal side chains, TARGET_ITERS steps, then Adam warm starts);
  - decoys are kept as relaxed two-bead structures (the relaxed competitors), and each round's blind folds add their
    own lowest structures and low-temperature snapshots;
  - more rounds (default 4).
Cost control (all stated in the report):
  - at the start of each round every decoy of the pool is relaxed from its stored coordinates with each chain's
    sequence (FULL_ITERS steps); the K_ACTIVE lowest (outside the target's 'folded' RMSD after relaxation) become
    the chain's active competitors;
  - each Monte Carlo proposal (one point mutation) re-relaxes the target and the active competitors from the
    parent's relaxed coordinates (WARM_ITERS steps) and is accepted by Metropolis on the gap;
  - at the end of each round the best sequences' gaps are re-evaluated against the WHOLE pool, fully relaxed from the
    stored coordinates (the gaps reported).
Gap = softmin over relaxed decoys (1 kT) - E(relaxed target), in kT. A decoy whose relaxation ends within the
folded RMSD of the target is not a competitor (it is the target) and is skipped.
Usage: python design26.py --out DIR [--rounds 4] [--model JSON]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tertiary as TT  # noqa: E402
import twobead as TB  # noqa: E402
import run_tb as RT  # noqa: E402
import analyse_step3 as A3  # noqa: E402

KT = TB.KT0
DEV = 'cuda'
T23 = r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23'
MK = dict(elec='cd', h_charge='iso', helix='coop')


def rfold(L):
    return A3.RMSD_FOLD32 * math.sqrt(L / 32.0)


def pad_batch(seqs, xs, Lmax):
    """seqs: list of int arrays; xs: list of (2L, 3) arrays -> idx, P, X (n, 2Lmax, 3) torch, padded on a far line."""
    n = len(seqs)
    idx, P = TB.seq_params([np.asarray(s) for s in seqs], Lmax, helix=MK.get('helix', 'v23'))
    X = np.zeros((n, 2 * Lmax, 3), np.float32)
    ar = np.arange(Lmax)
    line = np.stack([100.0 + 0.3 * ar, 0.2 * (ar % 2), 0.15 * ((ar // 2) % 2)], 1)
    for k, (s, x) in enumerate(zip(seqs, xs)):
        L = len(s)
        X[k, :Lmax] = line; X[k, Lmax:] = line + np.array([0, 0.5, 0])
        X[k, :L] = x[:L]; X[k, Lmax:Lmax + L] = x[L:2 * L]
    return idx, P, torch.tensor(X, device=DEV)


def unpad(X, L, Lmax):
    return torch.cat([X[..., :L, :], X[..., Lmax:Lmax + L, :]], -2)


def relax_model(m, x, iters, lr=0.004):
    x = x.clone().requires_grad_(True)
    opt = torch.optim.Adam([x], lr=lr)
    m3 = m.mask[:, :, None].float()
    for k in range(iters):
        for g in opt.param_groups:
            g['lr'] = lr * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * k / max(1, iters))))
        opt.zero_grad()
        e = m.energy(x)
        e.sum().backward()
        x.grad.nan_to_num_(); x.grad.mul_(m3)
        opt.step()
    with torch.no_grad():
        e = m.energy(x)
    return x.detach(), e.detach()


def relax(seqs, xs, iters, chunk=1500, lr=0.008):
    """relax each (sequence, two-bead structure) pair; returns list of relaxed (2L, 3) numpy and energies (kT)."""
    out_x, out_e = [None] * len(seqs), np.zeros(len(seqs))
    order = np.argsort([len(s) for s in seqs])
    for c0 in range(0, len(seqs), chunk):
        sel = order[c0:c0 + chunk]
        Lmax = max(len(seqs[i]) for i in sel)
        idx, P, X = pad_batch([seqs[i] for i in sel], [xs[i] for i in sel], Lmax)
        m = TB.Model2(idx, P, device=DEV, **MK)
        xr, e = relax_model(m, X, iters, lr)
        xr = xr.cpu().numpy(); e = e.double().cpu().numpy() / KT
        for j, i in enumerate(sel):
            L = len(seqs[i])
            out_x[i] = np.concatenate([xr[j, :L], xr[j, Lmax:Lmax + L]], 0)
            out_e[i] = e[j]
    return out_x, out_e


def softmin(E):
    E = np.asarray(E, float)
    if len(E) == 0:
        return float('inf')
    mn = E.min()
    return float(mn - np.log(np.exp(-(E - mn)).sum()))


def ideal_target(seq, xb):
    idx, P = TB.seq_params([np.asarray(seq)], len(seq), helix=MK.get('helix', 'v23'))
    m = TB.Model2(idx, P, device=DEV, **MK)
    return TB.place_sc(m, torch.tensor(xb[None], dtype=torch.float32, device=DEV))[0].cpu().numpy()


def pool_from_results(res, L, n_snap, rng):
    """two-bead decoys from fold_batch results (lower two thirds of the ladder) plus each run's lowest structure."""
    out = []
    for r in res:
        if r['L'] != L:
            continue
        sx = r['snapX'].astype(np.float32)          # (nr, K, S, 2L, 3)
        K = sx.shape[1]
        flat = sx[:, :K * 2 // 3].reshape(-1, 2 * L, 3)
        pick = rng.choice(len(flat), min(n_snap, len(flat)), replace=False)
        out.extend(list(flat[pick]))
        out.extend(list(np.asarray(r['best_x'], np.float32)))
    return out


def pool_from_t23(name, L, n_snap, rng):
    z = np.load(os.path.join(T23, 'designs_final_b00.npz'))
    meta = json.loads(str(z['meta']))
    out = []
    for k, nm in enumerate(meta['names']):
        if nm.split('__')[0] != name:
            continue
        sx = z[f's{k}_snapX'].astype(np.float32)
        K = sx.shape[1]
        flat = sx[:, :K * 2 // 3].reshape(-1, sx.shape[-2], 3)[:, :2 * L]
        pick = rng.choice(len(flat), min(n_snap, len(flat)), replace=False)
        out.extend(list(flat[pick]))
        out.extend(list(z[f's{k}_best_x'].astype(np.float32)[:, :2 * L]))
    return out


def relax_targets(seqs, tbs, iters=2000):
    """targets: ideal side chains on the target backbone, relaxed by capped gradient descent (tertiary.minimise, as
    task 23's relax_targets_tb.py). Adam from ideal side chains failed here (first try: targets 10-70 kT above this,
    and some bba targets stuck at +2,000 kT with side chains on top of each other; bug of my own, fixed)."""
    Lmax = max(len(s) for s in seqs)
    xs = [ideal_target(s, tb) for s, tb in zip(seqs, tbs)]
    idx, P, X = pad_batch([np.asarray(s) for s in seqs], xs, Lmax)
    m = TB.Model2(idx, P, device=DEV, **MK)
    x, e = TT.minimise(m, X, iters=iters)
    x = x.cpu().numpy(); e = e.double().cpu().numpy() / KT
    return [np.concatenate([x[k, :len(s)], x[k, Lmax:Lmax + len(s)]], 0) for k, s in enumerate(seqs)], e


def far_from_target(xs, tx, L):
    if not len(xs):
        return np.zeros(0, bool)
    X = np.stack([x[:L] for x in xs]).astype(np.float64)
    return A3.kabsch(X, tx) > rfold(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-16\task26\design')
    ap.add_argument('--rounds', type=int, default=4)
    ap.add_argument('--chains', type=int, default=8)
    ap.add_argument('--mc-steps', type=int, default=80)
    ap.add_argument('--active', type=int, default=24)
    ap.add_argument('--warm-iters', type=int, default=80)
    ap.add_argument('--full-iters', type=int, default=300)
    ap.add_argument('--target-iters', type=int, default=2000)
    ap.add_argument('--max-pool', type=int, default=300)
    ap.add_argument('--keep', type=int, default=4)
    ap.add_argument('--fold-runs', type=int, default=4)
    ap.add_argument('--fold-steps', type=int, default=30000)
    ap.add_argument('--decoy-steps', type=int, default=20000)
    ap.add_argument('--model', default=json.dumps(MK))
    ap.add_argument('--final-out', default=os.path.join(HERE, 'results', 't26_designs.json'))
    a = ap.parse_args()
    MK.clear(); MK.update(json.loads(a.model))
    os.makedirs(a.out, exist_ok=True)
    T = json.load(open(os.path.join(HERE, 'results', 'tb_targets.json')))
    names = list(T)
    tb = {n: np.array(T[n]['x'], float) for n in names}
    Ls = {n: len(tb[n]) for n in names}
    rng = np.random.default_rng(26)
    t0 = time.time()
    state = dict(model=MK, args=vars(a), rounds=[], timing={})
    # ---- round 0 pool: task 23's blind folds of these targets' designs, and REMD of random sequences (this model)
    items = []
    for n in names:
        for k in range(4):
            items.append((n, rng.integers(0, 16, Ls[n]).tolist()))
        if T[n]['hand_seq']:
            items.append((n, T[n]['hand_seq']))
    res, meta = RT.fold_batch([np.array(q) for _, q in items], 2, a.decoy_steps, seed=26, **MK)
    state['timing']['decoy_fold_s'] = meta['total_s']
    pool = {}
    for n in names:
        p = pool_from_t23(n, Ls[n], 120, rng) + pool_from_results([r for (m, _), r in zip(items, res) if m == n], Ls[n], 120, rng)
        p = [x for x, f in zip(p, far_from_target(p, tb[n], Ls[n])) if f]
        pool[n] = p
    RT.log('round 0 pool', {n: len(v) for n, v in pool.items()}, '%.0fs' % meta['total_s'])
    # chains: (target, sequence)
    chains = []
    for n in names:
        for k in range(a.chains):
            s = rng.integers(0, 16, Ls[n])
            chains.append(dict(target=n, seq=s))
    allbest = {n: [] for n in names}
    t_relax = 0.0
    n_relaxed = 0
    for rd in range(a.rounds):
        t1 = time.time()
        # trim pools (keep the most recent and a random rest)
        for n in names:
            if len(pool[n]) > a.max_pool:
                keep = list(range(len(pool[n]) - a.max_pool // 3, len(pool[n])))
                rest = rng.choice(len(pool[n]) - a.max_pool // 3, a.max_pool - len(keep), replace=False).tolist()
                pool[n] = [pool[n][i] for i in sorted(rest) + keep]
        # full relaxation of the pool for every chain's current sequence -> active competitors
        S, X, own = [], [], []
        ts = time.time()
        xt_all, et_all = relax_targets([c['seq'] for c in chains], [tb[c['target']] for c in chains], a.target_iters)
        t_relax += time.time() - ts
        for ci, c in enumerate(chains):
            n = c['target']
            for j, x in enumerate(pool[n]):
                S.append(c['seq']); X.append(x); own.append((ci, j))
        ts = time.time()
        xr, er = relax(S, X, a.full_iters)
        t_relax += time.time() - ts; n_relaxed += len(S)
        for ci, c in enumerate(chains):
            n, L = c['target'], Ls[c['target']]
            kd = [k for k, (cc, j) in enumerate(own) if cc == ci]
            c['xt'], c['et'] = xt_all[ci], float(et_all[ci])
            far = far_from_target([xr[k] for k in kd], tb[n], L)
            kd = [k for k, f in zip(kd, far) if f]
            kd = sorted(kd, key=lambda k: er[k])[:a.active]
            c['xa'] = [xr[k] for k in kd]; c['ea'] = np.array([er[k] for k in kd])
            c['gap'] = softmin(c['ea']) - c['et']
        RT.log('round', rd, 'start gaps', {n: np.round(sorted([c['gap'] for c in chains if c['target'] == n])[::-1][:4], 1).tolist() for n in names})
        # Monte Carlo in sequence space, all chains at once
        for step in range(a.mc_steps):
            tau = 2.0 * (0.1 ** (step / max(1, a.mc_steps - 1)))
            S, X, own = [], [], []
            props = []
            for ci, c in enumerate(chains):
                t = c['seq'].copy(); i = rng.integers(len(t)); t[i] = (t[i] + rng.integers(1, 16)) % 16
                props.append(t)
                S.append(t); X.append(c['xt']); own.append(ci)
                for x in c['xa']:
                    S.append(t); X.append(x); own.append(ci)
            ts = time.time()
            xr, er = relax(S, X, a.warm_iters, lr=0.004)
            t_relax += time.time() - ts; n_relaxed += len(S)
            own = np.array(own)
            for ci, c in enumerate(chains):
                ks = np.nonzero(own == ci)[0]
                et, ea = er[ks[0]], er[ks[1:]]
                n, L = c['target'], Ls[c['target']]
                # a competitor that relaxed into the target is skipped (it is the target)
                far = far_from_target([xr[k] for k in ks[1:]], tb[n], L)
                g = softmin(ea[far]) - et if far.any() else -1e9
                if g >= c['gap'] or rng.random() < math.exp((g - c['gap']) / tau):
                    c['seq'], c['gap'], c['et'] = props[ci], g, et
                    c['xt'] = xr[ks[0]]; c['xa'] = [xr[k] for k in ks[1:]]; c['ea'] = ea
                    if not c.get('best') or g > c['best'][0]:
                        c['best'] = (g, props[ci].copy())
            if step % 20 == 0:
                RT.log('round', rd, 'mc', step, 'tau %.2f' % tau, 'gaps', {n[:8]: round(max(c['gap'] for c in chains if c['target'] == n), 1) for n in names},
                       'relax %.0fs' % t_relax)
        t_mc = time.time() - t1
        # candidates: per target the best distinct sequences (by the chains' own best gaps)
        cand = []
        for n in names:
            bs = sorted([c['best'] for c in chains if c['target'] == n and c.get('best')], key=lambda t: -t[0])
            seen = []
            for g, s in bs:
                if s.tolist() not in seen:
                    seen.append(s.tolist())
                if len(seen) >= a.keep:
                    break
            cand.extend([(n, s) for s in seen])
        # gaps re-evaluated against the whole pool, fully relaxed from the stored coordinates
        S, X, own = [], [], []
        ts = time.time()
        xtc, etc = relax_targets([np.array(s) for _, s in cand], [tb[n] for n, _ in cand], a.target_iters)
        for ki, (n, s) in enumerate(cand):
            for x in pool[n]:
                S.append(np.array(s)); X.append(x); own.append(ki)
        xr, er = relax(S, X, a.full_iters)
        t_relax += time.time() - ts; n_relaxed += len(S)
        own = np.array(own)
        full = []
        for ki, (n, s) in enumerate(cand):
            ks = np.nonzero(own == ki)[0]
            far = far_from_target([xr[k] for k in ks], tb[n], Ls[n])
            full.append(dict(gap_full_kT=softmin(er[ks][far]) - float(etc[ki]), E_target_relaxed_kT=float(etc[ki]),
                             E_best_decoy_kT=float(er[ks][far].min()) if far.any() else None,
                             target_drift_nm=float(A3.kabsch(xtc[ki][None, :Ls[n]].astype(np.float64), tb[n])[0])))
        # fold the candidates blind (short REMD); their structures join the pool as relaxed competitors
        tf = time.time()
        res, meta = RT.fold_batch([np.array(s) for _, s in cand], a.fold_runs, a.fold_steps, seed=60 + rd, **MK)
        rows = []
        for (n, s), r, fu in zip(cand, res, full):
            L = Ls[n]
            E = r['best_e'].astype(float) / KT
            XB = r['best_x'][:, :L].astype(float)
            ib = int(np.argmin(E))
            rm = A3.kabsch(XB, tb[n])
            lab = A3.cluster(XB, E)
            row = dict(target=n, seq=list(map(int, s)), round=rd, E_fold_best_kT=float(E[ib]),
                       rmsd_best_to_target=float(rm[ib]), rmsd_runs=rm.round(3).tolist(),
                       frac_same=float((lab == lab[ib]).mean()),
                       target_minus_fold_kT=fu['E_target_relaxed_kT'] - float(E[ib]), **fu)
            rows.append(row)
            allbest[n].append(row)
            new = pool_from_results([r], L, 60, rng)
            new = [x for x, f in zip(new, far_from_target(new, tb[n], L)) if f]
            pool[n].extend(new)
        t_fold = time.time() - tf
        # next round starts from the best sequences so far (closest blind fold, then the full gap), one per chain
        for n in names:
            allbest[n].sort(key=lambda t: (t['rmsd_best_to_target'] > rfold(Ls[n]), -t['gap_full_kT']))
            starts = [np.array(t['seq']) for t in allbest[n][:a.chains]]
            cs = [c for c in chains if c['target'] == n]
            for k, c in enumerate(cs):
                c['seq'] = starts[k % len(starts)].copy() if starts else c['seq']
                c.pop('best', None)
        state['rounds'].append(dict(round=rd, mc_s=t_mc, fold_s=t_fold, rows=rows, pool={n: len(v) for n, v in pool.items()}))
        RT.log('round', rd, 'folded', len(cand), '%.0fs' % t_fold, [(r['target'][:6], round(r['rmsd_best_to_target'], 2),
               r['frac_same'], round(r['gap_full_kT'], 1), round(r['target_minus_fold_kT'], 1)) for r in rows])
        state['timing'].update(total_s=time.time() - t0, relax_s=t_relax, n_relaxed=n_relaxed)
        json.dump(state, open(os.path.join(a.out, 'design_state.json'), 'w'))
    state['timing'].update(total_s=time.time() - t0, relax_s=t_relax, n_relaxed=n_relaxed)
    json.dump(state, open(os.path.join(a.out, 'design_state.json'), 'w'))
    final = {}
    for n in names:
        for k, t in enumerate(allbest[n][:3]):
            final[f'{n}__d{k}'] = t['seq']
        if T[n]['hand_seq']:
            final[f'{n}__hand'] = T[n]['hand_seq']
    json.dump(final, open(a.final_out, 'w'), indent=0)
    RT.log('design done %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
