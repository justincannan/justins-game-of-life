# 32: the task-22 population models on the GPU

From: gpu session (scheduled check), 16 November 2026, about 15:40 New York. Answers
`to_gpu/2026-11-16_32_population-runs-on-gpu.md`.

## What was run (measured)
- Model: `popdish/pop22_store.py` (task 22's per-cell-store model), unchanged; the CPU path is kept (`--device cpu` is
  still the default). Only `--device cuda` was passed.
- Same runs as task 22 item 2: sugar 1, 3 and 10; the five variants (full, noa, nob, noc, none); 6 seeds; 2,000 ticks;
  same seeding call (`torch.manual_seed` from sugar, variant and seed). GPU queue, label `jgol32-pop22-gpu`, 2 CPU
  threads. Results: `jgol_2026-11-13/results/2026-11-16/task32/gpu/`.
- CPU reference: task 22's runs (`results/2026-11-15/task22/item2/main/`, torch on the CPU, 4 threads).

## Speed (measured)
| | CPU (s per variant, 6 seeds) | GPU (s) | speedup |
|---|---|---|---|
| full | 808–822 | 52 | 15.5–15.7× |
| noa | 902–927 | 52–55 | 16.5–17.3× |
| nob | 789–801 | 56–57 | 14.0–14.1× |
| noc | 424–434 | 38–43 | 9.9–11.2× |
| none | 362–375 | 38–43 | 8.8–9.4× |

All 15 runs: about 3.5 hours of CPU against 12.5 minutes of GPU. The CPU runs were made beside other queue jobs, so
part of the gap may be load, not hardware.

## Do the results match? (measured)
- **Not run for run.** The GPU draws a different random stream from the same seed (torch's CPU and CUDA generators
  differ), so the same seed does not give the same run. Exact repeatability on the GPU holds GPU to GPU only.
- **Statistically, yes.** Seed means compared GPU against CPU, every variant, sugar and recorded tick (100 to 2,000),
  over seven readouts (live, active, still cells, r95, both roughness measures, sugar left): 734 comparisons, 32 with
  |z| > 2 (4.4%, about what chance gives at 6 seeds a side), the largest |z| 3.9 (noa, sugar 10, r95 at tick 2,000).
- Live cells, for example (mean ± s.d. over 6 seeds):

| | sugar 1, t1000 | sugar 3, t1000 | sugar 10, t1000 | sugar 3, t2000 |
|---|---|---|---|---|
| full, CPU / GPU | 120±9 / 117±16 | 496±30 / 546±49 | 2738±48 / 2749±60 | 698±57 / 679±55 |
| none, CPU / GPU | 3267±214 / 3354±210 | 6007±443 / 6337±383 | 12215±520 / 12473±603 | 7624±579 / 7193±449 |

So task 22's conclusions (report 22, item 2) stand on the GPU path.

## Proposal (Justin decides)
Run later population-model work (task 28's model too) on the GPU through the GPU queue, keeping the CPU path for
checks. A seed-for-seed CPU/GPU match would need the random numbers drawn on the CPU and copied over, which would
lose much of the speed; not proposed unless wanted.
