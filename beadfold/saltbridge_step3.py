"""Task 15, step 3: task 20's salt-bridge benchmarks in the tertiary model's own energy (CPU, seconds).

A monomer in a packed core is modelled as having n_core non-local neighbours (6, the count at which the cooperative
burial factor is 0.99), all of one oily filler type unless stated. The energy of putting a monomer (or a pair) into
the core is the burial term h_a B(n) plus its contacts e_ab g_a g_b, measured against the same monomers fully exposed
(n = 0, no contacts, energy 0). Everything in kT at 300 K, 150 mM, pH 7.

Benchmarks (task 20, Claude's reading of Hendsch and Tidor 1994 and Waldburger et al. 1995; Lehninger ch. 4):
  A. a buried unpartnered charge should be far worse than a buried partnered pair (per charge);
  B. a buried partnered pair should be worse than an oily isostere pair by about 0-6 kT.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tertiary as TT  # noqa: E402

E = TT.E_TAB / TT.KT0
H = TT.H_TAB / TT.KT0
N_CORE = 6.0
FILLERS = (1, 3, 5, 13)              # oily filler monomers for the core around the tested pair
PAIRS = {'0-8': (0, 8), '2-8': (2, 8), '0-10': (0, 10), '2-10': (2, 10)}
# oily isosteres (same number of side-chain beads, sizes close, charge replaced by apolar): Hendsch-Tidor's comparison
ISO = {0: 13, 2: 3, 8: 3, 10: 3}


def bf(n, mode='coop'):
    if mode == 'coop':
        s0 = 1 / (1 + math.exp(TT.N_HALF / TT.W_BURIAL))
        return (1 / (1 + math.exp(-(n - TT.N_HALF) / TT.W_BURIAL)) - s0) / (1 - s0)
    return min(n / TT.N_FULL, 1.0)


def single(a, filler, mode='coop'):
    """bury a among N_CORE filler neighbours (fillers themselves assumed buried too, g = 1)."""
    g = bf(N_CORE, mode)
    gc = g if mode == 'coop' else 1.0
    return H[a] * g + N_CORE * E[a, filler] * gc * 1.0


def pair(a, b, filler, mode='coop'):
    """bury a and b in contact, each with N_CORE - 1 filler neighbours besides the partner."""
    g = bf(N_CORE, mode)
    gc = g if mode == 'coop' else 1.0
    return (H[a] + H[b]) * g + E[a, b] * gc * gc + (N_CORE - 1) * (E[a, filler] + E[b, filler]) * gc


def main():
    out = dict(n_core=N_CORE, fillers=FILLERS, isosteres=ISO, rows=[])
    for mode in ('coop', 'additive'):
        for name, (a, b) in PAIRS.items():
            for f in FILLERS:
                p = pair(a, b, f, mode)
                ua, ub = single(a, f, mode), single(b, f, mode)
                ia, ib = ISO[a], ISO[b]
                iso = pair(ia, ib, f, mode)
                out['rows'].append(dict(
                    mode=mode, pair=name, filler=f,
                    pair_kT=round(p, 2), per_charge_partnered_kT=round(p / 2, 2),
                    unpartnered_a_kT=round(ua, 2), unpartnered_b_kT=round(ub, 2),
                    two_unpartnered_kT=round(ua + ub, 2), partner_relief_kT=round(ua + ub - p, 2),
                    iso_pair=f'{ia}-{ib}', iso_kT=round(iso, 2), pair_minus_iso_kT=round(p - iso, 2),
                    A_pass=bool((ua + ub - p) > 3.0), B_pass=bool(0.0 <= p - iso <= 6.0)))
    # electrostatic part only of the pair contacts (step 1's sampled pair, water permittivity)
    out['note'] = ('A passes if partnering relieves more than 3 kT of the cost of two unpartnered buried charges; '
                   'B passes if the pair is 0-6 kT worse than its oily isostere pair.')
    path = os.path.join(HERE, 'results', 'step3_saltbridge.json')
    json.dump(out, open(path, 'w'), indent=1)
    for r in out['rows']:
        if r['filler'] == 5:
            print(r)
    print('wrote', path)


if __name__ == '__main__':
    main()
