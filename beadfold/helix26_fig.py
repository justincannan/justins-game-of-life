"""Task 26 step 2: figure comms/from_gpu/26_helix.png from helix26.py's JSON (PIL).
Usage: python helix26_fig.py SCAN.json CONFIG [CONFIG ...]"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import summary_step3 as S3  # noqa: E402

COL = [(150, 150, 150), (31, 119, 180), (44, 160, 44), (148, 103, 189), (255, 127, 14)]
OILY = (214, 39, 40)


def main():
    d = json.load(open(sys.argv[1]))
    shown = sys.argv[2:]
    img = Image.new('RGB', (1500, 520), 'white')
    p1 = S3.Panel(img, (80, 50, 680, 430), (0, 1), (0, 1), 'helix content at 300 K: model against Zimm-Bragg (step 2)',
                  'Zimm-Bragg (step 2)', 'model (H-bond share)')
    p1.line([0, 1], [0, 1], (200, 200, 200), 1)
    for c, col in zip(shown, COL):
        rr = [r for r in d['rows'] if r['config'] == c]
        pol = [r for r in rr if 'oily' not in r['name']]
        oil = [r for r in rr if 'oily' in r['name']]
        p1.dots([r['zb'] for r in pol], [r['hb_share']['300'] for r in pol], col, 5)
        p1.dots([r['zb'] for r in oil], [r['hb_share']['300'] for r in oil], OILY, 3)
    p1.legend([(c, col) for c, col in zip(shown, COL)] + [('oily homopolymers', OILY)], at=(90, 58))
    p2 = S3.Panel(img, (800, 50, 1400, 430), (10, 34), (0, 1), 'polar host 12 x L: helix content against length',
                  'length L', 'helix content')
    Ls = [12, 16, 20, 24, 32]
    zb = [d['zb'][f'12x{L}'] for L in Ls]
    p2.line(Ls, zb, (0, 0, 0), 2)
    p2.dots(Ls, zb, (0, 0, 0), 4)
    leg = [('Zimm-Bragg (step 2)', (0, 0, 0))]
    for c, col in zip(shown, COL):
        m = [next(r['hb_share']['300'] for r in d['rows'] if r['config'] == c and r['name'] == f'12x{L}') for L in Ls]
        p2.line(Ls, m, col, 2); p2.dots(Ls, m, col, 4)
        leg.append((c, col))
    p2.legend(leg)
    img.save(os.path.join(HERE, '..', 'comms', 'from_gpu', '26_helix.png'))


if __name__ == '__main__':
    main()
