"""Figures for the task 02 report (PIL only) and a summary of the numbers: results/summary.json.
Usage: python figs.py [OUTDIR]   (default: ../comms/from_gpu)"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
import os
RES = Path(os.environ.get('FOLD3D_RES', str(HERE / 'results')))
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / 'comms' / 'from_gpu'
sys.path.insert(0, str(HERE))
from lattice import oily_table  # noqa: E402

PAL = ['#2a6fdb', '#e8590c', '#2b8a3e', '#9c36b5', '#c92a2a', '#5c940d', '#1098ad', '#868e96']


def font(sz):
    for f in ('arial.ttf', 'segoeui.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


F, FS, FT = font(15), font(12), font(17)


def load(n):
    p = RES / (n + '.json')
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


class Ax:
    def __init__(self, img, box, xr, yr, xlog=False, ylog=False, title='', xl='', yl=''):
        self.d = ImageDraw.Draw(img)
        self.x0, self.y0, self.x1, self.y1 = box
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog
        d = self.d
        d.rectangle(box, outline='#444')
        d.text(((self.x0 + self.x1) / 2, self.y0 - 22), title, fill='#111', font=FT, anchor='mm')
        d.text(((self.x0 + self.x1) / 2, self.y1 + 34), xl, fill='#222', font=F, anchor='mm')
        tmp = Image.new('RGBA', (300, 24), (255, 255, 255, 0))
        ImageDraw.Draw(tmp).text((150, 12), yl, fill='#222', font=F, anchor='mm')
        tmp = tmp.rotate(90, expand=True)
        img.paste(tmp, (int(self.x0 - 62), int((self.y0 + self.y1) / 2 - 150)), tmp)

    def _t(self, v, r, lg):
        if lg:
            v, r = math.log10(max(v, 1e-12)), (math.log10(r[0]), math.log10(r[1]))
        return (v - r[0]) / (r[1] - r[0])

    def px(self, x, y):
        return (self.x0 + self._t(x, self.xr, self.xlog) * (self.x1 - self.x0),
                self.y1 - self._t(y, self.yr, self.ylog) * (self.y1 - self.y0))

    def ticks(self, xs, ys, fx=str, fy=str):
        for x in xs:
            p = self.px(x, self.yr[0])
            self.d.line([p, (p[0], p[1] + 5)], fill='#444')
            self.d.text((p[0], p[1] + 14), fx(x), fill='#333', font=FS, anchor='mm')
        for y in ys:
            p = self.px(self.xr[0], y)
            self.d.line([p, (p[0] - 5, p[1])], fill='#444')
            self.d.line([(p[0] + 1, p[1]), (self.x1 - 1, p[1])], fill='#eee')
            self.d.text((p[0] - 8, p[1]), fy(y), fill='#333', font=FS, anchor='rm')

    def line(self, xs, ys, c, w=2, dots=True):
        pts = [self.px(x, y) for x, y in zip(xs, ys) if y is not None and not (isinstance(y, float) and math.isnan(y))]
        if len(pts) > 1:
            self.d.line(pts, fill=c, width=w)
        if dots:
            for p in pts:
                self.d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=c)

    def bar(self, x, y, wd, c, base=0):
        a, b = self.px(x - wd / 2, base), self.px(x + wd / 2, y)
        self.d.rectangle([a[0], min(a[1], b[1]), b[0], max(a[1], b[1])], fill=c)

    def legend(self, items, x=None, y=None):
        x = self.x0 + 12 if x is None else x
        y = self.y0 + 10 if y is None else y
        for k, (lab, c) in enumerate(items):
            self.d.rectangle([x, y + 18 * k + 3, x + 12, y + 18 * k + 13], fill=c)
            self.d.text((x + 18, y + 18 * k + 8), lab, fill='#222', font=FS, anchor='lm')


def fig_speed(summary):
    sp = load('speed')
    if not sp:
        return
    sweeps = load('repro_default')['sweeps'] if load('repro_default') else 2000
    R = 8
    img = Image.new('RGB', (900, 520), 'white')
    ax = Ax(img, (100, 50, 860, 440), (12, 160), (1e-2, 1e4), xlog=True, ylog=True,
            title=f'GPU time per fold (one run: {R} replicas x {sweeps} sweeps), from measured step times', xl='chain length', yl='seconds per fold')
    ax.ticks([16, 32, 64, 128], [1e-2, 1e-1, 1, 10, 100, 1000, 1e4], fy=lambda v: f'{v:g}')
    rows = []
    for k, B in enumerate((1, 256, 4096)):
        r = sorted([x for x in sp if x['B'] == B], key=lambda x: x['L'])
        secs = [x['ms_per_step'] * 1e-3 * sweeps * x['L'] * R / B for x in r]
        ax.line([x['L'] for x in r], secs, PAL[k])
        rows += [dict(L=x['L'], B=B, ms_per_step=x['ms_per_step'], sec_per_fold=s) for x, s in zip(r, secs)]
    ax.legend([(f'batch {B}', PAL[k]) for k, B in enumerate((1, 256, 4096))], x=700, y=60)
    img.save(OUT / '02_speed.png')
    summary['speed'] = rows


def fig_conv(summary):
    cv = load('conv')
    if not cv:
        return
    img = Image.new('RGB', (900, 520), 'white')
    ax = Ax(img, (100, 50, 860, 440), (150, 25000), (0, 1), xlog=True, title='Plain annealing (T 2 to 0.1): random sequences, 24 x 8 anneals per length',
            xl='sweeps per anneal', yl='fraction of anneals reaching the best known energy')
    ax.ticks([250, 1000, 4000, 16000], [0, .2, .4, .6, .8, 1], fy=lambda v: f'{v:.1f}')
    Ls = sorted({x['L'] for x in cv})
    for k, L in enumerate(Ls):
        r = sorted([x for x in cv if x['L'] == L], key=lambda x: x['sweeps'])
        ax.line([x['sweeps'] for x in r], [x['frac_anneals_at_best'] for x in r], PAL[k])
    ax.legend([(f'length {L}', PAL[k]) for k, L in enumerate(Ls)], x=700, y=330)
    img.save(OUT / '02_convergence.png')
    summary['conv'] = cv


def repro_stats(rep):
    rows = rep['rows']
    def part(rr):
        if not rr:
            return None
        same = np.array([r['n_same_fold'] for r in rr]) / 10
        hitE = np.array([r['n_hit_E'] for r in rr]) / 10
        degen = np.array([r['n_distinct_at_min'] for r in rr])
        q = np.array([np.mean(r['q_to_native']) for r in rr])
        return dict(n=len(rr), mean_len=float(np.mean([r['n'] for r in rr])), frac_same_fold=float(same.mean()),
                    frac_reach_Emin=float(hitE.mean()), seqs_found_ge_8_of_10=float((same >= .8).mean()),
                    seqs_found_once=float((same <= .1).mean()), mean_distinct_folds_at_Emin=float(degen.mean()),
                    mean_native_contact_overlap=float(q.mean()), emin_mean=float(np.mean([r['emin'] for r in rr])))
    pg = [r for r in rows if r['world'] != 'random32']
    return dict(page=part(pg), page_short=part([r for r in pg if r['n'] <= 20]), page_long=part([r for r in pg if r['n'] > 20]),
                random32=part([r for r in rows if r['world'] == 'random32']))


def fig_repro(summary):
    rep = load('repro_default')
    if not rep:
        return
    img = Image.new('RGB', (900, 520), 'white')
    ax = Ax(img, (100, 50, 860, 440), (-0.5, 10.5), (0, 0.6), title='Reproducibility: anneals (of 10) finding the same lowest fold',
            xl='anneals of 10 that found the most common lowest-energy fold', yl='fraction of sequences')
    ax.ticks(range(0, 11), [0, .1, .2, .3, .4, .5, .6], fy=lambda v: f'{v:.1f}')
    groups = [('page, length 12-20', lambda r: r['world'] != 'random32' and r['n'] <= 20),
              ('page, length 21-36', lambda r: r['world'] != 'random32' and r['n'] > 20),
              ('random, length 32', lambda r: r['world'] == 'random32')]
    for k, (lab, f) in enumerate(groups):
        rr = [r for r in rep['rows'] if f(r)]
        if not rr:
            continue
        h = np.bincount([r['n_same_fold'] for r in rr], minlength=11) / len(rr)
        for v in range(11):
            ax.bar(v - 0.27 + 0.27 * k, h[v], 0.25, PAL[k])
    ax.legend([(g[0], PAL[k]) for k, g in enumerate(groups)], x=560, y=60)
    img.save(OUT / '02_reproducibility.png')
    summary['repro_default'] = repro_stats(rep)


def fig_melt(summary):
    m = load('melt_default')
    if not m:
        return
    T = m['temps']
    img = Image.new('RGB', (1300, 520), 'white')
    ax = Ax(img, (90, 50, 620, 440), (0, max(T)), (0, 1), title='Melting: native contacts against temperature',
            xl='temperature (energy units)', yl='fraction of native contacts, Q')
    ax.ticks([0, .5, 1, 1.5, 2], [0, .2, .4, .6, .8, 1], fx=lambda v: f'{v:g}', fy=lambda v: f'{v:.1f}')
    for k, r in enumerate(m['rows'][:20]):
        ax.line(T, r['qmean'], '#9bb7e8', w=1, dots=False)
    qm = np.mean([r['qmean'] for r in m['rows']], 0)
    ax.line(T, qm, '#c92a2a', w=3)
    ax.legend([('20 single sequences', '#9bb7e8'), (f'mean of all {len(m["rows"])}', '#c92a2a')], x=420, y=60)
    # Q distribution at the temperature nearest each sequence's Tm: bimodal = two-state
    ax2 = Ax(img, (740, 50, 1260, 440), (0, 1), (0, 0.3), title='Q at each sequence\'s Tm (pooled samples)',
             xl='Q', yl='fraction of samples')
    ax2.ticks([0, .2, .4, .6, .8, 1], [0, .1, .2, .3], fx=lambda v: f'{v:.1f}', fy=lambda v: f'{v:.1f}')
    pooled = []
    for r in m['rows']:
        if r['tm'] is None:
            continue
        ti = int(np.argmin(np.abs(np.array(T) - r['tm'])))
        pooled += r['q_samples_flat'][ti]
    if pooled:
        h, e = np.histogram(pooled, bins=20, range=(0, 1))
        h = h / h.sum()
        for v, c in zip(h, (e[:-1] + e[1:]) / 2):
            ax2.bar(c, v, 0.045, '#2a6fdb')
    img.save(OUT / '02_melting.png')
    tms = np.array([r['tm'] for r in m['rows'] if r['tm'] is not None])
    ws = np.array([r['width'] for r in m['rows'] if r['tm'] is not None])
    tf = np.array([r['tm_fit'] for r in m['rows'] if r['tm'] is not None])
    lens = np.array([r['n'] for r in m['rows'] if r['tm'] is not None])
    # heat capacity peak sharpness
    summary['melt_default'] = dict(n=len(m['rows']), n_with_tm=int(len(tms)), tm_mean=float(tms.mean()), tm_sd=float(tms.std()),
                                   tm_min=float(tms.min()), tm_max=float(tms.max()), width_over_tm_median=float(np.median(ws / tf)),
                                   width_median=float(np.median(ws)), q_lowT_mean=float(qm[0]),
                                   corr_tm_length=float(np.corrcoef(tms, lens)[0, 1]) if len(tms) > 2 else None,
                                   corr_tm_emin=float(np.corrcoef(tms, [r['emin'] for r in m['rows'] if r['tm'] is not None])[0, 1]) if len(tms) > 2 else None,
                                   q_at_tm_bimodality=bimodality(pooled), normalised=melt_summary(m),
                                   cv_mean=np.round(np.mean([r['cv'] for r in m['rows']], 0), 2).tolist(), temps=T)


def norm_transition(T, q):
    """Q rescaled between its low-T and high-T values; Tm at 0.5, width = T(0.2) - T(0.8)."""
    T = np.asarray(T, float); q = np.asarray(q, float)
    qn = (q - q[-1]) / max(1e-9, q[0] - q[-1])
    def cross(level):
        for i in range(len(T) - 1):
            if qn[i] >= level > qn[i + 1]:
                return T[i] + (qn[i] - level) / (qn[i] - qn[i + 1]) * (T[i + 1] - T[i])
        return None
    tm, t8, t2 = cross(0.5), cross(0.8), cross(0.2)
    return tm, (t2 - t8) if (t8 is not None and t2 is not None) else None


def melt_summary(m, k=None):
    rows = m['rows'][:k] if k else m['rows']
    T = m['temps']
    tm = []; wd = []; sharp = []
    for r in rows:
        a, w = norm_transition(T, r['qmean'])
        if a is not None and w is not None:
            tm.append(a); wd.append(w)
        q = np.asarray(r['qmean'])
        sharp.append(float(np.max(q[:-1] - q[1:])))     # largest single drop between neighbouring temperatures
    tm, wd = np.array(tm), np.array(wd)
    return dict(n=len(rows), n_ok=int(len(tm)), tm_norm_mean=float(tm.mean()) if len(tm) else None, tm_norm_sd=float(tm.std()) if len(tm) else None,
                tm_norm_min=float(tm.min()) if len(tm) else None, tm_norm_max=float(tm.max()) if len(tm) else None,
                width_median=float(np.median(wd)) if len(wd) else None, width_over_tm_median=float(np.median(wd / tm)) if len(tm) else None,
                frac_abrupt=float(np.mean(wd / tm < 0.3)) if len(tm) else None, largest_step_drop_median=float(np.median(sharp)),
                q_lowT_mean=float(np.mean([r['qmean'][0] for r in rows])), q_highT_mean=float(np.mean([r['qmean'][-1] for r in rows])))


def bimodality(x):
    x = np.asarray(x)
    if len(x) < 10:
        return None
    n = len(x)
    from scipy.stats import skew, kurtosis
    g, k = skew(x), kurtosis(x)
    return float((g * g + 1) / (k + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))))   # > 0.555 suggests two peaks


def fig_params(summary):
    names = ['default', 'eP0', 'eP2', 'eB0', 'eB1', 'low']
    labs = {'default': 'default\n(odd, eP 1, eB .5)', 'eP0': 'eP 0', 'eP2': 'eP 2', 'eB0': 'eB 0', 'eB1': 'eB 1', 'low': 'rule m<8'}
    tab = {}
    for n in names:
        rep = load('repro_' + n)
        melt = load('melt_' + n)
        if not rep:
            continue
        rows = rep['rows'] if n != 'default' else rep['rows'][:60]
        st = repro_stats(dict(rows=rows))
        e = dict(repro_page=st['page'], repro_random32=st['random32'])
        if melt:
            rr = melt['rows'][:16]
            tms = [r['tm'] for r in rr if r['tm'] is not None]
            e['tm_mean'] = float(np.mean(tms)) if tms else None
            e['tm_sd'] = float(np.std(tms)) if tms else None
            e['width_over_tm'] = float(np.median([r['width'] / r['tm_fit'] for r in rr if r['tm'] is not None])) if tms else None
            e['q_lowT'] = float(np.mean([r['qmean'][0] for r in rr]))
            e['normalised'] = melt_summary(melt, 16)
        tab[n] = e
    summary['params'] = tab
    img = Image.new('RGB', (1300, 520), 'white')
    ax = Ax(img, (90, 50, 620, 420), (-0.6, len(tab) - 0.4), (0, 1), title='Same lowest fold found (first 60 sequences)',
            xl='', yl='fraction of runs')
    ax.ticks([], [0, .2, .4, .6, .8, 1], fy=lambda v: f'{v:.1f}')
    for k, n in enumerate(tab):
        p = tab[n]['repro_page']; q = tab[n]['repro_random32']
        if p:
            ax.bar(k - 0.18, p['frac_same_fold'], 0.34, PAL[0])
        if q:
            ax.bar(k + 0.18, q['frac_same_fold'], 0.34, PAL[1])
        for i, line in enumerate(labs[n].split('\n')):
            ax.d.text((ax.px(k, 0)[0], 440 + 16 * i), line, fill='#222', font=FS, anchor='mm')
    ax.legend([('page sequences', PAL[0])] + ([('random, length 32', PAL[1])] if any(tab[n]['repro_random32'] for n in tab) else []), x=420, y=60)
    ax2 = Ax(img, (740, 50, 1260, 420), (-0.6, len(tab) - 0.4), (0, 1.2), title='Melting temperature (16 page sequences)',
             xl='', yl='Tm (mean and spread)')
    ax2.ticks([], [0, .2, .4, .6, .8, 1, 1.2], fy=lambda v: f'{v:.1f}')
    for k, n in enumerate(tab):
        if tab[n].get('tm_mean') is not None:
            ax2.bar(k, tab[n]['tm_mean'], 0.5, PAL[2])
            a, b = ax2.px(k, tab[n]['tm_mean'] - tab[n]['tm_sd']), ax2.px(k, tab[n]['tm_mean'] + tab[n]['tm_sd'])
            ax2.d.line([a, b], fill='#111', width=2)
        for i, line in enumerate(labs[n].split('\n')):
            ax2.d.text((ax2.px(k, 0)[0], 440 + 16 * i), line, fill='#222', font=FS, anchor='mm')
    img.save(OUT / '02_parameters.png')


def fig_page(summary):
    pg = load('page')
    if not pg:
        return
    summary['page'] = pg
    names = [n for n in ('eP0', 'default', 'eP2', 'low') if n in pg]
    labs = {'eP0': 'eP 0', 'default': 'eP 1 (default)', 'eP2': 'eP 2', 'low': 'rule m<8, eP 1'}
    img = Image.new('RGB', (1300, 520), 'white')
    ax = Ax(img, (90, 50, 620, 420), (-0.6, len(names) - 0.4), (0, 1), title='Page bracket pairs in lattice contact',
            xl='', yl='fraction of non-adjacent pairs')
    ax.ticks([], [0, .2, .4, .6, .8, 1], fy=lambda v: f'{v:.1f}')
    for k, n in enumerate(names):
        ax.bar(k - 0.18, pg[n]['frac_pairs_in_contact'], 0.34, PAL[0])
        ax.bar(k + 0.18, pg[n]['baseline_same_separation'], 0.34, '#adb5bd')
        ax.d.text((ax.px(k, 0)[0], 440), labs[n], fill='#222', font=FS, anchor='mm')
    ax.legend([('bracket pairs', PAL[0]), ('any pair, same separation', '#adb5bd')], x=360, y=60)
    ax2 = Ax(img, (740, 50, 1260, 420), (-0.6, len(names) - 0.4), (0, 0.6), title='Domains: contacts kept inside',
             xl='', yl='inside contacts / all contacts touching it')
    ax2.ticks([], [0, .1, .2, .3, .4, .5, .6], fy=lambda v: f'{v:.1f}')
    for k, n in enumerate(names):
        ax2.bar(k - 0.18, pg[n]['domain_intra_frac'], 0.34, PAL[2])
        ax2.bar(k + 0.18, pg[n]['domain_baseline'], 0.34, '#adb5bd')
        ax2.d.text((ax2.px(k, 0)[0], 440), labs[n], fill='#222', font=FS, anchor='mm')
    ax2.legend([('bracket domain', PAL[2]), ('any window, same length', '#adb5bd')], x=1000, y=60)
    img.save(OUT / '02_page_brackets.png')


def fig_mut(summary):
    mu = load('mut')
    if not mu:
        return
    same = np.array([m['same_fold'] for m in mu]); still = np.array([m['wt_fold_still_lowest'] for m in mu])
    q = np.array([m['q_wt_contacts_kept'] for m in mu]); oc = np.array([m['oily_change'] for m in mu])
    rel = np.array([m['wt_repro'] >= 0.8 for m in mu])
    summary['mut'] = dict(n=len(mu), same_fold=float(same.mean()), wt_fold_still_lowest=float(still.mean()),
                          q_kept_mean=float(q.mean()), same_fold_when_polarity_changes=float(same[oc].mean()) if oc.any() else None,
                          same_fold_when_polarity_kept=float(same[~oc].mean()) if (~oc).any() else None,
                          still_lowest_when_polarity_changes=float(still[oc].mean()) if oc.any() else None,
                          still_lowest_when_polarity_kept=float(still[~oc].mean()) if (~oc).any() else None,
                          n_reliable_wt=int(rel.sum()), same_fold_reliable_wt=float(same[rel].mean()) if rel.any() else None,
                          energy_change_mean=float(np.mean([m['mut_emin'] - m['wt_emin'] for m in mu])))


def fig_example(summary):
    p = HERE / 'sample_folds.json'
    if not p.exists():
        return
    folds = json.loads(p.read_text(encoding='utf-8'))['folds']
    img = Image.new('RGB', (1300, 460), 'white')
    d = ImageDraw.Draw(img)
    picks = sorted(folds, key=lambda f: -f['length'])[:3]
    for k, f in enumerate(picks):
        X = np.array(f['coords'], dtype=float)
        X -= X.mean(0)
        # an oblique projection
        a, b = 0.6, 0.35
        P = np.stack([X[:, 0] + a * X[:, 2], -X[:, 1] - b * X[:, 2]], 1)
        depth = X[:, 2]
        cx, cy = 220 + 430 * k, 230
        sc = 150 / max(1.0, np.abs(P).max())
        Q = P * sc + [cx, cy]
        for i in range(len(Q) - 1):
            d.line([tuple(Q[i]), tuple(Q[i + 1])], fill='#555', width=3)
        for i in np.argsort(depth):
            r = 9
            c = '#e8a33d' if f['oily'][i] else '#3d7be8'
            d.ellipse([Q[i][0] - r, Q[i][1] - r, Q[i][0] + r, Q[i][1] + r], fill=c, outline='#222')
            d.text(tuple(Q[i]), f['seq'][i], fill='white', font=FS, anchor='mm')
        for i, j in f['bracket_pairs']:
            if j > i + 1:
                d.line([tuple(Q[i]), tuple(Q[j])], fill='#c92a2a', width=1)
        tm = f['tm']
        d.text((cx, 30), f"{f['seq']}", fill='#111', font=FS, anchor='mm')
        d.text((cx, 50), f"length {f['length']}, E = {f['energy']:g}, Tm = {tm:.2f}" if tm else f"length {f['length']}, E = {f['energy']:g}", fill='#111', font=F, anchor='mm')
    d.text((650, 440), 'orange = oily, blue = polar; thin red lines join the page\'s bracket pairs (non-adjacent)', fill='#333', font=F, anchor='mm')
    img.save(OUT / '02_example_folds.png')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    for f in (fig_speed, fig_conv, fig_repro, fig_melt, fig_params, fig_page, fig_mut, fig_example):
        f(summary)
    rep = {n: repro_stats(load('repro_' + n)) for n in ('default',) if load('repro_' + n)}
    summary['repro_full'] = rep
    (RES / 'summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    print(json.dumps(summary, indent=1)[:6000])


if __name__ == '__main__':
    main()
