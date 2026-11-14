// The 3D version of the in-page harness: runOne3(env, ticks, overrides) waits for each GPU readback, so the cells see the 3D water.
window.runOne3 = async function (env, T, o) {
  running = false; Object.assign(P, o || {}); P.water3d = true; P.env = env; envInit(); reset('organism'); await g3Setup();
  let a200 = null; const t0 = performance.now();
  for (let k = 0; k < T; k++) { step(); if ((tick & 1) === 0) await g3Sync(); if (tick === 200) { let q = 0; for (let i = 0; i < N; i++) q += alive[i]; a200 = q; } }
  let aEnd = 0; for (let i = 0; i < N; i++) aEnd += alive[i];
  const r = airStat.recent.slice().sort((a, b) => a - b);
  return {env, g3: G3.state, a200, aEnd, ms: +((performance.now() - t0) / T).toFixed(1), settled: airStat.settled, medDist: r.length ? r[r.length >> 1] | 0 : null, maxDist: airStat.maxDist | 0};
};
