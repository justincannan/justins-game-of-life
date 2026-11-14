"""Batched Metropolis Monte Carlo of self-avoiding chains on the 3D cubic lattice (PyTorch, GPU).

Model (task 02; every choice here is a proposal and a parameter):
- a chain of monomers with codes 0..15 (the page's a..p), one monomer per lattice site, bonds of length 1;
- energy summed over lattice neighbours that are not chain neighbours ("contacts"):
    oily-oily contact            -1      (Dill 1985, HP model)
    complement contact (m, m^8)  -eP     (adds to the oily term when both apply)
  plus +eB for every polar monomer whose six lattice neighbours are all occupied (by any monomer, bonded or not)
  with no complement among those six;
- polarity rule 'odd': oily when (m & 1) == 1; rule 'low': oily when m < 8;
- moves: end moves, corner flips, crankshaft (90/180/270 degrees) and pull moves (Lesh et al. 2003) in both directions,
  one move attempt per chain per step, Metropolis acceptance at a per-chain temperature.

Implementation: each chain has its own occupancy grid of G^3 cells (coordinates taken mod G, G = 32). A move into a cell
that is occupied, also by a monomer 32 sites away (an alias), is refused, so states never alias; this forbids only chains
more than 32 sites across, which do not occur at the temperatures used. Energy is recomputed in full after every
tentative move (O(L) per chain), which keeps the code simple and correct for moves of any size.
"""
import math
import numpy as np
import torch

G = 32
G3 = G * G * G
DIRS = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], dtype=np.int64)


def oily_table(rule):
    m = np.arange(16)
    if rule == 'odd':
        return (m & 1) == 1
    if rule == 'low':
        return m < 8
    raise ValueError(rule)


def pair_table(rule, eP):
    oily = oily_table(rule)
    t = np.zeros((16, 16), dtype=np.float32)
    for a in range(16):
        for b in range(16):
            if oily[a] and oily[b]:
                t[a, b] -= 1.0
            if b == (a ^ 8):
                t[a, b] -= eP
    return t


# ---------------------------------------------------------------- CPU helpers (energy check, initial chains, symmetry)
def energy_np(seq, X, rule='odd', eP=1.0, eB=0.5):
    """Reference energy of one chain (numpy), used to check the GPU code."""
    n = len(seq)
    pos = {tuple(X[k]): k for k in range(n)}
    pt = pair_table(rule, eP)
    oily = oily_table(rule)
    E = 0.0
    for k in range(n):
        occ = 0
        comp = False
        for d in DIRS:
            j = pos.get(tuple(X[k] + d))
            if j is None:
                continue
            occ += 1
            if seq[j] == (seq[k] ^ 8):
                comp = True
            if abs(j - k) > 1 and j > k:
                E += pt[seq[k], seq[j]]
        if not oily[seq[k]] and occ == 6 and not comp:
            E += eB
    return E


def random_saw(n, rng, tries=1000):
    """A random self-avoiding walk of n sites (simple growth with restarts), alias-free mod G."""
    for _ in range(tries):
        X = np.zeros((n, 3), dtype=np.int64)
        occ = {(0, 0, 0)}
        ok = True
        for k in range(1, n):
            cand = [X[k - 1] + d for d in DIRS if tuple(X[k - 1] + d) not in occ]
            if not cand:
                ok = False
                break
            X[k] = cand[rng.integers(len(cand))]
            occ.add(tuple(X[k]))
        if ok and len({tuple(x) for x in (X % G)}) == n:
            return X
    raise RuntimeError('no SAW')


def _symmetries():
    mats = []
    import itertools
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3), dtype=np.int64)
            for r in range(3):
                M[r, perm[r]] = signs[r]
            mats.append(M)
    return np.stack(mats)          # 48 rotations and reflections


SYM = _symmetries()


def canon(X):
    """Canonical key of a conformation up to translation, rotation and reflection (chain direction kept)."""
    Y = X - X[0]
    Z = np.einsum('sij,nj->sni', SYM, Y)            # 48 x n x 3
    flat = Z.reshape(48, -1)
    best = min(range(48), key=lambda s: tuple(flat[s]))
    return flat[best].tobytes()


def contacts(X, n=None):
    """Set of non-bonded contacts (i, j), i < j, of one chain."""
    n = len(X) if n is None else n
    pos = {tuple(X[k]): k for k in range(n)}
    out = set()
    for k in range(n):
        for d in DIRS:
            j = pos.get(tuple(X[k] + d))
            if j is not None and j > k + 1:
                out.add((k, j))
    return out


# ---------------------------------------------------------------- the GPU engine
class Batch:
    def __init__(self, seqs, rule='odd', eP=1.0, eB=0.5, seed=0, device='cuda', init=None):
        """seqs: list of int arrays (codes 0..15). init: optional list of (n,3) starting coordinates."""
        self.dev = torch.device(device)
        B = len(seqs)
        L = max(len(s) for s in seqs)
        self.B, self.L = B, L
        rng = np.random.default_rng(seed)
        S = np.zeros((B, L), dtype=np.int64)
        X = np.zeros((B, L, 3), dtype=np.int64)
        nn = np.zeros(B, dtype=np.int64)
        for b, s in enumerate(seqs):
            n = len(s)
            nn[b] = n
            S[b, :n] = s
            Xi = random_saw(n, rng) if init is None else np.asarray(init[b], dtype=np.int64)
            X[b, :n] = Xi
            X[b, n:] = Xi[-1]                       # padding sits on the last site; it is never written to the grid
        d = self.dev
        self.S = torch.tensor(S, device=d)
        self.X = torch.tensor(X, device=d)
        self.n = torch.tensor(nn, device=d)
        self.ar = torch.arange(L, device=d)
        self.inchain = self.ar[None, :] < self.n[:, None]
        self.bidx = torch.arange(B, device=d)
        self.dirs = torch.tensor(DIRS, device=d)
        self.set_params(rule, eP, eB)
        self.grid = torch.zeros(B * G3 + 1, dtype=torch.int16, device=d)      # last cell: a dummy for masked writes
        self.dummy = B * G3
        idx = self._cells(self.X, self.inchain)
        self.grid.index_put_((idx.reshape(-1),), (self.ar[None, :].expand(B, L) + 1).reshape(-1).to(torch.int16))
        self.grid[self.dummy:].zero_()
        self.T = torch.ones(B, device=d)
        self.E = self.energy(self.X)
        self.Ebest = self.E.clone()
        self.Xbest = self.X.clone()
        self.gen = None                                   # the default CUDA generator (graph-safe); seeded here
        torch.manual_seed(seed + 12345)
        self.acc_count = torch.zeros(B, device=d)

    def set_params(self, rule, eP, eB):
        self.rule, self.eP, self.eB = rule, eP, eB
        self.pt = torch.tensor(pair_table(rule, eP), device=self.dev).reshape(-1)
        self.polar = torch.tensor(~oily_table(rule), device=self.dev)

    def _cells(self, X, mask):
        c = (((X[..., 0] & (G - 1)) * G + (X[..., 1] & (G - 1))) * G + (X[..., 2] & (G - 1)))
        c = c + self.bidx.view(-1, *([1] * (X.dim() - 2))) * G3
        return torch.where(mask, c, torch.full_like(c, self.dummy))

    def energy(self, X):
        """Full energy of every chain, given coordinates X consistent with the grid."""
        B, L = self.B, self.L
        nb = X[:, :, None, :] + self.dirs[None, None, :, :]                  # B L 6 3
        cell = self._cells(nb, self.inchain[:, :, None].expand(B, L, 6))
        j = self.grid[cell].long() - 1                                        # B L 6
        jc = j.clamp(min=0)
        K = ((X[..., 0] & 1023) << 20) | ((X[..., 1] & 1023) << 10) | (X[..., 2] & 1023)      # packed coordinates
        Kn = ((nb[..., 0] & 1023) << 20) | ((nb[..., 1] & 1023) << 10) | (nb[..., 2] & 1023)
        Kj = torch.gather(K, 1, jc.reshape(B, L * 6)).reshape(B, L, 6)
        real = (j >= 0) & (Kj == Kn) & self.inchain[:, :, None]                # not an alias 32 sites away
        Sj = torch.gather(self.S, 1, jc.reshape(B, L * 6)).reshape(B, L, 6)
        Sk = self.S[:, :, None].expand(B, L, 6)
        nonbond = (j - self.ar[None, :, None]).abs() > 1
        pe = self.pt[Sk * 16 + Sj] * (real & nonbond)
        E = 0.5 * pe.sum((1, 2))
        if self.eB != 0:
            occ6 = real.all(-1)
            comp = (real & (Sj == (Sk ^ 8))).any(-1)
            bur = occ6 & ~comp & self.polar[self.S] & self.inchain
            E = E + self.eB * bur.sum(1)
        return E

    def _propose(self):
        B, L, d = self.B, self.L, self.dev
        X, n, ar = self.X, self.n, self.ar
        g = self.gen
        u = torch.rand(B, 4, device=d, generator=g)
        r = (u[:, 0] * n).long().clamp(max=L - 1)
        mtype = (u[:, 1] * 3).long()                                         # 0 corner, 1 crankshaft, 2 pull
        q = (u[:, 2] * 6).long().clamp(max=5)                                # a direction choice
        sgn = torch.where(u[:, 3] < 0.5, 1, -1)                              # pull direction
        def at(k):
            return X[self.bidx, k.clamp(0, L - 1)]
        xr, xp, xn, xn2 = at(r), at(r - 1), at(r + 1), at(r + 2)
        is_end = (r == 0) | (r == n - 1)
        newX = X.clone()
        moved = torch.zeros(B, L, dtype=torch.bool, device=d)
        oh_r = ar[None, :] == r[:, None]
        oh_r1 = ar[None, :] == (r + 1)[:, None]
        # end move: to a random neighbour of the next monomer in
        anc = torch.where((r == 0)[:, None], xn, xp)
        p_end = anc + self.dirs[q]
        v_end = is_end & (n >= 2)
        # corner flip
        dpn = xp - xn
        v_cor = ~is_end & (mtype == 0) & ((dpn * dpn).sum(-1) == 2)
        p_cor = xp + xn - xr
        # crankshaft on (r, r+1)
        a = xn2 - xp
        v_cr = ~is_end & (mtype == 1) & (r + 2 <= n - 1) & ((a * a).sum(-1) == 1)
        dd = xr - xp
        cr = torch.cross(a, dd, dim=-1)
        rot = q % 3
        dpr = torch.where((rot == 0)[:, None], cr, torch.where((rot == 1)[:, None], -dd, -cr))
        p_c1 = xp + dpr
        p_c2 = xn2 + dpr
        single = v_end | v_cor
        p1 = torch.where(v_end[:, None], p_end, p_cor)
        newX = torch.where((oh_r & single[:, None])[..., None], p1[:, None, :], newX)
        newX = torch.where((oh_r & v_cr[:, None])[..., None], p_c1[:, None, :], newX)
        newX = torch.where((oh_r1 & v_cr[:, None])[..., None], p_c2[:, None, :], newX)
        moved = moved | (oh_r & (single | v_cr)[:, None]) | (oh_r1 & v_cr[:, None])
        # pull move at i = r toward anchor i + s; residues i - s, i - 2s, ... follow
        s = sgn
        xa = at(r + s)
        xb = at(r - s)
        v_pl = ~is_end & (mtype == 2) & (r + s >= 0) & (r + s <= n - 1) & (r - s >= 0) & (r - s <= n - 1)
        bvec = xa - xr
        uu = self.dirs[q]
        v_pl = v_pl & ((uu * bvec).sum(-1) == 0)
        Lp = xa + uu
        Cp = xr + uu
        c_is_b = (Cp == xb).all(-1)
        t = s[:, None] * (r[:, None] - ar[None, :])                          # 0 at i, 1 at i - s, ...
        Xp2 = torch.cat([X[:, 2:], X[:, -1:].expand(B, 2, 3)], 1)          # X[k + 2]
        Xm2 = torch.cat([X[:, :1].expand(B, 2, 3), X[:, :-2]], 1)          # X[k - 2]
        Xp3 = torch.cat([X[:, 3:], X[:, -1:].expand(B, 3, 3)], 1)
        Xm3 = torch.cat([X[:, :1].expand(B, 3, 3), X[:, :-3]], 1)
        sp = (s == 1)[:, None, None]
        X2s = torch.where(sp, Xp2, Xm2)                                     # old X[k + 2s]
        X3s = torch.where(sp, Xp3, Xm3)                                     # old X[k + 3s]
        ref = torch.where((t == 2)[..., None], Cp[:, None, :], X3s)         # new X[k + s]
        dr = X - ref
        cond = ((dr * dr).sum(-1) == 1) & (t >= 2) & self.inchain
        ci = cond.int()
        blk_up = torch.flip(torch.cummax(torch.flip(ci, [1]), 1).values, [1])   # any stop at index >= k
        blk_dn = torch.cummax(ci, 1).values                                      # any stop at index <= k
        blocked = torch.where(s[:, None] == 1, blk_up, blk_dn).bool()
        mv_tail = (t >= 2) & self.inchain & ~blocked & ~c_is_b[:, None]
        mv_pl = (t == 0) | ((t == 1) & ~c_is_b[:, None]) | mv_tail
        mv_pl = mv_pl & v_pl[:, None]
        pl_X = torch.where((t == 0)[..., None], Lp[:, None, :], torch.where((t == 1)[..., None], Cp[:, None, :], X2s))
        newX = torch.where(mv_pl[..., None], pl_X, newX)
        moved = moved | mv_pl
        return newX, moved

    def step(self):
        B = self.B
        X = self.X
        newX, moved = self._propose()
        cn = self._cells(newX, moved)
        occ = self.grid[cn].long() - 1                                        # occupant before the move
        occ_moved = torch.gather(moved, 1, occ.clamp(min=0))
        ok1 = ((occ < 0) | occ_moved | ~moved).all(1)
        moved = moved & ok1[:, None]                                          # a move into an occupied site is not tried
        cn = self._cells(newX, moved)
        co = self._cells(X, moved)
        idx1 = (self.ar[None, :].expand(B, self.L) + 1).to(torch.int16)
        self.grid.index_put_((co.reshape(-1),), torch.zeros(1, dtype=torch.int16, device=self.dev).expand(co.numel()))
        self.grid.index_put_((cn.reshape(-1),), idx1.reshape(-1))
        self.grid[self.dummy:].zero_()
        ok2 = ((self.grid[cn] == idx1) | ~moved).all(1)
        valid = ok2 & moved.any(1)
        Xt = torch.where(moved[..., None], newX, X)
        En = self.energy(Xt)
        dE = En - self.E
        u = torch.rand(B, device=self.dev, generator=self.gen)
        acc = valid & ((dE <= 0) | (u < torch.exp(-dE.clamp(min=0) / self.T)))
        # undo rejected moves in the grid
        rm = moved & ~acc[:, None]
        cn2 = torch.where(rm, cn, torch.full_like(cn, self.dummy))
        co2 = torch.where(rm, co, torch.full_like(co, self.dummy))
        self.grid.index_put_((cn2.reshape(-1),), torch.zeros(1, dtype=torch.int16, device=self.dev).expand(cn2.numel()))
        self.grid.index_put_((co2.reshape(-1),), idx1.reshape(-1))
        self.grid[self.dummy:].zero_()
        self.X = torch.where((moved & acc[:, None])[..., None], newX, X)
        self.E = torch.where(acc, En, self.E)
        self.acc_count += acc.float()
        better = self.E < self.Ebest - 1e-6
        self.Ebest = torch.where(better, self.E, self.Ebest)
        self.Xbest = torch.where(better[:, None, None], self.X, self.Xbest)

    # --------------------------------------------------------- schedules
    def run(self, steps, T=None):
        """Run `steps` move attempts per chain (eager) at temperature(s) T (scalar or per-chain tensor)."""
        if T is not None:
            self.T = torch.as_tensor(T, dtype=torch.float32, device=self.dev).expand(self.B).clone()
        for _ in range(steps):
            self.step()

    def anneal(self, sweeps, T0=2.0, T1=0.12, stages=40, final_sweeps=None):
        """Geometric cooling from T0 to T1 in `stages` stages over `sweeps` sweeps (a sweep = L move attempts)."""
        steps_total = sweeps * self.L
        per = max(1, steps_total // stages)
        for s in range(stages):
            T = T0 * (T1 / T0) ** (s / (stages - 1))
            self.run(per, T)
        return self.Ebest

    def check(self, k=4):
        """Compare GPU energies with the numpy reference on k chains and check self-avoidance."""
        S = self.S.cpu().numpy()
        X = self.X.cpu().numpy()
        n = self.n.cpu().numpy()
        E = self.E.cpu().numpy()
        bad = 0
        for b in range(min(k, self.B)):
            Xi = X[b, :n[b]]
            assert len({tuple(x) for x in Xi}) == n[b], 'overlap'
            dif = np.abs(np.diff(Xi, axis=0)).sum(1)
            assert (dif == 1).all(), 'broken bond'
            e = energy_np(S[b, :n[b]], Xi, self.rule, self.eP, self.eB)
            if abs(e - E[b]) > 1e-4:
                bad += 1
        return bad


class GraphRunner:
    """Captures `chunk` steps of a Batch into a CUDA graph and replays it (cuts kernel-launch overhead)."""
    def __init__(self, batch, chunk=20):
        self.b = batch
        self.chunk = chunk
        self.g = None
        try:
            torch.cuda.synchronize()
            st = torch.cuda.Stream()
            st.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(st):
                for _ in range(3):
                    batch.step()
            torch.cuda.current_stream().wait_stream(st)
            self._static()
            g = torch.cuda.CUDAGraph()
            with torch.cuda.graph(g):
                for _ in range(chunk):
                    batch.step()
                self._copy_back()
            self.g = g
        except Exception as e:                                         # fall back to eager steps
            print('CUDA graph capture failed, running eagerly:', repr(e)[:200])
            self.g = None

    def _static(self):
        b = self.b
        # tensors reassigned by step() must live at fixed addresses inside the graph: keep static copies
        self.sX, self.sE, self.sEb, self.sXb = b.X.clone(), b.E.clone(), b.Ebest.clone(), b.Xbest.clone()
        self.sT = b.T.clone()
        self.sacc = b.acc_count.clone()
        b.X, b.E, b.Ebest, b.Xbest, b.T, b.acc_count = self.sX, self.sE, self.sEb, self.sXb, self.sT, self.sacc

    def _copy_back(self):
        b = self.b
        self.sX.copy_(b.X); self.sE.copy_(b.E); self.sEb.copy_(b.Ebest); self.sXb.copy_(b.Xbest); self.sacc.copy_(b.acc_count)
        b.X, b.E, b.Ebest, b.Xbest, b.acc_count = self.sX, self.sE, self.sEb, self.sXb, self.sacc

    def set_T(self, T):
        T = torch.as_tensor(T, dtype=torch.float32, device=self.b.dev)
        self.sT.copy_(T.expand(self.b.B))
        self.b.T = self.sT

    def run(self, steps):
        if self.g is None:
            for _ in range(steps):
                self.b.step()
            return
        for _ in range(max(1, round(steps / self.chunk))):
            self.g.replay()

    def anneal(self, sweeps, T0=2.0, T1=0.12, stages=40):
        steps_total = sweeps * self.b.L
        per = max(self.chunk, steps_total // stages)
        for s in range(stages):
            self.set_T(T0 * (T1 / T0) ** (s / (stages - 1)))
            self.run(per)
        return self.b.Ebest

    def tempering(self, R, ladder, sweeps, swap_every=100):
        """Replica exchange: chains are in groups of R consecutive chains (same sequence); each group holds the
        temperatures `ladder` (low to high) and neighbouring temperatures swap by the Metropolis rule every
        `swap_every` steps. Returns the swap acceptance rate."""
        b = self.b
        Gn = b.B // R
        dev = b.dev
        lad = torch.tensor(ladder, dtype=torch.float32, device=dev)
        slot = (torch.arange(Gn, device=dev)[:, None] * R + torch.arange(R, device=dev)[None, :])   # rank -> chain
        T = torch.empty(b.B, device=dev)
        T[slot.reshape(-1)] = lad.repeat(Gn)
        self.set_T(T)
        steps = sweeps * b.L
        nsw = max(1, steps // swap_every)
        acc = tot = 0
        beta = 1.0 / lad
        for s in range(nsw):
            self.run(swap_every)
            E = b.E[slot]                                                   # Gn x R, by rank
            par = s % 2
            i = torch.arange(par, R - 1, 2, device=dev)
            if len(i) == 0:
                continue
            d = (beta[i] - beta[i + 1])[None, :] * (E[:, i] - E[:, i + 1])
            ok = torch.rand(d.shape, device=dev) < torch.exp(d.clamp(max=0))
            a_, c_ = slot[:, i].clone(), slot[:, i + 1].clone()
            slot[:, i] = torch.where(ok, c_, a_)
            slot[:, i + 1] = torch.where(ok, a_, c_)
            T = torch.empty(b.B, device=dev)
            T[slot.reshape(-1)] = lad.repeat(Gn)
            self.sT.copy_(T)
            acc += int(ok.sum()); tot += ok.numel()
        return acc / max(1, tot)

    def reset_best(self):
        self.sEb.copy_(self.sE)
        self.sXb.copy_(self.sX)
