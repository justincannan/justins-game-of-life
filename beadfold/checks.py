"""Task 15, steps 1 and 2: compute the table over the calibrated range, fit it, and run the checks. Writes
results/steps12.json and figures to OUT (default ../comms/from_gpu). Usage: python checks.py [OUT]"""
import json
import math
import os
import sys
import time

import numpy as np

import beads as B
import secondary as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'comms', 'from_gpu')
RES = os.path.join(HERE, 'results')
os.makedirs(RES, exist_ok=True)
TS = [280.0, 290.0, 300.0, 310.0, 320.0, 330.0, 340.0]
IS = [0.005, 0.02, 0.05, 0.15, 0.5, 1.0]
NSAMP = 60000
kT300 = B.R_GAS * 300
out = {}

# ---------------- step 1: tables over (T, I), then fit ----------------
t0 = time.time()
samples = {}
grid = np.zeros((len(TS), len(IS), 16, 16))
for i, T in enumerate(TS):
    for j, I in enumerate(IS):
        grid[i, j] = B.table(T, I, n=NSAMP, samples=samples)
t_table = time.time() - t0
H = np.array([[B.burial(m, T) for m in range(16)] for T in TS])
# a second, independent sampling at 300 K / 0.15 M for the sampling error
E300b = B.table(300.0, 0.15, n=NSAMP, samples={(a, b): B.PairSamples(a, b, n=NSAMP, seed=99000 + 17 * a + b)
                                                for a in range(16) for b in range(a, 16)})
i300, j150 = TS.index(300.0), IS.index(0.15)
E300 = grid[i300, j150]
samp_err = float(np.abs(E300 - E300b).max() / kT300)

# fit: e(T, I) = c . [1, t, t^2, x, x^2, t x], t = (T - 300)/20, x = log10 I
tt, xx = np.meshgrid([(T - 300) / 20 for T in TS], [math.log10(I) for I in IS], indexing='ij')
Xf = np.stack([np.ones_like(tt), tt, tt ** 2, xx, xx ** 2, tt * xx], -1).reshape(-1, 6)
coef = np.zeros((16, 16, 6))
fit_err = 0.0
for a in range(16):
    for b in range(a, 16):
        y = grid[:, :, a, b].reshape(-1)
        c, *_ = np.linalg.lstsq(Xf, y, rcond=None)
        coef[a, b] = coef[b, a] = c
        fit_err = max(fit_err, float(np.abs(Xf @ c - y).max()))
hcoef = [np.polyfit([(T - 300) / 20 for T in TS], H[:, m], 2).tolist() for m in range(16)]

# readouts at 300 K, 150 mM
E = E300 / kT300
h = H[TS.index(300.0)] / kT300
odd = [m for m in range(16) if m & 1]
even = [m for m in range(16) if not m & 1]
z = 6.0   # contacts of a fully buried monomer (proposal, for the effective-contact readout only)
eff = E + (h[:, None] + h[None, :]) / z
comp_rank = {}
for m in range(16):
    order = list(np.argsort(E[m]))
    comp_rank[m] = order.index(m ^ 8) + 1
rows = E.copy()
dmin = min(float(np.linalg.norm(np.r_[rows[a], h[a]] - np.r_[rows[b], h[b]])) for a in range(16) for b in range(a + 1, 16))
odd_pairs = [E[a, b] for a in odd for b in odd if a <= b]
ratio = float(np.mean(np.abs(h[odd])) / ((z / 2) * np.mean(np.abs(odd_pairs))))
# screening: electrostatic part of the salt bridges against I, at 300 K
scr = {}
for a, b in ((0, 8), (2, 8), (2, 10)):
    ps = samples[(a, b)]
    scr[f'{a}-{b}'] = [ps.energy(300.0, I, parts=True)[2] / kT300 for I in [0.001] + IS]
lD = {I: B.debye(298.15, I) for I in IS}
# pH: the titratable pairs at pH 5, 7, 9
phs = {}
for pH in (5.0, 7.0, 9.0):
    phs[pH] = {f'{a}-{b}': samples[(a, b)].energy(300.0, 0.15, pH=pH) / kT300 for a, b in ((0, 8), (2, 10), (0, 10))}
out['step1'] = dict(
    seconds_tables=round(t_table, 1), samples_per_pair=NSAMP, conditions=dict(T=TS, I=IS, pH=7.0),
    sampling_error_kT_max=round(samp_err, 3), fit_error_kJ_max=round(fit_err, 3),
    bjerrum_nm_298=round(B.bjerrum(298.15), 3), debye_nm_298={str(k): round(v, 3) for k, v in lD.items()},
    e_kT_300_150mM=np.round(E, 2).tolist(), h_kT_300=np.round(h, 2).tolist(),
    net_charge_pH7=[round(B.net_charge(m), 2) for m in range(16)],
    clash_share=np.round(B.clash_table(samples), 3).tolist(),
    effective_contact_kT=np.round(eff, 2).tolist(),
    complement_rank_in_row=comp_rank, min_row_distance_kT=round(dmin, 3),
    burial_to_pair_ratio_odd=round(ratio, 2),
    covalent_ratio=dict(CC_bond_kT=round(350 / kT300, 1),
                        strongest_contact_kT=round(float(-eff.min()), 2)),
    screening_electrostatic_kT={'I': [0.001] + IS, **{k: np.round(v, 3).tolist() for k, v in scr.items()}},
    pH_pairs_kT={str(k): {kk: round(vv, 2) for kk, vv in v.items()} for k, v in phs.items()},
    h_kT_by_T={str(T): np.round(H[i] / (B.R_GAS * T), 2).tolist() for i, T in enumerate(TS)},
    coef_e=np.round(coef, 5).tolist(), coef_h=hcoef,
)

# ---------------- step 2: the secondary rule ----------------
s2 = {}
# (a) homopolymers against Zimm-Bragg's infinite-chain formula (interior of a 400-mer)
homo = {}
for m in range(16):
    s, _ = S.weights([m] * 400)
    p = S.helix_prob(s)
    homo[m] = dict(s=round(float(s[200]), 3), interior=round(float(p[150:250].mean()), 4),
                   zb=round(S.zb_infinite(float(s[200])), 4))
s2['homopolymer'] = homo
# (b) cooperativity: helix fraction against length for s = 1.3 (as monomer 7 alone would give)
lens = [8, 12, 16, 24, 32, 48, 64, 100, 200]
s2['length'] = {L: round(float(S.helix_prob(np.full(L, 1.3)).mean()), 4) for L in lens}
s2['sharpness'] = {f'{sv:.2f}': round(float(S.helix_prob(np.full(100, sv)).mean()), 4)
                   for sv in (0.8, 0.9, 1.0, 1.05, 1.1, 1.2, 1.3, 1.5)}
# (c) charge patterns in a helix-forming host (monomer 7, s 1.3), length 24
host = [7] * 24


def frac(seq, I=0.15, pH=7.0):
    return round(float(S.secondary(seq, I=I, pH=pH)[:, 0].mean()), 4)


pat = {}
pat['host 7x24'] = frac(host)
ek = [0, 0, 0, 0, 8, 8, 8, 8] * 3          # acid then base, i and i+4 opposite
pat['(0000 8888)x3'] = frac(ek)
pat['0 x24 (like charges)'] = frac([0] * 24)
pat['8 x24 (like charges)'] = frac([8] * 24)
alt = []
for k in range(24):
    alt.append(0 if k % 8 == 0 else (8 if k % 8 == 4 else 7))
pat['host with 0 at i, 8 at i+4'] = frac(alt)
same = [0 if k % 4 == 0 else 7 for k in range(24)]
pat['host with 0 every 4th (like at i, i+4)'] = frac(same)
pat['salt: (0000 8888)x3 at 5 mM'] = frac(ek, I=0.005)
pat['salt: (0000 8888)x3 at 1 M'] = frac(ek, I=1.0)
pat['salt: 0 x24 at 5 mM'] = frac([0] * 24, I=0.005)
pat['salt: 0 x24 at 1 M'] = frac([0] * 24, I=1.0)
pat['pH 3: 0 x24 (acid neutralised)'] = frac([0] * 24, pH=3.0)
pat['host with a 15 in the middle'] = frac(host[:12] + [15] + host[13:])
s2['charge_patterns'] = pat
# strand: alternation
st = {}
for name, seq in {'5 x24': [5] * 24, '(5 4)x12 alternating': [5, 4] * 12, '(5 5 4 4)x6': [5, 5, 4, 4] * 6,
                  '(3 12)x12 alternating': [3, 12] * 12, '9 x24 tiny': [9] * 24}.items():
    p = S.secondary(seq)
    st[name] = dict(helix=round(float(p[:, 0].mean()), 3), strand=round(float(p[:, 1].mean()), 3),
                    coil=round(float(p[:, 2].mean()), 3))
s2['strand_patterns'] = st
# (d) random sequences: helix probability against the monomer's own s, rank correlation
rng = np.random.default_rng(5)
xs, ys = [], []
t0 = time.time()
nseq = 2000
for _ in range(nseq):
    seq = list(rng.integers(0, 16, 32))
    p = S.secondary(seq)
    xs += [S.s_base(m) for m in seq]
    ys += list(p[:, 0])
dt = (time.time() - t0) / nseq
rx = np.argsort(np.argsort(xs)); ry = np.argsort(np.argsort(ys))
s2['random_32mers'] = dict(n=nseq, spearman_helix_vs_s=round(float(np.corrcoef(rx, ry)[0, 1]), 3),
                           mean_helix=round(float(np.mean(ys)), 3),
                           seconds_per_sequence_python=round(dt, 6))
s2['s_base'] = {m: S.s_base(m) for m in range(16)}
s2['b_base'] = {m: round(S.b_base(m), 3) for m in range(16)}
out['step2'] = s2
json.dump(out, open(os.path.join(RES, 'steps12.json'), 'w'), indent=1)

# ---------------- figures ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
lim = np.abs(E).max()
im = ax[0].imshow(E, cmap='RdBu', vmin=-lim, vmax=lim)
ax[0].set_title('e_ab (kT), 300 K, 150 mM, pH 7\n(blue attracts)')
ax[0].set_xticks(range(16)); ax[0].set_yticks(range(16)); plt.colorbar(im, ax=ax[0], shrink=0.8)
for m in range(16):
    ax[0].add_patch(plt.Rectangle(((m ^ 8) - 0.5, m - 0.5), 1, 1, fill=False, ec='k', lw=1.2))
ax[0].text(0, 17.3, 'boxes: complement pairs m, m^8', fontsize=8)
ax[1].bar(range(16), h, color=['tab:orange' if m & 1 else 'tab:blue' for m in range(16)])
ax[1].set_title('burial h_a (kT, 300 K): orange odd, blue even'); ax[1].set_xticks(range(16))
ax[1].axhline(0, color='k', lw=0.5)
Ix = [0.001] + IS
for k, v in scr.items():
    ax[2].semilogx(Ix, v, 'o-', label=k)
ax[2].axvline(0.15, color='gray', ls=':')
ax[2].set_xlabel('ionic strength (M)'); ax[2].set_ylabel('electrostatic part of e (kT)')
ax[2].set_title('screening of the charged pairs'); ax[2].legend()
plt.tight_layout(); plt.savefig(os.path.join(OUT, '15_step1_table.png'), dpi=110); plt.close()

fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
ms = sorted(homo)
ax[0].plot([homo[m]['zb'] for m in ms], [homo[m]['interior'] for m in ms], 'o')
ax[0].plot([0, 1], [0, 1], 'k:', lw=0.8)
ax[0].set_xlabel("Zimm-Bragg closed form"); ax[0].set_ylabel('transfer matrix, 400-mer interior')
ax[0].set_title('homopolymers of each monomer')
ax[1].semilogx(lens, [s2['length'][L] for L in lens], 'o-')
ax[1].set_xlabel('chain length'); ax[1].set_ylabel('helix fraction'); ax[1].set_title('s = 1.3, sigma = 1e-3')
names = list(pat)
ax[2].barh(range(len(names)), [pat[k] for k in names]); ax[2].set_yticks(range(len(names))); ax[2].set_yticklabels(names, fontsize=7)
ax[2].set_xlabel('helix fraction'); ax[2].set_title('charge patterns (24-mers)')
plt.tight_layout(); plt.savefig(os.path.join(OUT, '15_step2_secondary.png'), dpi=110); plt.close()
print(json.dumps({k: v for k, v in out['step1'].items() if not k.startswith('coef') and k not in ('e_kT_300_150mM', 'clash_share', 'effective_contact_kT', 'h_kT_by_T')}, indent=1))
print(json.dumps(out['step2'], indent=1))
