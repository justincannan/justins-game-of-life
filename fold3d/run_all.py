"""Task 02 measurements: speed, reproducibility, melting, sequence to fold, and the page's brackets against the 3D fold.

One command:  python run_all.py [--quick] [--only speed,conv,repro,params,melt,mut,page]
Results go to fold3d/results/*.json (a stage whose file exists is skipped), sample_folds.json beside this file.
Page sequences: fold3d/data/page_seqs.json (made by dump_seq.js through the page harness; see README).
"""
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lattice import Batch, GraphRunner, canon, contacts, energy_np, oily_table   # noqa: E402

RES = HERE / 'results'
MONO = 'abcdefghijklmnop'
DEFAULT = dict(rule='odd', eP=1.0, eB=0.5)
CONFIGS = {
    'default': dict(rule='odd', eP=1.0, eB=0.5),
    'eP0': dict(rule='odd', eP=0.0, eB=0.5),
    'eP2': dict(rule='odd', eP=2.0, eB=0.5),
    'eB0': dict(rule='odd', eP=1.0, eB=0.0),
    'eB1': dict(rule='odd', eP=1.0, eB=1.0),
    'low': dict(rule='low', eP=1.0, eB=0.5),
}


def s2a(s):
    return np.array([MONO.index(c) for c in s], dtype=np.int64)


def save(name, obj):
    RES.mkdir(exist_ok=True)
    tmp = RES / (name + '.json.part')
    tmp.write_text(json.dumps(obj), encoding='utf-8')
    os.replace(tmp, RES / (name + '.json'))


def load(name):
    p = RES / (name + '.json')
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


# ------------------------------------------------------------------ folding many chains
def buckets(lengths, edges=(16, 24, 36, 48, 64, 96, 128)):
    out = {}
    for k, n in enumerate(lengths):
        e = next(x for x in edges if n <= x)
        out.setdefault(e, []).append(k)
    return out


R_PT = 8
LADDER = list(np.geomspace(0.12, 1.0, R_PT))


def fold_many(seqs, reps, cfg, sweeps, seed=0, maxB=4096, method='pt'):
    """Fold every sequence in `reps` independent runs. A run is one replica-exchange simulation of R_PT chains at the
    temperatures LADDER (method 'pt', the default) or one anneal from T = 1 to 0.1 (method 'anneal'). The run's result
    is the lowest-energy fold any of its chains visited. Returns energies (S x reps) and coordinates (list of lists)."""
    R = R_PT if method == 'pt' else 1
    nS = len(seqs)
    E = np.zeros((nS, reps))
    Xs = [[None] * reps for _ in range(nS)]
    jobs = [(k, r) for k in range(nS) for r in range(reps)]
    lens = [len(seqs[k]) for k, r in jobs]
    per = max(1, maxB // R)
    for e, idx in sorted(buckets(lens).items()):
        for c0 in range(0, len(idx), per):
            part = idx[c0:c0 + per]
            b = Batch([seqs[jobs[i][0]] for i in part for _ in range(R)], seed=seed + c0 + 1000 * e, **cfg)
            gr = GraphRunner(b, chunk=20)
            if method == 'pt':
                gr.tempering(R, LADDER, sweeps)
            else:
                gr.anneal(sweeps, 1.0, 0.1)
            Eb = b.Ebest.cpu().numpy().reshape(len(part), R)
            Xb = b.Xbest.cpu().numpy().reshape(len(part), R, b.L, 3)
            for q, i in enumerate(part):
                k, r = jobs[i]
                n = len(seqs[k])
                z = int(np.argmin(Eb[q]))
                E[k, r] = Eb[q, z]
                Xs[k][r] = Xb[q, z, :n].copy()
            del gr, b
            torch.cuda.empty_cache()
    return E, Xs


def native_of(seq, Es, Xs, cfg):
    """Lowest energy over the anneals; the lowest folds (distinct up to symmetry); how often the top one recurs."""
    emin = Es.min()
    hit = [r for r in range(len(Es)) if Es[r] <= emin + 1e-6]
    keys = [canon(Xs[r]) for r in hit]
    cnt = {}
    for k in keys:
        cnt[k] = cnt.get(k, 0) + 1
    top = max(cnt, key=cnt.get)
    rtop = hit[keys.index(top)]
    return dict(emin=float(emin), n_hit_E=len(hit), n_distinct_at_min=len(cnt), n_top=cnt[top], native=Xs[rtop])


def qcontacts(Xa, Xb):
    ca, cb = contacts(Xa), contacts(Xb)
    return len(ca & cb) / max(1, len(ca)), len(ca)


# ------------------------------------------------------------------ the page's brackets (infold in tools/env.js)
def infold_pairs(s):
    st, pairs = [], []
    for h, m in enumerate(s):
        if st and s[st[-1]] == (m ^ 8):
            pairs.append((st.pop(), h))
        else:
            st.append(h)
    return pairs


def top_domains(pairs):
    """Outermost pairs and the spans they enclose (a pair together with everything inside it is a domain)."""
    doms = []
    for a, b in sorted(pairs, key=lambda p: p[0] - p[1]):     # longest first
        if not any(a > x and b < y for x, y in doms):
            doms.append((a, b))
    return sorted(doms)


# ------------------------------------------------------------------ page sequences
def page_sequences():
    p = HERE / 'data' / 'page_seqs.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    return d


def pick_page(d, nmin, nmax, count, seed):
    """Distinct page sequences with nmin <= length <= nmax, weighted toward common ones, both worlds mixed."""
    rnd = random.Random(seed)
    pool = [(w, s['seq'], s['n']) for w, lst in d['worlds'].items() for s in lst if nmin <= len(s['seq']) <= nmax]
    seen, out = set(), []
    pool.sort(key=lambda t: -t[2])
    # half the most common, half drawn at random from the rest
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


# ------------------------------------------------------------------ stages
def stage_speed(a):
    out = []
    rng = np.random.default_rng(5)
    for L in (16, 32, 64, 128):
        for B in (1, 256, 4096):
            seqs = [rng.integers(0, 16, size=L) for _ in range(B)]
            b = Batch(seqs, seed=1, **DEFAULT)
            gr = GraphRunner(b, chunk=20)
            gr.set_T(0.5)
            gr.run(100)
            torch.cuda.synchronize()
            steps = 400 if B < 4096 else 200
            t = time.time()
            gr.run(steps)
            torch.cuda.synchronize()
            ms = (time.time() - t) / steps * 1e3
            bad = b.check(4)
            out.append(dict(L=L, B=B, ms_per_step=ms, bad_energy=bad))
            log('speed', L, B, '%.3f ms/step' % ms, 'bad', bad)
            del gr, b
            torch.cuda.empty_cache()
    save('speed', out)


def stage_conv(a):
    """How many sweeps an anneal needs: best energy found against sweeps, 24 sequences x 8 anneals per length."""
    rng = np.random.default_rng(7)
    out = []
    lens = (16, 32, 48) if not a.quick else (16,)
    for L in lens:
        seqs = [rng.integers(0, 16, size=L) for _ in range(24)]
        res = {}
        for sw in (250, 1000, 4000, 16000) if L <= 32 else (250, 1000, 4000):
            t = time.time()
            E, X = fold_many(seqs, 8, DEFAULT, sw, seed=sw)
            res[sw] = (E, time.time() - t)
            log('conv', L, sw, 'mean best %.3f' % E.min(1).mean(), '%.0fs' % (time.time() - t))
        ref = np.min([r[0].min(1) for r in res.values()], axis=0)          # best known per sequence
        for sw, (E, dt) in res.items():
            out.append(dict(L=L, sweeps=sw, secs=dt, frac_anneals_at_best=float((E <= ref[:, None] + 1e-6).mean()),
                            frac_seqs_found=float((E.min(1) <= ref + 1e-6).mean()), mean_gap=float((E.mean(1) - ref).mean())))
    save('conv', out)


def stage_search(a):
    """Annealing against replica exchange at similar GPU time, 24 random sequences of length 32, 8 runs each."""
    rng = np.random.default_rng(7)
    _ = [rng.integers(0, 16, size=16) for _ in range(24)]
    seqs = [rng.integers(0, 16, size=32) for _ in range(24)]
    res = {}
    for name, (meth, sw) in {'anneal T 1 to 0.1, 4000 sweeps': ('anneal', 4000), 'replica exchange 8 x 500 sweeps': ('pt', 500),
                             'replica exchange 8 x 2000 sweeps': ('pt', 2000)}.items():
        t = time.time()
        E, _ = fold_many(seqs, 8, DEFAULT, sw, seed=3, method=meth)
        res[name] = (E, time.time() - t)
        log('search', name, '%.0fs' % (time.time() - t))
    conv = load('conv') or []
    ref = np.min([v[0].min(1) for v in res.values()], 0)
    out = [dict(method=k, secs=dt, mean_best=float(E.min(1).mean()), frac_runs_at_best=float((E <= ref[:, None] + 1e-6).mean()),
                frac_seqs_found=float((E.min(1) <= ref + 1e-6).mean()), mean_gap=float((E.mean(1) - ref).mean())) for k, (E, dt) in res.items()]
    save('search', dict(ref_mean=float(ref.mean()), rows=out))


def repro_set(a):
    d = page_sequences()
    page = pick_page(d, 12, 36, 120 if not a.quick else 20, seed=1)
    rng = np.random.default_rng(11)
    rnd = [('random32', ''.join(MONO[x] for x in rng.integers(0, 16, size=32))) for _ in range(80 if not a.quick else 10)]
    return page + rnd


def stage_repro(a, cfgname='default', subset=None, tag=None):
    cfg = CONFIGS[cfgname]
    items = repro_set(a)
    if subset:
        items = items[:subset]
    seqs = [s2a(q) for w, q in items]
    t = time.time()
    E, X = fold_many(seqs, 10, cfg, a.sweeps, seed=17)
    log('repro', cfgname, '%.0fs' % (time.time() - t))
    rows = []
    for k, (w, q) in enumerate(items):
        nat = native_of(seqs[k], E[k], X[k], cfg)
        allkeys = [canon(x) for x in X[k]]
        topkey = canon(nat['native'])
        qs = [qcontacts(nat['native'], x)[0] for x in X[k]]
        rows.append(dict(world=w, seq=q, n=len(q), E=E[k].tolist(), emin=nat['emin'], n_hit_E=nat['n_hit_E'],
                         n_distinct_at_min=nat['n_distinct_at_min'], n_same_fold=sum(kk == topkey for kk in allkeys),
                         q_to_native=qs, native=nat['native'].tolist(),
                         ncontacts=len(contacts(nat['native']))))
    save(tag or ('repro_' + cfgname), dict(cfg=cfg, sweeps=a.sweeps, secs=time.time() - t, rows=rows))


def stage_params(a):
    for name in CONFIGS:
        if name == 'default' or load('repro_' + name):
            continue
        stage_repro(a, name, subset=60 if not a.quick else 10)


def melt_batch(seqs, natives, cfg, temps, reps, eq_sweeps, meas_sweeps, nsamp, seed=3):
    """Equilibrium MC from the native fold at each temperature: Q (native-contact fraction) and E, averaged over samples."""
    jobs = [(k, ti, r) for k in range(len(seqs)) for ti in range(len(temps)) for r in range(reps)]
    Q = np.zeros((len(seqs), len(temps), reps, nsamp))
    En = np.zeros_like(Q)
    lens = [len(seqs[k]) for k, _, _ in jobs]
    for e, idx in sorted(buckets(lens).items()):
        for c0 in range(0, len(idx), 4096):
            part = idx[c0:c0 + 4096]
            b = Batch([seqs[jobs[i][0]] for i in part], seed=seed + c0, init=[natives[jobs[i][0]] for i in part], **cfg)
            # native contacts as index lists, padded
            cl = [sorted(contacts(np.asarray(natives[jobs[i][0]]))) for i in part]
            cm = max(1, max(len(c) for c in cl))
            I = np.zeros((len(part), cm), dtype=np.int64); J = np.zeros_like(I); M = np.zeros((len(part), cm), dtype=bool)
            for q, c in enumerate(cl):
                for z, (i, j) in enumerate(c):
                    I[q, z], J[q, z], M[q, z] = i, j, True
            I, J, M = (torch.tensor(v, device='cuda') for v in (I, J, M))
            Tt = torch.tensor([temps[jobs[i][1]] for i in part], dtype=torch.float32, device='cuda')
            gr = GraphRunner(b, chunk=20)
            gr.set_T(Tt)
            gr.run(eq_sweeps * b.L)
            per = max(20, meas_sweeps * b.L // nsamp)
            bi = torch.arange(b.B, device='cuda')[:, None]
            for s in range(nsamp):
                gr.run(per)
                X = b.X
                dd = (X[bi, I] - X[bi, J]).abs().sum(-1)
                qv = (((dd == 1) & M).sum(1).float() / M.sum(1).clamp(min=1)).cpu().numpy()
                ev = b.E.cpu().numpy()
                for q, i in enumerate(part):
                    k, ti, r = jobs[i]
                    Q[k, ti, r, s] = qv[q]
                    En[k, ti, r, s] = ev[q]
            del gr, b
            torch.cuda.empty_cache()
    return Q, En


def tm_fit(temps, q):
    """Tm where the mean Q curve crosses half its low-T value, and a two-state width: Q ~ Q0 / (1 + exp((T - Tm) / w))."""
    temps = np.asarray(temps); q = np.asarray(q)
    q0 = q[0]
    half = q0 / 2
    tm = None
    for i in range(len(temps) - 1):
        if q[i] >= half > q[i + 1]:
            tm = temps[i] + (q[i] - half) / (q[i] - q[i + 1]) * (temps[i + 1] - temps[i])
            break
    best = (1e9, None, None)
    for tmg in np.linspace(temps[0], temps[-1], 141):
        for w in np.geomspace(0.005, 1.0, 80):
            f = q0 / (1 + np.exp((temps - tmg) / w))
            err = ((f - q) ** 2).sum()
            if err < best[0]:
                best = (err, tmg, w)
    return tm, best[1], best[2]


def stage_melt(a, cfgname='default', nseq=48, reps=4, temps=None, tag=None):
    cfg = CONFIGS[cfgname]
    rep = load('repro_' + cfgname) or load('repro_default')
    rows = [r for r in rep['rows'] if r['world'] != 'random32']
    rows = sorted(rows, key=lambda r: -r['n'])
    rows = [r for r in rows if r['ncontacts'] >= 3][:nseq]
    temps = temps or [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.7, 2.0]
    seqs = [s2a(r['seq']) for r in rows]
    nat = [np.array(r['native']) for r in rows]
    t = time.time()
    Q, En = melt_batch(seqs, nat, cfg, temps, reps, eq_sweeps=a.melt_eq, meas_sweeps=a.melt_meas, nsamp=20)
    log('melt', cfgname, '%.0fs' % (time.time() - t))
    out = []
    for k, r in enumerate(rows):
        qm = Q[k].mean((1, 2))
        em = En[k].mean((1, 2))
        cv = En[k].reshape(len(temps), -1).var(1) / np.asarray(temps) ** 2
        tm, tm_fit_, w = tm_fit(temps, qm)
        out.append(dict(seq=r['seq'], n=r['n'], world=r['world'], emin=r['emin'], qmean=qm.tolist(), emean=em.tolist(), cv=cv.tolist(),
                        q_samples_flat=[Q[k, ti].ravel().round(3).tolist() for ti in range(len(temps))],
                        tm=tm, tm_fit=tm_fit_, width=w))
    save(tag or ('melt_' + cfgname), dict(cfg=cfg, temps=temps, secs=time.time() - t, rows=out))


def stage_melt_params(a):
    for name in CONFIGS:
        if name == 'default' or load('melt_' + name):
            continue
        if not load('repro_' + name):
            continue
        stage_melt(a, name, nseq=16, reps=2, temps=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5, 2.0])


def stage_mut(a):
    """One mutation: does the native fold change? 40 page sequences x 5 single mutants, 10 anneals each."""
    rep = load('repro_default')
    rows = [r for r in rep['rows'] if r['world'] != 'random32' and r['ncontacts'] >= 3]
    rnd = random.Random(4)
    rnd.shuffle(rows)
    rows = rows[:40 if not a.quick else 5]
    muts = []
    for r in rows:
        s = s2a(r['seq'])
        for _ in range(5):
            m = s.copy()
            p = rnd.randrange(len(m))
            m[p] = rnd.choice([x for x in range(16) if x != m[p]])
            muts.append((r, p, m))
    E, X = fold_many([m for _, _, m in muts], 5, DEFAULT, a.sweeps, seed=29)
    out = []
    for k, (r, p, m) in enumerate(muts):
        nat = native_of(m, E[k], X[k], DEFAULT)
        wt = np.array(r['native'])
        e_wt_on_mut = energy_np(m, wt, **DEFAULT)
        q, _ = qcontacts(wt, nat['native'])
        # the wild type's own reproducibility, to separate a real change from search noise
        out.append(dict(wt=r['seq'], pos=p, mut=''.join(MONO[x] for x in m), n=len(m), wt_emin=r['emin'], mut_emin=nat['emin'],
                        e_wt_fold_on_mut=float(e_wt_on_mut), same_fold=canon(wt) == canon(nat['native']),
                        wt_fold_still_lowest=bool(e_wt_on_mut <= nat['emin'] + 1e-6), q_wt_contacts_kept=q,
                        wt_repro=r['n_same_fold'] / 10, mut_repro=nat['n_top'] / 5,
                        oily_change=bool(oily_table('odd')[s2a(r['seq'])[p]] != oily_table('odd')[m[p]])))
    save('mut', out)


def stage_page(a):
    """Page brackets vs 3D folds: are paired monomers in lattice contact, are domains compact? For three eP values."""
    out = {}
    d = page_sequences()
    sel = [(w, s['seq']) for w, lst in d['worlds'].items() for s in lst
           if any(j > i + 1 for i, j in infold_pairs(s2a(s['seq'])))]
    rnd = random.Random(8)
    rnd.shuffle(sel)
    sel = sel[:120 if not a.quick else 12]
    for name in ('default', 'eP0', 'eP2', 'low'):
        rep = load('pagefold_' + name)
        if not rep:
            seqs = [s2a(q) for w, q in sel]
            E, X = fold_many(seqs, 5, CONFIGS[name], a.sweeps, seed=41)
            rows = []
            for k, (w, q) in enumerate(sel):
                nat = native_of(seqs[k], E[k], X[k], CONFIGS[name])
                rows.append(dict(world=w, seq=q, n=len(q), emin=nat['emin'], native=nat['native'].tolist(), n_top=nat['n_top']))
            save('pagefold_' + name, dict(cfg=CONFIGS[name], rows=rows))
            rep = load('pagefold_' + name)
        rows = rep['rows']
        n_pair = n_pair_c = n_pair_adj = 0
        base_num = base_den = 0.0
        dom_in = dom_base = 0.0; ndom = 0
        perseq = []
        for r in rows:
            s = s2a(r['seq']); X = np.array(r['native']); n = len(s)
            pairs = infold_pairs(s)
            C = contacts(X)
            dist = lambda i, j: np.abs(X[i] - X[j]).sum()
            cp = 0
            for i, j in pairs:
                if j == i + 1:
                    n_pair_adj += 1
                    continue
                n_pair += 1
                if (i, j) in C:
                    n_pair_c += 1; cp += 1
                # baseline: all pairs of the same sequence separation in the same fold
                sep = j - i
                cand = [(x, x + sep) for x in range(n - sep)]
                base_num += sum((x, y) in C for x, y in cand) / len(cand)
                base_den += 1
            for da, db in top_domains(pairs):
                Ld = db - da + 1
                if Ld < 4 or Ld > n - 2:
                    continue
                def frac_in(lo, hi):
                    tot = sum(1 for (i, j) in C if lo <= i <= hi or lo <= j <= hi)
                    ins = sum(1 for (i, j) in C if lo <= i <= hi and lo <= j <= hi)
                    return ins / tot if tot else np.nan
                fi = frac_in(da, db)
                fb = np.nanmean([frac_in(x, x + Ld - 1) for x in range(n - Ld + 1)])
                if not np.isnan(fi) and not np.isnan(fb):
                    dom_in += fi; dom_base += fb; ndom += 1
            perseq.append(dict(seq=r['seq'], pairs=len(pairs), pair_contacts=cp, domains=len(top_domains(pairs))))
        out[name] = dict(n_seq=len(rows), seqs_with_pairs=sum(p['pairs'] > 0 for p in perseq), pairs_nonadjacent=n_pair,
                         pairs_adjacent=n_pair_adj, frac_pairs_in_contact=n_pair_c / max(1, n_pair),
                         baseline_same_separation=base_num / max(1, base_den), domains=ndom,
                         domain_intra_frac=float(dom_in / max(1, ndom)), domain_baseline=float(dom_base / max(1, ndom)),
                         frac_native_reproduced=float(np.mean([r['n_top'] for r in rows]) / 5))
        log('page', name, out[name])
    save('page', out)


def stage_samples(a):
    melt = load('melt_default')
    rep = {r['seq']: r for r in load('repro_default')['rows']}
    out = []
    for r in melt['rows'][:50]:
        rr = rep[r['seq']]
        s = s2a(r['seq'])
        out.append(dict(seq=r['seq'], world=r['world'], length=r['n'], coords=rr['native'], energy=rr['emin'],
                        tm=r['tm'], tm_two_state_fit=r['tm_fit'], oily=[bool(x) for x in oily_table('odd')[s]],
                        bracket_pairs=infold_pairs(s), found_in_anneals=rr['n_same_fold'], anneals=10))
    meta = dict(model='3D cubic lattice HP-style; oily-oily -1, complement (m^8) contact -eP, buried unpartnered polar +eB',
                params=DEFAULT, sweeps=a.sweeps, note='coords are integer lattice sites, one per monomer, in sequence order; '
                'Tm in the model\'s energy units (oily-oily contact = 1); folds from fold3d/run_all.py (task 02)')
    (HERE / 'sample_folds.json').write_text(json.dumps(dict(meta=meta, folds=out), indent=1), encoding='utf-8')


STAGES = dict(speed=stage_speed, conv=stage_conv, search=stage_search, repro=stage_repro, params=stage_params, melt=stage_melt,
              meltp=stage_melt_params, mut=stage_mut, page=stage_page, samples=stage_samples)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=','.join(STAGES))
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--sweeps', type=int, default=2000)
    ap.add_argument('--melt-eq', type=int, default=1000)
    ap.add_argument('--melt-meas', type=int, default=3000)
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    global RES
    if a.quick:
        RES = Path(os.environ.get('FOLD3D_QUICK_DIR', str(HERE / 'results_quick')))
        a.sweeps = min(a.sweeps, 300); a.melt_eq = 100; a.melt_meas = 200
    names = {'speed': 'speed', 'conv': 'conv', 'search': 'search', 'repro': 'repro_default', 'melt': 'melt_default', 'mut': 'mut', 'page': 'page'}
    for st in a.only.split(','):
        if not a.force and st in names and load(names[st]):
            log('skip', st)
            continue
        log('stage', st)
        STAGES[st](a)
    log('done')


if __name__ == '__main__':
    main()
