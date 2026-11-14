// fold3d task 02: run the 'even' world and the 'vent' world to tick T and dump the sequences (seq/slen) of living cells.
// Read-only apart from the seed and the world choice. Run through jgol_2026-11-13/test/rates_driver.py with
// --script ../../justins-game-of-life/fold3d/dump_seq.js (the script path is fetched relative to test/rates.html).
(async () => {
  const C = window.RATES_CFG || {}, WD = C.W || 160, T = C.T || 1000, MAXU = 4000;
  running = false; render = () => {};
  const res = {cfg: C, worlds: {}};
  for (const env of ['even', 'vent']) {
    let s = ((C.seed || 1) * 2654435761) >>> 0 || 1;
    const rnd = () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    rng = rnd; Math.random = rnd;
    P.water3d = false; P.view3d = false; P.twoLayer = false; P.env = env; P.seqOn = true;
    allocWorld(WD, WD, false); try { fit(); } catch (e) {}
    reset('organism');
    const t0 = performance.now();
    for (let k = 1; k <= T; k++) { step(); if (k % 50 === 0) await new Promise(r => setTimeout(r, 0)); }
    const counts = new Map(); let live = 0;
    for (let i = 0; i < N; i++) {
      if (!alive[i] || !slen[i]) continue; live++;
      const o = i * SL, L = slen[i]; let key = '';
      for (let q = 0; q < L; q++) key += MONO[seq[o + q]];
      counts.set(key, (counts.get(key) || 0) + 1);
    }
    const uniq = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, MAXU).map(([q, c]) => ({seq: q, n: c}));
    res.worlds[env] = {tick: tick, live: live, distinct: counts.size, restarts: restarts, ms: Math.round(performance.now() - t0), seqs: uniq};
  }
  return res;
})()
