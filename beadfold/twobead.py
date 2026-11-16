"""Task 23: the tertiary folder with two beads per monomer (Justin's decision of 15 November, option D).

Everything here is a proposal (Claude's) on Justin's approved design. No native structure is an input: the energy
depends on the sequence only. The one-bead folder (tertiary.py) is untouched and still works.

The chain: L backbone beads B_i (C-alpha-like; bonds 0.38 nm) and L side-chain beads S_i (one per monomer, at the
side chain's centroid). Particles are stored as x[:, :L] = backbone, x[:, L:] = side chains. Units nm, kJ/mol, K.

Energy terms, each from its own physics (none is a rescaled copy of the step-1 table):
  1. backbone bonds, and step 2's local secondary bias on bend angles and dihedrals (as in tertiary.py). The helix
     probability is divided by the Boltzmann factor of one explicit backbone H-bond, so that the helix H-bond is not
     counted twice (once in Zimm-Bragg's s, once in term 5). Step 2's i, i+3/i+4 charge correction is switched off:
     the side-chain charges now act explicitly (term 7).
  2. side-chain placement: S_i is held near an ideal position from the backbone frame (C-beta-like direction,
     distance = the side chain's centroid arm) by a soft harmonic restraint (rotamer-like freedom of about 0.1 nm).
  3. excluded volume (WCA) between all non-bonded particles, diameters from bead volumes.
  4. packing (van der Waals) between side chains |i-j| >= 3: -EPS_VDW sqrt(A_a A_b) (1 - KAPPA |p_a - p_b|) s(r),
     A = surface share (diameter^2), p = polarity on step 1's ladder (step 1's like-attracts-like mixing rule). No
     complement term for oily monomers (the oily-partner rule, task 21): oily pairs differ only by size and polarity.
     Side-chain donor-acceptor pairs add EPS_DA (step 1's H-bond-like well); for odd (oily) monomers none.
  5. backbone H-bonds: helix i -> i+4 (C-alpha distances i, i+3 and i, i+4 at their alpha-helix values, right-handed),
     and strand pairing (|i-j| >= 3, extended, (anti)parallel), EPS_HB each.
  6. burial (desolvation): h_a B(n_a), n_a = side-chain and backbone neighbours of S_a; the approved cooperative term
     gates every side-chain contact by B(n_a) B(n_b) (mode 'coop'); mode 'additive' is the control.
  7. charges: Coulomb between side-chain charges with an environment-dependent dielectric:
       U = 138.9 q_a q_b / r [ (1 - G) exp(-r / lambda_D) / eps_w + G / eps_core ],  G = B(n_a) B(n_b),
     eps_w = water at 300 K; eps_core from Hendsch-Tidor's target (buried pair about 6 kT worse than an oily isostere),
     with Lehninger's factor of about 17 as the bound (eps_core >= eps_w / 17). No temperature dependence (no source).
"""
import math

import numpy as np
import torch

import beads as B
import secondary as S
import tertiary as TT

R = B.R_GAS
T0 = 300.0
KT0 = R * T0
COND = TT.COND

# ---- constants (all proposals; listed in the report) ----
B0, K_BOND = TT.B0, TT.K_BOND
SIG_BB = 0.42            # nm, backbone bead diameter (as the one-bead model's i, i+2)
SC_SC_F, SC_BB_F = 0.9, 0.85   # centroid beads interdigitate: their exclusion diameters are shrunk
VIRTUAL_SC = False       # True: side chain rigid on the backbone frame (tried; unstable at dt 0.004, so not used)
FRAME_EPS = 0.3          # nm, regulariser of the side-chain frame
_b0 = 2 * B0 * math.sin(math.radians(55.0)); _n0 = B0 * B0 * math.sin(math.radians(70.0))
NB0, NN0 = _b0 / (_b0 + FRAME_EPS), _n0 / (_n0 + FRAME_EPS * B0)
K_SC = 400.0             # kJ/mol/nm^2: side-chain restraint (about 0.08 nm rms per axis at 300 K)
BETA_SC = math.radians(20.0)   # tilt of the side-chain direction from the bend bisector, towards the N-terminus
EPS_VDW = 1.5 * KT0      # packing well between two large side chains (calibrated in stage 1 against Eriksson 1992)
KAPPA = B.KAPPA
EPS_DA = 1.0 * KT0       # side-chain donor-acceptor extra well
HB_DIVIDE = -2.0         # helix share x exp(-EPS_HB/kT * HB_DIVIDE) = x e^3: compensates the H-bond window's conformational entropy (calibrated in stage 1 so isolated helices approach step 2's Zimm-Bragg content)
EPS_HB = 1.5 * KT0       # one backbone H-bond (Pace et al. 2014: 1.1 +- 0.8 kcal/mol, i.e. about 1-3 kT)
R_HB, W_HB = 0.50, 0.06  # strand pairing window (as tertiary.py)
THETA_EXT = TT.THETA_EXT
R_H3, R_H4, W_H = 0.505, 0.620, 0.05   # alpha-helix C-alpha distances i, i+3 and i, i+4 (ideal helix), window
R_EXTRA, W_CON = 0.25, 0.03    # contact switch: (d_a + d_b) / 2 + R_EXTRA
BB_NEIGH = 0.5           # a backbone neighbour counts half a side-chain neighbour for burial
N_HALF, W_BURIAL, N_FULL = 6.0, 0.8, 10.0   # set in stage 1 from the targets' neighbour counts
EPS_W = B.eps_water(300.0)
LAMBDA_D = B.debye(300.0, 0.15)
EPS_CORE = 6.0           # calibrated in stage 1 (saltbridge_tb.py); bound eps_w / 17 = 4.6
COULOMB = 138.935458     # kJ/mol nm / e^2
EPS_WCA = KT0
F_CAP = TT.F_CAP
# task 26 step 1 (Justin's decision of 15 November; constants are proposals, to be checked against the papers):
# charges split into a self term and a charge-charge term with different dielectrics (Schutz and Warshel 2001;
# Sham, Muegge and Warshel 1998). elec='v23' keeps task 23's single-dielectric term.
EPS_SELF = 5.0           # eps for the Born-like self (desolvation) term, Justin's range 4-6
EPS_PAIR = 20.0          # effective eps for buried charge-charge interactions (staphylococcal nuclease: 20)
BORN_F = 0.5             # Born radius = BORN_F x side-chain bead diameter (proposal)
# task 27 (Justin's decision of 16 November, about 00:19): elec='cd' = 'split' plus a charge-dipole term. Polar
# neighbours of a buried charge (side-chain donors/acceptors that carry no charge, and backbone beads, |i-j| >= 2,
# inside the burial contact switch) pay back part of its Born cost:
#   S_a = 138.9 |q_a| MU_CD / EPS_CD * sum_j s(r_aj) / r_aj^2,   payback = U_self,a (1 - exp(-S_a / U_self,a))
# (an aligned point dipole at small eps, Sham, Muegge and Warshel 1998; saturating, so polar groups can at most give
# the charge back its water-like solvation). EPS_CD = eps_self (the same small eps as the self term). MU_CD is the one
# new constant, calibrated in charges27.py on benchmark B for a pair in a polar-lined pocket.
MU_CD = 0.085            # e nm (4.1 D), effective dipole of one polar group: calibrated in charges27.py at eps_self 5


def born_self(q, d, eps_self=EPS_SELF):
    """Born-like cost (kJ/mol) of moving charge q on a bead of diameter d from water into a core of eps_self."""
    return COULOMB * q * q / (2 * BORN_F * d) * (1.0 / eps_self - 1.0 / EPS_W)


def sc_props():
    """per monomer: side-chain diameter, arm, surface share, polarity, charge, donor, acceptor, burial h."""
    d, arm, pol, q, don, acc = [], [], [], [], [], []
    for m in range(16):
        bs = B.MONOMERS[m]['beads']
        d.append(sum(B.SIGMA[b.size] ** 3 for b in bs) ** (1 / 3))
        pos, z = [], B.ARM[bs[0].size]
        pos.append(z)
        for k in range(1, len(bs)):
            z += 0.75 * 0.5 * (B.SIGMA[bs[k - 1].size] + B.SIGMA[bs[k].size]); pos.append(z)
        arm.append(float(np.mean(pos)) if len(bs) > 1 else 0.75 * pos[0])
        w = np.array([B.SIZEF[b.size] for b in bs])
        pol.append(float((w * np.array([b.polarity() for b in bs])).sum() / w.sum()))
        q.append(B.net_charge(m, COND['pH']))
        don.append(any('d' in b.hb for b in bs)); acc.append(any('a' in b.hb for b in bs))
    d = np.array(d)
    return dict(d=d, arm=np.array(arm), A=(d / d.max()) ** 2, pol=np.array(pol), q=np.array(q),
                don=np.array(don), acc=np.array(acc), h=TT.H_TAB.copy())


SC = sc_props()
# side chains that act as dipoles for the charge-dipole term: donor or acceptor marks, no charge
DIP_SC = ((SC['don'] | SC['acc']) & (np.abs(SC['q']) < 1e-6)).astype(np.float64)
ISO = {0: 13, 2: 3, 8: 3, 10: 3}   # oily isosteres of the charged monomers (as saltbridge_tb.py)


def h_table(h_charge='keep'):
    h = SC['h'].copy()
    if h_charge == 'iso':
        for m, i in ISO.items():
            h[m] = SC['h'][i]
    return h


def pair_tables(eps_vdw=None, eps_da=None):
    """16 x 16 side-chain pair wells (kJ/mol, negative = attractive), from term 4."""
    ev = EPS_VDW if eps_vdw is None else eps_vdw
    ed = EPS_DA if eps_da is None else eps_da
    A, p = SC['A'], SC['pol']
    W = -ev * np.sqrt(A[:, None] * A[None]) * (1 - KAPPA * np.abs(p[:, None] - p[None]))
    da = (SC['don'][:, None] & SC['acc'][None]) | (SC['acc'][:, None] & SC['don'][None])
    odd = (np.arange(16) % 2 == 1)
    da &= ~(odd[:, None] & odd[None])
    return W - ed * da


def local_probs(seq):
    """step 2's (helix, strand, coil) without the charge corrections, helix divided by one H-bond's factor."""
    seq = list(seq)
    s = np.array([S.s_base(m) for m in seq], float)
    ph = S.helix_prob(s)
    fs = S.strand_share(seq, [0.0] * len(seq))
    P = np.stack([ph, (1 - ph) * fs, (1 - ph) * (1 - fs)], 1)
    P[:, 0] *= math.exp(-EPS_HB / KT0 * HB_DIVIDE)
    return P / P.sum(1, keepdims=True)


# task 26 step 2 (Justin's decision of 15 November, about 21:26): the cooperative helix term, helix='coop'.
# Zimm-Bragg's nucleation moves from the local bias into the tertiary energy, on the explicit helix H-bonds h_j
# (j -> j+4, in [0, 1]):  E_coop = EPS_NUC sum_j h_j (1 - h_{j-1}),  EPS_NUC = -kT0 ln(sigma) (step 2's sigma = 1e-3),
# so each helical stretch of H-bonds pays one nucleation cost, as in Zimm-Bragg, and no constant is new here.
# The local bias then carries only the per-monomer propagation weight s_i (step 2's s_base), not step 2's
# cooperative helix probability (which already contains nucleation): p_helix,i = K_HELIX s_i / (1 + K_HELIX s_i).
# K_HELIX is the one calibration constant (an entropy compensation for the H-bond window, as HB_DIVIDE was in task 23),
# fitted in helix26.py so isolated helices reach step 2's Zimm-Bragg content.
EPS_NUC = -KT0 * math.log(S.SIGMA_ZB)
K_HELIX = 4.0            # calibrated in helix26.py (see the report)


def local_probs_coop(seq, k_helix=None):
    k = K_HELIX if k_helix is None else k_helix
    seq = list(seq)
    s = np.array([S.s_base(m) for m in seq], float)
    ph = k * s / (1 + k * s)
    fs = S.strand_share(seq, [0.0] * len(seq))
    return np.stack([ph, (1 - ph) * fs, (1 - ph) * (1 - fs)], 1)


# helix='coop2' (the version used after the first scan; 'coop' above left isolated helices at 0.03-0.07 for every K
# up to 100, because the narrow H-bond window costs more entropy than the local bias can pay back):
# both Zimm-Bragg weights go into the tertiary H-bond term, and the local bias is neutral about helices
# (p_helix = 0.5 everywhere; step 2's strand/coil split of the rest is kept):
#   E_helix = sum_j h_j [ -(EPS_HB + EPS_PROP) - kT0 <ln s>_{j+1..j+3} ] + EPS_NUC sum_j h_j (1 - h_{j-1})
# <ln s> = the mean of ln s_i (step 2's propagation weights) over the three monomers inside the H-bond's turn, so the
# sequence enters as in Zimm-Bragg (a proline-like 15, s = 0.05, costs 3 kT / 3 per bond it sits in), and EPS_NUC =
# -kT0 ln sigma is step 2's nucleation. EPS_PROP is the one calibration constant (the entropy the narrow H-bond window
# costs), fitted in helix26.py so isolated helices reach step 2's Zimm-Bragg content.
EPS_PROP = 3.0 * KT0     # calibrated in helix26.py (see the report)
LN_S = np.log(np.array([S.s_base(m) for m in range(16)], float))


def local_probs_coop2(seq):
    seq = list(seq)
    ph = np.full(len(seq), 0.5)
    fs = S.strand_share(seq, [0.0] * len(seq))
    return np.stack([ph, (1 - ph) * fs, (1 - ph) * (1 - fs)], 1)


def seq_params(seqs, Lmax, helix='v23', k_helix=None):
    n = len(seqs)
    idx = -np.ones((n, Lmax), np.int64)
    P = np.zeros((n, Lmax, 3)); P[:, :, 2] = 1.0
    for k, s in enumerate(seqs):
        idx[k, :len(s)] = s
        P[k, :len(s)] = (local_probs_coop(s, k_helix) if helix == 'coop' else local_probs_coop2(s) if helix == 'coop2'
                         else local_probs(s))
    return idx, P


class Model2:
    """Energy of a batch of two-bead chains; x is (C, 2L, 3)."""

    def __init__(self, idx, P, mode='coop', device='cuda', eps_vdw=None, eps_da=None, eps_hb=EPS_HB,
                 eps_core=None, n_half=N_HALF, w_burial=W_BURIAL, charges=True, elec='v23',
                 eps_self=EPS_SELF, eps_pair=EPS_PAIR, h_charge='keep', mu_cd=None, eps_cd=None,
                 helix='v23', eps_nuc=None, eps_prop=None, w_h=None):
        """elec 'v23': task 23 (one dielectric eps_core for buried pairs). elec 'split' (task 26): buried pairs at
        eps_pair, plus a Born self term per buried charge at eps_self. h_charge 'keep' leaves the burial table as it
        is; 'iso' gives charged monomers their oily isostere's burial h, so the charge's desolvation is counted only
        once (by the Born term)."""
        dev = torch.device(device)
        self.elec, self.eps_pair = elec, eps_pair
        self.mu_cd = MU_CD if mu_cd is None else mu_cd
        self.helix = helix
        self.eps_nuc = EPS_NUC if eps_nuc is None else eps_nuc
        self.eps_prop = EPS_PROP if eps_prop is None else eps_prop
        if np.ndim(self.eps_prop):            # one value per chain (calibration scans only)
            self.eps_prop = torch.as_tensor(np.asarray(self.eps_prop, np.float32), device=dev)[:, None]
        self.w_h = W_H if w_h is None else w_h      # helix H-bond window width (nm); task 23: 0.05
        self.eps_cd = eps_self if eps_cd is None else eps_cd
        self.dev, self.mode = dev, mode
        self.eps_hb, self.n_half, self.w_burial = eps_hb, n_half, w_burial
        self.eps_core = EPS_CORE if eps_core is None else eps_core
        C, L = idx.shape
        self.C, self.L, self.N = C, L, 2 * L
        f = lambda a: torch.as_tensor(np.asarray(a, np.float32), device=dev)
        it = torch.as_tensor(np.asarray(idx), device=dev)
        m = it >= 0
        ii = it.clamp(0, 15)
        mf = m.float()
        self.maskL = mf
        self.mask = torch.cat([m, m], 1)
        ar = torch.arange(L, device=dev)
        sep = (ar[:, None] - ar[None]).abs()[None]
        pm = mf[:, :, None] * mf[:, None, :]
        d = f(SC['d'])[ii]
        dss = 0.5 * (d[:, :, None] + d[:, None, :])
        dsb = (0.5 * (d + SIG_BB))[:, :, None].expand(C, L, L)
        one = torch.ones_like(dss)
        sig = torch.cat([torch.cat([SIG_BB * one, (torch.where(sep == 1, 0.8, SC_BB_F) * dsb).transpose(1, 2)], 2),
                         torch.cat([torch.where(sep == 1, 0.8, SC_BB_F) * dsb, torch.where(sep == 1, 0.8, SC_SC_F) * dss], 2)], 1)
        evbb = (sep >= 2).float() * pm
        ev1 = (sep >= (2 if VIRTUAL_SC else 1)).float() * pm   # virtual side chains: i, i+1 set by the local terms
        ev = torch.cat([torch.cat([evbb, ev1.transpose(1, 2)], 2), torch.cat([ev1, ev1], 2)], 1)
        self.sig = sig
        self.ev = torch.triu(torch.ones(2 * L, 2 * L, device=dev), 1)[None] * ev
        self.rc_ss = dss + R_EXTRA
        self.rc_sb = dsb + R_EXTRA
        self.nb2 = (sep >= 2).float() * pm
        self.nl3 = (sep >= 3).float() * pm
        W = f(pair_tables(eps_vdw, eps_da))
        self.eab = W[ii[:, :, None], ii[:, None, :]] * self.nl3
        self.h = f(h_table(h_charge))[ii] * mf
        q = f(SC['q'])[ii] * mf * (1.0 if charges else 0.0)
        self.uself = f(born_self(SC['q'], SC['d'], eps_self))[ii] * mf * (1.0 if (charges and elec in ('split', 'cd')) else 0.0)
        self.qabs = q.abs()
        self.dip = f(DIP_SC)[ii] * mf
        self.qq = q[:, :, None] * q[:, None, :] * self.nb2
        self.arm = (f(SC['arm'])[ii] * mf)[:, :, None]
        self.logp = torch.log(f(P).clamp_min(1e-6))
        self.bmask = mf[:, 1:] * mf[:, :-1]
        self.amask = mf[:, 2:] * mf[:, 1:-1] * mf[:, :-2]
        self.dmask = mf[:, 3:] * mf[:, 2:-1] * mf[:, 1:-2] * mf[:, :-3]
        self.h4mask = mf[:, 4:] * mf[:, :-4]
        lns = f(LN_S)[ii] * mf
        if L > 4:
            self.lns_bond = (lns[:, 1:-3] + lns[:, 2:-2] + lns[:, 3:-1]) / 3.0
        else:
            self.lns_bond = torch.zeros(C, 0, device=dev)
        self.triu3 = torch.triu(torch.ones(L, L, device=dev), 3)[None] * pm
        self.last = m.sum(1) - 1
        z = torch.zeros(C, 1, device=dev)
        self.mid = torch.cat([z, self.amask, z], 1)

    def burial_factor(self, n):
        if self.mode == 'coop':
            s0 = 1.0 / (1.0 + math.exp(self.n_half / self.w_burial))
            return (torch.sigmoid((n - self.n_half) / self.w_burial) - s0) / (1 - s0)
        return torch.clamp(n / N_FULL, max=1.0)

    def sc_ideal(self, xb):
        """ideal side-chain positions from the backbone frame (C, L, 3)."""
        C, L = xb.shape[:2]
        u1 = torch.zeros_like(xb); u2 = torch.zeros_like(xb)
        u1[:, 1:] = xb[:, 1:] - xb[:, :-1]
        u2[:, :-1] = xb[:, 1:] - xb[:, :-1]
        bis = u1 - u2
        nrm = torch.cross(u1, u2, dim=-1)
        # regularised frame: a straight triple has no bisector or normal. Unregularised (or renormalised) frames
        # swing the side chain by up to 0.6 nm for a 0.02 nm backbone move near straight, and chains blew up (first
        # Go run, 440-480 K, and at 300 K with rigid side chains); bug of my own, fixed. Each component is scaled
        # to 1 at a 110-degree bend and shrinks smoothly to 0 as the triple straightens (Lipschitz ~ arm / FRAME_EPS).
        nb, nn = bis.norm(dim=-1, keepdim=True), nrm.norm(dim=-1, keepdim=True)
        bis = bis / (nb + FRAME_EPS) / NB0
        nrm = nrm / (nn + FRAME_EPS * B0) / NN0
        dmid = math.cos(BETA_SC) * bis - math.sin(BETA_SC) * nrm
        # termini: point away from the neighbour
        dend0 = -u2[:, :1] / (u2[:, :1].norm(dim=-1, keepdim=True) + 1e-6)
        ar = torch.arange(C, device=xb.device)
        ul = u1[ar, self.last][:, None]
        dendL = ul / (ul.norm(dim=-1, keepdim=True) + 1e-6)
        if not hasattr(self, 'endmask') or self.endmask.shape[0] != C:
            em0 = torch.zeros(C, L, 1, device=xb.device); em0[:, 0] = 1.0
            emL = torch.zeros(C, L, 1, device=xb.device); emL[ar, self.last] = 1.0
            self.endmask0, self.endmask = em0, emL
        dirn = dmid * self.mid[:, :, None] + self.endmask0 * dend0 + self.endmask * dendL
        return xb + self.arm * dirn

    def energy(self, x, parts=False):
        L = self.L
        xb, xs = x[:, :L], x[:, L:]
        bvec = xb[:, 1:] - xb[:, :-1]
        bl = bvec.norm(dim=-1)
        e_bond = (K_BOND * (bl - B0) ** 2 * self.bmask).sum(1)
        u1, u2 = -bvec[:, :-1], bvec[:, 1:]
        cosang = (u1 * u2).sum(-1) / (bl[:, :-1] * bl[:, 1:] + 1e-9)
        theta = torch.acos(cosang.clamp(-0.9999, 0.9999))
        th_h, ph_h = TT.GEOM['helix']; th_e, ph_e = TT.GEOM['strand']; th_c, _ = TT.GEOM['coil']
        lp = self.logp[:, 1:-1]
        ua = torch.stack([TT.K_THETA * (theta - th_h) ** 2, TT.K_THETA * (theta - th_e) ** 2,
                          TT.K_THETA_COIL * (theta - th_c) ** 2], -1)
        e_ang = (-KT0 * torch.logsumexp(lp - ua / KT0, -1) * self.amask).sum(1)
        b1, b2, b3 = bvec[:, :-2], bvec[:, 1:-1], bvec[:, 2:]
        n1 = torch.cross(b1, b2, dim=-1); n2 = torch.cross(b2, b3, dim=-1)
        m1 = torch.cross(n1, b2 / (b2.norm(dim=-1, keepdim=True) + 1e-9), dim=-1)
        phi = -torch.atan2((m1 * n2).sum(-1), (n1 * n2).sum(-1))
        pd = 0.5 * (self.logp[:, 1:-2].exp() + self.logp[:, 2:-1].exp())
        lpd = torch.log(pd.clamp_min(1e-6))
        sn2 = (1 - cosang.clamp(-1, 1) ** 2)
        wd = (sn2[:, :-1] * sn2[:, 1:])
        ud = wd[..., None] * torch.stack([TT.K_PHI * (1 - torch.cos(phi - ph_h)), TT.K_PHI * (1 - torch.cos(phi - ph_e)),
                                          torch.zeros_like(phi)], -1)
        e_dih = (-KT0 * torch.logsumexp(lpd - ud / KT0, -1) * self.dmask).sum(1)
        # side-chain placement
        if VIRTUAL_SC:
            xs = self.sc_ideal(xb)
            x = torch.cat([xb, xs], 1)
            e_sc = torch.zeros_like(e_bond)
        else:
            e_sc = (K_SC * (xs - self.sc_ideal(xb)).pow(2).sum(-1) * self.maskL).sum(1)
        # all pair distances
        dx = x[:, :, None, :] - x[:, None, :, :]
        r = (dx.pow(2).sum(-1) + 1e-6).sqrt()
        sr = (self.sig / r) ** 6
        wca = torch.where(r < self.sig * 1.122462, 4 * EPS_WCA * (sr * sr - sr) + EPS_WCA, torch.zeros_like(r))
        e_ev = (wca * self.ev).sum((1, 2))
        rss, rsb, rbb = r[:, L:, L:], r[:, L:, :L], r[:, :L, :L]
        s_ss = torch.sigmoid((self.rc_ss - rss) / W_CON)
        s_sb = torch.sigmoid((self.rc_sb - rsb) / W_CON)
        n = (s_ss * self.nb2).sum(2) + BB_NEIGH * (s_sb * self.nb2).sum(2)
        bf = self.burial_factor(n)
        e_bur = (self.h * bf).sum(1)
        g = bf.clamp(0, 1)
        G = g[:, :, None] * g[:, None, :]
        if self.mode == 'coop':
            e_pack = 0.5 * (self.eab * s_ss * G).sum((1, 2))
        else:
            e_pack = 0.5 * (self.eab * s_ss).sum((1, 2))
        rr = rss.clamp_min(0.35)
        eps_in = self.eps_pair if self.elec in ('split', 'cd') else self.eps_core
        e_el = 0.5 * (self.qq * COULOMB / rr * ((1 - G) * torch.exp(-rr / LAMBDA_D) / EPS_W + G / eps_in)).sum((1, 2))
        if self.elec == 'cd':
            rsc = rr; rbc = rsb.clamp_min(0.35)
            wsum = (s_ss * self.nb2 * self.dip[:, None, :] / rsc ** 2).sum(2) + (s_sb * self.nb2 / rbc ** 2).sum(2)
            S_cd = COULOMB * self.qabs * self.mu_cd / self.eps_cd * wsum
            us = self.uself.clamp_min(1e-6)
            e_cd = -self.uself * (1 - torch.exp(-S_cd / us))
            e_self = ((self.uself + e_cd) * g).sum(1)
            self._e_cd = (e_cd * g).sum(1)
        else:
            e_self = (self.uself * g).sum(1)
            self._e_cd = torch.zeros_like(e_self)
        e_el = e_el + e_self
        # backbone H-bonds: helix i -> i+4
        ar = torch.arange(L - 4, device=x.device) if L > 4 else None
        if self.eps_hb and L > 4:
            r4 = rbb.diagonal(4, 1, 2); r3 = rbb.diagonal(3, 1, 2)[:, :-1]
            chir = torch.sigmoid(torch.sin(phi) / 0.15)        # right-handed dihedrals i and i+1
            c2 = chir[:, :-1] * chir[:, 1:]
            hh = torch.exp(-((r4 - R_H4) / self.w_h) ** 2) * torch.exp(-((r3 - R_H3) / self.w_h) ** 2) * c2
            hm = hh * self.h4mask
            e_hh = -self.eps_hb * hm.sum(1)
            if self.helix in ('coop', 'coop2'):
                prev = torch.cat([torch.zeros_like(hm[:, :1]), hm[:, :-1]], 1)
                e_hh = e_hh + self.eps_nuc * (hm * (1 - prev)).sum(1)
            if self.helix == 'coop2':
                e_hh = e_hh - (hm * (self.eps_prop + KT0 * self.lns_bond)).sum(1)
            # strand pairing
            t = torch.zeros_like(xb)
            tv = xb[:, 2:] - xb[:, :-2]
            t[:, 1:-1] = tv / (tv.norm(dim=-1, keepdim=True) + 1e-9)
            ext = torch.zeros(xb.shape[:2], device=x.device)
            ext[:, 1:-1] = torch.sigmoid((theta - THETA_EXT) / 0.08) * self.amask
            tt = torch.einsum('cik,cjk->cij', t, t) ** 2
            w = torch.exp(-((rbb - R_HB) / TT.W_HB) ** 2)
            e_hs = -self.eps_hb * (w * tt * ext[:, :, None] * ext[:, None, :] * self.triu3).sum((1, 2))
        else:
            e_hh = torch.zeros_like(e_bond); e_hs = torch.zeros_like(e_bond)
        tot = e_bond + e_ang + e_dih + e_sc + e_ev + e_bur + e_pack + e_el + e_hh + e_hs
        if parts:
            return dict(total=tot, bond=e_bond, angle=e_ang, dihedral=e_dih, sc=e_sc, ev=e_ev, burial=e_bur,
                        pack=e_pack, elec=e_el, elec_self=e_self, elec_cd=self._e_cd, hb_helix=e_hh, hb_strand=e_hs, n=n)
        return tot


class REMD2(TT.REMD):
    """Replica exchange for two-bead chains (the integrator and exchange are tertiary.REMD's)."""

    def __init__(self, seqs, n_run, temps, mode='coop', dt=0.004, gamma=2.0, seed=0, device='cuda', P1=None,
                 k_helix=None, **kw):
        self.seqs = [np.asarray(s) for s in seqs]
        self.ns, self.nr, self.K = len(seqs), n_run, len(temps)
        self.L = max(len(s) for s in seqs)
        idx1, P1_ = seq_params(self.seqs, self.L, helix=kw.get('helix', 'v23'), k_helix=k_helix)
        P1 = P1_ if P1 is None else P1
        rep = n_run * self.K
        self.idx = np.repeat(idx1, rep, 0)
        self.P1 = P1
        self.model = Model2(self.idx, np.repeat(P1, rep, 0), mode=mode, device=device, **kw)
        self.dev = self.model.dev
        self.C = self.idx.shape[0]
        self.temps = np.asarray(temps, float)
        self.Tc = torch.tensor(np.tile(self.temps, self.ns * n_run), dtype=torch.float32, device=self.dev)
        self.dt, self.gamma = dt, gamma
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        self.rng = np.random.default_rng(seed)
        self.mask3 = self.model.mask[:, :, None].float()
        if VIRTUAL_SC:
            self.mask3[:, self.L:] = 0.0          # side-chain coordinates are not integrated; filled by sync_sc()
        self.x = self._init_coords()
        self.x, _ = TT.minimise(self.model, self.x, iters=600)
        self.sync_sc()
        self.v = torch.randn(self.x.shape, device=self.dev) * (R * self.Tc)[:, None, None].sqrt() * self.mask3
        self.f = torch.zeros_like(self.x)
        self.e = torch.zeros(self.C, device=self.dev)
        self.graph = None
        self.n_swap_try = np.zeros(self.K - 1); self.n_swap_acc = np.zeros(self.K - 1)

    def sync_sc(self):
        if VIRTUAL_SC:
            with torch.no_grad():
                self.x[:, self.L:] = self.model.sc_ideal(self.x[:, :self.L])

    def _init_coords(self):
        xb = TT.REMD._init_coords(self)                       # (C, L, 3), padded slots on a far line
        with torch.no_grad():
            xs = self.model.sc_ideal(xb)
        pad = torch.as_tensor(self.idx < 0, device=self.dev)[:, :, None]
        xs = torch.where(pad, xb + torch.tensor([0.0, 0.5, 0.0], device=self.dev), xs)
        return torch.cat([xb, xs], 1)


def fill_sc(model, x):
    """x (C, 2L, 3) with the side chains put at their (virtual) positions."""
    if not VIRTUAL_SC:
        return x
    with torch.no_grad():
        return torch.cat([x[:, :model.L], model.sc_ideal(x[:, :model.L])], 1)


def place_sc(model, xb):
    """two-bead coordinates from a backbone (side chains at their ideal positions)."""
    with torch.no_grad():
        return torch.cat([xb, model.sc_ideal(xb)], 1)
