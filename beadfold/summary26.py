"""Task 26 step 5: summarise the task-26 analyses (analyse_tb.py on DIR/analysis_<set>.json) into
results/t26_summary.json, side by side with task 23 (results/tb_summary.json) and step 3 (one bead), and draw
comms/from_gpu/26_melting.png and 26_uniqueness.png (PIL).
Usage: python summary26.py [--dir DIR]
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

SETS = ['page', 'random32', 'designs_final']
COL = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189), (140, 86, 75)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-16\task26')
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
        summ[s]['coulomb_kT'] = S3.stats([r['parts_kT'].get('elec') for r in rows])
        if any('rmsd_to_target' in r for r in rows):
            summ[s]['rmsd_to_target'] = S3.stats([r.get('rmsd_to_target') for r in rows])
    core = [r for s in ('page', 'random32') if s in data for r in data[s]]
    summ['charges'] = S3.charges(core)
    summ['odd_pairs_in_cores'] = {f'{s}_sep{k}': S3.odd_pairs(data[s], k) for s in ('page', 'random32') if s in data
                                  for k in (3, 4)}
    t23 = json.load(open(os.path.join(HERE, 'results', 'tb_summary.json')))
    summ['task23_two_beads'] = {k: t23.get(k) for k in ('page', 'random32', 'designs_final', 'charges')}
    summ['one_bead_step3'] = t23.get('one_bead_step3')
    json.dump(summ, open(os.path.join(HERE, 'results', 't26_summary.json'), 'w'), indent=1, default=float)

    Tg = np.arange(250.0, 480.5, 5.0)
    W, H = 1500, 520
    img = Image.new('RGB', (W, H), 'white')
    p1 = S3.Panel(img, (80, 50, 520, 430), (250, 480), (0, 1), 'task 26 model: Q(T), page (blue), random 32 (green)', 'T (K)', 'Q')
    p2 = S3.Panel(img, (600, 50, 1040, 430), (250, 480), (0, 1), 'heat capacity C(T) / C max', 'T (K)', 'C/Cmax')
    p3 = S3.Panel(img, (1120, 50, 1460, 430), (250, 480), (0, 1), 'designs: fraction in native f(T)', 'T (K)', 'f')
    for s, c in (('page', COL[0]), ('random32', COL[2])):
        rows = data.get(s, [])
        light = tuple(int(0.35 * 255 + 0.65 * v) for v in c)
        for r in rows[:40]:
            if 'Q_curve' in r:
                p1.line(Tg, r['Q_curve'], light, 1)
            C = np.array(r['C_curve']); p2.line(Tg, C / C.max(), light, 1)
        if rows:
            p1.line(Tg, np.mean([r['Q_curve'] for r in rows if 'Q_curve' in r], 0), c, 3)
            p2.line(Tg, np.mean([np.array(r['C_curve']) / max(r['C_curve']) for r in rows], 0), c, 3)
    p1.legend([('page', COL[0]), ('random 32', COL[2])])
    tg = {}
    for r in data.get('designs_final', []):
        t = r['name'].split('__')[0]
        k = list(dict.fromkeys(x['name'].split('__')[0] for x in data['designs_final'])).index(t)
        p3.line(Tg, r['f_curve'], COL[k % len(COL)], 2)
        tg[t] = COL[k % len(COL)]
    p3.legend([(t.replace('design_', ''), c) for t, c in tg.items()])
    img.save(os.path.join(a.fig, '26_melting.png'))

    img = Image.new('RGB', (W, H), 'white')
    p1 = S3.Panel(img, (80, 50, 520, 430), (0, 11), (0, 0.8), 'page: distinct folds tied within 1 kT', 'folds', 'share')
    t23p = os.path.join(r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23', 'analysis_page.json')
    one = os.path.join(r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-14\task15_step3', 'analysis_page.json')
    for off, path, c in ((-0.27, one, COL[1]), (0.0, t23p, (150, 150, 150))):
        if os.path.exists(path):
            o = json.load(open(path))
            p1.bars(np.arange(12) + off, np.bincount([r['n_distinct_tied'] for r in o], minlength=12)[:12] / len(o), c, 0.26)
    if 'page' in data:
        p1.bars(np.arange(12) + 0.27, np.bincount([r['n_distinct_tied'] for r in data['page']], minlength=12)[:12] /
                len(data['page']), COL[0], 0.26)
    p1.legend([('one bead (step 3)', COL[1]), ('two beads, task 23', (150, 150, 150)), ('two beads, task 26', COL[0])])
    p2 = S3.Panel(img, (600, 50, 1040, 430), (0, 1.0), (0, 1.0), 'share of runs in the best fold', 'share', 'share of seqs')
    edges = np.linspace(0, 1.0, 11)
    for k, (s, c) in enumerate((('page', COL[0]), ('random32', COL[2]), ('designs_final', COL[3]))):
        if s in data:
            h, _ = np.histogram([r['frac_same'] for r in data[s]], edges)
            p2.bars(edges[:-1] + 0.05 + (k - 1) * 0.03, h / len(data[s]), c, 0.03)
    p2.legend([('page', COL[0]), ('random 32', COL[2]), ('designs', COL[3])])
    p3 = S3.Panel(img, (1120, 50, 1460, 430), (0, 1.5), (0, 1.0), 'designs: RMSD of runs to target (nm)', 'nm', 'share')
    t23d = os.path.join(r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23', 'analysis_designs_final.json')
    for off, rows, c in ((0.0, json.load(open(t23d)) if os.path.exists(t23d) else [], (150, 150, 150)),
                         (0.04, data.get('designs_final', []), COL[3])):
        v = [x for r in rows for x in r.get('rmsd_runs_to_target', [])]
        if v:
            h, _ = np.histogram(v, np.linspace(0, 1.5, 16))
            p3.bars(np.linspace(0, 1.5, 16)[:-1] + 0.03 + off, h / len(v), c, 0.04)
    p3.legend([('task 23', (150, 150, 150)), ('task 26', COL[3])])
    img.save(os.path.join(a.fig, '26_uniqueness.png'))
    print(json.dumps({s: {k: summ[s].get(k) for k in ('n', 'distinct_tied_1kT', 'frac_runs_in_native_fold', 'foldable',
                                                       'f300', 'TmQ', 'gap_to_next_fold_kT', 'kappa2s_interior')}
                      for s in data}, indent=1, default=float)[:6000])


if __name__ == '__main__':
    main()
