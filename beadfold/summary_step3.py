"""Task 15, step 3: summarise the analysis files into results/step3_summary.json and draw the figures (PIL).

Usage: python summary_step3.py [--dir DIR] [--fig OUTDIR]
Reads DIR/analysis_<set>.json written by analyse_step3.py for the sets listed in SETS (missing ones are skipped).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tertiary as TT  # noqa: E402

SETS = ['page', 'random32', 'additive', 'conv_300000', 'go1_coop', 'go_coop_100000', 'go2_coop_100000',
        'go3_coop_100000', 'go4_coop_100000', 'go3_additive_100000']
FOLD_F300 = 0.5          # foldable: native population at 300 K at least this ...
FOLD_SAME = 0.5          # ... and at least this share of runs end in the native's fold
KT = TT.KT0


def fnum(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else x


def stats(v):
    v = np.array([x for x in v if x is not None and np.isfinite(x)], float)
    if not len(v):
        return dict(n=0)
    return dict(n=int(len(v)), mean=round(float(v.mean()), 3), sd=round(float(v.std()), 3),
                median=round(float(np.median(v)), 3), min=round(float(v.min()), 3), max=round(float(v.max()), 3))


def set_summary(rows):
    n = len(rows)
    fold = [r for r in rows if r['f300'] >= FOLD_F300 and r['frac_same'] >= FOLD_SAME]
    interior = [r for r in rows if 255 < r['Tmax'] < 475]
    return dict(
        n=n, mean_L=round(float(np.mean([r['L'] for r in rows])), 1),
        distinct_folds_in_runs=stats([r['n_distinct'] for r in rows]),
        distinct_tied_1kT=stats([r['n_distinct_tied'] for r in rows]),
        runs_tied_1kT=stats([r['n_tied'] for r in rows]),
        frac_runs_in_native_fold=stats([r['frac_same'] for r in rows]),
        seqs_native_in_8of10=int(sum(r['frac_same'] >= 0.8 for r in rows)),
        seqs_native_once=int(sum(r['frac_same'] <= 1.0 / len(r['E_runs_kT']) + 1e-9 for r in rows)),
        f300=stats([r['f300'] for r in rows]),
        foldable=len(fold), foldable_share=round(len(fold) / max(n, 1), 3),
        Tm_f=dict(stats([r['Tm'] for r in rows if np.isfinite(r['Tm'])]),
                  below_window=int(sum(r['Tm'] == -np.inf for r in rows)),
                  above_window=int(sum(r['Tm'] == np.inf for r in rows))),
        TmQ=dict(stats([r.get('TmQ') for r in rows if r.get('TmQ') is not None and np.isfinite(r['TmQ'])]),
                 above_window=int(sum(r.get('TmQ') == np.inf for r in rows))),
        widthQ_over_TmQ=stats([r['widthQ_K'] / r['TmQ'] for r in rows
                               if r.get('TmQ') and np.isfinite(r.get('TmQ', np.nan)) and np.isfinite(r.get('widthQ_K', np.nan))]),
        Q_lowT=stats([r.get('Q_lowT') for r in rows]),
        Tmax_C=stats([r['Tmax'] for r in rows]),
        Tmax_interior=len(interior),
        kappa2=stats([r['k2'] for r in rows]),
        kappa2_interior=stats([r['k2'] for r in interior]),
        kappa2s_interior=stats([r['k2s'] for r in interior]),
        dG300_kT=stats([r['dG300_kT'] for r in rows]),
        dG300_kT_foldable=stats([r['dG300_kT'] for r in fold]),
        E_best_kT=stats([r['E_best_kT'] for r in rows]),
        gap_to_next_fold_kT=stats([r.get('gap_kT') for r in rows]),
        rmsd_best_to_other_runs_nm=stats([np.median(r['rmsd_best_to_others']) for r in rows if r.get('rmsd_best_to_others')]),
        s_per_seq=stats([r['s_per_seq'] for r in rows]),
    )


ODD = [1, 3, 5, 7, 9, 11, 13, 15]


def odd_pairs(rows, min_sep=4):
    """contacts between buried odd monomers in the lowest structures; enrichment over the buried-odd composition.
    min_sep: only contacts at least this far apart along the chain (removes i, i+3 contacts that repeating page
    patterns such as 'phphph' force between complements)."""
    cnt = np.zeros((16, 16))
    for r in rows:
        seq, bur = r['seq'], r['buried']
        for i, j in r['native_contacts']:
            if abs(i - j) < min_sep:
                continue
            a, b = seq[i], seq[j]
            if bur[i] and bur[j] and a & 1 and b & 1:
                cnt[a, b] += 1
                cnt[b, a] += 1
    tot = cnt.sum()
    marg = cnt.sum(1) / max(tot, 1)
    enr = np.where(np.outer(marg, marg) > 0, (cnt / max(tot, 1)) / np.maximum(np.outer(marg, marg), 1e-12), np.nan)
    out = dict(n_contacts=int(tot / 2), min_sep=min_sep, rows=[])
    E = TT.E_TAB / KT
    for a in ODD:
        part = [b for b in ODD if cnt[a, b] > 0]
        if cnt[a].sum() < 6:
            out['rows'].append(dict(m=a, contacts=int(cnt[a].sum()), note='too few')); continue
        order = sorted(ODD, key=lambda b: -(enr[a, b] if np.isfinite(enr[a, b]) else -1))
        out['rows'].append(dict(
            m=a, contacts=int(cnt[a].sum()), complement=a ^ 8,
            complement_contacts=int(cnt[a, a ^ 8]), complement_enrichment=fnum(round(float(enr[a, a ^ 8]), 2)),
            complement_rank_among_odd=order.index(a ^ 8) + 1,
            best_partner=order[0], best_enrichment=fnum(round(float(enr[a, order[0]]), 2)),
            table_rank_among_odd=sorted(ODD, key=lambda b: E[a, b]).index(a ^ 8) + 1))
    # size classes
    size = {1: 'L', 3: 'L', 7: 'L', 5: 'M', 13: 'S', 11: 'S', 9: 'T', 15: 'T'}
    sc = {}
    for a in ODD:
        for b in ODD:
            k = ''.join(sorted(size[a] + size[b]))
            sc[k] = sc.get(k, 0) + cnt[a, b]
    ms = {}
    for a in ODD:
        ms[size[a]] = ms.get(size[a], 0) + cnt[a].sum()
    tot_s = sum(ms.values())
    out['size_class_enrichment'] = {}
    for k, v in sc.items():
        x, y = k[0], k[1]
        exp = (ms[x] / tot_s) * (ms[y] / tot_s) * (1 if x == y else 2) * tot
        out['size_class_enrichment'][k] = fnum(round(float(v / exp), 2)) if exp > 0 else None
    return out


def charges(rows):
    out = dict(seqs=len(rows), buried_charged=0, partnered=0, unpartnered=0, exposed_charged=0, charged_total=0)
    with_pair, without = [], []
    for r in rows:
        seq = r['seq']
        nch = sum(1 for m in seq if m in (0, 2, 8, 10))
        out['charged_total'] += nch
        bc = r['buried_charges']
        out['buried_charged'] += len(bc)
        out['partnered'] += sum(b['partnered'] for b in bc)
        out['unpartnered'] += sum(not b['partnered'] for b in bc)
        (with_pair if any(b['partnered'] for b in bc) else without).append(r)
    out['share_charged_buried'] = round(out['buried_charged'] / max(out['charged_total'], 1), 3)
    # burial share of other classes, for comparison
    def share(cls):
        n = b = 0
        for r in rows:
            for m, x in zip(r['seq'], r['buried']):
                if cls(m):
                    n += 1; b += x
        return round(b / max(n, 1), 3)
    out['share_buried_oily'] = share(lambda m: m & 1)
    out['share_buried_polar_uncharged'] = share(lambda m: not m & 1 and m not in (0, 2, 8, 10))
    out['seqs_with_buried_pair'] = len(with_pair)
    out['tied_with_pair'] = stats([r['n_distinct_tied'] for r in with_pair])
    out['tied_without_pair'] = stats([r['n_distinct_tied'] for r in without])
    out['distinct_with_pair'] = stats([r['n_distinct'] for r in with_pair])
    out['distinct_without_pair'] = stats([r['n_distinct'] for r in without])
    return out


# ------------------------------------------------------------------ figures (PIL)
def font(sz):
    for f in ('arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


COL = [(31, 119, 180), (214, 39, 40), (44, 160, 44), (148, 103, 189), (255, 127, 14), (23, 190, 207), (140, 86, 75)]


class Panel:
    def __init__(self, img, box, xr, yr, title='', xl='', yl=''):
        self.d = ImageDraw.Draw(img)
        self.box, self.xr, self.yr = box, xr, yr
        x0, y0, x1, y1 = box
        f = font(13)
        self.d.rectangle(box, outline=(0, 0, 0))
        self.d.text((x0, y0 - 20), title, fill=(0, 0, 0), font=font(14))
        self.d.text(((x0 + x1) / 2 - 3 * len(xl), y1 + 22), xl, fill=(0, 0, 0), font=f)
        self.d.text((x0 - 55, y0 - 4), yl, fill=(0, 0, 0), font=f)
        for k in range(5):
            xv = xr[0] + (xr[1] - xr[0]) * k / 4
            yv = yr[0] + (yr[1] - yr[0]) * k / 4
            px, py = self.px(xv, yv)
            self.d.line([(px, y1), (px, y1 + 4)], fill=(0, 0, 0))
            self.d.text((px - 12, y1 + 6), f'{xv:.3g}', fill=(0, 0, 0), font=f)
            self.d.line([(x0 - 4, py), (x0, py)], fill=(0, 0, 0))
            self.d.text((x0 - 40, py - 7), f'{yv:.3g}', fill=(0, 0, 0), font=f)

    def px(self, x, y):
        x0, y0, x1, y1 = self.box
        X = x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * (x1 - x0)
        Y = y1 - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * (y1 - y0)
        return X, Y

    def line(self, xs, ys, c, w=2):
        pts = [self.px(x, y) for x, y in zip(xs, ys) if np.isfinite(y)]
        if len(pts) > 1:
            self.d.line(pts, fill=c, width=w)

    def bars(self, xs, ys, c, w=0.8):
        for x, y in zip(xs, ys):
            a = self.px(x - w / 2, 0); b = self.px(x + w / 2, y)
            self.d.rectangle([a[0], b[1], b[0], a[1]], fill=c)

    def dots(self, xs, ys, c, r=3):
        for x, y in zip(xs, ys):
            if np.isfinite(x) and np.isfinite(y):
                X, Y = self.px(x, y); self.d.ellipse([X - r, Y - r, X + r, Y + r], fill=c)

    def legend(self, items, at=None):
        x0, y0, x1, y1 = self.box
        x, y = at or (x1 - 170, y0 + 8)
        for k, (name, c) in enumerate(items):
            self.d.rectangle([x, y + 16 * k + 3, x + 10, y + 16 * k + 13], fill=c)
            self.d.text((x + 15, y + 16 * k), name, fill=(0, 0, 0), font=font(12))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=r'D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-14\task15_step3')
    ap.add_argument('--fig', default=os.path.join(HERE, '..', 'comms', 'from_gpu'))
    a = ap.parse_args()
    data = {}
    for s in SETS + ['scan_lam1.00_60000', 'scan_lam1.50_60000', 'scan_lam2.00_60000', 'scan_lam3.00_60000']:
        p = os.path.join(a.dir, f'analysis_{s}.json')
        if os.path.exists(p):
            data[s] = json.load(open(p))
    summ = {s: set_summary(rows) for s, rows in data.items()}
    core_rows = [r for s in ('page', 'random32') if s in data for r in data[s]]
    summ['odd_pairs_in_cores'] = {f'{s}_sep{k}': odd_pairs(data[s], k) for s in ('page', 'random32') if s in data
                                  for k in (3, 4)}
    summ['charges'] = charges(core_rows)
    summ['constants'] = dict(FOLD_F300=FOLD_F300, FOLD_SAME=FOLD_SAME)
    json.dump(summ, open(os.path.join(HERE, 'results', 'step3_summary.json'), 'w'), indent=1, default=float)
    print(json.dumps({k: v for k, v in summ.items()}, indent=1, default=float)[:6000])

    # figure 1: melting curves (Q and C) for page sequences, coop against additive; f for designs
    W, H = 1500, 520
    img = Image.new('RGB', (W, H), 'white')
    Tg = TT_grid = np.arange(250.0, 480.5, 5.0)
    p1 = Panel(img, (80, 50, 520, 430), (250, 480), (0, 1), 'native contacts Q(T), page sequences', 'T (K)', 'Q')
    p2 = Panel(img, (600, 50, 1040, 430), (250, 480), (0, 1), 'heat capacity C(T) / C max', 'T (K)', 'C/Cmax')
    p3 = Panel(img, (1120, 50, 1460, 430), (250, 480), (0, 1), 'fraction in native fold f(T) (grey: page; colour: designs)', 'T (K)', 'f')
    for k, (s, c) in enumerate((('page', COL[0]), ('additive', COL[1]), ('random32', COL[2]))):
        for r in data.get(s, [])[:40]:
            if 'Q_curve' in r:
                p1.line(Tg, r['Q_curve'], tuple(int(0.35 * 255 + 0.65 * v) for v in c), 1)
            C = np.array(r['C_curve']); p2.line(Tg, C / C.max(), tuple(int(0.35 * 255 + 0.65 * v) for v in c), 1)
        rows = data.get(s, [])
        if rows and 'Q_curve' in rows[0]:
            p1.line(Tg, np.mean([r['Q_curve'] for r in rows if 'Q_curve' in r], 0), c, 3)
            p2.line(Tg, np.mean([np.array(r['C_curve']) / max(r['C_curve']) for r in rows], 0), c, 3)
    p1.legend([('page, cooperative', COL[0]), ('page, additive', COL[1]), ('random 32, coop.', COL[2])])
    for r in data.get('page', []):
        p3.line(Tg, r['f_curve'], (200, 200, 230), 1)
    for k, r in enumerate([r for r in data.get('conv_300000', []) if r['name'].startswith('design')]):
        p3.line(Tg, r['f_curve'], COL[3 + k % 3], 3)
    p3.legend([(r['name'].replace('design_', ''), COL[3 + k % 3]) for k, r in enumerate([r for r in data.get('conv_300000', []) if r['name'].startswith('design')])])
    img.save(os.path.join(a.fig, '15s3_melting.png'))

    # figure 2: uniqueness histogram against task 02, and kappa2
    img = Image.new('RGB', (W, H), 'white')
    p1 = Panel(img, (80, 50, 520, 430), (0, 11), (0, 0.6), 'distinct lowest folds in 10 runs', 'folds', 'share of seqs')
    t02 = json.load(open(os.path.join(HERE, '..', 'fold3d', 'results', 'repro_default.json')))
    t02n = [r['n_distinct_at_min'] for r in t02['rows'] if r['world'] != 'random32']
    h02 = np.bincount(t02n, minlength=12)[:12] / len(t02n)
    p1.bars(np.arange(12) - 0.2, h02, (180, 180, 180), 0.4)
    if 'page' in data:
        hn = np.bincount([r['n_distinct_tied'] for r in data['page']], minlength=12)[:12] / len(data['page'])
        p1.bars(np.arange(12) + 0.2, hn, COL[0], 0.4)
    p1.legend([('task 02 lattice, tied (120)', (180, 180, 180)), ('step 3, within 1 kT (80)', COL[0])])
    p2 = Panel(img, (600, 50, 1040, 430), (0, 11), (0, 1.0), 'distinct folds, all 10 runs (step 3)', 'folds', 'share')
    for k, (s, c) in enumerate((('page', COL[0]), ('random32', COL[2]))):
        if s in data:
            hn = np.bincount([r['n_distinct'] for r in data[s]], minlength=12)[:12] / len(data[s])
            p2.bars(np.arange(12) + (k - 0.5) * 0.4, hn, c, 0.4)
    p2.legend([('page', COL[0]), ('random 32', COL[2])])
    p3 = Panel(img, (1120, 50, 1460, 430), (0, 1.2), (0, 0.6), 'Kaya-Chan kappa2 (no baseline)', 'kappa2', 'share')
    edges = np.linspace(0, 1.2, 13)
    for k, (s, c) in enumerate((('page', COL[0]), ('additive', COL[1]))):
        if s in data:
            h, _ = np.histogram([r['k2'] for r in data[s]], edges)
            p3.bars(edges[:-1] + 0.05 + (k - 0.5) * 0.04, h / len(data[s]), c, 0.04)
    p3.legend([('cooperative', COL[0]), ('additive', COL[1])])
    img.save(os.path.join(a.fig, '15s3_uniqueness_kappa.png'))

    # figure 3: the Go instrument check against the real table, on the two designs: Q(T) and C(T)
    img = Image.new('RGB', (W, H), 'white')
    panels = {'design_sheet3': Panel(img, (80, 50, 520, 430), (250, 480), (0, 1), 'sheet design (25): Q(T)', 'T (K)', 'Q'),
              'design_helixhairpin': Panel(img, (600, 50, 1040, 430), (250, 480), (0, 1), 'helix hairpin (32): Q(T)', 'T (K)', 'Q')}
    pc = Panel(img, (1120, 50, 1460, 430), (250, 480), (0, 1), 'sheet design: C(T) / C max', 'T (K)', 'C/Cmax')
    series = [('conv_300000', 'step 1 table (coop.)', COL[0]), ('go2_coop_100000', 'Go 2 kT (coop.)', COL[2]),
              ('go3_coop_100000', 'Go 3 kT (coop.)', COL[1]), ('go3_additive_100000', 'Go 3 kT (additive)', COL[4]),
              ('go4_coop_100000', 'Go 4 kT (coop.)', COL[3])]
    for s_, lab, c in series:
        for r in data.get(s_, []):
            if r['name'] in panels and 'Q_curve' in r:
                panels[r['name']].line(Tg, r['Q_curve'], c, 3)
                if r['name'] == 'design_sheet3':
                    C = np.array(r['C_curve']); pc.line(Tg, C / C.max(), c, 3)
    panels['design_sheet3'].legend([(lab, c) for s_, lab, c in series if s_ in data], at=(300, 300))
    img.save(os.path.join(a.fig, '15s3_go_check.png'))
    print('figures written')


if __name__ == '__main__':
    main()
