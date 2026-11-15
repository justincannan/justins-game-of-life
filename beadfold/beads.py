"""Task 15, prototype step 1: beads, and the 16 x 16 contact table computed from them (design report 12, section 1).

Everything here is a proposal (Claude's) built on Justin's approved choices (report 12, section 9, all six approved):
the monomer assignment keeps the page's two rules (odd = oily; m pairs with m ^ 8), beads are Martini-style
(classes Q, P, N, C with levels; sizes regular, small, tiny; donor/acceptor marks), ions enter through ionic strength.
No number here is set per monomer pair: the table e_ab is computed from the beads.

Units: kJ/mol, nm, K, mol/L.

What a contact means here. Two monomers' centres (their backbone beads) are placed at a distance r drawn from a
shell (0.45-0.90 nm, weight r^2); each side chain points in a random direction. Only configurations in which the side
chains touch (closest side-chain bead pair within 1.3 of its contact diameter). Of those, the share c_ab that clash
(any bead pair closer than 0.85 of its diameter) measures how badly the two side chains pack; the rest give the
attraction. The contact free energy is
    e_ab(T, I) = -kT ln < exp(-U / kT) >_touch, no clash  +  kT [ -ln(1 - c_ab) + ln(1 - mean c) ]
the second part being packing relative to the average pair (so it does not shift the table as a whole; the
tertiary chain has its own excluded volume). Large with large packs worse than large with small: size
complementarity is a readout, not a setting. So clashes (large with large) cost, and pairs that
pack (large with small) can win: size complementarity is a readout, not a setting.
U sums, over bead pairs across the two monomers:
  - Lennard-Jones 12-6 between side-chain beads, depth from a mixing rule on the polarity ladder (like attracts like);
  - a donor-acceptor extra well (H-bond-like);
  - screened charges (Debye-Hueckel), with the Bjerrum length and Debye length computed at T and I;
  - backbone beads only exclude volume (repulsive WCA) from the other monomer's side chain. Backbone-backbone
    H-bonds belong to the secondary and tertiary steps, not to this table.
The one-body burial term h_a (each side-chain bead's water -> oil transfer free energy, scaled by size) is separate.
"""
import math

import numpy as np

R_GAS = 8.314462618e-3          # kJ/mol/K
TREF = 298.15

# ---- bead types: the polarity ladder (proposal: Martini's shape, our numbers) ----------------------------------
# Water -> oil transfer free energy at 298 K, kJ/mol (negative: prefers oil). One ladder, monotone, from charged to
# most apolar. Martini 3 calibrates its levels on octanol/water and hexadecane/water partitioning (Souza et al. 2021);
# we take the ladder's shape (charged >> polar > intermediate > apolar), not its values.
LADDER = {'Q': 18.0, 'P5': 8.0, 'P4': 6.0, 'P3': 4.5, 'P2': 3.0, 'P1': 1.5,
          'N2': 0.0, 'N1': -1.5, 'C5': -3.0, 'C4': -4.0, 'C3': -5.0, 'C2': -6.0, 'C1': -7.0}
# (Scale check: the largest apolar monomer, two C1 beads, then buries at about -14 kJ/mol, the order of the largest
#  measured side-chain transfer free energies; a first try at twice this gave -30 and was halved.)
LMAX, LMIN = max(LADDER.values()), min(LADDER.values())
SIGMA = {'R': 0.47, 'S': 0.41, 'T': 0.34}        # Martini 3's bead diameters for regular, small, tiny (nm)
SIZEF = {'R': 1.0, 'S': 0.75, 'T': 0.5}          # surface share of a bead by size (burial and well depth scale)
ARM = {'R': 0.27, 'S': 0.24, 'T': 0.20}          # distance of the first side-chain bead from the backbone bead (nm)
EPS0 = 2.0       # pairwise mixing well between like beads (kJ/mol), before size scaling: proposal
KAPPA = 0.75     # how fast the well falls with polarity difference: proposal
EPS_HB = 6.0     # extra donor-acceptor well (kJ/mol): proposal, aims at the 1-2 kT target for one H-bond contact
DCP_APOLAR = 0.015   # transfer heat capacity per unit transfer free energy for apolar beads (1/K): proposal, order of
                     # magnitude of small apolar solutes (not re-checked); gives the hydrophobic effect its T-dependence


class Bead:
    def __init__(self, level, size, q=0, pka=None, hb='', branched=False):
        self.level, self.size, self.q0, self.pka, self.hb, self.branched = level, size, q, pka, hb, branched

    def polarity(self):
        return (LADDER[self.level] - LMIN) / (LMAX - LMIN)

    def charge(self, pH=7.0):
        """mean charge at pH: fraction charged = 1 / (1 + 10^(+-(pH - pKa)))"""
        if self.q0 == 0 or self.pka is None:
            return float(self.q0)
        if self.q0 < 0:   # an acid: charged above its pKa
            return self.q0 / (1 + 10 ** (self.pka - pH))
        return self.q0 / (1 + 10 ** (pH - self.pka))

    def dg_transfer(self, T):
        """water -> oil transfer free energy of this bead at T (kJ/mol), scaled by its size."""
        g = LADDER[self.level] * SIZEF[self.size]
        if g >= 0:
            return g
        # apolar: entropy-driven at 298 K (dH = 0 there), with a negative transfer dCp, so the hydrophobic
        # effect strengthens with T over the calibrated range (proposal; the standard liquid-hydrocarbon picture)
        dcp = DCP_APOLAR * g                       # kJ/mol/K, negative
        dS = -g / TREF
        return dcp * (T - TREF) - T * (dS + dcp * math.log(T / TREF))


BACKBONE = Bead('P3', 'R', hb='da')               # the same for all 16: donor + acceptor, which lets helices form

# ---- the 16 monomers (proposal; keeps odd = oily and m with m ^ 8 as the complement) ---------------------------
# Odd: apolar or intermediate, complement pairs size-complementary (large with small).
# Even: polar or charged; 0-8 and 2-10 opposite charges (one titratable in each pair), 4-12 and 6-14 donor-acceptor.
# Extra marks used by the secondary rule: 'nodonor' (the backbone cannot donate: a proline-like helix breaker).
MONOMERS = {
    0:  dict(beads=[Bead('Q', 'S', q=-1, pka=4.0)]),                                  # titratable acid
    1:  dict(beads=[Bead('C1', 'R'), Bead('C1', 'R')]),                               # large, most apolar
    2:  dict(beads=[Bead('P2', 'S'), Bead('Q', 'S', q=-1)]),                          # acid, fixed charge, longer
    3:  dict(beads=[Bead('C2', 'R', branched=True), Bead('C3', 'S')]),                # large, branched
    4:  dict(beads=[Bead('P5', 'S', hb='d')]),                                        # small polar donor
    5:  dict(beads=[Bead('C2', 'R', branched=True)]),                                 # medium, branched (strand-former)
    6:  dict(beads=[Bead('P3', 'S'), Bead('P4', 'R', hb='d')]),                       # longer polar donor
    7:  dict(beads=[Bead('C1', 'R'), Bead('N1', 'R', hb='a')]),                       # large, weakly polar end
    8:  dict(beads=[Bead('C3', 'S'), Bead('Q', 'R', q=+1)]),                          # base, fixed charge, long
    9:  dict(beads=[Bead('C4', 'T')]),                                                # tiny apolar
    10: dict(beads=[Bead('P2', 'S'), Bead('Q', 'S', q=+1, pka=6.5)]),                 # titratable base
    11: dict(beads=[Bead('N2', 'S', hb='a')]),                                        # small intermediate
    12: dict(beads=[Bead('P4', 'R', hb='a')]),                                        # polar acceptor
    13: dict(beads=[Bead('C3', 'S')]),                                                # small apolar
    14: dict(beads=[Bead('P2', 'S', hb='a')]),                                        # small polar acceptor
    15: dict(beads=[Bead('N1', 'T')], nodonor=True),                                  # tiny, ring-closed backbone
}
NM = 16


def eps_water(T):
    """relative permittivity of water (Malmberg-Maryott fit, t in deg C)."""
    t = T - 273.15
    return 87.740 - 0.40008 * t + 9.398e-4 * t * t - 1.410e-6 * t ** 3


def bjerrum(T):
    """l_B = e^2 / (4 pi eps0 eps_r k T), nm."""
    return 1.67101e-5 / (eps_water(T) * T) * 1e9


def debye(T, I):
    """lambda_D for a 1:1 salt, nm: 0.304 / sqrt(I) at 25 deg C, scaled with sqrt(eps_r T)."""
    return 0.304 / math.sqrt(I) * math.sqrt(eps_water(T) * T / (eps_water(TREF) * TREF))


def burial(m, T):
    """h_a: free energy of burying monomer m's side chain completely (water -> oil), kJ/mol."""
    return sum(b.dg_transfer(T) for b in MONOMERS[m]['beads'])


def net_charge(m, pH=7.0):
    return sum(b.charge(pH) for b in MONOMERS[m]['beads'])


def _rand_dirs(rng, n):
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def _positions(m, centre, rng):
    """side-chain bead positions for monomer m around backbone centres (n, 3)."""
    n = len(centre)
    beads = MONOMERS[m]['beads']
    u = _rand_dirs(rng, n)
    pos = [centre + ARM[beads[0].size] * u]
    for b in beads[1:]:
        w = u + 0.7 * _rand_dirs(rng, n)            # a second bead roughly along the first's direction (about 35 deg)
        w /= np.linalg.norm(w, axis=1, keepdims=True)
        pos.append(pos[-1] + 0.5 * (SIGMA[beads[0].size] + SIGMA[b.size]) * 0.75 * w)
    return pos


def _lj(r, sig, eps):
    x = (sig / r) ** 6
    return 4 * eps * (x * x - x)


def _wca(r, sig, eps=1.0):
    rc = sig * 2 ** (1 / 6)
    return np.where(r < rc, _lj(r, sig, eps) + eps, 0.0)


def pair_eps(b1, b2):
    e = EPS0 * (1 - KAPPA * abs(b1.polarity() - b2.polarity())) * math.sqrt(SIZEF[b1.size] * SIZEF[b2.size])
    if ('d' in b1.hb and 'a' in b2.hb) or ('a' in b1.hb and 'd' in b2.hb):
        e += EPS_HB
    return e


class PairSamples:
    """Geometry sampled once per monomer pair (common random numbers across T and I)."""

    def __init__(self, a, b, n=40000, seed=0, shell=(0.45, 0.90)):
        rng = np.random.default_rng(seed)
        r0, r1 = shell
        r = (r0 ** 3 + rng.random(n) * (r1 ** 3 - r0 ** 3)) ** (1 / 3)
        ca = np.zeros((n, 3))
        cb = _rand_dirs(rng, n) * r[:, None]
        pa, pb = _positions(a, ca, rng), _positions(b, cb, rng)
        Ba, Bb = MONOMERS[a]['beads'], MONOMERS[b]['beads']
        self.u_short = np.zeros(n)                 # LJ + H-bond + steric, independent of T and I
        self.dh = []                               # (distance array, bead i, bead j) for charged pairs
        touch = np.zeros(n, bool)
        clash = np.zeros(n, bool)
        for i, bi in enumerate(Ba):
            for j, bj in enumerate(Bb):
                d = np.linalg.norm(pa[i] - pb[j], axis=1)
                touch |= d < 1.3 * 0.5 * (SIGMA[bi.size] + SIGMA[bj.size])
                clash |= d < 0.85 * 0.5 * (SIGMA[bi.size] + SIGMA[bj.size])
                self.u_short += _lj(d, 0.5 * (SIGMA[bi.size] + SIGMA[bj.size]), pair_eps(bi, bj))
                if bi.q0 and bj.q0:
                    self.dh.append((d, bi, bj))
        for i, bi in enumerate(Ba):                # backbone of b against a's side chain, and the reverse
            d = np.linalg.norm(pa[i] - cb, axis=1)
            clash |= d < 0.85 * 0.5 * (SIGMA[bi.size] + SIGMA['R'])
            self.u_short += _wca(d, 0.5 * (SIGMA[bi.size] + SIGMA['R']))
        for j, bj in enumerate(Bb):
            d = np.linalg.norm(pb[j] - ca, axis=1)
            clash |= d < 0.85 * 0.5 * (SIGMA[bj.size] + SIGMA['R'])
            self.u_short += _wca(d, 0.5 * (SIGMA[bj.size] + SIGMA['R']))
        self.clash = float(clash[touch].mean())
        keep = touch & ~clash
        self.u_short = self.u_short[keep]
        self.dh = [(d[keep], bi, bj) for d, bi, bj in self.dh]
        self.n_used = int(keep.sum())

    def energy(self, T, I, pH=7.0, parts=False):
        kT = R_GAS * T
        lb, ld = bjerrum(T), debye(T, I)
        u_el = np.zeros_like(self.u_short)
        for d, bi, bj in self.dh:
            dd = np.maximum(d, 0.3)
            u_el += bi.charge(pH) * bj.charge(pH) * lb * kT * np.exp(-dd / ld) / dd
        u = self.u_short + u_el
        x = -u / kT
        mx = x.max()
        e = -kT * (mx + math.log(np.mean(np.exp(x - mx))))
        if not parts:
            return e
        xs = -self.u_short / kT
        ms = xs.max()
        es = -kT * (ms + math.log(np.mean(np.exp(xs - ms))))
        return e, es, e - es


def table(T, I, pH=7.0, n=40000, samples=None, packing=True):
    """16 x 16 contact free energies e_ab (kJ/mol) at T, I, pH; samples: a dict reused across conditions."""
    E = np.zeros((NM, NM))
    C = np.zeros((NM, NM))
    for a in range(NM):
        for b in range(a, NM):
            key = (a, b)
            if samples is not None and key in samples:
                ps = samples[key]
            else:
                ps = PairSamples(a, b, n=n, seed=1000 + 17 * a + b)
                if samples is not None:
                    samples[key] = ps
            E[a, b] = E[b, a] = ps.energy(T, I, pH)
            C[a, b] = C[b, a] = ps.clash
    if packing:
        cbar = C[np.triu_indices(NM)].mean()
        E = E + R_GAS * T * (-np.log(1 - C) + math.log(1 - cbar))
    return E


def clash_table(samples):
    C = np.zeros((NM, NM))
    for (a, b), ps in samples.items():
        C[a, b] = C[b, a] = ps.clash
    return C
