# 01: connect to the repository: report

From: gpu session, 14 November 2026. This answers `comms/to_gpu/2026-11-14_01_hello.md`.

## 1. Connected

- **The repository is cloned** at `D:\labyrinth\automata\justins-game-of-life\` on the GPU machine.
- **Git was not installed on this machine.** Git for Windows 2.56.0 was installed for this task, with Justin's
  approval.
- **Commits from this side are signed** "Claude (gpu session) <noreply@anthropic.com>", to match the cloud session's.

## 2. The machine

| | |
|---|---|
| GPU | NVIDIA GeForce RTX 3070 Laptop GPU, 8 GB VRAM (driver 555.97) |
| CPU | AMD Ryzen 9 5900HS (8 cores, 16 threads) |
| RAM | 15.4 GB |
| OS | Windows 11 Home, 10.0.26200 |
| Python | 3.10 (numpy, scipy, PIL; no matplotlib) |
| Browser for headless runs | Chrome 157 |

- **Shared queues:** heavy jobs on this machine go through shared CPU and GPU queues, which other projects also use.
  So a long run may wait its turn.

## 3. The build: the content matches byte for byte; the line endings do not

```
python -I tools/patch.py src/digital_life.orig.html OUT \
    tools/newblock3.js tools/chem.js tools/env.js tools/chemui.js tools/gpu3d.js tools/view3d.js
```

- **The text matches exactly.** With the line endings normalised, the built page is identical to the committed
  `build/justins_game_of_life.html` (SHA-256 `52fc5987…`).
  - It is also identical to the page from `jgol_2026-11-13_8.zip`, which the sixth addendum's runs used.
- **The bytes differ only in the line endings.** On Windows the build writes CRLF line endings (319,759 bytes, against
  the committed 316,267). `tools/patch.py`, line 1109, opens the output in text mode:
  `open(dst, 'w', encoding='utf-8')`. On Windows that turns each `\n` into `\r\n`.
- **Git hides this here.** Git on this machine checks files out with CRLF (`core.autocrlf=true`). So in the working
  tree the built page and the checked-out page match byte for byte, and git would store it with LF again.
  - The difference shows only against the committed bytes. It was checked on a second clone with `core.autocrlf=false`.
- **Proposals (not made; `tools/` is the cloud session's side):**
  - write the build with `open(dst, 'w', encoding='utf-8', newline='\n')`, so that it is byte-identical on every
    platform;
  - and add a `.gitattributes` with `* text=auto eol=lf`, so that checkouts agree too.

## 4. Where the sixth addendum stands

**Done; no version passed, so no sweep was run.** The full report is beside this file:
`QUEUE_2026-11-13_day_addendum6_report.md`, with block maps of the dish (`addendum6_maps_sugar1.png`, `…3.png`,
`…10.png`).

**In brief:**
- **The fifth addendum's round had finished.** Its numbers are marked superseded; its structure is kept: which model
  forms fit.
- **Task 1 on page 8:**
  - **The sugar budget:** 1.49 page sugar per birth (R² 0.968).
  - **Upkeep paid from sugar** almost vanishes: 0.00016 per active cell-tick.
  - **Going still** depends on sugar (Matsushita's form).
  - **Waking** needs sugar.
- **The chemistry now pays:** a steady 0.0065 net energy per active cell-tick from the agar's molecules, measured with
  the page's own reaction counters.
  - That is about 8 times what sugar gives at page sugar 1, 2.5 times at sugar 3, and 0.7 times at sugar 10.
  - **So the dish runs on two resources:**
    - sugar 1 regrows after tick 500, out to radius 81;
    - sugar 3 has a second wave at tick 1,000;
    - sugar 10 grows about twice as fast midway.
- **The validation:**
  - **The variants:** Bcrw, Sm, and both proposals (start after the inoculum's stored births; division gated by the
    store), each refitted.
  - **The result:** none passes.
    - Starting at tick 5 still fixes the first 100 ticks.
    - The store gate is no better than the sugar-only models.
    - A constant chemistry-paid birth rate (a further proposal) gets sugar 1's radius right. It overshoots at sugar 3 and
      10, where the page's cells go still once the sugar is gone.
- **The block maps show the page growing as a front:** a ring of active cells around a core gone still. The models go
  still evenly across the colony. So going still also follows each block's own history.
- **What the fold needs next (proposal):**
  - a second field, the agar's molecules per square;
  - going still that depends on total income;
  - the task 1 harness recording molecules and reaction income per block.
- **Still in the page:** in `glidePass` (line 2770 of the build), `body[j] = body[i]; body[i] = 0;` sits inside a
  comment. So a gliding cell leaves its clump membership behind.

## 5. Next

**Ready for the 3D lattice folding task** when its task file arrives.
