"""Task 15, prototype step 3: the off-lattice tertiary folder on the GPU (design report 12, section 4).

Everything here is a proposal (Claude's), built on Justin's approved design. No native structure is ever an input:
the energy depends on the sequence only, through step 1's table and burial and step 2's secondary probabilities.

The chain: one bead per monomer, bonds 0.38 nm (stiff harmonic), off-lattice. Units: nm, kJ/mol, K.
Energy terms (all T-independent; the table is taken at 300 K, 150 mM, pH 7):
  1. bonds: K_BOND (|r| - B0)^2;
  2. local (secondary bias, never fixed): for each bend angle theta_i and dihedral phi_i,
       U = -kT0 ln sum_s p_s exp(-u_s / kT0),  s in {helix, strand, coil},  p_s from secondary.py;
     u_helix / u_strand are wells at the usual C-alpha geometry, u_coil is a weak, broad angle well, flat dihedral;
  3. excluded volume (WCA), |i - j| >= 2, diameter from side-chain volume for |i - j| >= 3;
  4. contacts: e_ab * s(r) for |i - j| >= 3, s a smooth switch at d_ab + R_CONTACT_EXTRA;
  5. burial: h_a * B(n_a), n_a = sum_j s(r_aj) (non-local neighbours);
  6. backbone H-bonds between extended stretches (strand pairing): -EPS_HB * w(r) (t_i . t_j)^2 x_i x_j;
  7. the cooperative (many-body desolvation) term, mode 'coop': B(n) is a steep sigmoid in n (a monomer counts as
     buried only beyond N_HALF neighbours), and each contact counts e_ab * s * B(n_a) * B(n_b): a pair's full contact
     energy needs both partners dehydrated. Mode 'additive' (the control): B(n) = min(n / N_FULL, 1), contacts
     unweighted. That is the plain additive contact model Kaya and Chan found falls short of two-state.
Search: replica exchange Langevin dynamics (BAOAB), many chains at once, CUDA graphs.
"""
import json
import math
import os
import time

import numpy as np
import torch

import beads as B
import secondary as S

HERE = os.path.dirname(os.path.abspath(__file__))
R = B.R_GAS
T0 = 300.0
KT0 = R * T0

# ---- constants (all choices; listed in the report) ----
B0 = 0.38            # nm, bond length (C-alpha-like)
K_BOND = 5000.0      # kJ/mol/nm^2
GEOM = dict(helix=(math.radians(91.0), math.radians(50.0)),     # (bend angle, dihedral), C-alpha helix
            strand=(math.radians(120.0), math.radians(-170.0)),  # C-alpha strand
            coil=(math.radians(110.0), None))
K_THETA = 10.0 * KT0     # per rad^2, helix and strand bend wells
K_THETA_COIL = 2.0 * KT0
K_PHI = 2.0 * KT0        # dihedral wells: K (1 - cos(phi - phi_s))
SIG_LOCAL = 0.42         # nm, excluded-volume diameter for i, i + 2
D_MIN, D_MAX = 0.42, 0.58  # nm, bead diameters for |i - j| >= 3, from side-chain volume
R_CONTACT_EXTRA = 0.20   # nm, contact switch midpoint = d_ab + this
W_CONTACT = 0.03         # nm, switch width
N_HALF = 3.5             # coop: neighbours at which a monomer is half-buried
W_BURIAL = 0.5           # coop: sigmoid width (neighbours)
N_FULL = 6.0             # additive: neighbours of a fully buried monomer (step 1 used 6 too)
EPS_HB = 1.5 * KT0       # one backbone H-bond (step 1 target 1.3-1.9 kT)
R_HB, W_HB = 0.50, 0.06  # nm, H-bond distance window (Gaussian)
THETA_EXT = math.radians(106.0)  # extendedness switch for H-bonding (strand-like bend)
EPS_WCA = KT0
F_CAP = 2.0e4          # kJ/mol/nm, cap on a single bead's force (safety; rarely reached)
COND = dict(T=300.0, I=0.15, pH=7.0)


# ------------------------------------------------------------------ per-monomer and per-pair parameters
def table_300(steps12=None):
    """e_ab (16x16) and h_a (16) in kJ/mol at 300 K, 150 mM, from step 1's fitted coefficients."""
    p = steps12 or os.path.join(HERE, 'results', 'steps12.json')
    d = json.load(open(p))['step1']
    c = np.array(d['coef_e'])
    t, x = (COND['T'] - 300) / 20, math.log10(COND['I'])
    E = c @ np.array([1, t, t * t, x, x * x, t * x])
    h = np.array([np.polyval(cc, t) for cc in d['coef_h']])
    return E, h


def diameters():
    v = np.array([sum(B.SIGMA[b.size] ** 3 for b in B.MONOMERS[m]['beads']) for m in range(16)])
    f = ((v - v.min()) / (v.max() - v.min())) ** (1 / 3)
    return D_MIN + (D_MAX - D_MIN) * f


E_TAB, H_TAB = table_300()
DIAM = diameters()


def seq_params(seqs, Lmax):
    """per-sequence tensors (numpy): seq index (padded -1), local probs (L, 3)."""
    n = len(seqs)
    idx = -np.ones((n, Lmax), np.int64)
    P = np.zeros((n, Lmax, 3))
    P[:, :, 2] = 1.0
    for k, s in enumerate(seqs):
        idx[k, :len(s)] = s
        P[k, :len(s)] = S.secondary(list(s), **COND)
    return idx, P


class Model:
    """Energy of a batch of chains. All chains have Lmax slots; mask marks real beads."""

    def __init__(self, idx, P, mode='coop', device='cuda', eps_hb=EPS_HB, n_half=N_HALF, w_burial=W_BURIAL,
                 e_tab=None, h_tab=None):
        dev = torch.device(device)
        self.dev, self.mode = dev, mode
        self.eps_hb, self.n_half, self.w_burial = eps_hb, n_half, w_burial
        e_tab = E_TAB if e_tab is None else e_tab
        h_tab = H_TAB if h_tab is None else h_tab
        C, L = idx.shape
        self.C, self.L = C, L
        m = idx >= 0
        ii = np.clip(idx, 0, 15)
        self.mask = torch.tensor(m, device=dev)
        maskf = m.astype(np.float32)
        sep = np.abs(np.arange(L)[:, None] - np.arange(L)[None, :])
        pm = maskf[:, :, None] * maskf[:, None, :]
        nl = (sep >= 3).astype(np.float32)[None] * pm                       # non-local pairs
        self.nl = torch.tensor(nl, device=dev)
        self.triu = torch.tensor(np.triu(np.ones((L, L), np.float32), 3)[None] * pm, device=dev)
        self.eab = torch.tensor(e_tab[ii[:, :, None], ii[:, None, :]] * nl, dtype=torch.float32, device=dev)
        self.h = torch.tensor(h_tab[ii] * maskf, dtype=torch.float32, device=dev)
        d = DIAM[ii]
        dab = 0.5 * (d[:, :, None] + d[:, None, :])
        sig = np.where(sep[None] == 2, SIG_LOCAL, dab)
        ev = ((sep >= 2)[None] * pm).astype(np.float32)
        self.sig = torch.tensor(sig, dtype=torch.float32, device=dev)
        self.ev = torch.tensor(np.triu(ev[0] * 0 + 1, 2)[None] * ev, device=dev)
        self.rc = torch.tensor(dab + R_CONTACT_EXTRA, dtype=torch.float32, device=dev)
        Pt = torch.tensor(P, dtype=torch.float32, device=dev)
        self.logp = torch.log(Pt.clamp_min(1e-6))                              # (C, L, 3)
        bm = maskf[:, 1:] * maskf[:, :-1]
        self.bmask = torch.tensor(bm, device=dev)
        am = maskf[:, 2:] * maskf[:, 1:-1] * maskf[:, :-2]
        self.amask = torch.tensor(am, device=dev)
        dm = maskf[:, 3:] * maskf[:, 2:-1] * maskf[:, 1:-2] * maskf[:, :-3]
        self.dmask = torch.tensor(dm, device=dev)
        self.ends = None

    # --- pieces reused by analysis ---
    def switch(self, r):
        return torch.sigmoid((self.rc - r) / W_CONTACT)

    def burial_factor(self, n):
        if self.mode == 'coop':
            s0 = 1.0 / (1.0 + math.exp(self.n_half / self.w_burial))
            return (torch.sigmoid((n - self.n_half) / self.w_burial) - s0) / (1 - s0)
        return torch.clamp(n / N_FULL, max=1.0)

    def energy(self, x, parts=False):
        """x: (C, L, 3). Returns total energy per chain (C,), kJ/mol."""
        bvec = x[:, 1:] - x[:, :-1]
        bl = bvec.norm(dim=-1)
        e_bond = (K_BOND * (bl - B0) ** 2 * self.bmask).sum(1)
        # bend angles at beads 1..L-2
        u1, u2 = -bvec[:, :-1], bvec[:, 1:]
        cosang = (u1 * u2).sum(-1) / (bl[:, :-1] * bl[:, 1:] + 1e-9)
        theta = torch.acos(cosang.clamp(-0.9999, 0.9999))
        th_h, ph_h = GEOM['helix']; th_e, ph_e = GEOM['strand']; th_c, _ = GEOM['coil']
        lp = self.logp[:, 1:-1]
        ua = torch.stack([K_THETA * (theta - th_h) ** 2, K_THETA * (theta - th_e) ** 2,
                          K_THETA_COIL * (theta - th_c) ** 2], -1)
        e_ang = (-KT0 * torch.logsumexp(lp - ua / KT0, -1) * self.amask).sum(1)
        # dihedrals over bonds (i, i+1), i = 1..L-3, using the mean probability of beads i, i+1
        b1, b2, b3 = bvec[:, :-2], bvec[:, 1:-1], bvec[:, 2:]
        n1 = torch.cross(b1, b2, dim=-1); n2 = torch.cross(b2, b3, dim=-1)
        m1 = torch.cross(n1, b2 / (b2.norm(dim=-1, keepdim=True) + 1e-9), dim=-1)
        xx = (n1 * n2).sum(-1); yy = (m1 * n2).sum(-1)
        phi = -torch.atan2(yy, xx)        # IUPAC sign: right-handed helix positive
        pd = 0.5 * (self.logp[:, 1:-2].exp() + self.logp[:, 2:-1].exp())
        lpd = torch.log(pd.clamp_min(1e-6))
        # weight by sin^2 of both bend angles: the dihedral is undefined for a straight triple, and its force
        # would diverge there (this made some chains blow up in the first pilot)
        sn2 = (1 - cosang.clamp(-1, 1) ** 2)
        wd = (sn2[:, :-1] * sn2[:, 1:])[..., None]
        ud = wd * torch.stack([K_PHI * (1 - torch.cos(phi - ph_h)), K_PHI * (1 - torch.cos(phi - ph_e)),
                               torch.zeros_like(phi)], -1)
        e_dih = (-KT0 * torch.logsumexp(lpd - ud / KT0, -1) * self.dmask).sum(1)
        # pairs
        dx = x[:, :, None, :] - x[:, None, :, :]
        r = (dx.pow(2).sum(-1) + 1e-6).sqrt()
        sr = (self.sig / r) ** 6
        rcut = self.sig * 2 ** (1 / 6)
        wca = torch.where(r < rcut, 4 * EPS_WCA * (sr * sr - sr) + EPS_WCA, torch.zeros_like(r))
        e_ev = (wca * self.ev).sum((1, 2))
        s = self.switch(r) * self.nl
        n = s.sum(2)
        bf = self.burial_factor(n)
        e_bur = (self.h * bf).sum(1)
        if self.mode == 'coop':
            g = bf.clamp(0, 1)
            e_con = 0.5 * (self.eab * s * g[:, :, None] * g[:, None, :]).sum((1, 2))
        else:
            e_con = 0.5 * (self.eab * s).sum((1, 2))
        # backbone H-bonds between extended stretches
        if self.eps_hb:
            t = torch.zeros_like(x)
            tv = x[:, 2:] - x[:, :-2]
            t[:, 1:-1] = tv / (tv.norm(dim=-1, keepdim=True) + 1e-9)
            ext = torch.zeros(x.shape[:2], device=x.device)
            ext[:, 1:-1] = torch.sigmoid((theta - THETA_EXT) / 0.08) * self.amask
            tt = torch.einsum('cik,cjk->cij', t, t) ** 2
            w = torch.exp(-((r - R_HB) / W_HB) ** 2)
            e_hb = -self.eps_hb * (w * tt * ext[:, :, None] * ext[:, None, :] * self.triu).sum((1, 2))
        else:
            e_hb = torch.zeros_like(e_bond)
        tot = e_bond + e_ang + e_dih + e_ev + e_bur + e_con + e_hb
        if parts:
            return dict(total=tot, bond=e_bond, angle=e_ang, dihedral=e_dih, ev=e_ev, burial=e_bur,
                        contact=e_con, hbond=e_hb, n=n)
        return tot


# ------------------------------------------------------------------ replica exchange Langevin
class REMD:
    """n_seq sequences x n_run independent runs x K temperatures, all chains at once.
    Chain c = (seq k, run r, temp slot j): c = (k * n_run + r) * K + j. Coordinates are swapped between slots."""

    def __init__(self, seqs, n_run, temps, mode='coop', dt=0.004, gamma=2.0, seed=0, device='cuda', **kw):
        self.seqs = [np.asarray(s) for s in seqs]
        self.ns, self.nr, self.K = len(seqs), n_run, len(temps)
        self.L = max(len(s) for s in seqs)
        idx1, P1 = seq_params(self.seqs, self.L)
        rep = n_run * self.K
        self.idx = np.repeat(idx1, rep, 0)
        P = np.repeat(P1, rep, 0)
        self.P1 = P1
        self.model = Model(self.idx, P, mode=mode, device=device, **kw)
        self.dev = self.model.dev
        self.C = self.idx.shape[0]
        self.temps = np.asarray(temps, float)
        self.Tc = torch.tensor(np.tile(self.temps, self.ns * n_run), dtype=torch.float32, device=self.dev)
        self.dt, self.gamma = dt, gamma
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        self.rng = np.random.default_rng(seed)
        self.mask3 = self.model.mask[:, :, None].float()
        self.x = self._init_coords()
        self.x, _ = minimise(self.model, self.x, iters=600)   # remove overlaps of the random start
        self.v = torch.randn(self.x.shape, device=self.dev) * (R * self.Tc)[:, None, None].sqrt() * self.mask3
        self.f = torch.zeros_like(self.x)
        self.e = torch.zeros(self.C, device=self.dev)
        self.graph = None
        self.n_swap_try = np.zeros(self.K - 1); self.n_swap_acc = np.zeros(self.K - 1)

    def _init_coords(self):
        # random self-avoiding-ish start: a random walk with fixed bond length and bend >= 80 deg
        C, L = self.C, self.L
        rng = self.rng
        x = np.zeros((C, L, 3))
        d = rng.normal(size=(C, 3)); d /= np.linalg.norm(d, axis=1, keepdims=True)
        for i in range(1, L):
            nd = d + 1.2 * rng.normal(size=(C, 3)); nd /= np.linalg.norm(nd, axis=1, keepdims=True)
            bad = (nd * d).sum(1) < -0.2
            nd[bad] = d[bad]
            x[:, i] = x[:, i - 1] + B0 * nd
            d = nd
        x -= x.mean(1, keepdims=True)
        # padded slots (shorter chains in a batch): fixed beads on a far straight line, so no length is ever zero
        # (zero-length bonds give NaN gradients even where the term is masked)
        pad = self.idx < 0
        ar = np.arange(L)
        line = np.stack([100.0 + 0.3 * ar, 0.2 * (ar % 2), 0.15 * ((ar // 2) % 2)], 1)   # not collinear
        x[pad] = np.broadcast_to(line, (C, L, 3))[pad]
        return torch.tensor(x, dtype=torch.float32, device=self.dev)

    def forces(self, x):
        with torch.enable_grad():
            xx = x.detach().requires_grad_(True)
            e = self.model.energy(xx)
            g, = torch.autograd.grad(e.sum(), xx)
        f = -torch.nan_to_num(g) * self.mask3
        fn = f.norm(dim=-1, keepdim=True)
        f = f * (F_CAP / fn.clamp_min(F_CAP))          # safety cap on rare huge forces (bead overlaps)
        return f, e.detach()

    def _steps(self, n):
        dt, g = self.dt, self.gamma
        c1 = math.exp(-g * dt)
        c2 = torch.sqrt((1 - c1 * c1) * R * self.Tc)[:, None, None]
        for _ in range(n):
            self.v.add_(0.5 * dt * self.f)
            self.x.add_(0.5 * dt * self.v)
            noise = torch.randn(self.x.shape, device=self.dev)
            self.v.mul_(c1).add_(c2 * noise * self.mask3)
            self.x.add_(0.5 * dt * self.v)
            f, e = self.forces(self.x)
            self.f.copy_(f); self.e.copy_(e)
            self.v.add_(0.5 * dt * self.f)

    def build(self, nblock, use_graph=True):
        f, e = self.forces(self.x)
        self.f.copy_(f); self.e.copy_(e)
        self.nblock = nblock
        if not use_graph:
            return
        s = torch.cuda.Stream(device=self.dev)
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            xs, vs, fs, es = self.x.clone(), self.v.clone(), self.f.clone(), self.e.clone()
            self._steps(3)                       # warm-up
            self.x.copy_(xs); self.v.copy_(vs); self.f.copy_(fs); self.e.copy_(es)
        torch.cuda.current_stream().wait_stream(s)
        self.graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.graph):
            self._steps(nblock)

    def run_block(self):
        if self.graph is not None:
            self.graph.replay()
        else:
            self._steps(self.nblock)

    def exchange(self, parity):
        e = self.e.view(self.ns * self.nr, self.K).cpu().numpy().astype(np.float64)
        beta = 1.0 / (R * self.temps)
        perm = np.arange(self.C).reshape(self.ns * self.nr, self.K).copy()
        for j in range(parity, self.K - 1, 2):
            delta = (beta[j] - beta[j + 1]) * (e[:, j] - e[:, j + 1])
            acc = np.log(self.rng.random(len(e)) + 1e-300) < delta
            self.n_swap_try[j] += len(e); self.n_swap_acc[j] += acc.sum()
            a = perm[acc, j].copy(); perm[acc, j] = perm[acc, j + 1]; perm[acc, j + 1] = a
        p = torch.tensor(perm.reshape(-1), device=self.dev)
        Told = self.Tc[p]
        scale = (self.Tc / Told).sqrt()[:, None, None]
        self.x.copy_(self.x[p]); self.v.copy_(self.v[p] * scale); self.f.copy_(self.f[p]); self.e.copy_(self.e[p])


def minimise(model, x, iters=3000, lr=4e-5):
    """plain gradient descent to the nearest local minimum (for comparing lowest structures)."""
    x = x.clone()
    m3 = model.mask[:, :, None].float()
    for k in range(iters):
        with torch.enable_grad():
            xx = x.detach().requires_grad_(True)
            e = model.energy(xx)
            g, = torch.autograd.grad(e.sum(), xx)
        g = torch.nan_to_num(g)
        gn = g.norm(dim=-1, keepdim=True).clamp_min(1.0)   # cap a step at 1 kJ/mol/nm-equivalent per bead
        x = x - lr * g / gn * gn.clamp(max=2000.0) * m3
    with torch.no_grad():
        e = model.energy(x)
    return x, e


# ------------------------------------------------------------------ analysis helpers
def kabsch_rmsd(A, Bm, mask=None):
    """A, Bm: (..., L, 3) torch; proper rotations only (mirror images differ). Returns (...,)."""
    if mask is None:
        mask = torch.ones(A.shape[:-1], device=A.device)
    w = mask[..., None]
    nw = w.sum(-2, keepdim=True)
    a = A - (A * w).sum(-2, keepdim=True) / nw
    b = Bm - (Bm * w).sum(-2, keepdim=True) / nw
    a, b = a * w, b * w
    H = a.transpose(-1, -2) @ b
    U, Sg, Vh = torch.linalg.svd(H)
    d = torch.sign(torch.linalg.det(U @ Vh))
    Sg = torch.cat([Sg[..., :2], (Sg[..., 2] * d)[..., None]], -1)
    e2 = (a.pow(2).sum((-1, -2)) + b.pow(2).sum((-1, -2)) - 2 * Sg.sum(-1)) / nw[..., 0, 0]
    return e2.clamp_min(0).sqrt()


def contact_map(x, L, rc):
    """boolean contacts |i-j| >= 3 at r < rc (numpy x (L, 3), rc (L, L))."""
    d = np.linalg.norm(x[:, None] - x[None], axis=-1)
    sep = np.abs(np.arange(L)[:, None] - np.arange(L)[None])
    return (d < rc) & (sep >= 3)


def wham(E, Tk, iters=2000, tol=1e-9):
    """multiple-histogram reweighting without bins. E: list over temperatures of energy arrays (kJ/mol).
    Returns a function giving per-sample log-weights at any T, plus the pooled energies."""
    Ea = np.concatenate(E)
    N = np.array([len(e) for e in E], float)
    bk = 1.0 / (R * np.asarray(Tk))
    f = np.zeros(len(Tk))
    emin = Ea.min()
    Es = Ea - emin
    for _ in range(iters):
        # log denominator per sample: log sum_k N_k exp(f_k - b_k E)
        a = np.log(N)[None] + f[None] - bk[None] * Es[:, None]
        mx = a.max(1, keepdims=True)
        lden = (mx[:, 0] + np.log(np.exp(a - mx).sum(1)))
        fn = np.empty_like(f)
        for k in range(len(Tk)):
            z = -bk[k] * Es - lden
            m = z.max()
            fn[k] = -(m + math.log(np.exp(z - m).sum()))
        fn -= fn[0]
        if np.abs(fn - f).max() < tol:
            f = fn
            break
        f = fn
    a = np.log(N)[None] + f[None] - bk[None] * Es[:, None]
    mx = a.max(1, keepdims=True)
    lden = mx[:, 0] + np.log(np.exp(a - mx).sum(1))

    def logw(T):
        lw = -Es / (R * T) - lden
        return lw - lw.max()
    return logw, Ea


def thermo(E, Tk, fold_ind, Tgrid):
    """from WHAM: <E>, C(T) (kJ/mol/K), fraction folded and dG_fold (kT) on Tgrid."""
    logw, Ea = wham(E, Tk)
    fi = np.concatenate(fold_ind).astype(float)
    out = dict(E=[], C=[], f=[], dG=[])
    for T in Tgrid:
        w = np.exp(logw(T)); w /= w.sum()
        m = (w * Ea).sum(); v = (w * (Ea - m) ** 2).sum()
        f = (w * fi).sum()
        out['E'].append(m); out['C'].append(v / (R * T * T)); out['f'].append(f)
        fo = min(max(f, 1e-300), 1 - 1e-16)
        # dG_fold = G_folded - G_unfolded = -kT ln (f / (1 - f)), in kT
        wf = (w * fi).sum(); wu = (w * (1 - fi)).sum()
        out['dG'].append(-math.log(max(wf, 1e-300) / max(wu, 1e-300)))
    return {k: np.array(v) for k, v in out.items()}


def kaya_chan(Tg, C, Eavg):
    """kappa2 = 2 Tmax sqrt(kB Cmax) / dH_cal, without and with baseline subtraction (Kaya and Chan 2000)."""
    j = int(np.argmax(C))
    Tm, Cm = Tg[j], C[j]
    dHcal = Eavg[-1] - Eavg[0]                     # integral of C dT over the window
    k2 = 2 * Tm * math.sqrt(R * Cm) / dHcal if dHcal > 0 else float('nan')
    # baseline subtraction (simplified from Kaya and Chan): a straight line through C at the window's two ends
    base = np.interp(Tg, [Tg[0], Tg[-1]], [C[0], C[-1]])
    Cs = (C - base).clip(min=0)
    dHs = (getattr(np, 'trapezoid', None) or np.trapz)(Cs, Tg)
    k2s = 2 * Tm * math.sqrt(R * Cs[j]) / dHs if dHs > 0 else float('nan')
    return dict(Tmax=float(Tm), Cmax=float(Cm), dHcal=float(dHcal), k2=float(k2), k2s=float(k2s),
                dHvH=float(2 * Tm * math.sqrt(R * Cm)))
