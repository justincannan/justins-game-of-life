"""Task 23: fold sequences with the two-bead folder (twobead.py); GPU stages.

Usage: python run_tb.py STAGE [--out DIR] [--nsteps N] [--nrun N] ...
Stages: probe, go (instrument check), page, random, additive, fold (sequences from a JSON file: --seqfile).
Each batch is written as OUT/<name>_bNN.npz (snapshots of all 2L particles, float16, centred).
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
import run_step3 as R3  # noqa: E402

OUT = r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23'
TEMPS = R3.TEMPS
NBLOCK, SNAP, BURN = R3.NBLOCK, R3.SNAP, R3.BURN
log = R3.log
MODEL_KW = ('eps_vdw', 'eps_da', 'eps_hb', 'eps_core', 'n_half', 'w_burial', 'charges', 'elec', 'eps_self', 'eps_pair',
            'h_charge', 'mu_cd', 'eps_cd', 'helix', 'eps_nuc', 'eps_prop', 'w_h')


def go_override2(model, natives, rep, eps_go):
    """INSTRUMENT CHECK ONLY: side-chain pair wells and burial replaced by -eps_go per native side-chain contact
    (|i-j| >= 3) of a given two-bead structure; charges off. Backbone, local terms and H-bonds are kept."""
    C, L = model.C, model.L
    e = torch.zeros((C, L, L), device=model.dev)
    eps_list = eps_go if np.ndim(eps_go) else [eps_go] * len(natives)
    for k, x in enumerate(natives):
        eps_go = eps_list[k]
        n = len(x) // 2
        xs = x[n:]
        d = np.linalg.norm(xs[:, None] - xs[None], axis=-1)
        rc = model.rc_ss[k * rep, :n, :n].cpu().numpy()
        sep = np.abs(np.arange(n)[:, None] - np.arange(n)[None])
        cm = ((d < rc) & (sep >= 3)).astype(np.float32)
        e[k * rep:(k + 1) * rep, :n, :n] = torch.tensor(-eps_go * cm, device=model.dev)
    model.eab = e * model.nl3
    model.h = torch.zeros_like(model.h)
    model.qq = torch.zeros_like(model.qq)


def fold_batch(seqs, n_run, nsteps, mode='coop', seed=0, temps=TEMPS, go=None, eps_go=0.0, **kw):
    t0 = time.time()
    sim = TB.REMD2(seqs, n_run, temps, mode=mode, seed=seed, **kw)
    if go is not None:
        go_override2(sim.model, go, n_run * len(temps), eps_go)
        sim.x, _ = TT.minimise(sim.model, sim.x, iters=300)
        sim.sync_sc()
    sim.build(NBLOCK)
    torch.cuda.synchronize()
    t_setup = time.time() - t0
    K, ns, nr, L = sim.K, sim.ns, sim.nr, sim.L
    N = 2 * L
    nb = nsteps // NBLOCK
    every = SNAP // NBLOCK
    burn_b = int(BURN * nb)
    snapE, snapX = [], []
    best_e = torch.full((ns * nr,), float('inf'), device=sim.dev)
    best_x = torch.zeros((ns * nr, N, 3), device=sim.dev)
    t1 = time.time()
    for b in range(nb):
        sim.run_block()
        sim.exchange(b % 2)
        if (b + 1) % every == 0:
            sim.sync_sc()
            e = sim.e.view(ns * nr, K)
            em, jm = e.min(1)
            better = em < best_e
            xr = sim.x.view(ns * nr, K, N, 3)[torch.arange(ns * nr, device=sim.dev), jm]
            best_e = torch.where(better, em, best_e)
            best_x = torch.where(better[:, None, None], xr, best_x)
            if b >= burn_b:
                snapE.append(sim.e.cpu().numpy().copy())
                xc = sim.x - (sim.x * sim.mask3).sum(1, keepdim=True) / sim.mask3.sum(1, keepdim=True)
                snapX.append(xc.half().cpu().numpy().copy())
    torch.cuda.synchronize()
    t_run = time.time() - t1
    idx1, _ = TB.seq_params(sim.seqs, L)
    P1 = sim.P1
    mq = TB.Model2(np.repeat(idx1, nr, 0), np.repeat(P1, nr, 0), mode=mode, device=sim.dev,
                   **{k: v for k, v in kw.items() if k in MODEL_KW})
    if go is not None:
        go_override2(mq, go, nr, eps_go)
    xq, eq = TT.minimise(mq, best_x, iters=3000)
    xq = TB.fill_sc(mq, xq)
    parts = mq.energy(xq, parts=True)
    torch.cuda.synchronize()
    t_all = time.time() - t0
    SE = np.stack(snapE, 1)
    SX = np.stack(snapX, 1)
    acc = (sim.n_swap_acc / np.maximum(sim.n_swap_try, 1)).tolist()
    out = []
    for k in range(ns):
        Lk = len(seqs[k])
        sl = slice(k * nr * K, (k + 1) * nr * K)
        rs = slice(k * nr, (k + 1) * nr)
        keep = np.r_[0:Lk, L:L + Lk]
        out.append(dict(
            seq=np.asarray(seqs[k]).tolist(), L=Lk,
            snapE=SE[sl].reshape(nr, K, -1), snapX=SX[sl][:, :, keep].reshape(nr, K, SE.shape[1], 2 * Lk, 3),
            best_e_raw=best_e[rs].cpu().numpy(), best_x=xq[rs][:, keep].cpu().numpy(), best_e=eq[rs].cpu().numpy(),
            best_parts={p: v[rs].cpu().numpy() for p, v in parts.items() if p != 'n'},
            best_n=parts['n'][rs, :Lk].cpu().numpy()))
    meta = dict(n_seq=ns, n_run=nr, K=K, L=L, chains=sim.C, nsteps=nsteps, temps=list(map(float, temps)),
                mode=mode, setup_s=t_setup, run_s=t_run, total_s=t_all, swap_acc=acc, two_bead=True,
                s_per_seq=t_all / ns, s_per_run=t_all / (ns * nr), eps_go=(list(map(float, np.atleast_1d(eps_go))) if go is not None else None))
    del sim
    torch.cuda.empty_cache()
    return out, meta


def run_set(name, items, n_run, nsteps, mode, out, max_chains, seed0=100, natives=None, **kw):
    """items: (name, seq); natives (optional, Go check): one two-bead structure per item."""
    os.makedirs(out, exist_ok=True)
    if natives is not None:
        order = sorted(range(len(items)), key=lambda i: len(items[i][1]))
        items = [items[i] for i in order]; natives = [natives[i] for i in order]
        if np.ndim(kw.get('eps_go', 0)):
            kw['eps_go'] = [kw['eps_go'][i] for i in order]
    else:
        items = sorted(items, key=lambda t: len(t[1]))
    per = max(1, max_chains // (n_run * len(TEMPS)))
    for bi, i0 in enumerate(range(0, len(items), per)):
        grp = items[i0:i0 + per]
        path = os.path.join(out, f'{name}_b{bi:02d}.npz')
        if os.path.exists(path):
            log('skip', path); continue
        seqs = [R3.s2a(q) if isinstance(q, str) else np.asarray(q) for w, q in grp]
        go = natives[i0:i0 + per] if natives is not None else None
        kb = dict(kw)
        if np.ndim(kb.get('eps_go', 0)):
            kb['eps_go'] = kb['eps_go'][i0:i0 + per]
        res, meta = fold_batch(seqs, n_run, nsteps, mode=mode, seed=seed0 + bi, go=go, **kb)
        R3.save_npz(path, res, meta, dict(names=[w for w, q in grp]))
        log(name, 'batch', bi, 'seqs', len(grp), 'L', meta['L'], 'chains', meta['chains'],
            '%.0fs' % meta['total_s'], 'swap', np.round(meta['swap_acc'], 2).tolist())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stage')
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--name', default=None)
    ap.add_argument('--nsteps', type=int, default=60000)
    ap.add_argument('--nrun', type=int, default=10)
    ap.add_argument('--count', type=int, default=0)
    ap.add_argument('--max-chains', type=int, default=2400)
    ap.add_argument('--mode', default='coop')
    ap.add_argument('--seqfile', default=None)
    ap.add_argument('--eps-go', type=float, nargs='*', default=[2.0])
    ap.add_argument('--native-file', default=None)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--model', default='{}', help='JSON of Model2 options (task 26), e.g. {"elec": "cd", "h_charge": "iso"}')
    a = ap.parse_args()
    mk = json.loads(a.model)
    log('model options', mk)
    t = time.time()
    if a.stage == 'probe':
        run_set(a.name or 'probe', R3.DESIGNS, a.nrun, a.nsteps, a.mode, a.out, a.max_chains, seed0=900 + a.seed, **mk)
    elif a.stage == 'go':
        # natives: JSON {name: {"seq": [...], "x": [[...]] (2L x 3)}}
        d = json.load(open(a.native_file))
        items, nats, eps = [], [], []
        for e in a.eps_go:
            for k, v in d.items():
                items.append((f'{k}@{e:g}', v['seq'])); nats.append(np.array(v['x'], float)); eps.append(e * TB.KT0)
        run_set(a.name or 'go', items, a.nrun, a.nsteps, a.mode, a.out, a.max_chains, seed0=800,
                natives=nats, eps_go=eps)
    elif a.stage == 'fold':
        d = json.load(open(a.seqfile))
        items = [(k, v) for k, v in d.items()]
        run_set(a.name, items, a.nrun, a.nsteps, a.mode, a.out, a.max_chains, seed0=1000 + a.seed, **mk)
    elif a.stage == 'page':
        items = R3.pick_page(120)
        items = items[:40] + items[60:100]
        run_set(a.name or 'page', items, a.nrun, a.nsteps, 'coop', a.out, a.max_chains, seed0=200, **mk)
    elif a.stage == 'additive':
        items = R3.pick_page(120)
        items = (items[:40] + items[60:100])[::2][:30][::2]   # every other one of step 3's 30 (15), cut for GPU time
        run_set(a.name or 'additive', items, a.nrun, a.nsteps, 'additive', a.out, a.max_chains, seed0=300, **mk)
    elif a.stage == 'random':
        rng = np.random.default_rng(11)
        items = [('random32', rng.integers(0, 16, size=32).tolist()) for _ in range(80)][:a.count or 30]
        run_set(a.name or 'random32', items, a.nrun, a.nsteps, 'coop', a.out, a.max_chains, seed0=400, **mk)
    log('stage', a.stage, 'done in %.0fs' % (time.time() - t))


if __name__ == '__main__':
    main()
