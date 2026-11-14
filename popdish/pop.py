# Population dish prototype: each square holds counts of active (A) and inactive (I) cells, and sugar (n).
# Every event is drawn at random from the counts, so chance comes from the real numbers of cells.
# Axes: n0 = sugar laid in the agar; soft = agar softness (how readily active cells move; on hard agar they move
# only where the local film made by cells and sugar is thick, as in Matsushita's lubrication term).
import numpy as np, sys, json
from PIL import Image
rng = np.random.default_rng(int(sys.argv[4]) if len(sys.argv) > 4 else 1)
def run(n0, soft, T=4000, L=300, K=100, out=None):
    yy, xx = np.mgrid[0:L, 0:L]; c = (L - 1) / 2; plate = (xx - c) ** 2 + (yy - c) ** 2 <= (0.48 * L) ** 2
    n = np.where(plate, n0, 0.0); A = np.zeros((L, L), np.int64); I = np.zeros((L, L), np.int64)
    A[int(c)-2:int(c)+3, int(c)-2:int(c)+3] = 20
    Dn, grow, use, Kn = 0.2, 0.05, 1.0, 1.0          # sugar diffusion, max division chance, sugar per division, half-saturation
    a0, n1, b1 = 0.02, 0.5, 30.0                      # going still: likelier where sugar is low and cells are many
    def lap(f): return np.roll(f,1,0)+np.roll(f,-1,0)+np.roll(f,1,1)+np.roll(f,-1,1)-4*f
    for t in range(T):
        # sugar spreads, not through the rim
        nn = n + Dn * 0.25 * lap(n) * 1.0; n = np.where(plate, nn, 0.0)
        tot = A + I; room = np.clip(1 - tot / K, 0, 1)
        p = grow * n / (n + Kn) * room
        b = rng.binomial(A, np.clip(p, 0, 1)); b = np.minimum(b, (n / use).astype(np.int64)); A += b; n -= b * use
        q = a0 / (1 + n / n1)                          # a cell goes still more readily where sugar is low
        s = rng.binomial(A, np.clip(q, 0, 1)); A -= s; I += s
        # movement: each active cell may step to a random neighbour; on hard agar only where the film is thick
        # movement: on soft agar cells move freely; on hard agar only where cells and sugar are both plentiful
        m = np.clip(soft * 0.5 + (1 - soft) * 0.5 * (A / K) * (n / (n0 + 1e-9)) * 4, 0, 1)
        mv = rng.binomial(A, m); A -= mv
        parts = [rng.binomial(mv, 1/4)]; rest = mv - parts[0]
        parts.append(rng.binomial(rest, 1/3)); rest -= parts[1]; parts.append(rng.binomial(rest, 1/2)); parts.append(rest - parts[2])
        for d, (dy, dx) in zip(parts, [(1,0),(-1,0),(0,1),(0,-1)]):
            moved = np.roll(np.roll(d, dy, 0), dx, 1)
            A += np.where(plate, moved, 0); back = np.roll(np.roll(np.where(plate, 0, moved), -dy, 0), -dx, 1); A += back
    if out:
        tot = A + I; v = np.clip(np.log1p(tot) / np.log1p(K), 0, 1)
        rgb = np.zeros((L, L, 3), np.uint8); rgb[..., 0] = 18 + 217 * v; rgb[..., 1] = 22 + 178 * v; rgb[..., 2] = 30 + 90 * v
        rgb[~plate] = (34, 33, 40); Image.fromarray(rgb).save(out)
    occ = (A + I) > 0
    return {'n0': n0, 'soft': soft, 'cells': int((A + I).sum()), 'active': int(A.sum()), 'covered': round(float(occ[plate].mean()), 3)}
if __name__ == '__main__':
    n0, soft, T = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
    print(json.dumps(run(n0, soft, T, out=f'/home/claude/popdish/p_{n0}_{soft}.png')))
