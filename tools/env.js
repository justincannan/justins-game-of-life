let amb = null;   // the ambient light at each place (13 November): separate from a cell's stored energy (light)
let divT = null;   // the tick a cell last divided: a cell divides at most once a tick
let dishCell = null, dishSq = null;   // the plate: 1 inside the rim, 0 outside (cells, and squares of the ground)
function dishMask() {
  if (!dishCell || dishCell.length !== N) dishCell = new Uint8Array(N);
  if (!dishSq || dishSq.length !== cw * chh) dishSq = new Uint8Array(cw * chh);
  const cx = (W - 1) / 2, cy = (H - 1) / 2, R = P.dishR * Math.min(W, H) / 2, R2 = R * R;
  dishSq.fill(0);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const i = y * W + x, inn = (x - cx) ** 2 + (y - cy) ** 2 <= R2 ? 1 : 0; dishCell[i] = inn; if (inn) dishSq[cmap[i]] = 1; }
}
const dishOut = j => P.env === 'dish' && dishCell !== null && dishCell.length === N && dishCell[j] === 0;   // a place beyond the rim
// remains: in the dish a dead cell leaves its remains in place, holding the colony's shape; they break down slowly
let husk = null, huskG = null;
let coatS = null, coatM = null, coatK = null;   // what each cell's coat is made of: sugar, and product molecules of kind coatK
function coatAlloc() { if (!coatS || coatS.length !== N) { coatS = new Float32Array(N); coatM = new Float32Array(N); coatK = new Uint8Array(N); } }
function coatReturn(i, f) { if (!coatS) return; const c = cmap[i], s = coatS[i] * f, m = coatM[i] * f; if (s) { en[c] += s; coatS[i] -= s; } if (m) { chem[(c << 4) + coatK[i]] += m; coatM[i] -= m; } }
const dishBlocked = j => dishOut(j) || (P.env === 'dish' && husk !== null && husk.length === N && husk[j] > 0);   // a place a cell cannot enter
function dishTick() {
  if (P.env !== 'dish') return; if (!husk || husk.length !== N) husk = new Float32Array(N);
  if (!huskG || huskG.length !== N) huskG = new Int32Array(N);
  const r = P.dishLysis; for (let i = 0; i < N; i++) if (husk[i] > 0) { husk[i] -= r; if (husk[i] <= 0) { husk[i] = 0; changed[i] = 1; if (huskG[i]) { releaseChem(cmap[i] << 4, huskG[i], 0); huskG[i] = 0; } } }   // remains break down and release what they held
}
let divTgt = null; // with no Life rule: the one empty neighbouring place each cell would divide into this tick, chosen at random
function divPick() {
  if (!divTgt || divTgt.length !== N) divTgt = new Int32Array(N);
  const nb = [0, 0, 0, 0, 0, 0, 0, 0];
  for (let y = 0; y < H; y++) { const ym = ((y - 1 + H) % H) * W, y0 = y * W, yp = ((y + 1) % H) * W;
    for (let x = 0; x < W; x++) { const i = y0 + x; divTgt[i] = -1; if (!alive[i] || dor[i] || soma[i]) continue;
      const xm = (x - 1 + W) % W, xp = (x + 1) % W; let e = 0;
      for (const j of [ym + xm, ym + x, ym + xp, y0 + xm, y0 + xp, yp + xm, yp + x, yp + xp]) if (!alive[j] && !dishBlocked(j)) nb[e++] = j;
      if (e) divTgt[i] = nb[(rng() * e) | 0]; } }
}
// ---------------- environments: light and heat that change in time and space
// A coarse field (one value per chemistry square) for the light the ground gets, the temperature of the water, and where vents or springs are.
const ENVS = {even: {heat: false}, pond: {heat: true}, vent: {heat: true}, springs: {heat: true}};
let temp = new Float32Array(1), tempTmp = new Float32Array(1), ltc = new Float32Array(1), tamb = new Float32Array(1), vglow = new Float32Array(1), dens = new Float32Array(1);
let vents = [], CLW = [], envSun = 1, envTemp = .35;
let lor = [1, 1, 20], chx = 0, chy = 0, chz = 0;      // a Lorenz system: the chaotic weather that drives the heat
let en = new Float32Array(1), enTmp = new Float32Array(1), enMade = 0, enTaken = 0, enGot = 0;   // the energy molecule: one value per chemistry square
let fx = new Float32Array(1), fy = new Float32Array(1);
let vhot = new Float32Array(1), tB = new Float32Array(1), tC = new Float32Array(1);
let fvx = new Float32Array(1), fvy = new Float32Array(1), fsrc = new Float32Array(1), fp = new Float32Array(1), fp2 = new Float32Array(1), fu2 = new Float32Array(1), fv2 = new Float32Array(1), fw = new Float32Array(1);
// the water as a fluid (seen from above): it carries its own motion along, warm water wells up and spreads out while cool water sinks,
// a gentle drift wanders with the weather, viscosity smooths it, and what does not well up or sink must go around (a pressure solve)
// heat is carried with a sharper scheme (MacCormack): forward, back again, correct by half the error, and keep within the values it came from
function advectSharp(a, u = fx, v = fy) {
  advect(a, tB, 1, u, v); for (let c = 0; c < u.length; c++) { u[c] = -u[c]; v[c] = -v[c]; } advect(tB, tC, 1, u, v); for (let c = 0; c < u.length; c++) { u[c] = -u[c]; v[c] = -v[c]; }
  for (let y = 0; y < chh; y++) for (let x = 0; x < cw; x++) {
    const c = y * cw + x, sx = x - u[c], sy = y - v[c], x0 = Math.floor(sx), y0 = Math.floor(sy), xa = ((x0 % cw) + cw) % cw, xb = (xa + 1) % cw, ya = ((y0 % chh) + chh) % chh, yb = (ya + 1) % chh;
    const q0 = a[ya * cw + xa], q1 = a[ya * cw + xb], q2 = a[yb * cw + xa], q3 = a[yb * cw + xb], lo = Math.min(q0, q1, q2, q3), hi = Math.max(q0, q1, q2, q3);
    const val = tB[c] + .5 * (a[c] - tC[c]); tempTmp[c] = val < lo ? lo : val > hi ? hi : val;
  }
  a.set(tempTmp);
}
function fluidStep(cur, th, sp) {
  const n = cw * chh;
  if (!(cur > 0)) { fx.fill(0); fy.fill(0); return; }
  let mT = 0; for (let c = 0; c < n; c++) mT += temp[c]; mT /= n;
  let ms = 0; for (let c = 0; c < n; c++) { const s = P.convect * cur * (temp[c] - mT); fsrc[c] = s; ms += s; } ms /= n; for (let c = 0; c < n; c++) fsrc[c] -= ms;
  const ax = Math.cos(th) * sp, ay = Math.sin(th) * sp;
  const dr = 1 - P.fdrag; for (let c = 0; c < n; c++) { fx[c] = fx[c] * dr + .02 * ax + fvx[c]; fy[c] = fy[c] * dr + .02 * ay + fvy[c]; }   // the floor drags on the water
  for (let y = 0; y < chh; y++) for (let x = 0; x < cw; x++) {       // the water carries its own motion along
    const c = y * cw + x, sx = x - fx[c], sy = y - fy[c], x0 = Math.floor(sx), y0 = Math.floor(sy), tx = sx - x0, ty = sy - y0;
    const xa = ((x0 % cw) + cw) % cw, xb = (xa + 1) % cw, ya = ((y0 % chh) + chh) % chh, yb = (ya + 1) % chh, i00 = ya * cw + xa, i10 = ya * cw + xb, i01 = yb * cw + xa, i11 = yb * cw + xb;
    fu2[c] = (1 - ty) * ((1 - tx) * fx[i00] + tx * fx[i10]) + ty * ((1 - tx) * fx[i01] + tx * fx[i11]);
    fv2[c] = (1 - ty) * ((1 - tx) * fy[i00] + tx * fy[i10]) + ty * ((1 - tx) * fy[i01] + tx * fy[i11]);
  }
  fx.set(fu2); fy.set(fv2);
  diffuseF(fx, P.visc); diffuseF(fy, P.visc);
  // pressure: the flow may only spread where water wells up and gather where it sinks
  for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) { const c = y0 + x; fw[c] = .5 * (fx[y0 + (x + 1) % cw] - fx[y0 + (x - 1 + cw) % cw] + fy[yp + x] - fy[ym + x]) - fsrc[c]; } }
  for (let it = 0; it < 10; it++) {
    for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
      for (let x = 0; x < cw; x++) { const c = y0 + x; fp2[c] = .25 * (fp[y0 + (x + 1) % cw] + fp[y0 + (x - 1 + cw) % cw] + fp[yp + x] + fp[ym + x] - fw[c]); } }
    [fp, fp2] = [fp2, fp];
  }
  for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) { const c = y0 + x; fx[c] -= .5 * (fp[y0 + (x + 1) % cw] - fp[y0 + (x - 1 + cw) % cw]); fy[c] -= .5 * (fp[yp + x] - fp[ym + x]); } }
  if (P.eddies > 0) {                                                // vorticity confinement: eddies are kept from smoothing away
    for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
      for (let x = 0; x < cw; x++) { const c = y0 + x; fw[c] = .5 * (fy[y0 + (x + 1) % cw] - fy[y0 + (x - 1 + cw) % cw] - fx[yp + x] + fx[ym + x]); } }
    for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
      for (let x = 0; x < cw; x++) { const c = y0 + x, gx = .5 * (Math.abs(fw[y0 + (x + 1) % cw]) - Math.abs(fw[y0 + (x - 1 + cw) % cw])), gy = .5 * (Math.abs(fw[yp + x]) - Math.abs(fw[ym + x])), m = Math.hypot(gx, gy) + 1e-6;
        fx[c] += P.eddies * (gy / m) * fw[c]; fy[c] -= P.eddies * (gx / m) * fw[c]; } }
  }
  for (let c = 0; c < n; c++) { const m = Math.hypot(fx[c], fy[c]); if (m > .9) { fx[c] *= .9 / m; fy[c] *= .9 / m; } else if (!(m >= 0)) { fx[c] = 0; fy[c] = 0; } }
}

// ---------------- two layers: a floor layer (where the cells live) and a surface layer above it
// Warm water rises out of the floor layer into the surface layer and spreads; cool water sinks and returns along the floor.
// Each layer is a 2D field on the coarse grid. The upwelling w (per square) comes from buoyancy: floor water warmer than the
// water above it rises. Mass is kept across both layers: the floor's divergence is -w, the surface's +w, and w sums to zero.
let ux = new Float32Array(1), uy = new Float32Array(1), tsurf = new Float32Array(1), wup = new Float32Array(1), sdiv = new Float32Array(1), fps = new Float32Array(1);
let air = [], airStat = {lifted: 0, settled: 0, lost: 0, died: 0, dist: 0, maxDist: 0, time: 0, recent: []};
// one layer: drag, a push, self-advection, viscosity, a pressure solve to the target divergence, eddies, a speed limit
function layerSolve(u, v, target, drag, ax, ay, spx, spy, p) {
  const n = cw * chh, dr = 1 - drag;
  for (let c = 0; c < n; c++) { u[c] = u[c] * dr + ax + (spx ? spx[c] : 0); v[c] = v[c] * dr + ay + (spy ? spy[c] : 0); }
  for (let y = 0; y < chh; y++) for (let x = 0; x < cw; x++) {
    const c = y * cw + x, sx = x - u[c], sy = y - v[c], x0 = Math.floor(sx), y0 = Math.floor(sy), tx = sx - x0, ty = sy - y0;
    const xa = ((x0 % cw) + cw) % cw, xb = (xa + 1) % cw, ya = ((y0 % chh) + chh) % chh, yb = (ya + 1) % chh, i00 = ya * cw + xa, i10 = ya * cw + xb, i01 = yb * cw + xa, i11 = yb * cw + xb;
    fu2[c] = (1 - ty) * ((1 - tx) * u[i00] + tx * u[i10]) + ty * ((1 - tx) * u[i01] + tx * u[i11]);
    fv2[c] = (1 - ty) * ((1 - tx) * v[i00] + tx * v[i10]) + ty * ((1 - tx) * v[i01] + tx * v[i11]);
  }
  u.set(fu2); v.set(fv2);
  diffuseF(u, P.visc); diffuseF(v, P.visc);
  for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) { const c = y0 + x; fw[c] = .5 * (u[y0 + (x + 1) % cw] - u[y0 + (x - 1 + cw) % cw] + v[yp + x] - v[ym + x]) - target[c]; } }
  let a = p, b = fp2;
  for (let it = 0; it < 10; it++) {
    for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
      for (let x = 0; x < cw; x++) { const c = y0 + x; b[c] = .25 * (a[y0 + (x + 1) % cw] + a[y0 + (x - 1 + cw) % cw] + a[yp + x] + a[ym + x] - fw[c]); } }
    [a, b] = [b, a];
  }
  // ten passes: the last result is back in p
  for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) { const c = y0 + x; u[c] -= .5 * (p[y0 + (x + 1) % cw] - p[y0 + (x - 1 + cw) % cw]); v[c] -= .5 * (p[yp + x] - p[ym + x]); } }
  if (P.eddies > 0) {
    for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
      for (let x = 0; x < cw; x++) { const c = y0 + x; fw[c] = .5 * (v[y0 + (x + 1) % cw] - v[y0 + (x - 1 + cw) % cw] - u[yp + x] + u[ym + x]); } }
    for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
      for (let x = 0; x < cw; x++) { const c = y0 + x, gx = .5 * (Math.abs(fw[y0 + (x + 1) % cw]) - Math.abs(fw[y0 + (x - 1 + cw) % cw])), gy = .5 * (Math.abs(fw[yp + x]) - Math.abs(fw[ym + x])), m = Math.hypot(gx, gy) + 1e-6;
        u[c] += P.eddies * (gy / m) * fw[c]; v[c] -= P.eddies * (gx / m) * fw[c]; } }
  }
  for (let c = 0; c < n; c++) { const m = Math.hypot(u[c], v[c]); if (m > .9) { u[c] *= .9 / m; v[c] *= .9 / m; } else if (!(m >= 0)) { u[c] = 0; v[c] = 0; } }
}
function fluidStep2(cur, th, sp) {
  const n = cw * chh;
  if (!(cur > 0)) { fx.fill(0); fy.fill(0); ux.fill(0); uy.fill(0); wup.fill(0); return; }
  // buoyancy: floor water warmer than the water above it rises; the mean is taken out, so what rises somewhere sinks elsewhere
  let m = 0; for (let c = 0; c < n; c++) { const w = P.convect * cur * P.buoy * (temp[c] - tsurf[c]); wup[c] = w; m += w; } m /= n;
  for (let c = 0; c < n; c++) { let w = wup[c] - m; w = w > .3 ? .3 : w < -.3 ? -.3 : w; wup[c] = w; sdiv[c] = -w; }
  const tx = P.tide > 0 ? .02 * Math.cos(th) * cur * P.tide : 0, ty = P.tide > 0 ? .02 * Math.sin(th) * cur * P.tide : 0;   // the old cross-current, kept as an optional tide
  layerSolve(fx, fy, sdiv, P.fdrag, tx, ty, fvx, fvy, fp);            // the floor: drag, the vents' swirl, and it converges where water rises
  for (let c = 0; c < n; c++) sdiv[c] = wup[c];
  layerSolve(ux, uy, sdiv, P.sdrag, tx, ty, null, null, fps);         // the surface: little drag, and it spreads where water rises
  const k = P.shear, f = P.coriolis;
  if (k > 0 || f) for (let c = 0; c < n; c++) {
    if (k > 0) { const du = k * (ux[c] - fx[c]), dv = k * (uy[c] - fy[c]); fx[c] += du; fy[c] += dv; ux[c] -= du; uy[c] -= dv; }   // the layers drag on each other
    if (f) { let a = fx[c], b = fy[c]; fx[c] = a + f * b; fy[c] = b - f * a; a = ux[c]; b = uy[c]; ux[c] = a + f * b; uy[c] = b - f * a; }   // a turning of the earth
  }
}
// heat in two layers: each carried by its own current, exchanged up and down with the water that rises or sinks, and mixed a little
function heat2(D, R, hv, hl) {
  const n = cw * chh;
  advectSharp(temp, fx, fy); advectSharp(tsurf, ux, uy);
  const wk = P.wheat, vm = P.vmix;
  for (let c = 0; c < n; c++) {
    const w = wup[c], Tf = temp[c], Ts = tsurf[c];
    let a = 0, b = 0;
    if (w > 0) a = Math.min(.5, w * wk); else b = Math.min(.5, -w * wk);
    const d = vm * (Ts - Tf);
    tsurf[c] = Ts + a * (Tf - Ts) - d; temp[c] = Tf + b * (Ts - Tf) + d;
  }
  for (let y = 0; y < chh; y++) {
    const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) {
      const xm = (x - 1 + cw) % cw, xp = (x + 1) % cw, c = y0 + x;
      let T = temp[c];
      let v = T + D * (.25 * (temp[y0 + xm] + temp[y0 + xp] + temp[ym + x] + temp[yp + x]) - T) + R * P.floorRelax * (tamb[c] - T) + R * (hv * (P.plumeW < 1 ? .3 * vglow[c] + .7 * vhot[c] : vglow[c])) + hl * dens[c] / 16;
      tempTmp[c] = v < 0 ? 0 : v > 1.3 ? 1.3 : v;
      T = tsurf[c];
      v = T + D * (.25 * (tsurf[y0 + xm] + tsurf[y0 + xp] + tsurf[ym + x] + tsurf[yp + x]) - T) + R * P.airLoss * (tamb[c] - T);   // the surface gives its heat to the air
      rtmp[c] = v < 0 ? 0 : v > 1.3 ? 1.3 : v;
    }
  }
  [temp, tempTmp] = [tempTmp, temp]; tsurf.set(rtmp);
}
// spores ride the plume: a dormant loose cell where water rises strongly may be lifted into the surface layer, carried by the
// surface current, and settle back where it falls, mostly where water sinks
function sporeAir() {
  if (!(P.twoLayer || P.water3d) || !(P.current > 0) || P.env === 'even') { if (air.length) air = []; return; }
  const lift = P.sporeLift, n = cw * chh;
  if (lift > 0 && air.length < P.airMax) for (let i = 0; i < N; i++) {
    if (!alive[i] || body[i]) continue;
    const c = cmap[i], w = wup[c]; if (w <= .005) continue;
    const x = i % W, y = (i / W) | 0;
    let pr = lift * w * 10;
    if (!dor[i]) {                                           // an active cell is carried only if loose (few neighbours), and less often
      const xm = (x - 1 + W) % W, xp = (x + 1) % W, ym = ((y - 1 + H) % H) * W, y0 = y * W, yp = ((y + 1) % H) * W;
      if (alive[ym + xm] + alive[ym + x] + alive[ym + xp] + alive[y0 + xm] + alive[y0 + xp] + alive[yp + xm] + alive[yp + x] + alive[yp + xp] > 2) continue;
      pr *= P.cellLift;
    }
    if (rng() >= pr) continue;
    air.push({x: x / 4, y: y / 4, ox: x, oy: y, g: gen[i], xg: xg[i], rsv: rsv[i], dor: dor[i], t0: tick, ...seqTake(i)});
    alive[i] = 0; gen[i] = 0; xg[i] = 0; rsv[i] = 0; dor[i] = 0; changed[i] = 1; airStat.lifted++;
    if (air.length >= P.airMax) break;
  }
  if (!air.length) return;
  const keep = [];
  for (const s of air) {
    const qx = ((Math.floor(s.x) % cw) + cw) % cw, qy = ((Math.floor(s.y) % chh) + chh) % chh, c = qy * cw + qx;
    s.x += ux[c] + (rng() - .5) * .3; s.y += uy[c] + (rng() - .5) * .3;
    s.x = ((s.x % cw) + cw) % cw; s.y = ((s.y % chh) + chh) % chh;
    if (rng() < (s.dor ? P.sporeDeath * 2 : P.aloftDeath)) { airStat.died++; continue; }
    const w = wup[c], pset = P.settle * (1 + 4 * Math.max(0, -w) / .05) * (w > .02 ? .2 : 1);
    if (rng() >= pset) { keep.push(s); continue; }
    const q2x = ((Math.floor(s.x) % cw) + cw) % cw, q2y = ((Math.floor(s.y) % chh) + chh) % chh;
    let landed = -1;
    for (let k = 0; k < 6 && landed < 0; k++) {
      const x = Math.min(W - 1, q2x * 4 + Math.floor(rng() * 4)), y = Math.min(H - 1, q2y * 4 + Math.floor(rng() * 4)), i = y * W + x;
      if (!alive[i]) landed = i;
    }
    if (landed < 0) { airStat.lost++; continue; }
    const i = landed; alive[i] = 1; gen[i] = s.g; xg[i] = s.xg; rsv[i] = s.rsv; dor[i] = s.dor ? 1 : 0; body[i] = 0; changed[i] = 1; seqPut(i, s);
    const x = i % W, y = (i / W) | 0, dx = Math.min(Math.abs(x - s.ox), W - Math.abs(x - s.ox)), dy = Math.min(Math.abs(y - s.oy), H - Math.abs(y - s.oy)), d = Math.hypot(dx, dy);
    airStat.settled++; airStat.dist += d; airStat.time += tick - s.t0; if (d > airStat.maxDist) airStat.maxDist = d;
    airStat.recent.push(d); if (airStat.recent.length > 300) airStat.recent.shift();
  }
  air = keep;
}

// reactions: carbon dioxide, oxygen and water, one value per chemistry square (the energy molecule, en, is the sugar)
let rxSeason = 1, drifted = 0, buried = 0, fe = new Float32Array(1);   // fe: the iron in the ground that rusts, taking up oxygen
let wat = new Float32Array(1), co2 = new Float32Array(1), o2 = new Float32Array(1), rtmp = new Float32Array(1), dried = 0, carbonless = 0, enAer = 0;
const avgF = a => (a.reduce((s, v) => s + v, 0) / a.length).toFixed(2);
function diffuseF(a, D) {
  for (let y = 0; y < chh; y++) { const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) { const c = y0 + x, s = a[c]; rtmp[c] = s + D * (.25 * (a[y0 + (x - 1 + cw) % cw] + a[y0 + (x + 1) % cw] + a[ym + x] + a[yp + x]) - s); } }
  a.set(rtmp);
}
function rxnStep() {                                       // the water and the gases: carried, spread, rained in, dried out, breathed in and out by the air
  if (!P.rxn) return;
  const n = cw * chh, heat = P.env !== 'even';
  const sea = P.seasonLen > 0 ? .5 + .5 * Math.sin(6.2832 * tick / P.seasonLen) : 1, rn = P.rain * (1 - P.drySeason * (1 - sea));   // wet and dry seasons
  rxSeason = sea;
  if (P.current > 0 && heat) { advect(co2, rtmp, 1); co2.set(rtmp); advect(o2, rtmp, 1); o2.set(rtmp); advect(wat, rtmp, 1); wat.set(rtmp); }
  const spz = P.env === 'springs' && P.springZone !== false;
  if (spz) {                                               // the springs' runoff: water runs downhill from the source, a little each step (upwind transfer along the slope)
    const ux = Math.cos(SPR.dir), uy = Math.sin(SPR.dir), f = P.springFlow, ax = Math.abs(ux) * f, ay = Math.abs(uy) * f, sx = ux > 0 ? 1 : -1, sy = uy > 0 ? 1 : -1;
    rtmp.set(wat);
    for (let y = 0; y < chh; y++) for (let x = 0; x < cw; x++) { const c = y * cw + x, w = wat[c], mx = ax * w, my = ay * w;
      rtmp[c] -= mx + my; rtmp[y * cw + ((x + sx + cw) % cw)] += mx; rtmp[((y + sy + chh) % chh) * cw + x] += my; }
    wat.set(rtmp);
  }
  diffuseF(co2, .2); diffuseF(o2, .2); diffuseF(wat, .05);
  if (P.env === 'pond' && P.pondInflow > 0 && PIN.mouths.length) {   // dissolved organic matter (sugar) arrives from outside the pond: an import, booked in enMade and PIN.got
    const tot = P.pondInflow * n / 1000 * (rn / Math.max(1e-9, P.rain)), ws = PIN.mouths.reduce((a, m) => a + m.w, 0);
    for (const m of PIN.mouths) { const r = Math.ceil(m.s * 2.5), cx = Math.round(m.x), cy = Math.round(m.y), k2 = 1 / (2 * m.s * m.s); let z = 0;
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r) z += Math.exp(-(dx * dx + dy * dy) * k2);
      const a = tot * m.w / ws / z;
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) { const d2 = dx * dx + dy * dy; if (d2 > r * r) continue;
        const ci = (((cy + dy) % chh + chh) % chh) * cw + (((cx + dx) % cw + cw) % cw), v = a * Math.exp(-d2 * k2); en[ci] += v; enMade += v; PIN.got += v; } }
  }
  for (let c = 0; c < n; c++) {
    if (spz) { const src = Math.min(1, vglow[c] / P.ventPower), r = (src > .05 ? .3 * src : 0) * (P.springSrc * src - wat[c]) + P.springRain * (P.wrain - wat[c]);   // water wells up at the springs; the land gets only a little rain
      if (r > 0) OLF.watW += r; wat[c] += r - P.evap * temp[c] * wat[c]; }
    else { const r = (heat ? rn : .2) * (P.wrain - wat[c]); if (r > 0) OLF.watW += r; wat[c] += r - (heat ? P.evap * temp[c] * wat[c] : 0); }
    { const ci = P.gasx * (P.co2air - co2[c]) + P.vco2 * vglow[c]; if (ci > 0) OLF.co2W += ci; co2[c] += ci; }
    if (fe[c] > 0 && o2[c] > 0) { const a = Math.min(fe[c], o2[c] * .3); fe[c] -= a; o2[c] -= a; }   // iron rusts, soaking up oxygen until it is used up
    o2[c] -= P.o2sink * o2[c];
    if (P.env === 'dish') o2[c] += P.dishAir * ((P.o2air || 4) - o2[c]);   // a dish sits open to today's air: oxygen comes in at its surface
    const bu = P.env === 'dish' ? 0 : P.bury * en[c]; en[c] -= bu; buried += bu;     // a little sugar sinks into the mud and is buried for good; its oxygen stays behind
    if (wat[c] < 0) wat[c] = 0; if (co2[c] < 0) co2[c] = 0; if (o2[c] < 0) o2[c] = 0;
  }
}
// a cell burns sugar from the water: with oxygen (sugar + O2 -> CO2 + water) at full yield, without it by fermenting (sugar -> CO2) at a lower one
function burn(sq, want, cap, y) {
  if (!P.rxn) { const t = Math.min(en[sq], cap, want / y); if (!(t > 0)) return 0; en[sq] -= t; enTaken += t; enGot += t * y; return t * y; }
  let a = Math.min(en[sq], cap, want / y, o2[sq]); if (!(a > 0)) a = 0;
  en[sq] -= a; o2[sq] -= a; co2[sq] += a; wat[sq] += a * P.wfix; OLF.co2L += a; OLF.watL += a * P.wfix; let e = a * y, t = a; enAer += a;
  const yf = y * P.ferm, rest = want - e, cap2 = cap - a;
  if (rest > 0 && cap2 > 0 && yf > 0) { const f = Math.min(en[sq], cap2, rest / yf); if (f > 0) { en[sq] -= f; co2[sq] += f; OLF.co2L += f; e += f * yf; t += f; } }
  enTaken += t; enGot += e; return e;
}
// drying: a cell in dry ground may lose its water and die; exposed cells dry faster, and a body shelters its cells
function dryKill(i, n) { const w = wat[cmap[i]]; if (w >= P.wdry) return false; const hit = rng() < P.dryHarm * (1 - w / P.wdry) * (.3 + .7 * (8 - n) / 8) * (body[i] ? .4 : 1) * (dor[i] ? .1 : 1) * (1 - .25 * CA(i, 3)); if (hit) dried++; return hit; }
// drift: a loose cell (few neighbours, not held in a body) is carried along by the current
function driftPass() {
  drifted = 0; const dr = P.drift; if (!(dr > 0) || !(P.current > 0) || P.env === 'even') return;
  hopm.fill(0);
  for (let y = 0; y < H; y++) { const ym = ((y - 1 + H) % H) * W, y0 = y * W, yp = ((y + 1) % H) * W;
    for (let x = 0; x < W; x++) {
      const i = y0 + x; if (!alive[i] || hopm[i] || body[i]) continue;
      const xm = (x - 1 + W) % W, xp = (x + 1) % W;
      const n = alive[ym + xm] + alive[ym + x] + alive[ym + xp] + alive[y0 + xm] + alive[y0 + xp] + alive[yp + xm] + alive[yp + x] + alive[yp + xp];
      if (n > (dor[i] ? 6 : 2)) continue;                // a spore is carried even out of a crowd
      const c = cmap[i], u = fx[c] * 4, v = fy[c] * 4, s = Math.abs(u) + Math.abs(v);   // the current in cells per two ticks
      if (s < 1e-4 || rng() >= dr * s * .5) continue;
      const dx = rng() * s < Math.abs(u) ? Math.sign(u) : 0, dy = rng() * s < Math.abs(v) ? Math.sign(v) : 0; if (!dx && !dy) continue;
      const j = ((y + dy + H) % H) * W + ((x + dx + W) % W); if (alive[j]) continue;
      alive[j] = 1; gen[j] = gen[i]; xg[j] = xg[i]; rsv[j] = rsv[i]; dor[j] = dor[i]; light[j] = light[i]; light[i] = 0; if (P.seqOn) moveSeq(i, j); virMove(i, j); alive[i] = 0; gen[i] = 0; rsv[i] = 0; dor[i] = 0; hopm[j] = 1;
      changed[i] = 1; changed[j] = 1; drifted++;
    } }
}
function hudSet(full, s) {                               // the status line: short by default, the full account on click (or on hover)
  const hd = document.getElementById('hud'), pp = series.length ? series[series.length - 1].pop : 0;
  const short = popActive() ? popHud() + ` · zoom ${s.toFixed(1)}` : popWin ? `patch open at the scale of single cells · tick ${tick} · ${pp.toLocaleString()} cells · born ${births} · died ${deaths} · zoom ${s.toFixed(1)}` : `tick ${tick} · ${pp.toLocaleString()} cells · born ${births} · died ${deaths}${(() => { const k = air.length + (typeof G3 === 'object' && G3.slots ? G3.slots.reduce((a, s) => a + (s ? 1 : 0), 0) : 0); return k ? ' · ' + k.toLocaleString() + ' in the water' : ''; })()}${P.fragOn && frAmt ? ' · ' + fragCount().toLocaleString() + ' kinds of chain in the ground (longest ' + FRS.longest + ')' : ''}${restarts ? ' · restarted ' + restarts + (restarts > 1 ? ' times' : ' time') : ''}${P.rxn && P.env !== 'even' && P.seasonLen > 0 ? (rxSeason < .5 ? ' · dry season' : ' · wet season') : ''} · zoom ${s.toFixed(1)}`;
  hd.textContent = P.hudFull ? full : short; hd.title = full;
}
// spores: a cell with the spore-forming gene that starves or dries out may go dormant; a spore wakes when light and water return
function sporePass() {
  if (!P.gSpore) return;
  for (let i = 0; i < N; i++) {
    if (!alive[i]) continue; const e = (xg[i] >> 14) & 3;
    if (!e) { if (dor[i]) dor[i] = 0; continue; }
    const c = cmap[i], dry = P.rxn && wat[c] < P.wdry;
    if (!dor[i]) { if ((dry || light[i] < P.sporeLight) && rng() < P.sporeRate * e) { dor[i] = 1; changed[i] = 1; } }
    else if (!dry && light[i] > P.wakeLight && rng() < P.wakeRate) { dor[i] = 0; changed[i] = 1; }
  }
}
// a start that fizzles out: the one organism carries Conway's rule, and a small seed under it often dies within a few
// hundred ticks. With autoRestart on, the page quietly sows a fresh seed (up to 20 times) instead of showing an empty world
let restarts = 0, lastMode = null;
// (13 November, Justin's note) a fizzle is judged by what the colony does, not by a headcount in the first 400 ticks:
// slow, long-lived colonies can keep 8 cells past tick 400 and still be doomed. Up to restartWindow ticks, restart if fewer
// than 8 cells are alive, or if no cell has been born for restartQuiet ticks. Not in the dish, where a colony that has
// stopped growing is the result.
let erB = 0, erT = 0, erStart = 0;   // erStart: the start's size, counted at tick 10
function earlyCheck() {
  if (!P.autoRestart || lastMode !== 'organism' || P.env === 'dish' || restarts >= 20) return;
  if (tick < erT || tick <= 1) { erT = tick; erB = 0; }
  erB += births; if (tick > P.restartWindow || tick % 10) return;
  const full = tick === 10 || tick === P.restartGrow; let n = 0; for (let i = 0; i < N && (full || n < 8); i++) n += alive[i];
  if (tick === 10) erStart = n;
  const quiet = tick - erT >= P.restartQuiet, failed = tick === P.restartGrow && n < erStart;   // by restartGrow it holds fewer cells than it began with
  if (n < 8 || (quiet && erB === 0) || failed) { restarts++; log(n < 8 ? 'The start fizzled out; a new one is seeded.' : failed ? `By tick ${P.restartGrow} the start held fewer cells than it began with (${n} of ${erStart}); a new one is seeded.` : `No cell was born in ${P.restartQuiet} ticks; the start is judged a fizzle and a new one is seeded.`); erT = 0; erB = 0; reset('organism', true); return; }
  if (quiet) { erT = tick; erB = 0; }
}
// ---------------- the line of expression: each cell carries an ordered sequence of monomers (the 16 molecules). Infolding it
// gives its compound: reading along, a monomer that meets its complement (the molecule eight places away) pairs with it and
// both are buried; the monomers left unpaired are exposed, and their counts (up to 3 each) are the compound's exponents
const SL = 256, MONO = 'abcdefghijklmnop';
let seq = new Uint8Array(1), slen = new Uint8Array(1), seqMut = 0, seqNeutral = 0;
// the buried pairs work: a pair of monomer k with its complement k+8 is an enzyme of kind k (strength up to 3), kept in cat[i], two bits a kind
let cat = new Uint16Array(1), lastCat = 0;
let cH = new Uint32Array(1), codeChg = 0, codeBirths = 0, coatMade = 0, rxAct = new Float32Array(1), coat = new Float32Array(1), rx = new Uint32Array(1), rxStr = new Uint8Array(1), rx2 = new Uint32Array(1), rxStr2 = new Uint8Array(1), rxRun = 0, rxGain = 0, rxCost = 0;   // each cell's reactions (see domReact)
const CATN = ['light harvest', 'respiration', 'uptake', 'keeping water', 'heat tolerance', 'copying fidelity', 'defence', 'building'];
const CA = (i, k) => P.catOn ? (cat[i] >> (2 * k)) & 3 : 0;
let sOrg = new Uint8Array(1); const oTmp = new Uint8Array(SL * 2);   // where each monomer came from (display only): 0 by descent, 1 from outside (another cell, the water), 2 from a virus
function ORG() { if (sOrg.length !== N * SL) sOrg = new Uint8Array(N * SL); return sOrg; }
const sTmp = new Uint8Array(SL * 2), sStk = new Uint8Array(SL * 2), sEx = new Uint8Array(16);
function seqAlloc() { cH = new Uint32Array(N); coat = new Float32Array(N); rxAct = new Float32Array(N); seq = new Uint8Array(N * SL); slen = new Uint8Array(N); cat = new Uint16Array(N); rx = new Uint32Array(N); rxStr = new Uint8Array(N); regd = new Uint8Array(N); regList.length = 0; }
// the nucleus regulates expression (the second articulation): a clump whose code says so silences one kind of monomer in its
// soma cells, which then infold without it. Their sequence is untouched, so a cell that leaves, and every child, expresses it all
let regd = new Uint8Array(1), regN = 0; const regList = [];
function regRestore() {
  for (const i of regList) { if (regd[i] && alive[i] && slen[i]) { gen[i] = infold(seq, i * SL, slen[i]); cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH; changed[i] = 1; } regd[i] = 0; }
  regList.length = 0; regN = 0;
}
function regApply(i, sk) {
  if (!slen[i]) seqFromGen(i, gen[i]); const o = i * SL, n = slen[i]; let m = 0;
  for (let h = 0; h < n; h++) if (seq[o + h] !== sk) sTmp[m++] = seq[o + h];
  gen[i] = infold(sTmp, 0, m); cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH; regd[i] = 1; regList.push(i); regN++; changed[i] = 1;
}
// domains: the pairs nest like brackets. A pair together with everything folded inside it is a domain; the outer pair names
// its job (enzyme kind k for a pair of k with k+8). Inner pairs of the same kind fold it more firmly (+1 strength each);
// inner pairs of other kinds are held inside it and do not act on their own. Only the outermost domains work.
// dN top-level domains, with kind dK, strength dS, and span dA..dB (inclusive, positions in the sequence)
const sPos = new Uint8Array(SL * 2), dK = new Uint8Array(SL), dS = new Uint8Array(SL), dA = new Uint8Array(SL), dB = new Uint8Array(SL), dO = new Uint8Array(SL), dQ = new Uint16Array(SL), dT = new Uint16Array(SL);
let lastRx = 0, lastRxS = 0, lastRx2 = 0, lastRxS2 = 0;
let dN = 0, dHidden = 0, dPairs = 0;
// reactions from shape: a domain turns one molecule into another. What it takes is the monomer that opens its outer pair;
// what it makes is set by the monomers folded inside it: (taken + 1 + the inner sum) mod 16, where the inner sum adds the
// opening monomers of the pairs inside, weighted by depth (once directly inside, twice one level deeper, and so on).
// So a lone pair makes the next molecule up, and every inner pair, of any kind, reshapes the pocket. Each molecule's energy
// is the log of its prime: a reaction down the ladder (a larger prime to a smaller) yields light, one up it costs light.
// Strength (inner pairs of the same kind) sets the rate. One byte a reaction, up to 4 a cell: taken << 4 | made.
const RXE = new Float32Array(16); { const pr = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]; for (let k = 0; k < 16; k++) RXE[k] = Math.log(pr[k]) / Math.log(53); }
// adaptors: the cell's own reading code. code[q] is the shift that an inner sum q gives; by default it is q itself (the fixed
// rule, kept as the primordial chemistry). The domains at the head of the sequence, before its first unpaired monomer, are
// adaptors: each sets code[its inner sum] = its opening monomer, the nearest to the front winning. They run no reaction.
const sCode = new Uint8Array(16), sAd = new Uint8Array(SL); let lastCH = 0, lastAd = 0;
function rxOf(d) { const s = dO[d] & 15; let t = (s + 1 + sCode[dQ[d] & 15]) & 15; if (t === s) t = s ^ 8; return (s << 4) | t; }
function domReact(i) { domReactW(i, rx[i], rxStr[i]); if (rx2[i]) domReactW(i, rx2[i], rxStr2[i]);
  if (P.domCost > 0) { let nr = 0; for (let q = 0; q < 4; q++) { if ((rx[i] >>> (8 * q)) & 255) nr++; if ((rx2[i] >>> (8 * q)) & 255) nr++; }   // each working domain costs a little to keep running (Justin, 16 November): a repeated reaction runs faster but each copy pays
    const c = P.domCost * nr; light[i] -= c; domCostSum += c; } }
let domCostSum = 0;   // a cell's reactions, from all its genes
function domReactW(i, r, st) {                             // run one word of reactions on the cell's own square's molecules
  const c = cmap[i] << 4;
  for (let q = 0; q < 4; q++) { const b = (r >>> (8 * q)) & 255; if (!b) break; const s = b >> 4, t = b & 15, k = (st >> (2 * q)) & 3 || 1;
    if (t === (s ^ 8) && P.cellClumps && P.sugarCoat > 0) {   // a fold that pairs a monomer with its complement chains sugar instead:
      const use = Math.min(P.sugarCoat * k, en[cmap[i]]), work = .2 * use; if (use > 0 && light[i] > P.sugarKeep + work) { coatAlloc(); en[cmap[i]] -= use; coatS[i] += use; light[i] -= work; coat[i] += use; rxCost += work; coatMade += use; }   // coat is made of sugar; building it costs a little energy
      continue; }
    // product inhibition: a reaction slows as its product builds up around the cell (in its square, and in its clump's matrix),
    // so the same fold works hard where its product is scarce and idles where it is plentiful. Regulation by position, from chemistry alone
    let f = chem[c + s] / (P.rxKm + chem[c + s]); if (P.rxInhib) { const S = chem[c + s], pl = body[i] && P.cellClumps ? mxPool.get(body[i]) : null, bo = pl ? bodies.get(body[i]) : null;
      const Pr = chem[c + t] + (pl && bo ? pl[t] * 16 / Math.max(16, bo.size) : 0); f = S / (P.rxKm + S + Pr); }   // Michaelis-Menten, with the product competing for the enzyme (inhibition constant = rxKm)
    const amt = P.rxRate * P.chunit * k * f; if (amt <= 0 || chem[c + s] < amt) continue; rxAct[i] += amt / P.chunit;
    const dR = RXE[s] - RXE[t], de = dR >= 0 ? P.rxE * k * f * dR : amt * dR * amt / (P.rxE * k * f + 1e-12); if (de < 0 && light[i] < -de) continue;   // downhill: a share of the energy released (rxE/rxRate); uphill: the energy stored, divided by the same share, and only if the cell can pay
    const kept = P.cellClumps ? P.coatFrac * amt : 0; if (kept) { coatAlloc(); coat[i] += (kept / P.chunit) * RXE[t]; if (coatM[i] && coatK[i] !== t) { chem[c + coatK[i]] += coatM[i]; coatM[i] = 0; } coatK[i] = t; coatM[i] += kept; }   // the kept molecules become coat, and stay matter
    const pl = body[i] && P.cellClumps ? mxPool.get(body[i]) : null, held = pl ? P.mxRetain * (amt - kept) : 0;   // the matrix keeps part of what a clump's cells make
    if (pl) pl[t] += held;
    chem[c + s] -= amt; chem[c + t] += amt - kept - held; light[i] += de; rxRun++; if (de > 0) rxGain += de; else rxCost -= de; }
}
function infoldGene(a, o, n) {
  let sp = 0; sEx.fill(0); dN = 0; dHidden = 0; dPairs = 0;
  for (let h = 0; h < n; h++) { const m = a[o + h];
    if (sp && sStk[sp - 1] === (m ^ 8)) { sp--; const k = m & 7, op = sPos[sp]; dPairs++;
      if (!P.domOn) { sEx[k]++; continue; }
      // the inner sum, weighted by depth: pairs directly inside count once, one level deeper twice, and so on (your option A).
      // dT keeps the plain total of the openers inside, so each level adds one more weight to everything beneath it
      let st = 1, q = 0, tt = 0; while (dN && dA[dN - 1] > op) { dN--; q += dO[dN] + dQ[dN] + (P.depthW ? dT[dN] : 0); tt += dO[dN] + dT[dN]; if (dK[dN] === k) st += dS[dN]; else dHidden++; }
      dK[dN] = k; dS[dN] = st; dA[dN] = op; dB[dN] = h; dO[dN] = a[o + op]; dQ[dN] = q; dT[dN] = tt; dN++; }
    else { sPos[sp] = h; sStk[sp++] = m; } }
  for (let q = 0; q < 16; q++) sCode[q] = q; lastCH = 0; lastAd = 0; for (let d = 0; d < dN; d++) sAd[d] = 0;
  if (P.adapt && P.domOn && sp > 0) { const head = sPos[0]; const set = new Uint8Array(16);
    for (let d = 0; d < dN && dB[d] < head; d++) { sAd[d] = 1; lastAd++; const q = dQ[d] & 15; if (!set[q]) { set[q] = 1; sCode[q] = dO[d] & 15; } }
    for (let q = 0; q < 16; q++) if (sCode[q] !== q) lastCH = (Math.imul(lastCH ^ (q * 16 + sCode[q] + 1), 2654435761) >>> 0) || 1; }
  lastRx = 0; lastRxS = 0; let nr = 0;
  if (P.domOn && P.rxDom) { for (let d = 0; d < dN && nr < 4; d++) if (dS[d] >= P.domMin && !sAd[d]) { lastRx |= rxOf(d) << (8 * nr); lastRxS |= Math.min(3, dS[d]) << (2 * nr); nr++; } }   // the domains' reactions; the named jobs are off
  else if (P.domOn) for (let d = 0; d < dN; d++) if (dS[d] >= P.domMin) sEx[dK[d]] += dS[d];     // a fold too small to be stable does not work
  lastCat = 0; for (let k = 0; k < 8; k++) lastCat |= Math.min(3, sEx[k]) << (2 * k);
  sEx.fill(0); for (let h = 0; h < sp; h++) sEx[sStk[h]]++;
  let g = 0; for (let k = 0; k < 16; k++) g = (g | (Math.min(3, sEx[k]) << (2 * k))) >>> 0; return g;
}
function seqFromGen(i, g) {                               // a cell with no sequence yet (the first organism, a painted cell) gets one that infolds to its compound
  if (slen.length !== N) seqAlloc(); g = g >>> 0;
  const o = i * SL; let n = 0; ORG().fill(0, o, o + SL);
  for (let k = 0; k < 16; k++) { const e = (g >>> (2 * k)) & 3; for (let q = 0; q < e; q++) seq[o + n++] = k; }
  slen[i] = n; if (infold(seq, o, n) === g) { cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH; return; }
  for (let t = 0; t < 40; t++) { for (let h = n - 1; h > 0; h--) { const r = (rng() * (h + 1)) | 0, x = seq[o + h]; seq[o + h] = seq[o + r]; seq[o + r] = x; } if (infold(seq, o, n) === g) break; }
  cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH;
}
function seqBirth(i, pj, pb, rate) {                      // copy (or cross) the parents' sequences into the child, with errors, duplications and deletions
  coat[i] = 0; rxAct[i] = 0; const pCH = pj >= 0 ? cH[pj] : 0;
  if (slen.length !== N) seqAlloc();
  if (!slen[pj]) seqFromGen(pj, gen[pj]);
  const L = slen[pj], o = pj * SL; let n = 0, ch = false; const OG = ORG();
  if (pb >= 0 && pb !== pj) { if (!slen[pb]) seqFromGen(pb, gen[pb]); const Lb = slen[pb], ob = pb * SL, cut = 1 + ((rng() * Math.max(1, Math.min(L, Lb) - 1)) | 0);
    for (let h = 0; h < Math.min(cut, L); h++) { oTmp[n] = OG[o + h]; sTmp[n++] = seq[o + h]; } for (let h = cut; h < Lb && n < SL; h++) { oTmp[n] = OG[ob + h]; sTmp[n++] = seq[ob + h]; } }
  else for (let h = 0; h < L; h++) { oTmp[n] = OG[o + h]; sTmp[n++] = seq[o + h]; }
  const p = rate * P.seqMu * (1 - .25 * CA(pj, 5));          // the parent's copying-fidelity enzyme proofreads the copy
  for (let h = 0; h < n; h++) if (rng() < p) { sTmp[h] = (rng() * 16) | 0; ch = true; }
  if (n > 1 && rng() < P.seqDup) { const len = 1 + ((rng() * Math.min(4, n)) | 0), a = (rng() * (n - len + 1)) | 0;      // a stretch copied twice: the second copy is free to vary
    if (n + len <= SL) { oTmp.copyWithin(a + len, a, n); for (let h = n - 1; h >= a + len; h--) sTmp[h + len] = sTmp[h]; for (let q = 0; q < len; q++) sTmp[a + len + q] = sTmp[a + q]; n += len; ch = true; } }
  if (P.domOn && P.domDup > 0 && n > 3 && rng() < P.domDup) {     // a whole domain copied twice: the second copy is free to drift into a new job
    infold(sTmp, 0, n); if (dN) { const d = (rng() * dN) | 0, a = dA[d], len = dB[d] - a + 1;
      if (n + len <= SL) { oTmp.copyWithin(dB[d] + 1 + len, dB[d] + 1, n); oTmp.copyWithin(dB[d] + 1, a, a + len); for (let h = n - 1; h > dB[d]; h--) sTmp[h + len] = sTmp[h]; for (let q = 0; q < len; q++) sTmp[dB[d] + 1 + q] = sTmp[a + q]; n += len; ch = true; domDupN++; } } }
  if (n > 2 && rng() < P.seqDel) { const len = 1 + ((rng() * Math.min(4, n - 1)) | 0), a = (rng() * (n - len + 1)) | 0;
    oTmp.copyWithin(a, a + len, n); for (let h = a; h + len < n; h++) sTmp[h] = sTmp[h + len]; n -= len; ch = true; }
  { const n1 = geneOps(sTmp, n, oTmp); if (n1 !== n) { n = n1; ch = true; } }   // whole genes duplicated or lost
  const oi = i * SL; for (let h = 0; h < n; h++) seq[oi + h] = sTmp[h]; slen[i] = n; OG.set(oTmp.subarray(0, n), oi);
  const g = infold(seq, oi, n); cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH; codeBirths++; if (lastCH !== pCH) codeChg++;
  if (ch && pb < 0) { seqMut++; if (g === (gen[pj] >>> 0)) seqNeutral++; }
  return g;
}
let hgtTried = 0, hgtFailed = 0, domDupN = 0;
function seqTransfer(i, j) { GT.j = -1; if (P.geneHGT > 0 && rng() < P.geneHGT) { const r = geneTransfer(i, j); if (r !== null) return r; }                              // contagion: a stretch of one cell's sequence is spliced into its neighbour's
  if (slen.length !== N) seqAlloc(); tuJ = -1;
  if (!slen[i]) seqFromGen(i, gen[i]); if (!slen[j]) seqFromGen(j, ngen[j]);
  const Li = slen[i], Lj = slen[j]; if (Li < 2 || Lj < 2) return ngen[j] >>> 0;
  let len = Math.min(2 + ((rng() * 5) | 0), Li, Lj), a = (rng() * (Li - len + 1)) | 0;
  if (P.domOn && P.domHGT) { infold(seq, i * SL, Li); if (!dN) return ngen[j] >>> 0;       // contagion moves a whole working domain
    const d = (rng() * dN) | 0; len = dB[d] - dA[d] + 1; a = dA[d]; if (len > Lj) return ngen[j] >>> 0; }
  let b = (rng() * (Lj - len + 1)) | 0;
  const k = P.hgtHom | 0;                                  // homology: the stretch goes in only where the k monomers before it match the
  if (k > 0) {                                             // recipient's, so the more two sequences differ, the less often a splice takes
    hgtTried++; if (a < k) { hgtFailed++; return ngen[j] >>> 0; }
    const oi = i * SL, oj = j * SL, at = [];
    for (let p = k; p + len <= Lj; p++) { let ok = true; for (let q = 1; q <= k; q++) if (seq[oj + p - q] !== seq[oi + a - q]) { ok = false; break; } if (ok) at.push(p); }
    if (!at.length) { hgtFailed++; return ngen[j] >>> 0; }
    b = at[(rng() * at.length) | 0];
  }
  tuJ = j; tuB = b; tuLen = len; tuCat = cat[j]; tuRx = rx[j]; tuRxS = rxStr[j]; tuCH = cH[j];   // kept so a refused splice can be undone
  { const OG = ORG(); for (let q = 0; q < len; q++) { tuOldO[q] = OG[j * SL + b + q]; if (seq[j * SL + b + q] !== seq[i * SL + a + q]) OG[j * SL + b + q] = OG[i * SL + a + q] || 1; } }   // only monomers that actually change are marked: a stretch identical to what was there leaves the tag as it was
  for (let q = 0; q < len; q++) { tuOld[q] = seq[j * SL + b + q]; seq[j * SL + b + q] = seq[i * SL + a + q]; }
  const g = infold(seq, j * SL, Lj); cat[j] = lastCat; rx[j] = lastRx; rxStr[j] = lastRxS; cH[j] = lastCH; return g;
}
let tuJ = -1, tuB = 0, tuLen = 0, tuCat = 0, tuRx = 0, tuRxS = 0, tuCH = 0; const tuOld = new Uint8Array(256), tuOldO = new Uint8Array(256);
function seqTransferUndo(j) { if (GT.j === j) { geneTransferUndo(j); return; }                             // the page refused the splice (the cell cannot pay): its sequence and program go back
  if (tuJ !== j) return; for (let q = 0; q < tuLen; q++) { seq[j * SL + tuB + q] = tuOld[q]; sOrg[j * SL + tuB + q] = tuOldO[q]; }
  cat[j] = tuCat; rx[j] = tuRx; rxStr[j] = tuRxS; cH[j] = tuCH; tuJ = -1;
}
function moveSeq(a, b) { if (slen.length !== N) seqAlloc(); { const OG = ORG(); OG.copyWithin(b * SL, a * SL, a * SL + slen[a]); } seq.copyWithin(b * SL, a * SL, a * SL + SL); slen[b] = slen[a]; slen[a] = 0; cat[b] = cat[a]; cat[a] = 0; rx[b] = rx[a]; rx[a] = 0; rxStr[b] = rxStr[a]; coat[b] = coat[a]; coat[a] = 0; cH[b] = cH[a]; cH[a] = 0; rxAct[b] = rxAct[a]; rxAct[a] = 0; if (regd[a]) { regd[b] = 1; regd[a] = 0; regList.push(b); } }
function seqHtml(i) {
  if (!P.seqOn || i == null || !alive[i]) return ''; if (slen.length !== N) seqAlloc(); if (!slen[i]) seqFromGen(i, gen[i]);
  const o = i * SL, n = slen[i], br = new Array(n).fill('·'), st = [];
  for (let h = 0; h < n; h++) { const m = seq[o + h]; if (st.length && seq[o + st[st.length - 1]] === (m ^ 8)) { br[st.pop()] = '('; br[h] = ')'; } else st.push(h); }
  let s = ''; for (let h = 0; h < n; h++) s += MONO[seq[o + h]];
  const work = P.catOn ? CATN.map((t, k) => CA(i, k) ? t + (CA(i, k) > 1 ? ' ×' + CA(i, k) : '') : '').filter(Boolean).join(', ') : '';
  let doms = ''; if (P.domOn && P.catOn) { infold(seq, o, n); const ds = [];
    for (let d = 0; d < dN; d++) { if (sAd[d]) { ds.push(`adaptor: inner sum ${dQ[d] & 15} now means a shift of ${MONO.indexOf ? dO[d] & 15 : dO[d]} (${dB[d] - dA[d] + 1} monomers, at the head)`); continue; }
      if (P.rxDom) { const b = rxOf(d), sm = b >> 4, t = b & 15, de = RXE[sm] - RXE[t];
        ds.push(`${t === (sm ^ 8) && P.cellClumps && P.sugarCoat > 0 ? 'sugar → coat (it chains its own sugar into a sticky coat)' : `${MONO[sm]} → ${MONO[t]}`} ×${dS[d]} (${t === (sm ^ 8) && P.cellClumps && P.sugarCoat > 0 ? '' : (de > 0 ? 'yields light; ' : 'costs light; ')}${dB[d] - dA[d] + 1} monomers${dS[d] < P.domMin ? ', too small to work' : ''})`); }
      else ds.push(`${CATN[dK[d]]} ×${dS[d]} (${dB[d] - dA[d] + 1} monomers)`); }
    doms = `<br>Domains, the outermost folds: ${ds.join(' · ') || 'none'}${dHidden ? `; ${dHidden} pair${dHidden > 1 ? 's' : ''} of other kinds held inside, not working` : ''}.`; }
  return `<div>Sequence, ${n} monomers (a = 2, b = 3, … p = 53):<br><span style="font-family:monospace">${s}<br>${br.join('')}</span><br>Infolded: the ${st.length} monomers left exposed make its compound${P.catOn && !P.rxDom ? `; the buried pairs work as enzymes: ${work || 'none'}` : ''}.${doms}</div>`;
}
function seqPanel() {
  if (!P.seqOn) return ''; if (slen.length !== N) seqAlloc();
  let n = 0, tl = 0; const ss = new Set(), gs = new Set();
  for (let i = 0; i < N; i += 3) { if (!alive[i] || !slen[i]) continue; n++; const o = i * SL, L = slen[i]; tl += L; let h = 2166136261; for (let q = 0; q < L; q++) h = Math.imul(h ^ seq[o + q], 16777619); ss.add((h ^ L) >>> 0); gs.add(gen[i]); }
  const ca = new Float32Array(8); if (P.catOn) for (let i = 0; i < N; i += 3) if (alive[i] && slen[i]) for (let k = 0; k < 8; k++) ca[k] += CA(i, k);
  const work = P.catOn && !P.rxDom && n ? '<br>Enzymes (average strength a cell): ' + CATN.map((t, k) => `${t} <b>${(ca[k] / n).toFixed(2)}</b>`).join(' · ') : '';
  let dom = ''; if (P.domOn && n) { let dn = 0, dsz = 0, dmul = 0, hid = 0, prs = 0, m = 0;
    for (let i = 0; i < N; i += 11) { if (!alive[i] || !slen[i]) continue; m++; infold(seq, i * SL, slen[i]); dn += dN; hid += dHidden; prs += dPairs;
      for (let d = 0; d < dN; d++) { dsz += dB[d] - dA[d] + 1; if (dS[d] > 1) dmul++; } }
    if (m && P.adapt) { const codes = new Map(); let wc = 0, tot2 = 0, ads = 0;
      for (let i = 0; i < N; i += 11) { if (!alive[i] || !slen[i]) continue; tot2++; const h = cH[i]; if (h) { wc++; codes.set(h, (codes.get(h) || 0) + 1); } }
      const top1 = [...codes.values()].sort((a, b) => b - a)[0] || 0;
      dom += `<br>Reading codes: <b>${Math.round(100 * wc / Math.max(1, tot2))}%</b> of cells read with a code their own adaptors changed · <b>${codes.size}</b> changed codes in the sample, the commonest held by ${Math.round(100 * top1 / Math.max(1, tot2))}% · code changed at <b>${codeBirths ? (100 * codeChg / codeBirths).toFixed(2) : 0}%</b> of births so far`; }
    if (m && P.rxDom) { const cnt = new Map(); let withRx = 0, tot = 0;
      for (let i = 0; i < N; i += 11) { if (!alive[i] || !slen[i]) continue; const r = rx[i]; if (r) withRx++; tot++;
        const seenR = new Set(); for (const w of [r, rx2[i]]) for (let q = 0; q < 4; q++) { const b = (w >>> (8 * q)) & 255; if (!b) break; seenR.add(b); } for (const b of seenR) cnt.set(b, (cnt.get(b) || 0) + 1); }   // each reaction counted once a cell, from both words
      const top = [...cnt.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5).map(([b, c]) => `${(b & 15) === ((b >> 4) ^ 8) && P.cellClumps && P.sugarCoat > 0 ? 'sugar→coat' : MONO[b >> 4] + '→' + MONO[b & 15]} ${Math.round(100 * c / Math.max(1, tot))}%`).join(', ');
      dom += `<br>Reactions: <b>${Math.round(100 * withRx / Math.max(1, tot))}%</b> of cells run at least one · most common: ${top || 'none'} · light gained <b>${rxGain.toFixed(0)}</b>, spent <b>${rxCost.toFixed(0)}</b> so far`; }
    if (m && P.seqOn) { let tg = 0, multi = 0, mk = 0, ml = 0, dupG = 0, mx = 1, nO = 0, nV = 0; const OG = ORG();
      for (let i = 0; i < N; i += 11) { if (!alive[i] || !slen[i]) continue; const o = i * SL, L = slen[i], k = geneSegs(seq, o, L); tg += k; if (k > 1) multi++; if (k > mx) mx = k; ml += L;
        let inG = 0; for (let q = 0; q < k; q++) inG += gSeg[2 * q + 1] - gSeg[2 * q]; mk += L - inG; for (let h = 0; h < L; h++) { const v = OG[o + h]; if (v === 1) nO++; else if (v === 2) nV++; }
        const seen = new Set(); for (let q = 0; q < k; q++) { const t = seq.slice(o + gSeg[2 * q], o + gSeg[2 * q + 1]).join(','); if (seen.has(t)) dupG++; else seen.add(t); } }
      dom += `<br>Genes: <b>${(tg / m).toFixed(2)}</b> a cell · <b>${Math.round(100 * multi / m)}%</b> of cells carry more than one (most <b>${mx}</b>) · <b>${ml ? Math.round(100 * mk / ml) : 0}%</b> of monomers are gene markers · <b>${tg ? Math.round(100 * dupG / tg) : 0}%</b> of genes are exact copies of another in the same cell · monomers by origin: <b>${ml ? (100 * nV / ml).toFixed(1) : 0}%</b> from viruses, <b>${ml ? (100 * nO / ml).toFixed(1) : 0}%</b> from outside, the rest by descent ${P.domCost > 0 ? ` · working domains have cost <b>${domCostSum.toFixed(0)}</b> light so far` : ''} · so far ${geneDupN} genes duplicated, ${geneDelN} lost, ${geneHGTN} passed between cells, ${virIntegN} taken in from viruses`; }
    if (m) dom = dom + `<br>Domains: <b>${(dn / m).toFixed(1)}</b> a cell, averaging <b>${dn ? (dsz / dn).toFixed(1) : 0}</b> monomers · <b>${dn ? Math.round(100 * dmul / dn) : 0}%</b> folded firmer by a same-kind pair inside · <b>${prs ? Math.round(100 * hid / prs) : 0}%</b> of pairs held inside another kind's domain${P.domDup > 0 ? ` · ${domDupN} whole domains duplicated so far` : ''}`; }
  return n ? `<div style="margin-bottom:6px;color:var(--muted)">Line of expression: sequences average <b>${(tl / n).toFixed(1)}</b> monomers · <b>${ss.size}</b> different sequences make <b>${gs.size}</b> compounds · <b>${seqMut ? Math.round(100 * seqNeutral / seqMut) : 0}%</b> of copying errors left the compound unchanged${work}${dom}</div>` : '';
}
// ---------------- open, lift and fold, as readouts (measures, not causes)
// open: an input stops being food once the living supply most of it. For CO2, water and the ground's molecules the page weighs
// what life puts back (breathing, rot, the dead, producers) against what the world brings (air, vents, rain, regrowth)
const OLF = {co2L: 0, co2W: 0, watL: 0, watW: 0, minL: 0, minW: 0, e: {co2: [0, 0], wat: [0, 0], min: [0, 0]}, st: {}};
function olfReset() { for (const k of ['co2L', 'co2W', 'watL', 'watW', 'minL', 'minW']) OLF[k] = 0; OLF.e = {co2: [0, 0], wat: [0, 0], min: [0, 0]}; OLF.st = {}; }
const olfShare = k => { const [l, w] = OLF.e[k]; return l + w > 0 ? l / (l + w) : 0; };
function olfMark(key, on, upText, downText) {          // log a crossing once, with a little hysteresis so noise does not flicker it
  const was = !!OLF.st[key];
  if (!was && on > .55) { OLF.st[key] = 1; log(upText); } else if (was && on < .45) { OLF.st[key] = 0; log(downText); }
}
function olfStep() {
  const a = .98;
  for (const [k, l, w] of [['co2', 'co2L', 'co2W'], ['wat', 'watL', 'watW'], ['min', 'minL', 'minW']]) { const e = OLF.e[k]; e[0] = a * e[0] + (1 - a) * OLF[l]; e[1] = a * e[1] + (1 - a) * OLF[w]; OLF[l] = 0; OLF[w] = 0; }
  if (tick % 50) return;
  if (P.rxn) { olfMark('co2', olfShare('co2'), 'Open: the living now supply most of the CO₂ in the water. It is no longer only food from the world.', 'The world again supplies most of the CO₂.');
    olfMark('wat', olfShare('wat'), 'Open: the living now supply most of the water coming into the ground.', 'Rain again supplies most of the water.'); }
  olfMark('min', olfShare('min'), 'Open: the living now return most of the molecules in the ground. It is no longer only food from the world.', 'The world again supplies most of the molecules.');
  let n = 0, ib = 0, dn = 0; for (let i = 0; i < N; i += 7) if (alive[i]) { n++; if (body[i]) ib++; if (dor[i]) dn++; }
  if (n > 50) { olfMark('lift', ib / n, 'Lift: clumps now hold most of the living.', 'Clumps no longer hold most of the living.');
    olfMark('fold', dn / n, 'Fold: most of the living are now dormant spores.', 'Most of the living are awake again.'); }
}
function olfPanel() {
  const pc = k => Math.round(100 * olfShare(k)) + '%';
  return `<div style="margin-bottom:6px;color:var(--muted)">Open, lift, fold: life supplies ${P.rxn ? `<b>${pc('co2')}</b> of the CO₂ · <b>${pc('wat')}</b> of the water · ` : ''}<b>${pc('min')}</b> of the molecules${P.rxn ? ' · all the oxygen and sugar' : ''}. Crossings are logged in the chronicle.</div>`;
}
// a cell carried off by the water takes its sequence and enzymes with it, and lands with them
function seqTake(i) { if (!P.seqOn || slen.length !== N || !slen[i]) return {sq: null, ct: 0}; const o = i * SL, r = {sq: seq.slice(o, o + slen[i]), og: ORG().slice(o, o + slen[i]), ct: cat[i], rx: rx[i], rs: rxStr[i], ch: cH[i]}; slen[i] = 0; return r; }
function seqPut(i, s) { if (slen.length !== N) seqAlloc(); if (s.sq) { seq.set(s.sq, i * SL); if (s.og) ORG().set(s.og, i * SL); else ORG().fill(0, i * SL, i * SL + s.sq.length); slen[i] = s.sq.length; cat[i] = s.ct; rx[i] = s.rx || 0; rxStr[i] = s.rs || 0; cH[i] = s.ch || 0; } else slen[i] = 0; }
// ---------------- species, as a readout (a measure, not a cause). Every 100 ticks a sample of living cells is fingerprinted
// by the three-letter stretches of their sequences (a MinHash of 16), and similar fingerprints are gathered into clusters.
// Clusters are matched to the last census so a species keeps its number; the chronicle logs the established ones as they
// appear and go. Niches are counted alongside: the enzyme profiles held by 1% or more
const SPH = 16, SPSEED = new Uint32Array(SPH).map((_, h) => (Math.imul(h + 1, 2654435761) ^ 0x5bd1e995) >>> 0);
let species = [], nextSpecies = 1, specStat = {n: 0, est: 0, within: 0, between: 0, niches: 0, sampled: 0, div: 0};
function specSig(i, out, o) {
  const s = i * SL, L = slen[i];
  for (let h = 0; h < SPH; h++) out[o + h] = 0xffffffff;
  for (let q = 0; q + 2 < L || (q === 0 && L > 0); q++) {
    const k = L >= 3 ? (seq[s + q] << 8) | (seq[s + q + 1] << 4) | seq[s + q + 2] : 4096 + seq[s];
    for (let h = 0; h < SPH; h++) { const v = Math.imul(k ^ SPSEED[h], 2246822519) >>> 0, w = (v ^ (v >>> 15)) >>> 0; if (w < out[o + h]) out[o + h] = w; }
    if (L < 3) break;
  }
}
const sigSim = (a, ao, b, bo) => { let m = 0; for (let h = 0; h < SPH; h++) if (a[ao + h] === b[bo + h]) m++; return m / SPH; };
function specStep() {
  if (!P.seqOn || slen.length !== N) return;
  const cap = 3000; let n = 0; for (let i = 0; i < N; i++) if (alive[i] && slen[i]) n++;
  if (n < 30) { specStat = {n: 0, est: 0, within: 0, between: 0, niches: 0, sampled: n, div: 0}; return; }
  const stride = Math.max(1, Math.floor(n / cap)), idx = []; let k0 = (rng() * stride) | 0;
  for (let i = 0, c = 0; i < N; i++) if (alive[i] && slen[i]) { if (c % stride === k0 % stride) idx.push(i); c++; }
  const m = idx.length, sig = new Uint32Array(m * SPH); for (let q = 0; q < m; q++) specSig(idx[q], sig, q * SPH);
  // leader clustering: each fingerprint joins the first cluster whose leader it resembles closely enough, or starts one
  const thr = P.specThr, lead = [], size = [], wsum = [], nich = new Map();
  for (let q = m - 1; q > 0; q--) { const r = (rng() * (q + 1)) | 0, t = idx[q]; idx[q] = idx[r]; idx[r] = t; }
  for (let q = 0; q < m; q++) specSig(idx[q], sig, q * SPH);
  for (let q = 0; q < m; q++) {
    const ct = P.rxDom ? rx[idx[q]] : cat[idx[q]]; nich.set(ct, (nich.get(ct) || 0) + 1);
    let best = -1, bs = 0; for (let c = 0; c < lead.length; c++) { const s = sigSim(sig, q * SPH, sig, lead[c] * SPH); if (s >= thr && s > bs) { bs = s; best = c; if (s === 1) break; } }
    if (best < 0) { lead.push(q); size.push(1); wsum.push(1); } else { size[best]++; wsum[best] += bs; }
  }
  // match the clusters to the species of the last census
  const minN = Math.max(15, Math.ceil(.01 * m)), order = size.map((s, c) => c).sort((a, b) => size[b] - size[a]), taken = new Set(), now = [];
  for (const c of order) {
    const ls = sig.slice(lead[c] * SPH, lead[c] * SPH + SPH); let best = null, bs = 0;
    for (const sp of species) { if (taken.has(sp.id)) continue; const s = sigSim(ls, 0, sp.sig, 0); if (s >= thr * .8 && s > bs) { bs = s; best = sp; } }
    if (best) { taken.add(best.id); best.sig = ls; best.n = size[c]; best.miss = 0; if (size[c] > best.peak) best.peak = size[c];
      if (!best.est && size[c] >= minN) { best.est = true; log(`A new species: #${best.id}, now ${Math.round(100 * size[c] / m)}% of the living.`); } now.push(best); }
    else if (size[c] >= 3) { const sp = {id: nextSpecies++, sig: ls, n: size[c], peak: size[c], born: tick, miss: 0, est: size[c] >= minN};
      if (sp.est && tick > 150) log(`A new species: #${sp.id}, now ${Math.round(100 * size[c] / m)}% of the living.`); now.push(sp); }
  }
  for (const sp of species) if (!taken.has(sp.id)) { sp.miss++; if (sp.miss < 3) now.push(sp); else if (sp.est) log(`Species #${sp.id} is gone, after ${tick - sp.born} ticks.`); }
  species = now;
  // distinctness: how alike members are to their leader, against how alike each established species is to its nearest neighbour
  const est = order.filter(c => size[c] >= minN); let w = 0, wn = 0, b = 0, bn = 0, H = 0;
  for (const c of est) { w += wsum[c]; wn += size[c]; let mx = 0; for (const d of est) if (d !== c) { const s = sigSim(sig, lead[c] * SPH, sig, lead[d] * SPH); if (s > mx) mx = s; } if (est.length > 1) { b += mx; bn++; } }
  for (const c of order) { const p = size[c] / m; H -= p * Math.log(p); }
  let ni = 0; for (const v of nich.values()) if (v >= minN) ni++;
  specStat = {n: est.length, est: est.length, within: wn ? w / wn : 0, between: bn ? b / bn : 0, niches: ni, sampled: m, div: Math.exp(H)};
}
// mating compatibility: two parents may fuse only if their sequences share enough three-letter stretches
let mateTried = 0, mateRefused = 0; const mBits = new Uint32Array(8);
function seqSim(a, b) {
  if (!slen[a]) seqFromGen(a, gen[a]); if (!slen[b]) seqFromGen(b, gen[b]);
  const oa = a * SL, La = slen[a], ob = b * SL, Lb = slen[b]; if (La < 3 || Lb < 3) return 0;
  mBits.fill(0); for (let q = 0; q + 2 < La; q++) { const k = ((seq[oa + q] << 8) | (seq[oa + q + 1] << 4) | seq[oa + q + 2]) * 2654435761 >>> 24; mBits[k >> 5] |= 1 << (k & 31); }
  let hit = 0; for (let q = 0; q + 2 < Lb; q++) { const k = ((seq[ob + q] << 8) | (seq[ob + q + 1] << 4) | seq[ob + q + 2]) * 2654435761 >>> 24; if (mBits[k >> 5] & (1 << (k & 31))) hit++; }
  return hit / (Lb - 2);
}
function mateOK(cand, candI, c, a, b) {
  let ia = -1, ib = -1; for (let k = 0; k < c; k++) { if (ia < 0 && cand[k] === a) ia = candI[k]; if (ib < 0 && cand[k] === b) ib = candI[k]; }
  if (ia < 0 || ib < 0) return true; mateTried++;
  const ok = seqSim(ia, ib) >= P.mateThr; if (!ok) mateRefused++; return ok;
}
function specPanel() {
  if (!P.seqOn || !specStat.sampled) return '';
  const s = specStat;
  return `<div style="margin-bottom:6px;color:var(--muted)">Species (clusters of similar sequences, each 1% or more of the living): <b>${s.n}</b> · effective number of clusters <b>${s.div.toFixed(1)}</b> · members resemble their species <b>${Math.round(100 * s.within)}%</b>, a species resembles its nearest neighbour <b>${Math.round(100 * s.between)}%</b> · niches (enzyme profiles held by 1% or more): <b>${s.niches}</b>${P.mateThr > 0 && mateTried ? ` · <b>${Math.round(100 * mateRefused / mateTried)}%</b> of would-be matings refused as too unlike` : ''}${P.hgtHom > 0 && hgtTried ? ` · <b>${Math.round(100 * hgtFailed / hgtTried)}%</b> of contagions failed for want of a matching stretch` : ''}</div>`;
}
function carbonTotal() { let s = 0; for (let c = 0; c < co2.length; c++) s += co2[c] + en[c]; let k = 0; for (let i = 0; i < N; i++) k += alive[i]; return s + k * P.birth + buried; }        // the current: how far water moves, in chemistry squares, per step
let sig = new Float32Array(1), sigTmp = new Float32Array(1);   // the signal cells give off: a smoothed density, one value per chemistry square
const VW = [.5, 1.2, 1.2, 1, .8, .5, .3, .2, .1, .1, .3, .3, .2, .6, .1, .1];     // which molecules a vent pours out
const TOPT = [.30, .45, .60, .75];                                                // the temperature each degree of thermophily prefers
const thermFit = (g, T) => { const d = (T - TOPT[(g >>> 26) & 3]) / .30, f = 1 - d * d; return f > 0 ? f : 0; };
function envAlloc() {
  const n = cw * chh;
  temp = new Float32Array(n).fill(.35); tempTmp = new Float32Array(n); ltc = new Float32Array(n).fill(1); tamb = new Float32Array(n).fill(.35);
  vglow = new Float32Array(n); dens = new Float32Array(n); sig = new Float32Array(n); sigTmp = new Float32Array(n); fx = new Float32Array(n); fy = new Float32Array(n); fvx = new Float32Array(n); fvy = new Float32Array(n); vhot = new Float32Array(n); tB = new Float32Array(n); tC = new Float32Array(n); fsrc = new Float32Array(n); fp = new Float32Array(n); fp2 = new Float32Array(n); fu2 = new Float32Array(n); fv2 = new Float32Array(n); fw = new Float32Array(n); en = new Float32Array(n); enTmp = new Float32Array(n); wat = new Float32Array(n).fill(P.wrain || 2); co2 = new Float32Array(n).fill(P.co2air || 4); o2 = new Float32Array(n); rtmp = new Float32Array(n); fe = new Float32Array(n).fill(P.feStart || 0);
  ux = new Float32Array(n); uy = new Float32Array(n); tsurf = new Float32Array(n).fill(.35); wup = new Float32Array(n); sdiv = new Float32Array(n); fps = new Float32Array(n); air = [];
  if (typeof G3 === 'object' && P.water3d) { if (G3.dev) g3Alloc(); else g3Setup(); }
  envBuild();
}
const SPR = {dir: 0}, PIN = {mouths: [], got: 0};   // PIN: where streams bring organic matter into the pond                                   // the hot springs' slope
function envBuild() {                                    // where the vents are, and the shape of the clouds
  lor = [.5 + rng() * 2, .5 + rng() * 2, 18 + rng() * 6]; chx = chy = chz = 0;
  vents = []; const kind = P.env;
  if (kind === 'vent' || kind === 'springs') {
    const count = kind === 'vent' ? Math.max(4, Math.round(cw * chh / 4500)) : Math.max(6, Math.round(cw * chh / 2500));
    for (let q = 0; q < count; q++) vents.push({x: rng() * cw, y: rng() * chh, s: kind === 'vent' ? 5 + rng() * 4 : 2.5 + rng() * 2, per: 500 + rng() * 1500, ph: rng() * 6.2832, w1: rng() * 2 - 1, w2: rng() * 2 - 1, w3: rng() * 2 - 1, burst: 0});
    if (kind === 'springs' && P.springZone !== false) {   // a source zone (Justin, 15 November): one main spring and two small ones beside it, not springs all over the ground
      vents.length = 3; SPR.dir = rng() * 6.2832;           // the way the ground slopes: the runoff flows downhill from the source
      for (let q = 1; q < 3; q++) { const a = SPR.dir + (q === 1 ? 1.2 : -1.2) + (rng() - .5), d = 6 + rng() * 6; vents[q].x = cw / 2 + Math.cos(a) * d; vents[q].y = chh / 2 + Math.sin(a) * d; vents[q].s = 1.5 + rng(); }
    }
    vents[0].x = cw / 2; vents[0].y = chh / 2; vents[0].s = Math.max(vents[0].s, kind === 'vent' ? 8 : 4);   // the first cells live near one
    vents[0].ph = 1.5708;                                  // and it starts at full strength
  }
  PIN.mouths = []; PIN.got = 0;                            // the pond's inflows (Justin, 15 November): streams carry organic matter from the land around it, more in the wet season
  if (kind === 'pond') for (let q = 0; q < 3; q++) PIN.mouths.push({x: rng() * cw, y: rng() * chh, s: 2 + rng() * 2, w: .5 + rng()});
  CLW = []; for (let q = 0; q < 3; q++) { let kx = Math.floor(rng() * 5) - 2, ky = Math.floor(rng() * 5) - 2; if (!kx && !ky) kx = 1; CLW.push({kx, ky, ph: rng() * 6.2832, sp: .002 + rng() * .004}); }
}
function envInit() { sig.fill(0); fx.fill(0); fy.fill(0); fp.fill(0); en.fill(0); enMade = enTaken = enGot = 0; wat.fill(P.wrain); co2.fill(P.co2air); o2.fill(0); fe.fill(P.feStart); buried = 0; dried = carbonless = enAer = 0; fx.fill(0); fy.fill(0); envBuild(); if (P.env !== 'even') { envStep(); temp.set(tamb); for (let c = 0; c < temp.length; c++) temp[c] = Math.min(1.2, tamb[c] + HV() * vglow[c]); } else { ltc.fill(1); tamb.fill(.35); temp.fill(.35); vglow.fill(0); }
  ux.fill(0); uy.fill(0); wup.fill(0); fps.fill(0); tsurf.set(tamb); air = []; if (typeof G3 === 'object') G3.needInit = true; airStat = {lifted: 0, settled: 0, lost: 0, died: 0, dist: 0, maxDist: 0, time: 0, recent: []}; }
const HV = () => P.env === 'vent' ? .5 : P.env === 'springs' ? .5 : 0;
function chaosStep() {
  let [x, y, z] = lor; const dt = .005;
  const dx = 10 * (y - x), dy = x * (28 - z) - y, dz = x * y - 8 / 3 * z;
  x += dx * dt; y += dy * dt; z += dz * dt; lor = [x, y, z];
  chx = Math.max(-1, Math.min(1, x / 20)); chy = Math.max(-1, Math.min(1, y / 25)); chz = Math.max(-1, Math.min(1, (z - 25) / 20));
}
function advect(a, b, K, u = fx, v = fy) {               // carry a field along the current: each square takes what was upstream of it
  for (let y = 0; y < chh; y++) for (let x = 0; x < cw; x++) {
    const c = y * cw + x, sx = x - u[c], sy = y - v[c], x0 = Math.floor(sx), y0 = Math.floor(sy), tx = sx - x0, ty = sy - y0;
    const xa = ((x0 % cw) + cw) % cw, xb = (xa + 1) % cw, ya = ((y0 % chh) + chh) % chh, yb = (ya + 1) % chh;
    const i00 = (ya * cw + xa) * K, i10 = (ya * cw + xb) * K, i01 = (yb * cw + xa) * K, i11 = (yb * cw + xb) * K, o = c * K;
    for (let k = 0; k < K; k++) b[o + k] = (1 - ty) * ((1 - tx) * a[i00 + k] + tx * a[i10 + k]) + ty * ((1 - tx) * a[i01 + k] + tx * a[i11 + k]);
  }
}
function envStep() {
  const e = P.env, t = tick, n = cw * chh, dl = Math.max(20, P.dayLen), sun = .5 + .5 * Math.sin(6.2832 * t / dl + 1.5708), amp = P.nightDepth;
  envSun = sun; vglow.fill(0); vhot.fill(0);
  const ch = P.heatChaos || 0; if (ch > 0) chaosStep(); else chx = chy = chz = 0;
  const cur = P.current || 0;                              // the current: a slow ambient drift that wanders with the chaos, plus an outflow and a swirl around every vent
  const th = .6 + t * .0006 + 1.6 * ch * chx, sp = cur * P.crossflow * (1 + .5 * ch * chy); fvx.fill(0); fvy.fill(0);
  for (const v of vents) {
    if (ch > 0) {                                           // vents wander, and now and then one erupts
      v.x += ch * .10 * v.w2 * chy; v.y += ch * .10 * v.w3 * chz;
      if (rng() < ch * .004) v.burst = 1; v.burst *= .96;
    }
    const act = Math.max(0, (.75 + .25 * Math.sin(6.2832 * t / v.per + v.ph)) * (1 + ch * .7 * (v.w1 * chx + v.w2 * chy + v.w3 * chz)) + ch * v.burst) * P.ventPower, r = Math.ceil(v.s * 3), cx = Math.round(v.x), cy = Math.round(v.y), k2 = 1 / (2 * v.s * v.s);
    for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
      const d2 = dx * dx + dy * dy; if (d2 > r * r) continue;
      const ci = (((cy + dy) % chh + chh) % chh) * cw + (((cx + dx) % cw + cw) % cw), gv = act * Math.exp(-d2 * k2);
      vglow[ci] += gv; vhot[ci] += act * Math.exp(-d2 * k2 / (P.plumeW * P.plumeW));   // the hot core of a vent: narrower than its glow
      if (cur > 0) { const g = gv * cur * .03, sg = v.ph < 3.14 ? 1 : -1; fvx[ci] -= g * sg * dy / v.s; fvy[ci] += g * sg * dx / v.s; }   // a vent sets the water spinning a little
    }
  }
  const hv = HV(), D = Math.min(.24, P.heatDiff * 2), R = Math.min(.5, P.heatRelax * 2), hl = P.heatLife * .02;
  for (let y = 0; y < chh; y++) for (let x = 0; x < cw; x++) {
    const c = y * cw + x; let L = 1, A = .35;
    if (e === 'pond' || e === 'springs') {
      let s = 0; for (const w of CLW) s += Math.cos(6.2832 * (w.kx * x / cw + w.ky * y / chh) + w.ph + t * w.sp);
      L = ((1 - amp) + amp * sun) * (1 - .3 * (.5 + .5 * s / 3)); A = (e === 'pond' ? .24 : .18) + .12 * sun + .12 * (1 - .5 - .5 * s / 3);   // shade from the clouds cools the water beneath them
    } else if (e === 'vent') { L = P.ventGlow * Math.min(1, vglow[c]); A = .20; }   // the deep sea is dark: only the vents' dim geothermal glow (Beatty et al. 2005); vent life runs on chemistry
    else if (e === 'dish') { L = P.dishLight; A = .30; }     // the dish: dark and still
    A += ch * .18 * chx; if (A < 0) A = 0;
    ltc[c] = L; tamb[c] = A;
  }
  if (P.water3d) {                                         // 3D water on the GPU, when there is one; else the two layers below
    if (G3.state === 'off') g3Setup(); else if (G3.state === 'ready' && (G3.nx !== cw || G3.ny !== chh)) g3Alloc();
    if (g3Ready()) {
      g3Step(cur, th, R, hv, hl); g3Lift();
      let s3 = 0; for (let c = 0; c < n; c += 7) s3 += temp[c]; envTemp = s3 / Math.ceil(n / 7);
      return;
    }
  }
  if (P.twoLayer || P.water3d) {
    if (cur > 0) { fluidStep2(cur, th, sp); heat2(D, R, hv, hl); }
    else { fx.fill(0); fy.fill(0); ux.fill(0); uy.fill(0); wup.fill(0); heat2(D, R, hv, hl); }
    sporeAir();
    let s2 = 0; for (let c = 0; c < n; c += 7) s2 += temp[c]; envTemp = s2 / Math.ceil(n / 7);
    return;
  }
  fluidStep(cur, th, sp); if (cur > 0) advectSharp(temp);
  for (let y = 0; y < chh; y++) {
    const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) {
      const xm = (x - 1 + cw) % cw, xp = (x + 1) % cw, c = y0 + x, T = temp[c];
      const v = T + D * (.25 * (temp[y0 + xm] + temp[y0 + xp] + temp[ym + x] + temp[yp + x]) - T) + R * (tamb[c] + hv * (P.plumeW < 1 ? .3 * vglow[c] + .7 * vhot[c] : vglow[c]) - T) + hl * dens[c] / 16;
      tempTmp[c] = v < 0 ? 0 : v > 1.3 ? 1.3 : v;
    }
  }
  [temp, tempTmp] = [tempTmp, temp];
  let s = 0; for (let c = 0; c < n; c += 7) s += temp[c]; envTemp = s / Math.ceil(n / 7);
}

// the first organism is suited to the water around its starting place
function setThermo(g) {
  let best = 0, bf = -1;
  for (let e = 0; e < 4; e++) {
    let f = 0, n = 0;
    for (let dy = -5; dy <= 5; dy += 2) for (let dx = -5; dx <= 5; dx += 2) { const T = temp[(((chh >> 1) + dy + chh) % chh) * cw + (((cw >> 1) + dx + cw) % cw)], d = (T - TOPT[e]) / .30; f += Math.max(0, 1 - d * d); n++; }
    f /= n; if (f > bf) { bf = f; best = e; }
  }
  return ((g & ~(3 << 26)) | (best << 26)) >>> 0;
}

// heat vision: an infrared palette, black through purple, red and orange to white
const IRL = new Uint8ClampedArray(256 * 3);
{
  const st = [[0, 0, 0, 20], [.25, 70, 0, 110], [.5, 200, 30, 60], [.75, 255, 150, 0], [.9, 255, 230, 80], [1, 255, 255, 230]];
  for (let q = 0; q < 256; q++) {
    const u = q / 255; let a = st[0], b = st[1];
    for (let s = 1; s < st.length; s++) if (u <= st[s][0]) { a = st[s - 1]; b = st[s]; break; }
    const f = (u - a[0]) / (b[0] - a[0] || 1);
    for (let c = 0; c < 3; c++) IRL[q * 3 + c] = a[c + 1] + f * (b[c + 1] - a[c + 1]);
  }
}
const irIdx = T => (Math.max(0, Math.min(255, Math.round(255 * T / 1.0)))) * 3;

// ---------------- clumps made by their cells (no clump code). A cell keeps part of what its reactions make on its surface,
// and larger molecules stick more: that is its coat. Cells whose coats pass a threshold stick to each other, and a clump is
// simply a connected group of sticky cells (8 neighbours). Nothing else defines it: it grows, splits and merges as its cells'
// coats come and go; the matrix spans gaps of up to clumpReach - 1 cells. Identity carries over from one census to the next by the largest overlap, so splits and merges can be logged.
const ccMark = new Int32Array(1), mxPool = new Map(); let ccId = null, ccStat = {formed: 0, split: 0, merged: 0, fromFree: 0, fromSplit: 0, rel: null, relN: 0};
function cellClumpCensus() {
  if (!ccId || ccId.length !== N) ccId = new Int32Array(N);
  const dec = Math.pow(1 - P.coatDecay, 8); for (let i = 0; i < N; i++) { if (coat[i]) { if (alive[i]) coatReturn(i, 1 - dec); coat[i] = alive[i] ? coat[i] * dec : 0; } if (rxAct[i]) rxAct[i] *= .5; }   // shed coat goes back to the ground
  const sticky = i => alive[i] && !dor[i] && coat[i] >= P.coatMin;
  ccId.fill(0); let nc = 0; const comps = [];
  for (let i0 = 0; i0 < N; i0++) {
    if (ccId[i0] || !sticky(i0)) continue; nc++; const out = [i0]; ccId[i0] = nc;
    for (let h = 0; h < out.length; h++) { const i = out[h], x = i % W, y = (i / W) | 0;
      const R = P.clumpReach;                     // the matrix spans small gaps: sticky cells up to R apart are in one clump (your rule: 1–2 cell gaps are fine)
      for (let dy = -R; dy <= R; dy++) for (let dx = -R; dx <= R; dx++) { if (!dx && !dy) continue; const j = ((y + dy + H) % H) * W + ((x + dx + W) % W);
        if (!ccId[j] && sticky(j)) { ccId[j] = nc; out.push(j); } } }
    comps.push(out);
  }
  // match each component to the old clumps its cells belonged to
  const keep = new Map(), claimed = new Map();
  for (let q = 0; q < comps.length; q++) { const m = comps[q]; if (m.length < P.clumpMin) continue;
    const ov = new Map(); for (const i of m) { const b = body[i]; if (b) ov.set(b, (ov.get(b) || 0) + 1); }
    let best = 0, bc = 0; for (const [b, c] of ov) if (c > bc && bodies.has(b)) { bc = c; best = b; }
    keep.set(q, {best, bc, olds: ov.size});
    if (best) { const cl = claimed.get(best); if (!cl || cl.bc < bc) claimed.set(best, {q, bc}); } }
  for (let i = 0; i < N; i++) body[i] = 0;
  const live = new Set();
  for (const [q, k] of keep) { const m = comps[q]; let id = k.best;
    if (id && claimed.get(id).q === q) { const bo = bodies.get(id); if (k.olds > 1) { ccStat.merged++; if (ccStat.merged <= 3 || ccStat.merged % 100 === 0) log(`Clumps merge into #${id} (merger ${ccStat.merged}): their cells' coats meet.`); } bo.size = m.length; }
    else { const [dc] = dominant(m), tint = (Math.imul(dc ^ 0x9e3779b9, 2654435761) >>> 24) & 255;
      const from = id ? [id] : []; id = newBody((tint << 12) >>> 0, m, from, id ? 'splitting' : 'forming');
      if (from.length) { ccStat.split++; ccStat.fromSplit++; if (ccStat.split <= 3 || ccStat.split % 100 === 0) log(`Clump #${from[0]} splits; #${id} goes its own way (split ${ccStat.split}).`); }
      else { ccStat.formed++; ccStat.fromFree++; if (ccStat.formed <= 3 || ccStat.formed % 100 === 0) log(`Sticky cells form clump #${id} (${m.length} cells; clump ${ccStat.formed} to form).`); } }
    for (const i of m) body[i] = id; live.add(id); }
  for (const id of [...bodies.keys()]) if (!live.has(id)) bodies.delete(id);
  // the matrix: each clump holds a pool of molecules. It leaks a little back to the ground each census, and a clump that
  // comes apart spills all of it where it last was
  for (const [id, pl] of mxPool) { const c = pl[16] | 0;
    if (!bodies.has(id)) { for (let k = 0; k < 16; k++) chem[(c << 4) + k] += pl[k]; mxPool.delete(id); continue; }
    for (let k = 0; k < 16; k++) { const q = pl[k] * P.mxLeak; pl[k] -= q; chem[(c << 4) + k] += q; } }
  for (const [q] of keep) { const m = comps[q], id = body[m[0]]; if (!id) continue; let pl = mxPool.get(id); if (!pl) { pl = new Float32Array(17); mxPool.set(id, pl); } pl[16] = cmap[m[(m.length / 2) | 0]]; }
  // extents, for drawing
  const mem = new Map(); for (let i = 0; i < N; i++) { const b = body[i]; if (b) (mem.get(b) || mem.set(b, []).get(b)).push(i); }
  for (const [id, bo] of bodies) { const m = mem.get(id); if (!m) { bodies.delete(id); continue; }
    const ax = m[0] % W, ay = (m[0] / W) | 0; let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const i of m) { const x = ax + wrapd(i % W - ax, W), y = ay + wrapd(((i / W) | 0) - ay, H); if (x < x0) x0 = x; if (y < y0) y0 = y; if (x > x1) x1 = x; if (y > y1) y1 = y; }
    Object.assign(bo, {x0, y0, x1, y1, size: m.length}); }
  if (tick % 200 === 0) ccRelate(mem);
}
// relatedness: how alike a clump's cells are, against random pairs of living cells (0 = no more alike than strangers, 1 = clones)
function ccRelate(mem) {
  if (!P.seqOn) return; let ws = 0, wn = 0, rs = 0, rn = 0; const all = [];
  for (let i = 0; i < N; i += 13) if (alive[i] && slen[i] > 2) all.push(i);
  for (let k = 0; k < 300 && all.length > 1; k++) { rs += seqSim(all[(rng() * all.length) | 0], all[(rng() * all.length) | 0]); rn++; }
  let nb = 0; for (const [, m] of mem) { if (m.length < P.clumpMin || nb++ > 60) continue; for (let k = 0; k < 6; k++) { const a = m[(rng() * m.length) | 0], b = m[(rng() * m.length) | 0]; if (a !== b) { ws += seqSim(a, b); wn++; } } }
  if (!wn || !rn) return; const w = ws / wn, r = rs / rn; ccStat.rel = r < 1 ? (w - r) / (1 - r) : 0; ccStat.relN = nb; ccStat.within = w; ccStat.random = r;
}
function ccPanel() {
  if (!P.cellClumps || !P.gAdh) return ''; let inC = 0, n = 0, st = 0; for (let i = 0; i < N; i++) if (alive[i]) { n++; if (body[i]) inC++; if (coat[i] >= P.coatMin) st++; }
  let ie = [0, 0, 0, 0]; for (let i = 0; i < N; i++) { if (!alive[i] || !body[i]) continue; const x = i % W, y = (i / W) | 0; let inn = true;
    for (let dy = -1; dy <= 1 && inn; dy++) for (let dx = -1; dx <= 1; dx++) { if (!dx && !dy) continue; const j = ((y + dy + H) % H) * W + ((x + dx + W) % W); if (!alive[j] || body[j] !== body[i]) { inn = false; break; } }
    ie[inn ? 0 : 2] += rxAct[i]; ie[inn ? 1 : 3]++; }
  const ieTxt = ie[1] && ie[3] ? ` · reactions run by a clump's inner cells <b>${(ie[0] / ie[1]).toFixed(2)}</b> against <b>${(ie[2] / ie[3]).toFixed(2)}</b> at its edge (${ie[1]} inner, ${ie[3]} edge cells)` : '';
  return `<div style="margin-bottom:6px;color:var(--muted)">Clumps, made by their cells: <b>${bodies.size}</b> clumps hold <b>${n ? Math.round(100 * inC / n) : 0}%</b> of cells · <b>${n ? Math.round(100 * st / n) : 0}%</b> of cells are sticky · new clumps so far: <b>${ccStat.fromFree}</b> formed from free cells, <b>${ccStat.fromSplit}</b> split off others; <b>${ccStat.merged}</b> mergers · <b>${coatMade.toFixed(0)}</b> light spent on coat so far · the matrix holds <b>${(()=>{let t=0;for(const[,pl] of mxPool)for(let k=0;k<16;k++)t+=pl[k];return (t/P.chunit).toFixed(0)})()}</b> units of molecules${ccStat.rel != null ? ` · relatedness within clumps <b>${ccStat.rel.toFixed(2)}</b> (0 = strangers, 1 = clones)` : ''}${ieTxt}</div>`;
}

// the cost of size: a clump's cells shade each other, and in water a larger colony sinks out of the light. A clump's cell
// gets this share of its square's light
function clumpShade(i) { const bo = bodies.get(body[i]); return bo ? 1 / (1 + bo.size / P.sinkSize) : 1; }

// gliding: a cell creeps on its own slime. Each tick a coated cell may push into an empty neighbouring place, spending
// some of its coat as the slime it leaves behind; the more coat, the likelier. Direction is random: nothing steers it,
// though cells that have stopped making coat stop moving. Dormant cells don't glide. It carries the cell and its energy.
let glided = 0;
function glidePass() {
  glided = 0; const g0 = P.glide; if (!(g0 > 0) || !P.cellClumps) return; hopm.fill(0);
  for (let y = 0; y < H; y++) { const ym = ((y - 1 + H) % H) * W, y0 = y * W, yp = ((y + 1) % H) * W;
    for (let x = 0; x < W; x++) { const i = y0 + x; if (!alive[i] || hopm[i] || dor[i]) continue; const ct = coat[i]; if (ct < P.glideCost) continue;
      if (rng() >= g0 * Math.min(1, ct)) continue;
      const xm = (x - 1 + W) % W, xp = (x + 1) % W, nb = [ym + xm, ym + x, ym + xp, y0 + xm, y0 + xp, yp + xm, yp + x, yp + xp];
      const j = nb[(rng() * 8) | 0]; if (alive[j] || hopm[j] || dishBlocked(j)) continue;
      alive[j] = 1; gen[j] = gen[i]; xg[j] = xg[i]; rsv[j] = rsv[i]; rsv[i] = 0; dor[j] = 0; light[j] = light[i]; light[i] = 0; body[j] = body[i]; body[i] = 0; virMove(i, j);   // the cell takes its stored energy (ambient light is in amb) and its clump membership with it
      if (P.seqOn) moveSeq(i, j); coat[j] -= P.glideCost; alive[i] = 0; gen[i] = 0; xg[i] = 0; hopm[j] = 1; changed[i] = 1; changed[j] = 1; glided++; } }
}
// the dish: a dark, still, closed plate. Every molecule is laid down once, evenly, at P.dishFood of the ground's usual
// level, and nothing re-forms; molecules only spread, and come back only from the dead. The first cells are given a fold that burns
// p (a lone pair p…h), like an inoculated strain.
function dishSetup() {
  if (P.env !== 'dish' || !chem) return; if (P.dishPop) popInit(); else popWin = null; const n = cw * chh, f = P.dishFood;
  for (let c = 0; c < n; c++) for (let k = 0; k < 16; k++) { const q = (c << 4) + k; if (chem[q] <= chemCap[q] * 1.01) chem[q] = f * chemCap[q]; }   // the plate: every molecule laid once at P.dishFood of the ground's level (the inoculum's broth is kept)
  dishMask(); if (typeof fit === 'function') fit(); if (!amb || amb.length !== N) amb = new Float32Array(N); amb.fill(P.dishLight); ltc.fill(P.dishLight); for (let i = 0; i < N; i++) if (!alive[i]) light[i] = 0; if (!husk || husk.length !== N) husk = new Float32Array(N); husk.fill(0); if (huskG && huskG.length === N) huskG.fill(0);   // the plate is dark from the start; show the whole plate
  for (let c = 0; c < n; c++) if (!dishSq[c]) for (let k = 0; k < 16; k++) chem[(c << 4) + k] = 0;   // nothing lies beyond the rim
  en.fill(f * P.dishSugar); for (let c = 0; c < n; c++) if (!dishSq[c]) en[c] = 0; o2.fill(P.o2air || 4); fe.fill(0);   // the plate starts in air, with no iron to soak up the oxygen          // the agar's sugar, laid once with the rest of the food
  for (let i = 0; i < N; i++) if (alive[i]) xg[i] |= (3 << 10) | (P.dishDorm ? 3 << 14 : 0);   // and, if dishDorm, goes dormant when starved   // the inoculum eats sugar (the heterotroph gene, at full strength)
  if (!P.seqOn || slen.length !== N) return;
  for (let i = 0; i < N; i++) { if (!alive[i]) continue; if (!slen[i]) seqFromGen(i, gen[i]); if (!slen[i] || slen[i] + 2 > SL) continue; const o = i * SL;
    let at = slen[i]; while (at > 0 && seq[o + at - 1] === 15) at--; if (slen[i] - at < 3) at = slen[i];   // the pair goes before a trailing run of three 15s, so it cannot make a run of four, a gene marker (report 29; Justin, 16 November)
    for (let h = slen[i] - 1; h >= at; h--) seq[o + h + 2] = seq[o + h]; seq[o + at] = 15; seq[o + at + 1] = 7; slen[i] += 2;
    gen[i] = infold(seq, o, slen[i]); cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH; }
}

// ---------------- the dish as populations (13 November, Justin's decision): Matsushita's approach, with each square of
// the plate holding counts of active and inactive cells and its sugar, and every division, inactivation and move drawn
// at random from those counts. A patch can be opened down to single cells, run by the page's own cell rules, and folded
// back. While a patch is open, the rest of the plate waits.
const POP = {L: 300, K: 100, Dn: .2, grow: .05, use: 1, Kn: 1, a0: .02, n1: .5};    // the prototype's values (popdish/pop.py)
let popA = null, popI = null, popN = null, popPlate = null, popTmp = null, popMv = null, popWin = null, popTick = 0, popG = 0;
const popActive = () => P.env === 'dish' && P.dishPop && popA !== null && popWin === null;
function binom(n, p) {                                    // a binomial draw: exact for small counts, normal beyond
  if (n <= 0 || p <= 0) return 0; if (p >= 1) return n;
  if (n < 30) { let k = 0; for (let j = 0; j < n; j++) if (rng() < p) k++; return k; }
  const m = n * p, sd = Math.sqrt(m * (1 - p)); let u = 0; while (u === 0) u = rng();
  const g = Math.sqrt(-2 * Math.log(u)) * Math.cos(6.2832 * rng()), k = Math.round(m + sd * g); return k < 0 ? 0 : k > n ? n : k;
}
function popInit() {
  const L = POP.L, M = L * L, c = (L - 1) / 2, R2 = (.48 * L) ** 2;
  popA = new Int32Array(M); popI = new Int32Array(M); popN = new Float32Array(M); popTmp = new Float32Array(M); popMv = new Int32Array(M); popPlate = new Uint8Array(M);
  for (let y = 0; y < L; y++) for (let x = 0; x < L; x++) { const q = y * L + x; popPlate[q] = (x - c) ** 2 + (y - c) ** 2 <= R2 ? 1 : 0; popN[q] = popPlate[q] ? P.popSugar : 0; }
  const m = Math.round(c); for (let y = m - 2; y <= m + 2; y++) for (let x = m - 2; x <= m + 2; x++) popA[y * L + x] = 20;   // the inoculum
  popWin = null; popTick = 0; popStrainC = null; popRec.clear(); popGT.length = 0; popGTi.clear(); popUI();
}
function popStep() {
  const L = POP.L, M = L * L, K = POP.K, n0 = P.popSugar, soft = P.popSoft, A = popA, I = popI, n = popN, pl = popPlate; popTick++;
  for (let y = 0; y < L; y++) for (let x = 0; x < L; x++) { const q = y * L + x; if (!pl[q]) { popTmp[q] = 0; continue; }   // sugar spreads; nothing crosses the rim
    const s = n[q], g = j => pl[j] ? n[j] : s; popTmp[q] = s + POP.Dn * .25 * (g(q - 1) + g(q + 1) + g(q - L) + g(q + L) - 4 * s); }
  n.set(popTmp); popMv.fill(0);
  for (let q = 0; q < M; q++) { if (!pl[q]) continue; let a = A[q]; if (!a && !popMv[q]) continue;
    const room = Math.max(0, 1 - (a + I[q]) / K);
    let b = binom(a, POP.grow * n[q] / (n[q] + POP.Kn) * room); b = Math.min(b, Math.floor(n[q] / POP.use)); a += b; n[q] -= b * POP.use;   // division uses sugar
    const s = binom(a, POP.a0 / (1 + n[q] / POP.n1)); a -= s; I[q] += s;                                                                  // going still where sugar is low
    const mv = binom(a, Math.min(1, soft * .5 + (1 - soft) * .5 * (a / K) * (n[q] / (n0 + 1e-9)) * 4)); a -= mv; A[q] = a;               // moving: freely on soft agar, only where cells and sugar abound on hard
    let r = mv; for (const d of [1, -1, L, -L]) { const k = d === -L ? r : binom(r, 1 / (d === 1 ? 4 : d === -1 ? 3 : 2)); r -= k; const j = q + d; if (k) { if (j >= 0 && j < M && pl[j]) popMv[j] += k; else popMv[q] += k; } } }
  for (let q = 0; q < M; q++) if (popMv[q]) A[q] += popMv[q];
}
function popGeom() { const s = Math.min(W, H) / POP.L; return {s, ox: (W - POP.L * s) / 2, oy: (H - POP.L * s) / 2}; }
function popDraw(d) {
  const L = POP.L, {s, ox, oy} = popGeom(), lk = Math.log1p(POP.K);
  for (let y = 0; y < H; y++) { const qy = Math.floor((y - oy) / s);
    for (let x = 0; x < W; x++) { const p = (y * W + x) * 4, qx = Math.floor((x - ox) / s);
      if (qx < 0 || qy < 0 || qx >= L || qy >= L || !popPlate[qy * L + qx]) { d[p] = 34; d[p + 1] = 33; d[p + 2] = 40; d[p + 3] = 255; continue; }
      const q = qy * L + qx, v = Math.min(1, Math.log1p(popA[q] + popI[q]) / lk), act = popA[q] ? Math.min(1, popA[q] / 20) : 0;
      d[p] = 18 + 217 * v; d[p + 1] = 22 + 178 * v + 30 * act; d[p + 2] = 30 + 90 * v; d[p + 3] = 255; } }
}
function popHud() { let a = 0, i = 0; for (let q = 0; q < popA.length; q++) { a += popA[q]; i += popI[q]; }
  return `tick ${popTick} · ${(a + i).toLocaleString()} cells counted (${a.toLocaleString()} active) · click the plate to open a patch at the scale of single cells`; }
// open: a patch of the plate, one square to a block of 10 × 10 places, becomes the page's world of single cells
const POPB = 10;
function popOpen(x, y) {
  const L = POP.L, {s, ox, oy} = popGeom(), cq = [Math.floor((x - ox) / s), Math.floor((y - oy) / s)];
  const ww = Math.floor(W / POPB), wh = Math.floor(H / POPB), x0 = cq[0] - (ww >> 1), y0 = cq[1] - (wh >> 1);
  popWin = {x0, y0, w: ww, h: wh, t0: tick};
  const sqOf = i => { const cx = i % W, cy = (i / W) | 0, qx = x0 + Math.floor(cx / POPB), qy = y0 + Math.floor(cy / POPB);
    return cx < ww * POPB && cy < wh * POPB && qx >= 0 && qy >= 0 && qx < L && qy < L && popPlate[qy * L + qx] ? qy * L + qx : -1; };
  // the place: rim where the patch leaves the plate; ground and sugar from the square's counts
  dishMask(); dishSq.fill(0); for (let i = 0; i < N; i++) { const q = sqOf(i); dishCell[i] = q >= 0 ? 1 : 0; if (q >= 0) dishSq[cmap[i]] = 1; }
  if (!husk || husk.length !== N) husk = new Float32Array(N); husk.fill(0); if (huskG && huskG.length === N) huskG.fill(0);
  en.fill(0); const nc = cw * chh; chem.fill(0);
  for (let i = 0; i < N; i++) { const q = sqOf(i); if (q < 0) continue; const c = cmap[i] << 4, rec = popRec.get(q);   // each place gets its share of its square's molecules
    for (let k = 0; k < 16; k++) chem[c + k] += rec ? rec.m[k] / (POPB * POPB) : P.dishFood * chemCap[c + k] / 16; }
  for (let i = 0; i < N; i++) { const q = sqOf(i); if (q >= 0) en[cmap[i]] += popN[q] * .5 / (POPB * POPB); }   // a unit of plate sugar is a division's worth: half a unit of the cell world's sugar   // a unit of sugar is a division's worth: half a unit of the cell world's sugar
  o2.fill(P.o2air || 4); fe.fill(0); light.fill(0); ltc.fill(P.dishLight); if (amb) amb.fill(P.dishLight);
  // the cells: each square's cells are rebuilt from its folded record if it has one (genotypes, their energy, remains,
  // molecules), otherwise from the inoculum; places within a square are summarised, so cells are placed at random in it
  alive.fill(0); gen.fill(0); xg.fill(0); dor.fill(0); body.fill(0); rsv.fill(0); changed.fill(1); if (coatS) { coatS.fill(0); coatM.fill(0); } coat.fill(0);
  if (!huskG || huskG.length !== N) huskG = new Int32Array(N); huskG.fill(0);
  const g0 = popStrain(), blk = new Int32Array(POPB * POPB), BB = POPB * POPB;
  for (let by = 0; by < wh; by++) for (let bx = 0; bx < ww; bx++) { const qx = x0 + bx, qy = y0 + by; if (qx < 0 || qy < 0 || qx >= L || qy >= L) continue;
    const q = qy * L + qx; if (!popPlate[q]) continue; const rec = popRec.get(q);
    const placeAt = k => (by * POPB + ((blk[k] / POPB) | 0)) * W + bx * POPB + blk[k] % POPB;
    const na = Math.min(popA[q], BB), ni = Math.min(popI[q], BB - na);
    for (let k = 0; k < BB; k++) blk[k] = k; for (let k = BB - 1; k > 0; k--) { const j = (rng() * (k + 1)) | 0; [blk[k], blk[j]] = [blk[j], blk[k]]; }
    // draw each cell's genotype from the record, in proportion to its active (or inactive) count
    // exact counts: each genotype gets its share of the square's present totals, by largest remainder, so none is lost
    const gl = rec && rec.g.length ? rec.g : null;
    const share = (key, n) => { if (!gl || n <= 0) return []; let tot = 0; for (const r of gl) tot += r[key]; if (tot <= 0) { key = key === 'a' ? 'i' : 'a'; for (const r of gl) tot += r[key]; } if (tot <= 0) return [];
      const q = gl.map(r => ({r, x: n * r[key] / tot})), out = []; let used = 0; for (const z of q) { z.f = Math.floor(z.x); used += z.f; } q.sort((u, v) => (v.x - v.f) - (u.x - u.f)); for (let k = 0; k < n - used; k++) q[k % q.length].f++;
      for (const z of q) for (let k = 0; k < z.f; k++) out.push(z.r); return out; };
    const sa = share('a', na), si = share('i', ni);
    for (let k = 0; k < na + ni; k++) { const i = placeAt(k), inact = k >= na, r = gl ? (inact ? si[k - na] : sa[k]) : null;
      if (r) popPlace(i, popGT[r.k], inact, inact ? 0 : r.e / Math.max(1, r.a)); else popPlace(i, {gen: g0.g, xg: (3 << 10) | (3 << 14), seq: g0.s || null, len: g0.len}, inact, .1); }
    // remains go back into free places, with how far along they were in breaking down
    if (rec) { let k = na + ni; for (const h of rec.h) { if (k >= BB) break; const i = placeAt(k++); husk[i] = h.t; huskG[i] = h.c; } }
  }
  if (typeof fit === 'function') fit(); popUI();
  log(`A patch of ${ww} × ${wh} squares is opened at the scale of single cells. Fold it back to return it to the plate.`);
}
// the strain: the page's one-organism seed with the dish's p–h fold, built once
let popStrainC = null;
function popStrain() {
  if (popStrainC) return popStrainC; const g = 375; let o = -1, len = 0;
  if (P.seqOn) { const i = 0; seqFromGen(i, g); if (slen[i] + 2 <= SL) { const b = i * SL; seq[b + slen[i]] = 15; seq[b + slen[i] + 1] = 7; slen[i] += 2; }
    popStrainC = {g: infold(seq, 0, slen[0]), o: -1, len: slen[0], s: seq.slice(0, slen[0])}; popStrainC.o = -1; }
  else popStrainC = {g, o: -1, len: 0};
  return popStrainC;
}
// fold: the patch's single cells are counted back into its squares; its sugar goes back too. Remains are not kept
function popFold() {
  if (!popWin) return; const {x0, y0, w, h} = popWin, L = POP.L;
  // each square of the ground is shared among its places inside the patch, so nothing is lost at the patch's edges
  const nin = new Uint16Array(cw * chh); for (let by = 0; by < h; by++) for (let bx = 0; bx < w; bx++) { const qx = x0 + bx, qy = y0 + by; if (qx < 0 || qy < 0 || qx >= L || qy >= L || !popPlate[qy * L + qx]) continue;
    for (let yy = 0; yy < POPB; yy++) for (let xx = 0; xx < POPB; xx++) nin[cmap[(by * POPB + yy) * W + bx * POPB + xx]]++; }
  for (let by = 0; by < h; by++) for (let bx = 0; bx < w; bx++) { const qx = x0 + bx, qy = y0 + by; if (qx < 0 || qy < 0 || qx >= L || qy >= L) continue;
    const q = qy * L + qx; if (!popPlate[q]) continue; let a = 0, ii = 0, s = 0; const rec = {g: [], h: [], m: new Float32Array(16)}, byG = new Map();
    for (let yy = 0; yy < POPB; yy++) for (let xx = 0; xx < POPB; xx++) { const i = (by * POPB + yy) * W + bx * POPB + xx;
      if (alive[i]) { if (coat[i]) { coatReturn(i, 1); coat[i] = 0; }   // a cell's coat goes back to the ground before it is counted
        const k = popGid(i); let r = byG.get(k); if (!r) { r = {k, a: 0, i: 0, e: 0}; byG.set(k, r); rec.g.push(r); }
        if (dor[i]) { ii++; r.i++; } else { a++; r.a++; r.e += Math.max(0, light[i]); } }
      else if (husk && husk[i] > 0) rec.h.push({c: huskG ? huskG[i] : 0, t: husk[i]}); }
    for (let yy = 0; yy < POPB; yy++) for (let xx = 0; xx < POPB; xx++) { const i = (by * POPB + yy) * W + bx * POPB + xx, c = cmap[i] << 4;
      const sh = 1 / nin[cmap[i]]; s += en[cmap[i]] * sh; for (let k = 0; k < 16; k++) rec.m[k] += chem[c + k] * sh; }
    popA[q] = a; popI[q] = ii; popN[q] = s * 2; popRec.set(q, rec); }
  log(`The patch is folded back after ${tick - popWin.t0} ticks at the scale of single cells. Its squares keep a record: their genotypes and those genotypes' energy, their remains and their molecules.`);
  popWin = null; alive.fill(0); changed.fill(1); if (typeof fit === 'function') fit(); popUI();
}
// the folded record: a table of distinct genotypes, each stored once, and for each folded square its genotypes' counts
const popRec = new Map(), popGT = [], popGTi = new Map();
function popGid(i) {
  const n = P.seqOn ? slen[i] : 0, o = i * SL; let key = gen[i] + '|' + xg[i] + '|'; for (let m = 0; m < n; m++) key += MONO[seq[o + m]];
  let k = popGTi.get(key); if (k === undefined) { k = popGT.length; popGT.push({gen: gen[i], xg: xg[i], seq: n ? seq.slice(o, o + n) : null, len: n}); popGTi.set(key, k); } return k;
}
function popPlace(i, gt, inact, e) {
  alive[i] = 1; gen[i] = gt.gen; xg[i] = gt.xg; dor[i] = inact ? 1 : 0; light[i] = e;
  if (P.seqOn) { if (gt.seq) { seq.set(gt.seq, i * SL); ORG().fill(0, i * SL, i * SL + gt.len); slen[i] = gt.len; } else seqFromGen(i, gt.gen); gen[i] = infold(seq, i * SL, slen[i]); cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH; }
}
function popUI() { const b = document.getElementById('popFold'); if (b) b.style.display = popWin ? '' : 'none'; }

// ---------------- short chains in the ground (13 November, Justin's decisions: expand the ground's chemistry; joining and
// catalysed joining). A dying cell may release a fragment of its line of expression, built from the ground's molecules,
// one per monomer. Chains join: two copies in a square link into one longer copy, spending one high-energy molecule
// (one of the four highest, which becomes its low-energy counterpart), as activation is spent in real ligation. A chain
// whose fold pairs a monomer with its partner (the chaining fold cells use for coat) speeds up joining in its square, as
// a ligase would. Chains break at a random bond into two pieces, more often the longer they are; pieces under 3 monomers
// return to the ground as molecules. A chain whose fold works a reaction catalyses it, downhill only, without being used
// up. A cell may take a chain up: like natural transformation, it replaces the best-matching stretch of the cell's
// sequence, if at least half of it matches. Each square holds up to FR kinds of chain, each with an amount of copies.
const FR = 8, FL = 32;
let frSeq = null, frLen = null, frAmt = null, frRx = null, frStr = null, frLig = null;
const FRS = {made: 0, broken: 0, taken: 0, catalysed: 0, joined: 0, copied: 0, miscopied: 0, longest: 0};
function fragAlloc() { const n = cw * chh * FR; if (!frAmt || frAmt.length !== n) { frSeq = new Uint8Array(n * FL); frLen = new Uint8Array(n); frAmt = new Float32Array(n); frRx = new Uint32Array(n); frStr = new Uint8Array(n); frLig = new Uint8Array(n); } }
function fragReturnBuf(c, buf, o, L, a) { const c16 = c << 4, u = a * P.chunit; for (let m = 0; m < L; m++) chem[c16 + buf[o + m]] += u; }
function fragReturn(sl, a) { fragReturnBuf((sl / FR) | 0, frSeq, sl * FL, frLen[sl], a); }
// put amount a of the chain buf[o..o+L) into square c: the same chain gains copies; otherwise an empty slot, or the
// scarcest chain is broken down to make room (if it is scarcer than what arrives; if not, what arrives is broken down)
function fragInsert(c, buf, o, L, a) {
  if (L < 3) { fragReturnBuf(c, buf, o, L, a); return; }
  let slot = -1, low = -1;
  for (let s = 0; s < FR; s++) { const sl = c * FR + s; if (!frAmt[sl]) { if (slot < 0) slot = sl; continue; }
    if (frLen[sl] === L) { let same = true; for (let m = 0; m < L; m++) if (frSeq[sl * FL + m] !== buf[o + m]) { same = false; break; } if (same) { frAmt[sl] += a; return; } }
    if (low < 0 || frAmt[sl] < frAmt[low]) low = sl; }
  if (slot < 0) { if (frAmt[low] >= a) { fragReturnBuf(c, buf, o, L, a); return; } fragReturn(low, frAmt[low]); frAmt[low] = 0; slot = low; }
  for (let m = 0; m < L; m++) frSeq[slot * FL + m] = buf[o + m]; frLen[slot] = L; frAmt[slot] = a;
  infold(frSeq, slot * FL, L); frRx[slot] = lastRx; frStr[slot] = lastRxS;
  let lig = 0; for (let q = 0; q < 4; q++) { const b = (lastRx >>> (8 * q)) & 255; if (!b) break; if ((b & 15) === ((b >> 4) ^ 8)) lig += ((lastRxS >> (2 * q)) & 3) || 1; } frLig[slot] = lig;
  if (L > FRS.longest) FRS.longest = L;
}
function fragRelease(i) {
  if (!P.fragOn || !P.seqOn || !chem || rng() >= P.fragRel) return; fragAlloc();
  const n = slen[i]; if (n < 3) return; const L = Math.min(n, 3 + ((rng() * 6) | 0)), st = (rng() * (n - L + 1)) | 0, o = i * SL + st, c = cmap[i], c16 = c << 4;
  const need = new Uint8Array(16); for (let m = 0; m < L; m++) need[seq[o + m]]++;
  for (let k = 0; k < 16; k++) if (need[k] && chem[c16 + k] < need[k] * P.chunit) return;   // not enough molecules to build it
  for (let k = 0; k < 16; k++) if (need[k]) chem[c16 + k] -= need[k] * P.chunit;
  fragInsert(c, seq, o, L, 1); FRS.made++;
}
const frBuf = new Uint8Array(2 * FL);
function fragStep() {                                  // every 8 ticks: breaking, joining, catalysis, uptake
  if (!P.fragOn || !frAmt || frAmt.length !== cw * chh * FR) return;
  const nsq = cw * chh;
  for (let c = 0; c < nsq; c++) { const b0 = c * FR; let any = false; for (let s = 0; s < FR; s++) if (frAmt[b0 + s]) { any = true; break; } if (!any) continue;
    const c16 = c << 4;
    // breaking: per bond, at a random bond, into two pieces
    for (let s = 0; s < FR; s++) { const sl = b0 + s, a = frAmt[sl]; if (!a) continue; const L = frLen[sl];
      let d = a * (1 - Math.pow(1 - P.fragDecay * (L - 1) / 2, 8)); if (a - d < .05) d = a; if (!(d > 0)) continue;
      frAmt[sl] = a - d; FRS.broken += d; const cut = 1 + ((rng() * (L - 1)) | 0);
      for (let m = 0; m < L; m++) frBuf[m] = frSeq[sl * FL + m];
      if (frAmt[sl] < .05) { if (frAmt[sl] > 0) fragReturn(sl, frAmt[sl]); frAmt[sl] = 0; }
      fragInsert(c, frBuf, 0, cut, d); fragInsert(c, frBuf, cut, L - cut, d); }
    // joining: pick two chains (possibly the same kind); a ligase chain in the square speeds it up
    let lig = 0, occ = 0; for (let s = 0; s < FR; s++) { const sl = b0 + s; if (frAmt[sl]) { occ++; if (frLig[sl]) lig += frLig[sl] * Math.min(1, frAmt[sl]); } }
    for (let tries = 0; tries < occ; tries++) { const sa = b0 + ((rng() * FR) | 0), sb = b0 + ((rng() * FR) | 0), a1 = frAmt[sa], a2 = frAmt[sb];   // one try for each kind of chain present
      if (a1 >= 1 && a2 >= (sa === sb ? 2 : 1) && frLen[sa] + frLen[sb] <= FL && rng() < P.fragJoin * (1 + P.fragLig * lig) * Math.min(1, a1) * Math.min(1, a2)) {
        let act = -1, best = 0; for (let k = 12; k < 16; k++) if (chem[c16 + k] >= P.chunit && RXE[k] > best) { best = RXE[k]; act = k; }   // the activating molecule
        if (act >= 0) { const L1 = frLen[sa], L2 = frLen[sb]; for (let m = 0; m < L1; m++) frBuf[m] = frSeq[sa * FL + m]; for (let m = 0; m < L2; m++) frBuf[L1 + m] = frSeq[sb * FL + m];
          chem[c16 + act] -= P.chunit; chem[c16 + act - 12] += P.chunit;   // spent: the energy goes into the bond and as heat
          frAmt[sa] -= 1; frAmt[sb] -= 1; if (frAmt[sa] < .05) { if (frAmt[sa] > 0) fragReturn(sa, frAmt[sa]); frAmt[sa] = 0; } if (sb !== sa && frAmt[sb] < .05) { if (frAmt[sb] > 0) fragReturn(sb, frAmt[sb]); frAmt[sb] = 0; }
          fragInsert(c, frBuf, 0, L1 + L2, 1); FRS.joined++; } } }
    // templated copying (13 November, Justin's decision): a chain lines up free monomers against itself, each with its
    // partner (position ^ 8), making the complementary strand, which runs the other way; copying that gives back the
    // original. A copy takes one molecule per monomer from the ground and one high-energy molecule per bond; each
    // monomer may be miscopied. The template is not used up. Ligase chains in the square speed it up
    if (P.fragCopy > 0) for (let s = 0; s < FR; s++) { const sl = b0 + s, a = frAmt[sl]; if (a < 1) continue; const L = frLen[sl];
      if (rng() >= P.fragCopy * Math.min(1, 8 / L) * (1 + P.fragLig * lig) * Math.min(1, a / 2)) continue;
      const o = sl * FL; let err = 0;
      for (let m = 0; m < L; m++) { let x = frSeq[o + L - 1 - m] ^ 8; if (rng() < P.fragErr) { x = (rng() * 16) | 0; err++; } frBuf[m] = x; }
      const need = new Uint8Array(16); for (let m = 0; m < L; m++) need[frBuf[m]]++;
      let ok = true; for (let k = 0; k < 16; k++) if (need[k] && chem[c16 + k] < need[k] * P.chunit) { ok = false; break; }
      // the bonds' activation: L - 1 high-energy molecules, taken from the four highest kinds, highest first
      let act = (L - 1) * P.chunit, have = 0; for (let k = 12; k < 16; k++) have += Math.max(0, chem[c16 + k] - need[k] * P.chunit);
      if (!ok || have < act) continue;
      for (let k = 0; k < 16; k++) if (need[k]) chem[c16 + k] -= need[k] * P.chunit;
      for (let k = 15; k >= 12 && act > 0; k--) { const t = Math.min(act, chem[c16 + k]); chem[c16 + k] -= t; chem[c16 + k - 12] += t; act -= t; }
      fragInsert(c, frBuf, 0, L, 1); FRS.copied++; if (err) FRS.miscopied++; }
    // catalysis: downhill only
    for (let s = 0; s < FR; s++) { const sl = b0 + s, r = frRx[sl]; if (!r || !frAmt[sl]) continue; const st = frStr[sl];
      for (let q = 0; q < 4; q++) { const b = (r >>> (8 * q)) & 255; if (!b) break; const S0 = b >> 4, t = b & 15; if (RXE[S0] <= RXE[t]) continue;
        const k = (st >> (2 * q)) & 3 || 1, S = chem[c16 + S0], amt = Math.min(S, 8 * P.rxRate * P.fragCat * P.chunit * k * Math.min(1, frAmt[sl]) * S / (P.rxKm + S + chem[c16 + t]));
        if (amt > 0) { chem[c16 + S0] -= amt; chem[c16 + t] += amt; FRS.catalysed += amt; } } } }
  // uptake: an active cell meets the chains in its square
  if (!P.seqOn) return;
  for (let i = 0; i < N; i++) { if (!alive[i] || dor[i]) continue; const c = cmap[i];
    for (let s = 0; s < FR; s++) { const sl = c * FR + s, a = frAmt[sl]; if (a < 1 || rng() >= P.fragUp * Math.min(1, a / 4)) continue;
      const L = frLen[sl], n0 = slen[i], o = i * SL, fo = sl * FL; if (n0 < L) continue;
      let best = -1, bm = -1; for (let p = 0; p + L <= n0; p++) { let m = 0; for (let h = 0; h < L; h++) if (seq[o + p + h] === frSeq[fo + h]) m++; if (m > bm) { bm = m; best = p; } }
      if (bm * 2 < L || bm === L) continue;                                   // too little homology, or nothing would change
      const old = seq.slice(o + best, o + best + L), g0 = gen[i];
      const oldO = ORG().slice(o + best, o + best + L);
      for (let h = 0; h < L; h++) { if (seq[o + best + h] !== frSeq[fo + h]) sOrg[o + best + h] = 1; seq[o + best + h] = frSeq[fo + h]; }
      const g1 = infold(seq, o, n0);
      if (g1 !== g0 && P.chemOn && !swapChem(c << 4, g0, g1)) { seq.set(old, o + best); sOrg.set(oldO, o + best); continue; }   // the cell cannot pay for its new compound
      gen[i] = g1; cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH; changed[i] = 1;
      fragReturn(sl, 1); frAmt[sl] -= 1; if (frAmt[sl] < .05) { if (frAmt[sl] > 0) fragReturn(sl, frAmt[sl]); frAmt[sl] = 0; } FRS.taken++; break; } }
}
function fragCount() { if (!frAmt) return 0; let k = 0; for (let s = 0; s < frAmt.length; s++) if (frAmt[s] >= .5) k++; return k; }

// ---------------- the fold viewer (Tier 1, display only): the inspected cell's chain drawn in 3D from its bracket fold.
// Oily monomers (odd codes, task 12's assignment) are amber, polar ones blue; paired monomers are joined by thin grey
// lines. The shape is a relaxed layout of the brackets, not a computed physical fold. Drag to turn it.
const FV = {seq: null, n: 0, pairs: [], xyz: null, yaw: 0, pitch: .35, raf: 0, drag: null};
function fvLayout(a, n) {
  const pairs = [], mark = new Uint8Array(n), k = geneSegs(a, 0, n); mark.fill(1);   // each gene folds on its own; marker monomers belong to none
  for (let q = 0; q < k; q++) { const st = []; for (let h = gSeg[2 * q]; h < gSeg[2 * q + 1]; h++) { mark[h] = 0; const m = a[h]; if (st.length && a[st[st.length - 1]] === (m ^ 8)) pairs.push([st.pop(), h]); else st.push(h); } }
  FV.mark = mark; FV.genes = k;
  const p = new Float32Array(n * 3);
  for (let h = 0; h < n; h++) { const t = h * 1.75; p[3 * h] = Math.cos(t) * 1.6; p[3 * h + 1] = h * .25 - n * .125; p[3 * h + 2] = Math.sin(t) * 1.6; }   // start as a loose coil
  const f = new Float32Array(n * 3), spr = (i, j, L, k) => {
    const dx = p[3 * j] - p[3 * i], dy = p[3 * j + 1] - p[3 * i + 1], dz = p[3 * j + 2] - p[3 * i + 2], d = Math.hypot(dx, dy, dz) || 1e-6, s = k * (d - L) / d;
    f[3 * i] += s * dx; f[3 * i + 1] += s * dy; f[3 * i + 2] += s * dz; f[3 * j] -= s * dx; f[3 * j + 1] -= s * dy; f[3 * j + 2] -= s * dz; };
  for (let it = 0; it < 220; it++) { f.fill(0);
    for (let h = 1; h < n; h++) spr(h - 1, h, 1, .5);                            // the chain's bonds
    for (const [i, j] of pairs) spr(i, j, 1.1, .3);                               // paired monomers sit side by side
    for (let i = 0; i < n; i++) for (let j = i + 2; j < n; j++) {                  // nothing overlaps
      const dx = p[3 * j] - p[3 * i], dy = p[3 * j + 1] - p[3 * i + 1], dz = p[3 * j + 2] - p[3 * i + 2], d2 = dx * dx + dy * dy + dz * dz;
      if (d2 < 2.25) { const d = Math.sqrt(d2) || 1e-6, s = -.2 * (1.5 - d) / d; f[3 * i] += s * dx; f[3 * i + 1] += s * dy; f[3 * i + 2] += s * dz; f[3 * j] -= s * dx; f[3 * j + 1] -= s * dy; f[3 * j + 2] -= s * dz; } }
    for (let q = 0; q < 3 * n; q++) p[q] += Math.max(-.3, Math.min(.3, f[q])); }
  let cx = 0, cy = 0, cz = 0; for (let h = 0; h < n; h++) { cx += p[3 * h]; cy += p[3 * h + 1]; cz += p[3 * h + 2]; }
  cx /= n; cy /= n; cz /= n; let r = 1; for (let h = 0; h < n; h++) { p[3 * h] -= cx; p[3 * h + 1] -= cy; p[3 * h + 2] -= cz; r = Math.max(r, Math.hypot(p[3 * h], p[3 * h + 1], p[3 * h + 2])); }
  for (let q = 0; q < 3 * n; q++) p[q] /= r;
  return {pairs, xyz: p};
}
function fvDraw() {
  const cvs = document.querySelectorAll('canvas.foldview'); if (!cvs.length || !FV.xyz) { FV.raf = 0; return; }
  if (!FV.drag) FV.yaw += .01;
  const n = FV.n, p = FV.xyz, cy = Math.cos(FV.yaw), sy = Math.sin(FV.yaw), cp = Math.cos(FV.pitch), sp = Math.sin(FV.pitch), s = new Float32Array(n * 3);
  for (let h = 0; h < n; h++) { const x = p[3 * h], y = p[3 * h + 1], z = p[3 * h + 2], x1 = cy * x + sy * z, z1 = -sy * x + cy * z, y1 = cp * y - sp * z1, z2 = sp * y + cp * z1; s[3 * h] = x1; s[3 * h + 1] = y1; s[3 * h + 2] = z2; }
  for (const cv of cvs) { const g = cv.getContext('2d'), w = cv.width, hh = cv.height, k = Math.min(w, hh) * .42, X = q => w / 2 + s[3 * q] * k, Y = q => hh / 2 - s[3 * q + 1] * k;
    g.clearRect(0, 0, w, hh); g.lineWidth = 1; g.strokeStyle = 'rgba(160,160,160,.45)'; g.setLineDash([2, 2]);
    for (const [i, j] of FV.pairs) { g.beginPath(); g.moveTo(X(i), Y(i)); g.lineTo(X(j), Y(j)); g.stroke(); }
    g.setLineDash([]); g.lineWidth = 2; g.strokeStyle = 'rgba(200,200,200,.7)'; g.beginPath(); for (let h = 0; h < n; h++) h ? g.lineTo(X(h), Y(h)) : g.moveTo(X(h), Y(h)); g.stroke();
    const ord = [...Array(n).keys()].sort((a, b) => s[3 * a + 2] - s[3 * b + 2]);
    for (const h of ord) { const d = .65 + .35 * s[3 * h + 2]; g.fillStyle = FV.mark && FV.mark[h] ? `rgba(150,150,150,${d})` : (FV.seq[h] & 1) ? `rgba(230,160,40,${d})` : `rgba(70,140,230,${d})`;
      g.beginPath(); g.arc(X(h), Y(h), Math.max(2, k * .07 * (1 + .3 * s[3 * h + 2])), 0, 7); g.fill(); } }
  FV.raf = requestAnimationFrame(fvDraw);
}
function fvShow(i) {
  if (typeof seq === 'undefined' || !seq || !slen || !alive[i] || !slen[i]) return;
  const n = slen[i], a = seq.slice(i * SL, i * SL + n), L = fvLayout(a, n); FV.seq = a; FV.n = n; FV.pairs = L.pairs; FV.xyz = L.xyz;
  const html = `<div style="margin-top:6px"><b>Its fold</b> <span style="color:var(--muted)">(${n} monomers in ${FV.genes} gene${FV.genes === 1 ? '' : 's'}, ${L.pairs.length} pairs; amber oily, blue polar, grey gene markers; a layout of the brackets, not a physical fold; drag to turn)</span></div><canvas class="foldview" width="240" height="190" style="width:240px;height:190px;touch-action:none;cursor:grab"></canvas>`;
  for (const el of [document.getElementById('insp'), typeof inspFloatBody !== 'undefined' ? inspFloatBody : null]) if (el) el.insertAdjacentHTML('beforeend', html);
  document.querySelectorAll('canvas.foldview').forEach(cv => {
    cv.onpointerdown = e => { FV.drag = {x: e.clientX, y: e.clientY, yaw: FV.yaw, pitch: FV.pitch}; cv.setPointerCapture(e.pointerId); e.stopPropagation(); };
    cv.onpointermove = e => { if (!FV.drag) return; FV.yaw = FV.drag.yaw + (e.clientX - FV.drag.x) * .01; FV.pitch = Math.max(-1.5, Math.min(1.5, FV.drag.pitch + (e.clientY - FV.drag.y) * .01)); };
    cv.onpointerup = () => { FV.drag = null; }; });
  if (!FV.raf) FV.raf = requestAnimationFrame(fvDraw);
}
{ const _inspFV = inspect; inspect = function (x, y) { _inspFV(x, y); try { fvShow(idx(x, y)); } catch (e) { console.warn('fold viewer', e); } }; }

// ---------------- the gene list (display only): each gene of the inspected cell with its own domains and reactions.
function geneListHtml(i) {
  if (typeof seq === 'undefined' || !seq || !slen || !alive[i] || !slen[i] || !P.seqOn) return '';
  const o = i * SL, n = slen[i], k = geneSegs(seq, o, n), segs = []; for (let q = 0; q < k; q++) segs.push([gSeg[2 * q], gSeg[2 * q + 1]]);
  const rxName = b => (b & 15) === ((b >> 4) ^ 8) && P.cellClumps && P.sugarCoat > 0 ? 'sugar→coat' : MONO[b >> 4] + '→' + MONO[b & 15];
  const seen = new Map(), rows = []; let total = 0;
  segs.forEach(([s0, e0], q) => { const txt = Array.from(seq.slice(o + s0, o + e0), m => MONO[m]).join('');
    infoldGene(seq, o + s0, e0 - s0); let ads = 0, work = 0; for (let d = 0; d < dN; d++) { if (sAd[d]) ads++; else if (dS[d] >= P.domMin) work++; }
    const rs = []; for (let r = 0; r < 4; r++) { const b = (lastRx >>> (8 * r)) & 255; if (!b) break; rs.push(`${rxName(b)}${((lastRxS >> (2 * r)) & 3) > 1 ? ' ×' + ((lastRxS >> (2 * r)) & 3) : ''}`); }
    const capped = Math.max(0, Math.min(rs.length, 8 - total)); total += rs.length;
    let oO = 0, oV = 0; { const OG = ORG(); for (let h = s0; h < e0; h++) { const v = OG[o + h]; if (v === 1) oO++; else if (v === 2) oV++; } }
    const L0 = e0 - s0, from = oV * 2 > L0 ? 'from a virus' : oO * 2 > L0 ? 'from outside' : (oV || oO) ? 'by descent, partly from outside' : 'by descent';
    const twin = seen.has(txt) ? ` <span style="color:var(--muted)">(a copy of gene ${seen.get(txt)})</span>` : ''; if (!seen.has(txt)) seen.set(txt, q + 1);
    rows.push(`<div><b>Gene ${q + 1}</b> · monomers ${s0 + 1}–${e0} (${e0 - s0}) · ${dN} domain${dN === 1 ? '' : 's'}${ads ? ` (${ads} adaptor${ads === 1 ? '' : 's'})` : ''} · ${from}${(oV || oO) ? ` (${oV ? oV + ' virus' : ''}${oV && oO ? ', ' : ''}${oO ? oO + ' outside' : ''} of ${L0})` : ''}${twin}<br><span style="font-family:monospace;font-size:11px;word-break:break-all">${txt.length > 64 ? txt.slice(0, 64) + '…' : txt}</span><br>Reactions: ${rs.length ? rs.map((t, r) => r < capped ? t : `<span style="color:var(--muted);text-decoration:line-through">${t}</span>`).join(', ') : '<span style="color:var(--muted)">none</span>'}</div>`); });
  const mk = n - segs.reduce((a, [s0, e0]) => a + e0 - s0, 0);
  return `<div style="margin-top:6px"><b>Its genes</b> <span style="color:var(--muted)">(${k} gene${k === 1 ? '' : 's'}${mk ? `, ${mk} marker monomers` : ''}; reactions past the cell's 8 are struck through: they are carried but do not run)</span>${rows.join('')}</div>`;
}
{ const _inspGL = inspect; inspect = function (x, y) { _inspGL(x, y); try { const h = geneListHtml(idx(x, y)); if (h) for (const el of [document.getElementById('insp'), typeof inspFloatBody !== 'undefined' ? inspFloatBody : null]) if (el) el.insertAdjacentHTML('beforeend', h); } catch (e) { console.warn('gene list', e); } }; }

// ---------------- the visiting order (Justin, 14 November): a fresh random order of the places each tick, from the seeded rng.
// For speed the shuffle keeps neighbours together: 8 x 8 tiles are visited in random order, and inside each tile the 64
// places follow one of 32 random orders drawn afresh each tick. No row, column or tile position is favoured.
let VORD = null, VORDt = -1, VPOOL = null;
function visitOrder() {
  if (!VORD || VORD.length !== N) { VORD = new Int32Array(N); VPOOL = new Uint8Array(32 * 64); VORDt = -1; }
  if (VORDt === tick) return; VORDt = tick;
  if (P.randOrder === false) { for (let i = 0; i < N; i++) VORD[i] = i; return; }
  for (let q = 0; q < 32; q++) { const o = q * 64; for (let h = 0; h < 64; h++) VPOOL[o + h] = h;
    for (let h = 63; h > 0; h--) { const r = (rng() * (h + 1)) | 0, t = VPOOL[o + h]; VPOOL[o + h] = VPOOL[o + r]; VPOOL[o + r] = t; } }
  const tw = Math.ceil(W / 8), th = Math.ceil(H / 8), nt = tw * th, T = new Int32Array(nt);
  for (let t = 0; t < nt; t++) T[t] = t;
  for (let h = nt - 1; h > 0; h--) { const r = (rng() * (h + 1)) | 0, t = T[h]; T[h] = T[r]; T[r] = t; }
  let k = 0;
  for (let t = 0; t < nt; t++) { const tx = (T[t] % tw) * 8, ty = ((T[t] / tw) | 0) * 8, o = ((rng() * 32) | 0) * 64;
    for (let h = 0; h < 64; h++) { const v = VPOOL[o + h], x = tx + (v & 7), y = ty + (v >> 3); if (x < W && y < H) VORD[k++] = y * W + x; } }
}

// ---------------- pigments (P.pigment): light is absorbed only through a pigment the cell has made and keeps in its coat.
// Pigments are the four costliest molecules (kinds 12-15): making them runs uphill, so phototrophy has a price and has to evolve.
function pigOf(i) { if (!coatM || !coatK || coatK[i] < 12) return P.pigBase; return Math.min(1, P.pigBase + coatM[i] / P.pigSat); }

// ---------------- viruses (Justin's queue, 15 November): selfish chains. Nothing here names a virus; the parts are:
// - entry through a receptor: a chain in the ground can enter a cell when its first monomer is the molecule one of the
//   cell's own domains takes (the domain binds the chain's end as if it were its substrate). So which chains get in depends
//   on what the cell's enzymes do, and a cell can escape a chain only by changing them;
// - a chain inside a cell (an episome; one kind per cell) is copied by the cell only if the chain itself carries a copying
//   fold (a domain pairing a monomer with its complement, the same fold that ligates chains in the ground); each copy is paid
//   for by the cell in molecules from its square and in energy;
// - at virBurst copies the cell bursts: it dies, and the copies go back into the ground as chains, to meet other cells;
// - a dividing cell gives half its copies to its daughter; a cell that dies otherwise spills its copies.
const VIR = {seq: null, len: null, n: null, kill: null, lig: null, entered: 0, copied: 0, burst: 0, spilled: 0};
function virAlloc() { if (!VIR.n || VIR.n.length !== N) { VIR.seq = new Uint8Array(N * FL); VIR.len = new Uint8Array(N); VIR.n = new Float32Array(N); VIR.kill = new Uint8Array(N); VIR.lig = new Uint8Array(N); } }
function virSpill(i) { if (!VIR.n || !(VIR.n[i] > 0)) return; fragAlloc(); fragInsert(cmap[i], VIR.seq, i * FL, VIR.len[i], VIR.n[i]); VIR.spilled += VIR.n[i]; VIR.n[i] = 0; VIR.len[i] = 0; VIR.kill[i] = 0; }
function virMove(i, j) { if (!VIR.n || !(VIR.n[i] > 0)) return; VIR.seq.copyWithin(j * FL, i * FL, i * FL + FL); VIR.len[j] = VIR.len[i]; VIR.n[j] = VIR.n[i]; VIR.lig[j] = VIR.lig[i]; VIR.kill[j] = VIR.kill[i]; VIR.n[i] = 0; VIR.len[i] = 0; VIR.kill[i] = 0; }
function virBorn(i, pj) {                                   // a newborn: whatever an earlier occupant left is spilled; the parent shares its copies
  if (!VIR.n) return; if (VIR.n[i] > 0) virSpill(i); VIR.kill[i] = 0;
  if (pj < 0 || !(VIR.n[pj] >= 1)) return; const h = Math.floor(VIR.n[pj] / 2); if (h < 1) return;
  VIR.seq.copyWithin(i * FL, pj * FL, pj * FL + FL); VIR.len[i] = VIR.len[pj]; VIR.lig[i] = VIR.lig[pj]; VIR.n[i] = h; VIR.n[pj] -= h;
}
function virStep() {                                       // every 8 ticks, after the chains' own chemistry
  if (!P.virOn || !P.fragOn || !P.seqOn || !frAmt) return; virAlloc();
  for (let i = 0; i < N; i++) {
    if (!alive[i]) { if (VIR.n[i] > 0) virSpill(i); continue; }
    const c = cmap[i];
    if (!(VIR.n[i] > 0)) {                                  // entry: a chain whose first monomer one of this cell's domains takes
      const r = rx[i], r2 = rx2[i]; if (!r || dor[i]) continue;
      for (let s = 0; s < FR; s++) { const sl = c * FR + s, a = frAmt[sl]; if (a < 1) continue; const m0 = frSeq[sl * FL];
        let fits = false; for (let q = 0; q < 8; q++) { const b = ((q < 4 ? r : r2) >>> (8 * (q & 3))) & 255; if (!b) { if (q < 4) { q = 3; continue; } break; } if ((b >> 4) === m0) { fits = true; break; } }
        if (!fits || rng() >= P.virUp * Math.min(1, a / 4)) continue;
        for (let h = 0; h < frLen[sl]; h++) VIR.seq[i * FL + h] = frSeq[sl * FL + h];
        VIR.len[i] = frLen[sl]; VIR.lig[i] = frLig[sl]; VIR.n[i] = 1; frAmt[sl] -= 1; if (frAmt[sl] < .05) { if (frAmt[sl] > 0) fragReturn(sl, frAmt[sl]); frAmt[sl] = 0; }
        VIR.entered++; break; }
      continue;
    }
    if (P.virInteg > 0 && P.seqOn && slen[i] && !dor[i] && rng() < P.virInteg && virIntegrate(i) && !(VIR.n[i] > 0)) continue;   // the chain may join the genome as a gene (a prophage)
    if (!VIR.lig[i] || dor[i]) continue;                    // copying: only a chain with a copying fold gets the cell to copy it
    const L = VIR.len[i], o = i * FL, c16 = c << 4, k = Math.min(4, VIR.n[i]) * VIR.lig[i] * P.virCopy;
    let copies = Math.floor(k) + (rng() < k - Math.floor(k) ? 1 : 0);
    while (copies-- > 0) {
      const eCost = P.virE * L; if (light[i] < eCost) break;
      let ok = true; for (let h = 0; h < L; h++) if (chem[c16 + VIR.seq[o + h]] < P.chunit) { ok = false; break; } if (!ok) break;
      for (let h = 0; h < L; h++) chem[c16 + VIR.seq[o + h]] -= P.chunit; light[i] -= eCost; VIR.n[i] += 1; VIR.copied++;
    }
    if (VIR.n[i] >= P.virBurst) { VIR.kill[i] = 1; VIR.burst++; }
  }
}
{ const _resetV = reset; reset = function (...a) { if (VIR.n) { VIR.n.fill(0); VIR.len.fill(0); VIR.kill.fill(0); VIR.lig.fill(0); } VIR.entered = VIR.copied = VIR.burst = VIR.spilled = 0; return _resetV.apply(this, a); }; }   // a new world starts free of chains inside cells

// ---------------- the first organism in a sunlit world carries a pigment-making fold (Justin, 15 November, option b): it stands
// for an ancestor that has already evolved phototrophy. The fold is appended to its line of expression as one closed domain,
// so its compound (the unpaired monomers) is unchanged; descendants inherit, vary or lose it like any other fold.
function pigFounder() {
  if (!P.pigment || !P.seqOn || !P.domOn || !P.rxDom || P.env === 'vent' || P.env === 'dish') return 0;
  if (slen.length !== N) seqAlloc();
  const fs = []; for (let i = 0; i < N; i++) if (alive[i]) fs.push(i); if (!fs.length) return 0;
  const tryD = (i, D) => { const o = i * SL, n0 = slen[i]; if (n0 + D.length > SL) return null; const g0 = infold(seq, o, n0);
    for (let h = 0; h < D.length; h++) seq[o + n0 + h] = D[h]; const g = infold(seq, o, n0 + D.length), r = lastRx;
    for (let q = 0; q < 4; q++) { const b = (r >>> (8 * q)) & 255; if (!b) break; const s = b >> 4, t = b & 15;
      if (t >= 12 && t !== (s ^ 8) && g === g0) return {g, s, t}; }
    return null; };
  let D = null, pt = -1; const i0 = fs[0]; if (!slen[i0]) seqFromGen(i0, gen[i0]);
  outer: for (let s = 0; s < 16; s++) for (let a = 0; a < 16; a++) { const core = [[s, a, a ^ 8, s ^ 8], [s, s, s ^ 8, s ^ 8]][a & 1 ? 1 : 0], mk = (s + 5) & 15, cand = (s === mk || (s ^ 8) === mk) ? core : [mk, mk, mk, mk, ...core];   // its own gene, behind a marker
    const r0 = tryD(i0, cand); if (r0) { D = cand; pt = r0.t; break outer; } }
  if (!D) return 0;
  let k = 0; for (const i of fs) { if (!slen[i]) seqFromGen(i, gen[i]); const o = i * SL, n0 = slen[i]; if (n0 + D.length > SL) continue;
    for (let h = 0; h < D.length; h++) seq[o + n0 + h] = D[h]; slen[i] = n0 + D.length;
    gen[i] = infold(seq, o, slen[i]); cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; cH[i] = lastCH; changed[i] = 1; k++;
    if (P.cellClumps && pt >= 0) { coatAlloc(); const c16 = cmap[i] << 4, m = Math.min(P.pigSat, chem[c16 + pt]);   // it starts with some pigment in its coat, taken from the ground's own molecules of that kind
      if (m > 0) { if (coatM[i] && coatK[i] !== pt) { chem[c16 + coatK[i]] += coatM[i]; coatM[i] = 0; } chem[c16 + pt] -= m; coatK[i] = pt; coatM[i] += m; } } }
  return k;
}
{ const _resetP = reset; reset = function (...a) { const r = _resetP.apply(this, a); if (a[0] === 'organism') { const k = pigFounder(); if (k) log(`The first organism carries a fold that makes a pigment, so it can use light.`); } return r; }; }
// the vent founder's chemotroph gene (Justin, 16 November, report 29 proposal 1): as the sunlit founder gets a pigment gene,
// the vent founder gets one closed domain behind a marker whose reaction runs downhill on a molecule plentiful in its
// square, found by the same search; the compound is unchanged. Scored by the energy released times the square's supply.
function chemoFounder() {
  if (P.chemoFounder === false || !P.seqOn || !P.domOn || !P.rxDom || P.env !== 'vent') return 0;
  if (slen.length !== N) seqAlloc();
  const fs = []; for (let i = 0; i < N; i++) if (alive[i]) fs.push(i); if (!fs.length) return 0;
  const i0 = fs[0]; if (!slen[i0]) seqFromGen(i0, gen[i0]); const c16 = cmap[i0] << 4;
  let D = null, best = 0;
  for (let s0 = 0; s0 < 16; s0++) for (let a = 0; a < 16; a++) { const core = [[s0, a, a ^ 8, s0 ^ 8], [s0, s0, s0 ^ 8, s0 ^ 8]][a & 1 ? 1 : 0], mk = (s0 + 5) & 15, cand = (s0 === mk || (s0 ^ 8) === mk) ? core : [mk, mk, mk, mk, ...core];
    const o = i0 * SL, n0 = slen[i0]; if (n0 + cand.length > SL) continue; const g0 = infold(seq, o, n0);
    for (let h = 0; h < cand.length; h++) seq[o + n0 + h] = cand[h]; const g = infold(seq, o, n0 + cand.length), r = lastRx; if (g !== g0) continue;
    for (let q = 0; q < 4; q++) { const b = (r >>> (8 * q)) & 255; if (!b) break; const sk = b >> 4, t = b & 15; if (t === (sk ^ 8)) continue;
      const sc = (RXE[sk] - RXE[t]) * chem[c16 + sk]; if (sc > best) { best = sc; D = cand; } } }
  infold(seq, i0 * SL, slen[i0]); if (!D) return 0;
  let k = 0; for (const i of fs) { if (!slen[i]) seqFromGen(i, gen[i]); const o = i * SL, n0 = slen[i]; if (n0 + D.length > SL) continue;
    for (let h = 0; h < D.length; h++) seq[o + n0 + h] = D[h]; slen[i] = n0 + D.length;
    gen[i] = infold(seq, o, slen[i]); cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; rx2[i] = lastRx2; rxStr2[i] = lastRxS2; cH[i] = lastCH; changed[i] = 1; k++; }
  CHF.gene = D.map(m => MONO[m]).join(''); return k;
}
const CHF = {gene: ''};
{ const _resetC = reset; reset = function (...a) { const r = _resetC.apply(this, a); if (a[0] === 'organism') { const k = chemoFounder(); if (k) log(`The first organism carries a fold that runs a reaction downhill on the vent's molecules, so it can live on chemistry (${CHF.gene}).`); } return r; }; }
function pigBorn(i, pj) {                                  // a dividing cell shares its pigment: the daughter gets half the pigment in the parent's coat
  if (!P.pigment || pj < 0 || !coatM || !(coatM[pj] > 0) || coatK[pj] < 12) return;
  const c16 = cmap[i] << 4; if (coatM[i] > 0) { chem[c16 + coatK[i]] += coatM[i]; coatM[i] = 0; }
  const h = coatM[pj] * .5; coatM[pj] -= h; coatK[i] = coatK[pj]; coatM[i] = h;
}

// ---------------- the decay economy (Justin, 15 November). Before: a dying cell released a fixed bit of sugar, and the energy it
// had stored was lost; dissolved sugar rotted away at edecay a tick, as if eaten by microbes the page did not model.
// Now a dying cell's stored energy becomes remains (detritus) in its square. Remains do not spread. They leach a little sugar
// on their own (detLeach) and rot slowly to CO2 (detRot), but mostly they are broken down by heterotrophs: each living cell
// in the square adds its heterotrophy level (the het gene, 0-3) to the square's enzymes, and enzymes free detBreak of the
// remains per unit per tick as sugar into the water. The sugar is shared, so decomposers feed their neighbours too.
const DET = {a: null, made: 0, toSugar: 0, rot: 0, hs: null};
function detAlloc() { const n = cw * chh; if (!DET.a || DET.a.length !== n) { DET.a = new Float32Array(n); DET.hs = new Float32Array(n); } }
function detDie(i) {
  if (!P.detOn || P.env === 'dish') return; detAlloc(); const e = light[i]; if (e > 0) { DET.a[cmap[i]] += e; DET.made += e; light[i] = 0; } }
function detStep() {
  if (!P.detOn || P.env === 'dish' || !DET.a) return; const n = cw * chh, hs = DET.hs; hs.fill(0);
  if (P.gHet) for (let i = 0; i < N; i++) if (alive[i] && !dor[i]) { const h = (xg[i] >> 10) & 3; if (h) hs[cmap[i]] += h; }
  for (let c = 0; c < n; c++) { const d = DET.a[c]; if (!(d > 0)) continue;
    const brk = d * Math.min(.5, P.detBreak * hs[c]), lch = d * P.detLeach, rot = d * P.detRot, s = brk + lch;
    DET.a[c] = d - s - rot; en[c] += s; enMade += s; DET.toSugar += s; DET.rot += rot;
    if (P.rxn) { co2[c] += rot; OLF.co2L += rot; } }
}
{ const _resetD = reset; reset = function (...a) { if (DET.a) DET.a.fill(0); DET.made = DET.toSugar = DET.rot = 0; return _resetD.apply(this, a); }; }

// ---------------- stage 1 of the genome (Justin, 15 November; design/genome_stage1.md)
// A run of 4 or more identical monomers marks a gene boundary. The marker's monomers belong to no gene. Each gene folds on
// its own with infoldGene (the old infold): pairs never cross a marker, and adapters act inside their own gene. The cell's
// compound is the genes' unpaired monomers summed (capped at 3 per kind, as before); its reactions are the genes' reactions,
// up to 4 per gene and 8 per cell (lastRx, then lastRx2). A line with no marker is one gene and folds exactly as before.
const GMARK = 4, gK = new Uint8Array(SL), gS = new Uint8Array(SL), gA = new Uint8Array(SL), gB = new Uint8Array(SL), gO = new Uint8Array(SL),
  gQ = new Uint16Array(SL), gT = new Uint16Array(SL), gAd = new Uint8Array(SL), gSeg = new Int16Array(SL * 2), gEx = new Uint8Array(16);
let lastGenes = 1;
function geneSegs(a, o, n) {                               // the genes of a line: [start, end) pairs in gSeg; returns how many
  let k = 0, s = 0, h = 0;
  while (h < n) { let r = h + 1; while (r < n && a[o + r] === a[o + h]) r++;
    if (r - h >= GMARK) { if (h > s) { gSeg[2 * k] = s; gSeg[2 * k + 1] = h; k++; } s = r; }
    h = r; }
  if (n > s) { gSeg[2 * k] = s; gSeg[2 * k + 1] = n; k++; }
  return k;
}
function infold(a, o, n) {
  const k = geneSegs(a, o, n);
  if (k === 1 && gSeg[0] === 0 && gSeg[1] === n) { lastGenes = 1; const g = infoldGene(a, o, n); lastRx2 = 0; lastRxS2 = 0; return g; }   // one gene, no marker: as before
  lastGenes = k; gEx.fill(0); let catS = new Uint8Array(8), rxs = [], strs = [], ch = 0, ad = 0, hid = 0, prs = 0, nd = 0;
  for (let q = 0; q < k; q++) { const s0 = gSeg[2 * q], e0 = gSeg[2 * q + 1], g = infoldGene(a, o + s0, e0 - s0);
    for (let m = 0; m < 16; m++) gEx[m] = Math.min(3, gEx[m] + ((g >>> (2 * m)) & 3));
    for (let m = 0; m < 8; m++) catS[m] = Math.min(3, catS[m] + ((lastCat >> (2 * m)) & 3));
    for (let r = 0; r < 4; r++) { const b = (lastRx >>> (8 * r)) & 255; if (!b) break; rxs.push(b); strs.push((lastRxS >> (2 * r)) & 3); }
    if (lastCH) ch = (Math.imul(ch ^ lastCH ^ (q + 1), 2654435761) >>> 0) || 1; ad += lastAd; hid += dHidden; prs += dPairs;
    for (let d = 0; d < dN && nd < SL; d++, nd++) { gK[nd] = dK[d]; gS[nd] = dS[d]; gA[nd] = dA[d] + s0; gB[nd] = dB[d] + s0; gO[nd] = dO[d]; gQ[nd] = dQ[d]; gT[nd] = dT[d]; gAd[nd] = sAd[d]; } }
  dN = nd; for (let d = 0; d < nd; d++) { dK[d] = gK[d]; dS[d] = gS[d]; dA[d] = gA[d]; dB[d] = gB[d]; dO[d] = gO[d]; dQ[d] = gQ[d]; dT[d] = gT[d]; sAd[d] = gAd[d]; }
  dHidden = hid; dPairs = prs; lastCH = ch; lastAd = ad;
  lastRx = 0; lastRxS = 0; lastRx2 = 0; lastRxS2 = 0;
  for (let r = 0; r < Math.min(8, rxs.length); r++) { if (r < 4) { lastRx |= rxs[r] << (8 * r); lastRxS |= strs[r] << (2 * r); } else { lastRx2 |= rxs[r] << (8 * (r - 4)); lastRxS2 |= strs[r] << (2 * (r - 4)); } }
  lastRx >>>= 0; lastRx2 >>>= 0;
  lastCat = 0; for (let m = 0; m < 8; m++) lastCat |= catS[m] << (2 * m);
  sEx.set(gEx); let g = 0; for (let m = 0; m < 16; m++) g = (g | (gEx[m] << (2 * m))) >>> 0; return g;
}
function markerFor(a, o, n, at, next) {                    // a marker kind that does not run on into its neighbours
  for (let m = 0; m < 16; m++) { const k = (at * 7 + m * 5 + 3) & 15; if ((at > 0 && a[o + at - 1] === k) || next === k) continue; return k; }
  return 0;
}
function geneOps(buf, n, ob) {                                 // at division: a whole gene duplicated (after itself) or lost
  if (!(P.geneDup > 0 || P.geneDel > 0)) return n;
  if (P.geneDup > 0 && rng() < P.geneDup) { const k = geneSegs(buf, 0, n), q = (rng() * k) | 0, s0 = gSeg[2 * q], e0 = gSeg[2 * q + 1], L = e0 - s0;
    if (L > 0 && n + L + GMARK <= SL) { const tail = buf.slice(e0, n), mk = markerFor(buf, 0, n, e0, buf[s0]);
      if (ob) { const ot = ob.slice(e0, n), o0 = ob[s0]; let v = e0; for (let h = 0; h < GMARK; h++) ob[v++] = o0; ob.copyWithin(v, s0, e0); v += L; ob.set(ot, v); }
      let w = e0; for (let h = 0; h < GMARK; h++) buf[w++] = mk; for (let h = 0; h < L; h++) buf[w++] = buf[s0 + h]; for (let h = 0; h < tail.length; h++) buf[w++] = tail[h];
      n = w; geneDupN++; } }
  if (P.geneDel > 0 && rng() < P.geneDel) { const k = geneSegs(buf, 0, n); if (k >= 2) { const q = (rng() * k) | 0;
      let s0 = gSeg[2 * q], e0 = gSeg[2 * q + 1]; if (q > 0) s0 = gSeg[2 * (q - 1) + 1]; else e0 = gSeg[2]; // take one neighbouring marker with it
      if (ob) ob.copyWithin(s0, e0, n); const tail = buf.slice(e0, n); let w = s0; for (let h = 0; h < tail.length; h++) buf[w++] = tail[h]; n = w; geneDelN++; } }
  return n;
}
let geneDupN = 0, geneDelN = 0, geneHGTN = 0, virIntegN = 0;
const GT = {j: -1, len: 0, cat: 0, rx: 0, rs: 0, rx2: 0, rs2: 0, ch: 0};
function geneTransfer(i, j) {                              // contagion carries one whole gene of the donor and adds it to the recipient as a new gene
  const Li = slen[i], Lj = slen[j]; const k = geneSegs(seq, i * SL, Li), q = (rng() * k) | 0, s0 = gSeg[2 * q], e0 = gSeg[2 * q + 1], L = e0 - s0;
  if (L < 2 || Lj + GMARK + L > SL) return null;
  { const oi = i * SL, oj = j * SL, kj = geneSegs(seq, oj, Lj);              // a gene the recipient already has is not taken again (kin share their genes)
    for (let r = 0; r < kj; r++) { const a0 = gSeg[2 * r], b0 = gSeg[2 * r + 1]; if (b0 - a0 !== L) continue; let same = true;
      for (let h = 0; h < L; h++) if (seq[oj + a0 + h] !== seq[oi + s0 + h]) { same = false; break; } if (same) return null; } }
  GT.j = j; GT.len = Lj; GT.cat = cat[j]; GT.rx = rx[j]; GT.rs = rxStr[j]; GT.rx2 = rx2[j]; GT.rs2 = rxStr2[j]; GT.ch = cH[j];
  const oj = j * SL, mk = markerFor(seq, oj, Lj, Lj, seq[i * SL + s0]); let w = Lj;
  { const OG = ORG(); for (let h = 0; h < GMARK; h++) OG[oj + Lj + h] = 1; for (let h = 0; h < L; h++) OG[oj + Lj + GMARK + h] = OG[i * SL + s0 + h] || 1; }
  for (let h = 0; h < GMARK; h++) seq[oj + w++] = mk; for (let h = 0; h < L; h++) seq[oj + w++] = seq[i * SL + s0 + h]; slen[j] = w; geneHGTN++;
  const g = infold(seq, oj, w); cat[j] = lastCat; rx[j] = lastRx; rxStr[j] = lastRxS; rx2[j] = lastRx2; rxStr2[j] = lastRxS2; cH[j] = lastCH; return g;
}
function geneTransferUndo(j) { slen[j] = GT.len; cat[j] = GT.cat; rx[j] = GT.rx; rxStr[j] = GT.rs; rx2[j] = GT.rx2; rxStr2[j] = GT.rs2; cH[j] = GT.ch; GT.j = -1; geneHGTN--; }
function virIntegrate(i) {                                  // a chain inside a cell joins its genome as a new gene (a prophage), if the cell can pay for the change in its compound
  const n0 = slen[i], L = VIR.len[i], o = i * SL; if (!L || n0 + GMARK + L > SL) return false;
  const g0 = gen[i] >>> 0, mk = markerFor(seq, o, n0, n0, VIR.seq[i * FL]); let w = n0;
  for (let h = 0; h < GMARK; h++) seq[o + w++] = mk; for (let h = 0; h < L; h++) seq[o + w++] = VIR.seq[i * FL + h]; ORG().fill(2, o + n0, o + w);
  const g1 = infold(seq, o, w);
  if (g1 !== g0 && !swapChem(cmap[i] << 4, g0, g1)) { infold(seq, o, n0); return false; }
  slen[i] = w; gen[i] = g1; cat[i] = lastCat; rx[i] = lastRx; rxStr[i] = lastRxS; rx2[i] = lastRx2; rxStr2[i] = lastRxS2; cH[i] = lastCH; changed[i] = 1;
  VIR.n[i] -= 1; if (VIR.n[i] < 1) { VIR.n[i] = 0; VIR.len[i] = 0; } virIntegN++; return true;
}
let sameCompN = 0;                                          // contagion splices that changed a cell's sequence (and maybe its program) but not its compound: kept, counted
{ const _resetS = reset; reset = function (...a) { sameCompN = 0; return _resetS.apply(this, a); }; }

// ---------------- repeatable runs (16 November): with P.seed set, every new world (not an automatic restart) reseeds the
// random numbers and redraws the geography from that seed, and the sequence buffer is cleared, so the same seed gives the
// same run. P.seed 0 keeps the old behaviour (Math.random).
function seedRng(s0) { let s = (s0 >>> 0) || 1; rng = () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
{ const _resetR = reset; reset = function (...a) {
  if (!a[1]) domCostSum = 0;
  if (P.seed > 0 && !a[1]) { seedRng(P.seed); geoSeed(); chemCapFill(); Z.list.length = 0; layoutZones(); envAlloc(); }   // fresh environment arrays: nothing of the old weather is left   // zone climates redrawn from the seed too
  if (frAmt) { frAmt.fill(0); frLen.fill(0); frSeq.fill(0); frRx.fill(0); frStr.fill(0); frLig.fill(0); }   // free chains from the old world do not carry into the new one
  if (coatS) { coatS.fill(0); coatM.fill(0); coatK.fill(0); } VORDt = -1;
  if (!a[1]) tick = 0;   // the new world's first weather step runs at tick 0, not at the old world's time
  if (typeof seq !== 'undefined' && seq && seq.fill) { seq.fill(0); if (sOrg.length > 1) sOrg.fill(0); for (const a of [slen, cat, rx, rxStr, rx2, rxStr2, cH, rxAct, coat]) if (a && a.fill) a.fill(0); }
  return _resetR.apply(this, a); }; }
