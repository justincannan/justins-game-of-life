"""Task 23, stage 2: the design test. Sequences are designed for a target backbone with the model's own energy, by
Monte Carlo in sequence space, maximising the energy gap between the target and its competitors (decoys); then they
are folded blind (run_tb.py fold) and judged with step 3's readouts (analyse_tb.py).

Method (Claude's; the standard negative-design loop, e.g. Shakhnovich and Gutin 1993 on lattices, here off-lattice):
  - energy of a sequence on a backbone: twobead.Model2 with side chains at their ideal positions (no relaxation);
  - competitors: snapshots and lowest structures from REMD folding runs of the same length (random sequences in
    round 0, then the designed sequences themselves), minus those within the 'folded' RMSD of the target;
  - objective: gap = softmin_d E_d - E_target, softmin at 1 kT (= -kT ln sum exp(-E_d / kT));
  - Metropolis on the gap, 8 parallel chains per target, temperature annealed 2 -> 0.2 kT, one point mutation per step;
  - after each round the designs are folded (short REMD), their own competing folds are added to the decoys, and the
    design is repeated from the best sequences so far.
Usage: python design_tb.py --rounds 3 --out DIR    (GPU; writes DIR/design_state.json and results/tb_designs.json)
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


def energies(seqs, backbones, chunk=4000):
    """E (kT) of each sequence (M, L) on each backbone (D, L, 3), side chains placed ideally. Returns (M, D)."""
    M, D = len(seqs), len(backbones)
    Pm = np.stack([TB.local_probs(s) for s in seqs])
    S = np.asarray(seqs)
    bb = torch.tensor(backbones, dtype=torch.float32, device=DEV)
    out = np.zeros(M * D)
    with torch.no_grad():
        for c0 in range(0, M * D, chunk):
            c1 = min(M * D, c0 + chunk)
            ci = np.arange(c0, c1)
            m = TB.Model2(S[ci // D], Pm[ci // D], device=DEV)
            x = TB.place_sc(m, bb[torch.as_tensor(ci % D, device=DEV)])
            out[c0:c1] = m.energy(x).double().cpu().numpy() / KT
    return out.reshape(M, D)


def gap(Et, Ed):
    """softmin over decoys minus target, kT; Et (M,), Ed (M, D)."""
    mn = Ed.min(1)
    sm = mn - np.log(np.exp(-(Ed - mn[:, None])).sum(1))
    return sm - Et


def design(target, decoys, n_chain=8, n_step=400, seed=0, start=None):
    rng = np.random.default_rng(seed)
    L = len(target)
    allx = np.concatenate([target[None], decoys], 0)
    S = [rng.integers(0, 16, L) for _ in range(n_chain)] if start is None else [np.array(s) for s in start]
    while len(S) < n_chain:
        S.append(rng.integers(0, 16, L))
    E = energies(S, allx)
    G = gap(E[:, 0], E[:, 1:])
    best = [(G[k], S[k].copy(), E[k, 0]) for k in range(n_chain)]
    for step in range(n_step):
        tau = 2.0 * (0.1 ** (step / max(1, n_step - 1)))
        prop = []
        for s in S:
            t = s.copy(); i = rng.integers(L); t[i] = (t[i] + rng.integers(1, 16)) % 16
            prop.append(t)
        Ep = energies(prop, allx)
        Gp = gap(Ep[:, 0], Ep[:, 1:])
        for k in range(n_chain):
            if Gp[k] >= G[k] or rng.random() < math.exp((Gp[k] - G[k]) / tau):
                S[k], G[k] = prop[k], Gp[k]
                if G[k] > best[k][0]:
                    best[k] = (G[k], S[k].copy(), Ep[k, 0])
    return [(float(g), s.tolist(), float(e)) for g, s, e in best]


def decoys_from(res, target, L, n_snap=200, rng=None):
    """backbone decoys from a fold_batch result list (only entries of length L); far from the target."""
    rng = rng or np.random.default_rng(0)
    out = []
    for r in res:
        if r['L'] != L:
            continue
        sx = r['snapX'][:, :, :, :L].astype(np.float64)        # (nr, K, S, L, 3)
        nr, K, Sn = sx.shape[:3]
        flat = sx[:, :K * 2 // 3].reshape(-1, L, 3)             # the lower two thirds of the ladder
        pick = rng.choice(len(flat), min(n_snap, len(flat)), replace=False)
        out.append(flat[pick])
        out.append(r['best_x'][:, :L].astype(np.float64))
    if not out:
        return np.zeros((0, L, 3))
    X = np.concatenate(out, 0)
    rf = A3.RMSD_FOLD32 * math.sqrt(L / 32.0)
    far = A3.kabsch(X, target) > rf
    return X[far]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounds', type=int, default=3)
    ap.add_argument('--out', default=os.path.join(RT.OUT, 'design'))
    ap.add_argument('--fold-steps', type=int, default=30000)
    ap.add_argument('--fold-runs', type=int, default=4)
    ap.add_argument('--mc-steps', type=int, default=400)
    ap.add_argument('--keep', type=int, default=4)
    ap.add_argument('--max-decoys', type=int, default=600)
    ap.add_argument('--decoy-steps', type=int, default=20000)
    ap.add_argument('--final-out', default=os.path.join(HERE, 'results', 'tb_designs.json'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    T = json.load(open(os.path.join(HERE, 'results', 'tb_targets.json')))
    names = list(T)
    tx = {n: np.array(T[n]['x'], float) for n in names}
    rng = np.random.default_rng(5)
    t0 = time.time()
    state = dict(rounds=[], timing={})
    # round 0 decoys: REMD of random sequences of each target's length (and the hand designs)
    items = []
    for n in names:
        L = len(tx[n])
        for k in range(4):
            items.append((n, rng.integers(0, 16, L).tolist()))
        if T[n]['hand_seq']:
            items.append((n, T[n]['hand_seq']))
    res, meta = RT.fold_batch([np.array(q) for _, q in items], 2, a.decoy_steps, seed=11)
    state['timing']['decoy_fold_s'] = meta['total_s']
    dec = {n: decoys_from([r for (m, _), r in zip(items, res) if m == n], tx[n], len(tx[n]), rng=rng) for n in names}
    RT.log('round 0 decoys', {n: len(v) for n, v in dec.items()}, '%.0fs' % meta['total_s'])
    starts = {n: None for n in names}
    allbest = {n: [] for n in names}
    for rd in range(a.rounds):
        t1 = time.time()
        cand = []
        for n in names:
            D = dec[n]
            if len(D) > a.max_decoys:
                # keep the lowest structures (by the current best sequences' energies) and a random rest
                D = D[rng.choice(len(D), a.max_decoys, replace=False)]
            best = design(tx[n], D, n_step=a.mc_steps, seed=100 * rd + names.index(n), start=starts[n])
            best.sort(key=lambda t: -t[0])
            uniq = []
            for g, s, e in best:
                if s not in [u[1] for u in uniq]:
                    uniq.append((g, s, e))
            for g, s, e in uniq[:a.keep]:
                cand.append((n, s, g, e))
            RT.log('round', rd, n, 'decoys', len(D), 'gaps', [round(u[0], 1) for u in uniq[:a.keep]])
        t_mc = time.time() - t1
        res, meta = RT.fold_batch([np.array(s) for _, s, _, _ in cand], a.fold_runs, a.fold_steps, seed=50 + rd)
        rows = []
        for (n, s, g, e), r in zip(cand, res):
            L = len(s)
            E = r['best_e'].astype(float); X = r['best_x'][:, :L].astype(float)
            ib = int(np.argmin(E))
            rm = A3.kabsch(X, tx[n])
            lab = A3.cluster(X, E)
            # the lowest structure's energy against the target's, with this sequence (ideal side chains vs relaxed)
            rows.append(dict(target=n, seq=s, gap_kT=g, E_target_kT=e, E_fold_best_kT=float(E[ib] / KT),
                             rmsd_best_to_target=float(rm[ib]), rmsd_runs=rm.round(3).tolist(),
                             frac_same=float((lab == lab[ib]).mean()), round=rd))
            dec[n] = np.concatenate([dec[n], decoys_from([r], tx[n], L, n_snap=120, rng=rng)], 0)
            allbest[n].append(rows[-1])
        for n in names:
            allbest[n].sort(key=lambda t: (t['rmsd_best_to_target'], -t['gap_kT']))
            starts[n] = [t['seq'] for t in allbest[n][:8]]
        state['rounds'].append(dict(round=rd, mc_s=t_mc, fold_s=meta['total_s'], rows=rows))
        RT.log('round', rd, 'folded', len(cand), '%.0fs' % meta['total_s'],
               [(r['target'][:6], round(r['rmsd_best_to_target'], 2), r['frac_same']) for r in rows])
        json.dump(state, open(os.path.join(a.out, 'design_state.json'), 'w'))
    state['timing']['total_s'] = time.time() - t0
    json.dump(state, open(os.path.join(a.out, 'design_state.json'), 'w'))
    # the final designs: the 3 best per target (closest lowest fold to the target, then the gap), for the blind fold
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
