"""Task 15, step 3: fold page and random sequences with the off-lattice folder and measure them (report 12, sec. 11).

Usage: python run_step3.py STAGE [--out DIR] [--quick]
Stages (each writes OUT/STAGE.json; GPU work):
  pilot     a few sequences, to check search convergence and the temperature window
  page      page sequences (fold3d/data/page_seqs.json, task 02's picker), coop model
  random    random sequences of length 32 (and 20), coop model
  additive  the additive control (no many-body term) on a subset of the page set
Analysis (CPU): analyse_step3.py.
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
sys.path.insert(0, os.path.join(HERE, '..', 'fold3d'))
import tertiary as TT  # noqa: E402

MONO = 'abcdefghijklmnop'
TEMPS = np.geomspace(250.0, 480.0, 12)       # replica ladder (K): a choice, wide enough to hold every Tm seen in the pilot
NBLOCK = 100                                 # steps between exchange attempts
SNAP = 500                                   # steps between snapshots
BURN = 0.3                                   # share of each run discarded before snapshots count


# designed positive controls (Claude's, by hand from the beads' rules; not from any fold of this model):
#  helical hairpin: two amphipathic helices (oily at heptad a and d; i, i+4 opposite charges), a tiny/proline-like turn;
#  three-stranded sheet: oily branched 5 alternating with polar 4 and 12, turns of 9 and 15.
_H = [1, 12, 0, 7, 12, 8, 6, 1, 12, 0, 7, 12, 8, 6]
DESIGNS = [('design_helixhairpin', _H + [9, 15, 9, 14] + _H),
           ('design_sheet3', [5, 4, 5, 12, 5, 4, 5, 9, 15, 5, 12, 5, 4, 5, 12, 5, 9, 15, 5, 4, 5, 12, 5, 4, 5])]


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def s2a(s):
    return np.array([MONO.index(c) for c in s], dtype=np.int64)


def pick_page(count, seed=1, nmin=12, nmax=36):
    """task 02's picker (fold3d/run_all.py, pick_page), so the page set is the same as task 02's."""
    import random
    d = json.load(open(os.path.join(HERE, '..', 'fold3d', 'data', 'page_seqs.json')))
    rnd = random.Random(seed)
    pool = [(w, s['seq'], s['n']) for w, lst in d['worlds'].items() for s in lst if nmin <= len(s['seq']) <= nmax]
    seen, out = set(), []
    pool.sort(key=lambda t: -t[2])
    for w, q, c in pool:
        if len(out) >= count // 2:
            break
        if q not in seen:
            seen.add(q); out.append((w, q))
    rest = [t for t in pool if t[1] not in seen]
    rnd.shuffle(rest)
    for w, q, c in rest:
        if len(out) >= count:
            break
        if q not in seen:
            seen.add(q); out.append((w, q))
    return out


def fold_batch(seqs, n_run, nsteps, mode='coop', seed=0, temps=TEMPS, **kw):
    """Fold sequences (lists of ints) together. Returns per-sequence dicts with snapshots and best structures."""
    t0 = time.time()
    go = kw.pop('go', None)
    sim = TT.REMD(seqs, n_run, temps, mode=mode, seed=seed, **kw)
    if go is not None:
        go_override(sim.model, go, n_run * len(temps))
        sim.x, _ = TT.minimise(sim.model, sim.x, iters=300)
    sim.build(NBLOCK)
    torch.cuda.synchronize()
    t_setup = time.time() - t0
    K, ns, nr, L = sim.K, sim.ns, sim.nr, sim.L
    nb = nsteps // NBLOCK
    every = SNAP // NBLOCK
    burn_b = int(BURN * nb)
    snapE, snapX = [], []
    best_e = torch.full((ns * nr,), float('inf'), device=sim.dev)
    best_x = torch.zeros((ns * nr, L, 3), device=sim.dev)
    t1 = time.time()
    for b in range(nb):
        sim.run_block()
        sim.exchange(b % 2)
        if (b + 1) % every == 0:
            e = sim.e.view(ns * nr, K)
            em, jm = e.min(1)
            better = em < best_e
            xr = sim.x.view(ns * nr, K, L, 3)[torch.arange(ns * nr, device=sim.dev), jm]
            best_e = torch.where(better, em, best_e)
            best_x = torch.where(better[:, None, None], xr, best_x)
            if b >= burn_b:
                snapE.append(sim.e.cpu().numpy().copy())
                xc = sim.x - (sim.x * sim.mask3).sum(1, keepdim=True) / sim.mask3.sum(1, keepdim=True)
                snapX.append(xc.half().cpu().numpy().copy())     # centred, so float16 keeps 0.01 nm
    torch.cuda.synchronize()
    t_run = time.time() - t1
    # quench each run's lowest structure
    idx1, P1 = TT.seq_params(sim.seqs, L)
    mq = TT.Model(np.repeat(idx1, nr, 0), np.repeat(P1, nr, 0), mode=mode, device=sim.dev,
                  **{k: v for k, v in kw.items() if k in ('eps_hb', 'n_half', 'w_burial', 'e_tab', 'h_tab')})
    if go is not None:
        go_override(mq, go, nr)
    xq, eq = TT.minimise(mq, best_x, iters=3000)
    parts = mq.energy(xq, parts=True)
    torch.cuda.synchronize()
    t_all = time.time() - t0
    SE = np.stack(snapE, 1)            # (C, S)
    SX = np.stack(snapX, 1)            # (C, S, L, 3)
    acc = (sim.n_swap_acc / np.maximum(sim.n_swap_try, 1)).tolist()
    out = []
    for k in range(ns):
        Lk = len(seqs[k])
        sl = slice(k * nr * K, (k + 1) * nr * K)
        rs = slice(k * nr, (k + 1) * nr)
        out.append(dict(
            seq=np.asarray(seqs[k]).tolist(), L=Lk,
            snapE=SE[sl].reshape(nr, K, -1), snapX=SX[sl, :, :Lk].reshape(nr, K, SE.shape[1], Lk, 3),
            best_e_raw=best_e[rs].cpu().numpy(), best_x=xq[rs, :Lk].cpu().numpy(), best_e=eq[rs].cpu().numpy(),
            best_parts={p: v[rs].cpu().numpy() for p, v in parts.items() if p != 'n'},
            best_n=parts['n'][rs, :Lk].cpu().numpy()))
    meta = dict(n_seq=ns, n_run=nr, K=K, L=L, chains=sim.C, nsteps=nsteps, temps=list(map(float, temps)),
                mode=mode, setup_s=t_setup, run_s=t_run, total_s=t_all, swap_acc=acc,
                s_per_seq=t_all / ns, s_per_run=t_all / (ns * nr))
    del sim
    torch.cuda.empty_cache()
    return out, meta


EPS_GO = 1.0 * TT.KT0      # Go contact energy (instrument check only)


def go_override(model, natives, rep):
    """INSTRUMENT CHECK ONLY (never part of the model): replace the table and burial by a Go energy, -EPS_GO per
    contact of a given native structure, to test whether the search and the two-state readouts detect folding
    where folding certainly exists. One native (L, 3) per sequence; rep = chains per sequence."""
    C, L = model.C, model.L
    e = torch.zeros((C, L, L), device=model.dev)
    for k, x in enumerate(natives):
        n = len(x)
        d = np.linalg.norm(x[:, None] - x[None], axis=-1)
        rc = model.rc[k * rep, :n, :n].cpu().numpy()
        sep = np.abs(np.arange(n)[:, None] - np.arange(n)[None])
        cm = ((d < rc) & (sep >= 3)).astype(np.float32)
        e[k * rep:(k + 1) * rep, :n, :n] = torch.tensor(-EPS_GO * cm, device=model.dev)
    model.eab = e * model.nl
    model.h = torch.zeros_like(model.h)


def save_npz(path, results, meta, extra=None):
    """one .npz per batch: compact (float16 coordinates)."""
    d = {}
    for k, r in enumerate(results):
        for key, v in r.items():
            if key == 'best_parts':
                for p, vv in v.items():
                    d[f's{k}_part_{p}'] = vv
            else:
                d[f's{k}_{key}'] = np.asarray(v)
    d['meta'] = np.array(json.dumps(dict(meta, **(extra or {}))))
    np.savez_compressed(path, **d)


def batches(items, max_chains, n_run, K):
    per = max(1, max_chains // (n_run * K))
    # group by length so padding stays small
    items = sorted(items, key=lambda t: len(t[1]))
    for i in range(0, len(items), per):
        yield items[i:i + per]


def run_set(name, items, n_run, nsteps, mode, out, max_chains, seed0=100, **kw):
    os.makedirs(out, exist_ok=True)
    metas = []
    for bi, grp in enumerate(batches(items, max_chains, n_run, len(TEMPS))):
        path = os.path.join(out, f'{name}_b{bi:02d}.npz')
        if os.path.exists(path):
            log('skip', path); continue
        seqs = [s2a(q) if isinstance(q, str) else np.asarray(q) for w, q in grp]
        res, meta = fold_batch(seqs, n_run, nsteps, mode=mode, seed=seed0 + bi, **kw)
        save_npz(path, res, meta, dict(names=[w for w, q in grp]))
        log(name, 'batch', bi, 'seqs', len(grp), 'L', meta['L'], 'chains', meta['chains'],
            '%.0fs' % meta['total_s'], 'swap', np.round(meta['swap_acc'], 2).tolist())
        metas.append(meta)
    return metas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stage')
    ap.add_argument('--out', default=r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-14\task15_step3')
    ap.add_argument('--nsteps', type=int, default=60000)
    ap.add_argument('--nrun', type=int, default=10)
    ap.add_argument('--count', type=int, default=0)
    ap.add_argument('--max-chains', type=int, default=3000)
    ap.add_argument('--mode', default='coop')
    ap.add_argument('--eps-go', type=float, default=1.0)
    ap.add_argument('--lams', type=float, nargs='*', default=[1.0])
    a = ap.parse_args()
    t = time.time()
    if a.stage == 'pilot':
        page = pick_page(120)
        rng = np.random.default_rng(3)
        items = [page[i] for i in (0, 10, 30, 60, 90, 110)] + \
                [('random32', rng.integers(0, 16, 32).tolist()) for _ in range(2)]
        run_set('pilot_%d' % a.nsteps, items, a.nrun, a.nsteps, 'coop', a.out, a.max_chains)
    elif a.stage == 'scan':
        # calibration scan: one global scale lam on the table and burial (e_ab, h_a), pilot sequences
        page = pick_page(120)
        rng = np.random.default_rng(3)
        items = [page[i] for i in (0, 10, 30, 60, 90, 110)] +                 [('random32', rng.integers(0, 16, 32).tolist()) for _ in range(2)]
        for lam in a.lams:
            run_set('scan_lam%.2f_%d' % (lam, a.nsteps), items, a.nrun, a.nsteps, 'coop', a.out, a.max_chains,
                    e_tab=TT.E_TAB * lam, h_tab=TT.H_TAB * lam)
    elif a.stage == 'conv':
        # search convergence (long runs on the pilot set) plus two designed positive controls
        page = pick_page(120)
        rng = np.random.default_rng(3)
        items = [page[i] for i in (0, 10, 30, 60, 90, 110)] +                 [('random32', rng.integers(0, 16, 32).tolist()) for _ in range(2)] + DESIGNS
        run_set('conv_%d' % a.nsteps, items, a.nrun, a.nsteps, 'coop', a.out, a.max_chains, seed0=600)
    elif a.stage == 'design':
        run_set('design_%s_%d' % (a.mode, a.nsteps), DESIGNS, a.nrun, a.nsteps, a.mode, a.out, a.max_chains, seed0=700)
    elif a.stage == 'go':
        # instrument check: Go energy on the two designs' lowest structures from the conv stage
        import glob
        z = np.load(glob.glob(os.path.join(a.out, 'conv_300000_b00.npz'))[0])
        meta = json.loads(str(z['meta']))
        names = meta['names']
        items, nats = [], []
        for k, nm in enumerate(names):
            if nm.startswith('design'):
                e = z[f's{k}_best_e']; x = z[f's{k}_best_x'][int(np.argmin(e))]
                items.append((nm, z[f's{k}_seq'].tolist())); nats.append(x.astype(float))
        # batches() sorts by length; keep natives aligned
        order = sorted(range(len(items)), key=lambda i: len(items[i][1]))
        items = [items[i] for i in order]; nats = [nats[i] for i in order]
        global EPS_GO
        EPS_GO = a.eps_go * TT.KT0
        run_set('go%g_%s_%d' % (a.eps_go, a.mode, a.nsteps), items, a.nrun, a.nsteps, a.mode, a.out, a.max_chains,
                seed0=800, go=nats)
    elif a.stage == 'page':
        items = pick_page(120)
        items = items[:40] + items[60:100]            # 40 most common + 40 drawn, all from task 02's 120
        run_set('page', items, a.nrun, a.nsteps, 'coop', a.out, a.max_chains, seed0=200)
    elif a.stage == 'additive':
        items = pick_page(120)
        items = (items[:40] + items[60:100])[::(80 // (a.count or 30)) or 1][:a.count or 30]
        run_set('additive', items, a.nrun, a.nsteps, 'additive', a.out, a.max_chains, seed0=300)
    elif a.stage == 'random':
        rng = np.random.default_rng(11)          # the same generator seed as task 02's random 32-mers
        items = [('random32', rng.integers(0, 16, size=32).tolist()) for _ in range(80)][:a.count or 30]
        run_set('random32', items, a.nrun, a.nsteps, 'coop', a.out, a.max_chains, seed0=400)
    elif a.stage == 'random20':
        rng = np.random.default_rng(12)
        items = [('random20', rng.integers(0, 16, size=20).tolist()) for _ in range(a.count or 80)]
        run_set('random20', items, a.nrun, a.nsteps, 'coop', a.out, a.max_chains, seed0=500)
    log('stage', a.stage, 'done in %.0fs' % (time.time() - t))


if __name__ == '__main__':
    main()
