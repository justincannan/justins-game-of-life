"""Task 15, prototype step 2: the secondary rule (design report 12, section 3). All of it a proposal (Claude's).

Helix: a Zimm-Bragg transfer matrix along the chain, two states per monomer (h, c). Statistical weights:
    c after c: 1;  h after c: sigma * s_i (nucleation);  h after h: s_i;  c after h: 1.
s_i is the monomer's propagation weight, from its beads (below), corrected for charges at i-3 and i-4: like charges
there lower s_i, opposite charges raise it (screened Debye-Hueckel energy at 0.62 nm, the i, i+4 side-chain distance
in a helix, roughly). The correction uses only the neighbour's charge, so the partition function stays exact in O(n)
for the corrected weights (an approximation: the pair energy is credited to the later monomer whenever it is helical,
not only when both are).
Forward-backward on the 2 x 2 matrices gives each monomer's helix probability.

Strand and coil: a strand propensity b_i per monomer from its beads (branched and large apolar side chains favour it;
tiny ones and charged ones do not), raised where apolar and polar alternate (i-1 and i+1 differ from i in oiliness; factor 1 + alt)
and lowered by like charges at i-2 or i+2 (same face of a strand). Of the non-helical probability, the share in strand
is b / (1 + b); the rest is coil. A strand here is only a candidate: it is kept only if the tertiary step pairs it.

Propagation weight from beads (proposal):
  - base 1.0; a side chain of one regular or two beads, unbranched: 1.30 (medium side chains favour helix);
  - branched first bead: 0.85; tiny: 0.45 (glycine-like flexibility); a backbone that cannot donate: 0.05
    (proline-like: it breaks the i -> i+4 H-bond chain);
  - charged side chains: 1.0 before the i-3/i-4 correction.
"""
import math

import numpy as np

import beads as B

SIGMA_ZB = 1e-3         # helix nucleation (Zimm-Bragg sigma), proposal in the range usually quoted for polypeptides
R_HELIX = 0.62          # nm: rough distance between side chains at i, i+4 (and i, i+3) on a helix
R_STRAND = 0.70         # nm: rough distance between side chains at i, i+2 on a strand


def s_base(m):
    mono = B.MONOMERS[m]
    bs = mono['beads']
    if mono.get('nodonor'):
        return 0.05
    if bs[0].size == 'T':
        return 0.45
    if bs[0].branched:
        return 0.85
    if any(b.q0 for b in bs):
        return 1.0
    if len(bs) == 2 or bs[0].size == 'R':
        return 1.30
    return 1.10


def b_base(m):
    """strand propensity (dimensionless, b / (1 + b) of the non-helical share)."""
    bs = B.MONOMERS[m]['beads']
    if B.MONOMERS[m].get('nodonor') or bs[0].size == 'T':
        return 0.15
    oily = sum(B.LADDER[b.level] < 0 for b in bs)
    b = 0.4 + 0.5 * oily + (0.8 if bs[0].branched else 0.0)
    if any(b_.q0 for b_ in bs):
        b *= 0.4
    return b


def _pair_dh(q1, q2, r, T, I):
    """screened charge-charge energy over kT."""
    if q1 == 0 or q2 == 0:
        return 0.0
    return q1 * q2 * B.bjerrum(T) * math.exp(-r / B.debye(T, I)) / r


def weights(seq, T=300.0, I=0.15, pH=7.0):
    q = [B.net_charge(m, pH) for m in seq]
    s = np.array([s_base(m) for m in seq], float)
    for i in range(len(seq)):
        u = 0.0
        for k in (3, 4):
            if i - k >= 0:
                u += _pair_dh(q[i], q[i - k], R_HELIX, T, I)
        s[i] *= math.exp(-u)
    return s, q


def helix_prob(s, sigma=SIGMA_ZB):
    """exact per-monomer helix probability for Zimm-Bragg weights s (forward-backward, rescaled)."""
    n = len(s)
    # state vector (h, c); first monomer: h with weight sigma*s, c with 1
    fw = np.zeros((n, 2))
    sc = np.zeros(n)
    v = np.array([sigma * s[0], 1.0])
    sc[0] = v.sum(); fw[0] = v / sc[0]
    for i in range(1, n):
        h = fw[i - 1, 0] * s[i] + fw[i - 1, 1] * sigma * s[i]
        c = fw[i - 1, 0] + fw[i - 1, 1]
        v = np.array([h, c]); sc[i] = v.sum(); fw[i] = v / sc[i]
    bw = np.zeros((n, 2))
    bw[-1] = 1.0
    for i in range(n - 2, -1, -1):
        # from state at i to state at i+1
        bh = s[i + 1] * bw[i + 1, 0] + bw[i + 1, 1]
        bc = sigma * s[i + 1] * bw[i + 1, 0] + bw[i + 1, 1]
        v = np.array([bh, bc]); bw[i] = v / sc[i + 1]
    p = fw * bw
    return p[:, 0] / p.sum(1)


def zb_infinite(s, sigma=SIGMA_ZB):
    """helix fraction of an infinite homopolymer (Zimm-Bragg's closed form)."""
    return 0.5 + (s - 1) / (2 * math.sqrt((s - 1) ** 2 + 4 * sigma * s))


def strand_share(seq, q, T=300.0, I=0.15):
    n = len(seq)
    oily = [m & 1 for m in seq]
    b = np.array([b_base(m) for m in seq], float)
    for i in range(n):
        alt = sum(1 for j in (i - 1, i + 1) if 0 <= j < n and oily[j] != oily[i])
        b[i] *= 1 + 1.0 * alt          # first try 0.5 failed its own check (alternation below pure 5); raised to 1.0
        u = sum(_pair_dh(q[i], q[j], R_STRAND, T, I) for j in (i - 2, i + 2) if 0 <= j < n)
        b[i] *= math.exp(-u)
    return b / (1 + b)


def secondary(seq, T=300.0, I=0.15, pH=7.0, sigma=SIGMA_ZB):
    """per monomer: probabilities (helix, strand, coil)."""
    s, q = weights(seq, T, I, pH)
    ph = helix_prob(s, sigma)
    fs = strand_share(seq, q, T, I)
    pe = (1 - ph) * fs
    return np.stack([ph, pe, 1 - ph - pe], 1)
