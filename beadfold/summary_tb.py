"""Task 23: summarise the two-bead analyses into results/tb_summary.json, side by side with step 3 (one bead) and
task 02, and draw the figures comms/from_gpu/23_*.png (PIL).

Usage: python summary_tb.py [--dir DIR] [--fig OUTDIR]
Reads DIR/analysis_<set>.json (analyse_tb.py) for the sets present.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import summary_step3 as S3  # noqa: E402
import twobead as TB  # noqa: E402

SETS = ['page', 'random32', 'additive', 'designs_final', 'go', 'hand_real', 'walk', 'neutral']
COL = S3.COL if hasattr(S3, 'COL') else [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189),
                                          (140, 86, 75)]


def odd_pairs_tb(rows, min_sep=4):
    """step 3's odd-pair enrichment, on the two-bead cores (buried flags from analyse_tb)."""
    return S3.odd_pairs(rows, min_sep)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23')
    ap.add_argument('--fig', default=os.path.join(HERE, '..', 'comms', 'from_gpu'))
    a = ap.parse_args()
    data = {}
    for s in SETS:
        p = os.path.join(a.dir, f'analysis_{s}.json')
        if os.path.exists(p):
            data[s] = json.load(open(p))
    summ = {s: S3.set_summary(rows) for s, rows in data.items()}
    for s, rows in data.items():
        summ[s]['s_per_run'] = S3.stats([r.get('s_per_run') for r in rows])
        summ[s]['Q300'] = S3.stats([r.get('Q300') for r in rows])
        summ[s]['helix_hb_share'] = S3.stats([r.get('helix_hb_share') for r in rows])
        if any('rmsd_to_target' in r for r in rows):
            summ[s]['rmsd_to_target'] = S3.stats([r.get('rmsd_to_target') for r in rows])
    core = [r for s in ('page', 'random32') if s in data for r in data[s]]
    summ['odd_pairs_in_cores'] = {f'{s}_sep{k}': odd_pairs_tb(data[s], k) for s in ('page', 'random32', 'designs_final')
                                  if s in data for k in (3, 4)}
    summ['charges'] = S3.charges(core)
    if 'designs_final' in data:
        summ['charges_designs'] = S3.charges(data['designs_final'])
    old = json.load(open(os.path.join(HERE, 'results', 'step3_summary.json')))
    summ['one_bead_step3'] = {k: old.get(k) for k in ('page', 'random32', 'additive')}
    summ['constants'] = dict(FOLD_F300=S3.FOLD_F300, FOLD_SAME=S3.FOLD_SAME, BURIED_N=5.5)
    json.dump(summ, open(os.path.join(HERE, 'results', 'tb_summary.json'), 'w'), indent=1, default=float)

    Tg = np.arange(250.0, 480.5, 5.0)
    W, H = 1500, 520
    # figure: melting of page and random sets, and the designs
    img = Image.new('RGB', (W, H), 'white')
    p1 = S3.Panel(img, (80, 50, 520, 430), (250, 480), (0, 1), 'two beads: Q(T), page (blue), random 32 (green)', 'T (K)', 'Q')
    p2 = S3.Panel(img, (600, 50, 1040, 430), (250, 480), (0, 1), 'heat capacity C(T) / C max', 'T (K)', 'C/Cmax')
    p3 = S3.Panel(img, (1120, 50, 1460, 430), (250, 480), (0, 1), 'designs: fraction in native f(T)', 'T (K)', 'f')
    for s, c in (('page', COL[0]), ('additive', COL[1]), ('random32', COL[2])):
        rows = data.get(s, [])
        light = tuple(int(0.35 * 255 + 0.65 * v) for v in c)
        for r in rows[:40]:
            if 'Q_curve' in r:
                p1.line(Tg, r['Q_curve'], light, 1)
            C = np.array(r['C_curve']); p2.line(Tg, C / C.max(), light, 1)
        if rows:
            p1.line(Tg, np.mean([r['Q_curve'] for r in rows if 'Q_curve' in r], 0), c, 3)
            p2.line(Tg, np.mean([np.array(r['C_curve']) / max(r['C_curve']) for r in rows], 0), c, 3)
    p1.legend([('page, cooperative', COL[0]), ('page, additive', COL[1]), ('random 32', COL[2])])
    tg = {}
    for r in data.get('designs_final', []):
        t = r['name'].split('__')[0]
        k = list(dict.fromkeys(x['name'].split('__')[0] for x in data['designs_final'])).index(t)
        p3.line(Tg, r['f_curve'], COL[k % len(COL)], 2)
        tg[t] = COL[k % len(COL)]
    p3.legend([(t.replace('design_', ''), c) for t, c in tg.items()])
    img.save(os.path.join(a.fig, '23_melting.png'))

    # figure: uniqueness, one bead against two beads against task 02
    img = Image.new('RGB', (W, H), 'white')
    p1 = S3.Panel(img, (80, 50, 520, 430), (0, 11), (0, 0.7), 'page: distinct folds tied within 1 kT', 'folds', 'share')
    t02 = json.load(open(os.path.join(HERE, '..', 'fold3d', 'results', 'repro_default.json')))
    t02n = [r['n_distinct_at_min'] for r in t02['rows'] if r['world'] != 'random32']
    p1.bars(np.arange(12) - 0.27, np.bincount(t02n, minlength=12)[:12] / len(t02n), (180, 180, 180), 0.26)
    one = os.path.join(r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-14\task15_step3', 'analysis_page.json')
    if os.path.exists(one):
        o = json.load(open(one))
        p1.bars(np.arange(12), np.bincount([r['n_distinct_tied'] for r in o], minlength=12)[:12] / len(o), COL[1], 0.26)
    if 'page' in data:
        p1.bars(np.arange(12) + 0.27, np.bincount([r['n_distinct_tied'] for r in data['page']], minlength=12)[:12] /
                len(data['page']), COL[0], 0.26)
    p1.legend([('task 02 lattice', (180, 180, 180)), ('one bead (step 3)', COL[1]), ('two beads', COL[0])])
    p2 = S3.Panel(img, (600, 50, 1040, 430), (0, 1.0), (0, 1.0), 'share of runs in the best fold', 'share', 'share of seqs')
    edges = np.linspace(0, 1.0, 11)
    for k, (s, c) in enumerate((('page', COL[0]), ('random32', COL[2]), ('designs_final', COL[3]))):
        if s in data:
            h, _ = np.histogram([r['frac_same'] for r in data[s]], edges)
            p2.bars(edges[:-1] + 0.05 + (k - 1) * 0.03, h / len(data[s]), c, 0.03)
    p2.legend([('page', COL[0]), ('random 32', COL[2]), ('designs', COL[3])])
    p3 = S3.Panel(img, (1120, 50, 1460, 430), (0, 1.5), (0, 1.0), 'designs: RMSD of runs to target (nm)', 'nm', 'share')
    if 'designs_final' in data:
        v = [x for r in data['designs_final'] for x in r.get('rmsd_runs_to_target', [])]
        h, _ = np.histogram(v, np.linspace(0, 1.5, 16))
        p3.bars(np.linspace(0, 1.5, 16)[:-1] + 0.05, h / max(len(v), 1), COL[3], 0.08)
    img.save(os.path.join(a.fig, '23_uniqueness.png'))
    # figure: the Go instrument check (two beads) and the hand designs with the real energy
    img = Image.new('RGB', (W, H), 'white')
    names = [('design_sheet3', 'sheet design (25)'), ('design_helixhairpin', 'helix hairpin (32)'), ('bundle3', 'three-helix bundle (45)')]
    for k, (nm, title) in enumerate(names):
        p = S3.Panel(img, (80 + 520 * k, 50, 80 + 520 * k + 400, 430), (250, 480), (0, 1), title + ': Q(T) vs native', 'T (K)', 'Q')
        leg = []
        for j, e in enumerate(('1', '1.5', '2.5')):
            for r in data.get('go', []):
                if r['name'] == f'{nm}@{e}':
                    p.line(Tg, r['Q_curve'], COL[j], 3); leg.append((f'Go {e} kT per contact', COL[j]))
        for r in data.get('hand_real', []):
            if r['name'] == nm:
                p.line(Tg, r['Q_curve'], (90, 90, 90), 2); leg.append(('real energy (Q vs own best)', (90, 90, 90)))
        p.legend(leg)
    img.save(os.path.join(a.fig, '23_go_check.png'))
    print(json.dumps({s: {k: summ[s].get(k) for k in ('n', 'distinct_tied_1kT', 'frac_runs_in_native_fold', 'foldable',
                                                       'f300', 'TmQ', 'kappa2s_interior')} for s in data}, indent=1,
                     default=float)[:5000])


if __name__ == '__main__':
    main()
