// An in-page test harness, for testing in a browser without Playwright: load the built page, then run this in its console
// (or fetch and eval it). runOne(env, ticks, overrides) runs one world and returns survival, timing and spore figures.
window.countAlive = () => { let k = 0; for (let i = 0; i < N; i++) k += alive[i]; return k; };
window.ventLineages = () => {
  if (!vents.length) return null;
  const sets = vents.map(() => new Set());
  for (let i = 0; i < N; i++) {
    if (!alive[i]) continue; const c = cmap[i], qx = c % cw, qy = (c / cw) | 0;
    vents.forEach((v, k) => { const dx = Math.min(Math.abs(qx - v.x), cw - Math.abs(qx - v.x)), dy = Math.min(Math.abs(qy - v.y), chh - Math.abs(qy - v.y)); if (dx * dx + dy * dy < 64) sets[k].add(gen[i] >>> 28); });
  }
  let occ = 0, pairs = 0, shared = 0; sets.forEach(s => { if (s.size) occ++; });
  for (let a = 0; a < sets.length; a++) for (let b = a + 1; b < sets.length; b++) { if (!sets[a].size || !sets[b].size) continue; pairs++; for (const x of sets[a]) if (sets[b].has(x)) { shared++; break; } }
  return {vents: vents.length, occupied: occ, pairsBothOccupied: pairs, pairsSharingALineage: shared};
};
window.runOne = function (env, T, o) {
  running = false; Object.assign(P, o || {}); P.env = env; envInit(); reset('organism');
  let a200 = null; const t0 = performance.now();
  for (let k = 0; k < T; k++) { step(); if (tick === 200) a200 = countAlive(); }
  const ms = (performance.now() - t0) / T, has = typeof airStat === 'object';
  const r = has ? airStat.recent.slice().sort((a, b) => a - b) : [];
  return {env, a200, aEnd: countAlive(), ms: +ms.toFixed(1), settled: has ? airStat.settled : null, medDist: r.length ? +r[r.length >> 1].toFixed(0) : null,
    maxDist: has ? +airStat.maxDist.toFixed(0) : null, vl: env === 'vent' ? ventLineages() : null};
};
