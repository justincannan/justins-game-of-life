"""Task 23, stage 2: target backbones for the design test, built geometrically and relaxed (CPU/GPU, seconds).

Targets (Claude's choices, 25-45 monomers): the two hand designs' intended folds (helix hairpin 32, three-stranded
sheet 25), a three-helix bundle (45), a four-stranded meander sheet (34) and a beta-beta-alpha fold (33).
Geometry: ideal C-alpha helices (radius 0.23 nm, rise 0.15 nm, 100 degrees per monomer), strands as pleated lines
(0.33 nm per monomer, pleat 0.09 nm), neighbouring strands 0.48 nm apart, packed helix axes 1.0 nm apart and 1.0 nm
above a sheet. Loops are placed on arcs and the whole backbone is relaxed with the model's own backbone terms (bonds,
local wells with the target's secondary state, excluded volume) under a weak pull to the built positions.
Writes results/tb_targets.json: {name: {"ss": "HHH...", "x": backbone (L x 3), "hand_seq": [...] or null}}.
"""
import json
import math
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tertiary as TT  # noqa: E402
import twobead as TB  # noqa: E402
import run_step3 as R3  # noqa: E402


def helix(n, base, axis, phase=0.0):
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    e1 = np.cross(axis, [0.0, 0.0, 1.0] if abs(axis[2]) < 0.9 else [1.0, 0.0, 0.0]); e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    t = phase + np.radians(100.0) * np.arange(n)
    return np.asarray(base) + 0.23 * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2) + 0.15 * np.arange(n)[:, None] * axis


def strand(n, start, u, w):
    u = np.asarray(u, float); u /= np.linalg.norm(u)
    k = np.arange(n)
    return np.asarray(start) + 0.33 * k[:, None] * u + 0.09 * ((-1.0) ** k)[:, None] * np.asarray(w, float)


def loop(p, q, m, bulge):
    """m points on an arc from p to q (exclusive), bulging along 'bulge'."""
    t = np.arange(1, m + 1) / (m + 1)
    mid = 0.5 * (p + q) + np.asarray(bulge)
    return ((1 - t) ** 2)[:, None] * p + (2 * t * (1 - t))[:, None] * mid + (t ** 2)[:, None] * q


def build():
    T = {}
    # helix hairpin: 14 + 4 + 14
    h1 = helix(14, [0, 0, 0], [0, 0, 1]); h2 = helix(14, [1.0, 0, 1.95], [0, 0, -1], phase=math.pi)
    T['design_helixhairpin'] = (np.vstack([h1, loop(h1[-1], h2[0], 4, [0, 0, 0.5]), h2]), 'H' * 14 + 'C' * 4 + 'H' * 14,
                                R3.DESIGNS[0][1])
    # three-stranded sheet: 7 + 2 + 7 + 2 + 7
    z = [0, 0, 1.0]
    s1 = strand(7, [0, 0, 0], [1, 0, 0], z); s2 = strand(7, [1.98, 0.48, 0], [-1, 0, 0], z)
    s3 = strand(7, [0, 0.96, 0], [1, 0, 0], z)
    T['design_sheet3'] = (np.vstack([s1, loop(s1[-1], s2[0], 2, [0.3, 0, 0]), s2, loop(s2[-1], s3[0], 2, [-0.3, 0, 0]), s3]),
                          'EEEEEEECCEEEEEEECCEEEEEEE', R3.DESIGNS[1][1])
    # three-helix bundle: 13 + 3 + 13 + 3 + 13
    a = helix(13, [0, 0, 0], [0, 0, 1]); b = helix(13, [1.0, 0, 1.8], [0, 0, -1]); c = helix(13, [0.5, 0.866, 0], [0, 0, 1])
    T['bundle3'] = (np.vstack([a, loop(a[-1], b[0], 3, [0, -0.3, 0.4]), b, loop(b[-1], c[0], 3, [0.3, 0, -0.4]), c]),
                    'H' * 13 + 'CCC' + 'H' * 13 + 'CCC' + 'H' * 13, None)
    # four-stranded meander: 7 + 2 + 7 + 2 + 7 + 2 + 7
    st = [strand(7, [0 if k % 2 == 0 else 1.98, 0.48 * k, 0], [1 if k % 2 == 0 else -1, 0, 0], z) for k in range(4)]
    parts = []
    for k in range(4):
        parts.append(st[k])
        if k < 3:
            parts.append(loop(st[k][-1], st[k + 1][0], 2, [0.3 if k % 2 == 0 else -0.3, 0, 0]))
    T['sheet4'] = (np.vstack(parts), 'EEEEEEECC' * 3 + 'EEEEEEE', None)
    # beta-beta-alpha: 7 + 2 + 7 + 3 + 14
    s1 = strand(7, [0, 0, 0], [1, 0, 0], z); s2 = strand(7, [1.98, 0.48, 0], [-1, 0, 0], z)
    hx = helix(14, [0.05, 0.24, 1.0], [1, 0, 0])
    T['bba'] = (np.vstack([s1, loop(s1[-1], s2[0], 2, [0.3, 0, 0]), s2, loop(s2[-1], hx[0], 3, [-0.4, 0, 0.2]), hx]),
                'EEEEEEECCEEEEEEECCC' + 'H' * 14, None)
    return T


class Pulled:
    def __init__(self, base, x0, k):
        self.base, self.x0, self.k, self.mask = base, x0, k, base.mask

    def energy(self, x, parts=False):
        L = self.base.L
        return self.base.energy(x) + self.k * (x[:, :L] - self.x0).pow(2).sum((1, 2))


def relax(xb, ss, dev='cuda'):
    L = len(ss)
    seq = [11] * L                                   # a small neutral monomer, only to give side chains a size
    P = np.array([[0.98, 0.01, 0.01] if c == 'H' else [0.01, 0.98, 0.01] if c == 'E' else [0.05, 0.05, 0.9] for c in ss])
    m = TB.Model2(np.array([seq]), P[None], device=dev, charges=False)
    m.eab = torch.zeros_like(m.eab); m.h = torch.zeros_like(m.h)
    x0 = torch.tensor(xb[None], dtype=torch.float32, device=dev)
    x = TB.place_sc(m, x0)
    for k in (2000.0, 500.0, 50.0):
        x, e = TT.minimise(Pulled(m, x0, k), x, iters=1500)
    return x[0, :L].cpu().numpy(), float(e[0])


def go_natives(path_in, path_out, names=('design_helixhairpin', 'design_sheet3', 'bundle3', 'sheet4', 'bba'),
               seqs=None):
    """two-bead natives (backbone + ideal side chains) for the Go instrument check; seqs: {name: seq} or hand seqs."""
    T = json.load(open(path_in))
    out = {}
    for n in names:
        seq = (seqs or {}).get(n) or T[n]['hand_seq'] or [11] * len(T[n]['ss'])
        xb = np.array(T[n]['x'], float)
        idx, P = TB.seq_params([seq], len(seq))
        m = TB.Model2(idx, P, device='cpu')
        x = TB.place_sc(m, torch.tensor(xb[None], dtype=torch.float32))[0].numpy()
        out[n] = dict(seq=list(map(int, seq)), x=x.round(4).tolist())
    json.dump(out, open(path_out, 'w'))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--go':
        go_natives(os.path.join(HERE, 'results', 'tb_targets.json'), sys.argv[2],
                   seqs=json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None)
        return
    out = {}
    for name, (xb, ss, hand) in build().items():
        assert len(xb) == len(ss), (name, len(xb), len(ss))
        xr, e = relax(xb, ss)
        bl = np.linalg.norm(np.diff(xr, axis=0), axis=1)
        rms = float(np.sqrt(((xr - xr.mean(0)) - (xb - xb.mean(0))) ** 2).sum(1).mean())
        print(name, len(ss), 'bond %.3f-%.3f' % (bl.min(), bl.max()), 'moved %.2f nm' % rms, 'E %.1f kT' % (e / TB.KT0))
        out[name] = dict(ss=ss, x=xr.round(4).tolist(), hand_seq=list(map(int, hand)) if hand is not None else None)
    json.dump(out, open(os.path.join(HERE, 'results', 'tb_targets.json'), 'w'))


if __name__ == '__main__':
    main()
