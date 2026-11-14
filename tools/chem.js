// ---------------- chemistry: the first sixteen primes are the world's molecules
// A cell's code is a compound: a product of these primes, kept as its list of exponents. Building a cell takes the molecules
// its compound is made of; when a cell dies, its molecules are set free. The ground holds each molecule in its own pattern.
const CSH = 2;                                          // a chemistry square is 4 x 4 cells
let cw = 1, chh = 1, chem = new Float32Array(16), chemTmp = new Float32Array(16), chemCap = new Float32Array(16), cmap = new Int32Array(1);
let chemRGB = new Uint8Array(3), tlin = new Uint8Array(1), tstr = new Float32Array(1);
const ABUND = [1, 1, 1, .9, .8, .7, .6, .5, .7, .5, .45, .5, .35, .8, .8, .8];   // how common each molecule is in the ground
const SPRGB = new Uint8Array(NP * 3);
for (let k = 0; k < NP; k++) {
  const h = (k * 137.508) % 360, a = .8 * Math.min(.55, .45), f = n => { const q = (n + h / 30) % 12; return .55 - a * Math.max(-1, Math.min(q - 3, 9 - q, 1)); };
  SPRGB[k * 3] = f(0) * 255; SPRGB[k * 3 + 1] = f(8) * 255; SPRGB[k * 3 + 2] = f(4) * 255;
}
const spCss = k => `rgb(${SPRGB[k * 3]},${SPRGB[k * 3 + 1]},${SPRGB[k * 3 + 2]})`;
let GEO = [];
function geoSeed() {
  GEO = [];
  for (let k = 0; k < NP; k++) {
    const w = [];
    for (let q = 0; q < 3; q++) { let kx = Math.floor(rng() * 5) - 2, ky = Math.floor(rng() * 5) - 2; if (!kx && !ky) kx = 1; w.push({kx, ky, ph: rng() * 6.2832}); }
    GEO.push(w);
  }
}
function chemCapFill() {
  const sig = .18 * Math.min(W, H);
  for (let y = 0; y < chh; y++) for (let x = 0; x < cw; x++) {
    const u = (x + .5) / cw, v = (y + .5) / chh, dx = ((x + .5) * 4 - W / 2), dy = ((y + .5) * 4 - H / 2);
    const bump = Math.exp(-(dx * dx + dy * dy) / (2 * sig * sig)), c = (y * cw + x) << 4;   // the first cells sit in an oasis that has a little of everything
    for (let k = 0; k < NP; k++) {
      let s = 0; for (const w of GEO[k]) s += Math.cos(6.2832 * (w.kx * u + w.ky * v) + w.ph);
      let f = Math.max(0, Math.min(1, .5 + .65 * s / 3 * 1.6)); f = f * f * (3 - 2 * f); f += (1 - f) * bump * .85;
      if (P.env === 'dish') f = .6;                                   // agar is even
      chemCap[c + k] = P.chrich * ABUND[k] * (.05 + .95 * f) * (1 + .4 * bump);
    }
  }
}
function chemAlloc() {
  cw = Math.ceil(W / 4); chh = Math.ceil(H / 4);
  chem = new Float32Array(cw * chh * 16); chemTmp = new Float32Array(cw * chh * 16); chemCap = new Float32Array(cw * chh * 16);
  chemRGB = new Uint8Array(cw * chh * 3); tlin = new Uint8Array(cw * chh); tstr = new Float32Array(cw * chh);
  cmap = new Int32Array(N);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) cmap[y * W + x] = (y >> CSH) * cw + (x >> CSH);
  if (!GEO.length) geoSeed();
  chemCapFill(); chem.set(chemCap);
  envAlloc();
}
function chemInit() {                                   // a new world: the ground at its own level, and a rich broth under the first cells
  chem.set(chemCap); tstr.fill(0); tlin.fill(0);
  const rich = P.chrich;
  for (let i = 0; i < N; i++) if (alive[i]) { const c = cmap[i] << 4; for (let k = 0; k < NP; k++) if (chem[c + k] < rich) chem[c + k] = rich; }
}
let GF = null, VR = null; const ONE16 = new Float32Array(16).fill(1);
function chemStep() {
  if (P.current > 0 && P.env !== 'even') { advect(chem, chemTmp, 16); [chem, chemTmp] = [chemTmp, chem]; }
  const D = Math.min(.24, P.chdiff * 2), R = Math.min(.5, P.chrate * 2), cp = chemCap;
  // when domains run reactions, energy must come from somewhere: the ground re-forms only the low-energy molecules (small
  // primes); the high-energy ones come from vents, which pour out mostly those, and from the dead. Otherwise it is as before.
  const gl = P.rxDom && P.rxGround; if (gl && !GF) { GF = new Float32Array(16); VR = new Float32Array(16);
    for (let k = 0; k < 16; k++) { const f = (RXE[k] - RXE[0]) / (1 - RXE[0]); GF[k] = 1 - f; VR[k] = .2 + 1.6 * f; } }
  const gf = gl ? GF : ONE16, vw = gl ? VR : VW, dishOn = P.env === 'dish', dq = dishOn && dishSq && dishSq.length === cw * chh ? dishSq : null;   // in the dish, everything is laid once and nothing re-forms: a closed plate
  for (let y = 0; y < chh; y++) {
    const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) {
      const ww = P.rxn ? Math.min(1, wat[y0 + x] / P.wrain) : 1, vb = vglow[y0 + x] * P.chrich, xm = (x - 1 + cw) % cw, xp = (x + 1) % cw, c = (y0 + x) << 4; let a = (y0 + xm) << 4, b = (y0 + xp) << 4, u = (ym + x) << 4, d = (yp + x) << 4;
      if (dq) { if (!dq[y0 + x]) { for (let k = 0; k < 16; k++) chemTmp[c + k] = 0; continue; }   // the rim: nothing flows through it
        if (!dq[y0 + xm]) a = c; if (!dq[y0 + xp]) b = c; if (!dq[ym + x]) u = c; if (!dq[yp + x]) d = c; }
      for (let k = 0; k < 16; k++) {
        const m = chem[c + k], rg = dishOn ? 0 : R * (gf[k] * cp[c + k] + vb * vw[k] - m), v = m + D * ww * (.25 * (chem[a + k] + chem[b + k] + chem[u + k] + chem[d + k]) - m) + rg; if (rg > 0) OLF.minW += rg;
        chemTmp[c + k] = v > 0 ? v : 0;
      }
    }
  }
  [chem, chemTmp] = [chemTmp, chem];
}
function payChem(c, g, mult, bid) {                     // can the ground here build this compound? if so, take its molecules
  const u = P.chunit * mult, pl = bid ? mxPool.get(bid) : null;          // a clump's cells draw on what its matrix holds first
  for (let k = 0; k < 16; k++) { const e = (g >>> (2 * k)) & 3; if (e && chem[c + k] + (pl ? pl[k] : 0) < e * u) return false; }
  for (let k = 0; k < 16; k++) { const e = (g >>> (2 * k)) & 3; if (!e) continue; let need = e * u;
    if (pl) { const t = Math.min(pl[k], need); pl[k] -= t; need -= t; } chem[c + k] -= need; }
  return true;
}
function swapChem(c, g0, g1) {                         // a compound rewritten in place: the difference comes from, or goes to, the ground
  const u = P.chunit; for (let k = 0; k < 16; k++) { const d = (((g1 >>> (2 * k)) & 3) - ((g0 >>> (2 * k)) & 3)) * u; if (d > 0 && chem[c + k] < d) return false; }
  for (let k = 0; k < 16; k++) chem[c + k] -= (((g1 >>> (2 * k)) & 3) - ((g0 >>> (2 * k)) & 3)) * u; return true;
}
function releaseChem(c, g, bid) {                       // a dead cell's compound breaks down into free molecules
  const f = P.chunit, pl = bid ? mxPool.get(bid) : null, kp = pl ? P.mxRetain : 0;   // in a clump, the matrix keeps part of them
  for (let k = 0; k < 16; k++) { const e = (g >>> (2 * k)) & 3; if (e) { chem[c + k] += e * f * (1 - kp); if (pl) pl[k] += e * f * kp; OLF.minL += e * f; } }
  en[c >> 4] += P.ebody; enMade += P.ebody; if (P.rxn) { wat[c >> 4] += P.wcell; OLF.watL += P.wcell; }            // and the energy it held is set free too
}
// copying with errors: a prime is gained, lost, or a unit moves from one prime to another
function mutate(g, rate) {
  const lam = rate * NP; if (rng() >= lam) return g;
  let cnt = 1; while (cnt < 3 && rng() < lam) cnt++;
  for (let q = 0; q < cnt; q++) {
    const k = (rng() * NP) | 0, e = (g >>> (2 * k)) & 3;
    if (rng() < .3) {
      const j = (rng() * NP) | 0, ej = (g >>> (2 * j)) & 3;
      if (e > 0 && ej < 3 && j !== k) g = g - (1 << (2 * k)) + (1 << (2 * j));
      continue;
    }
    const up = e === 0 ? true : e === 3 ? false : rng() < .5;
    g = up ? g + (1 << (2 * k)) : g - (1 << (2 * k));
  }
  return g >>> 0;
}

// ---------------- showing the molecules
let cutCv = null;
function airCount() { const a = new Uint16Array(cw * chh); for (const s of air) { const c = (((Math.floor(s.y) % chh) + chh) % chh) * cw + (((Math.floor(s.x) % cw) + cw) % cw); if (a[c] < 65535) a[c]++; } return a; }
// the cutaway: a side slice through the first vent's row, the surface layer above the floor layer
function drawCut() {
  if (!cutCv) {
    cutCv = document.createElement('canvas'); cutCv.id = 'cutaway';
    Object.assign(cutCv.style, {position: 'absolute', left: '10px', bottom: '52px', width: 'calc(100% - 20px)', height: '170px', border: '1px solid rgba(255,255,255,.25)', borderRadius: '6px', background: 'rgba(5,5,5,.92)', pointerEvents: 'none', zIndex: 3});
    (document.getElementById('stage') || document.body).appendChild(cutCv);
  }
  cutCv.style.display = 'block';
  const Wd = Math.max(320, cw * 4), Hd = 170; if (cutCv.width !== Wd) { cutCv.width = Wd; cutCv.height = Hd; }
  const g = cutCv.getContext('2d'), sx = Wd / cw, row = vents.length ? ((Math.round(vents[0].y) % chh) + chh) % chh : chh >> 1;
  g.clearRect(0, 0, Wd, Hd);
  const top0 = 18, top1 = 70, bot0 = 96, bot1 = 148;
  for (let x = 0; x < cw; x++) {
    const c = row * cw + x; let q = irIdx(tsurf[c]); g.fillStyle = `rgb(${IRL[q]},${IRL[q + 1]},${IRL[q + 2]})`; g.fillRect(x * sx, top0, sx + .5, top1 - top0);
    q = irIdx(temp[c]); g.fillStyle = `rgb(${IRL[q]},${IRL[q + 1]},${IRL[q + 2]})`; g.fillRect(x * sx, bot0, sx + .5, bot1 - bot0);
  }
  g.strokeStyle = 'rgba(240,239,236,.9)'; g.fillStyle = 'rgba(240,239,236,.9)'; g.lineWidth = 1.2;
  const step = Math.max(1, Math.round(cw / 40));
  for (let x = 0; x < cw; x += step) {
    const c = row * cw + x, X = (x + .5) * sx;
    const arrow = (x0, y0, x1, y1) => { g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); const a = Math.atan2(y1 - y0, x1 - x0), L = Math.hypot(x1 - x0, y1 - y0); if (L > 3) { g.beginPath(); g.moveTo(x1, y1); g.lineTo(x1 - 4 * Math.cos(a - .5), y1 - 4 * Math.sin(a - .5)); g.lineTo(x1 - 4 * Math.cos(a + .5), y1 - 4 * Math.sin(a + .5)); g.fill(); } };
    arrow(X, (top0 + top1) / 2, X + Math.max(-sx * step, Math.min(sx * step, ux[c] * 60)), (top0 + top1) / 2);
    arrow(X, (bot0 + bot1) / 2, X + Math.max(-sx * step, Math.min(sx * step, fx[c] * 60)), (bot0 + bot1) / 2);
    const w = wup[c], L = Math.max(-22, Math.min(22, w * 700));
    if (Math.abs(L) > 1.5) { g.strokeStyle = w > 0 ? 'rgba(255,150,60,.95)' : 'rgba(110,170,255,.95)'; g.fillStyle = g.strokeStyle; arrow(X, 83 + L / 2, X, 83 - L / 2); g.strokeStyle = 'rgba(240,239,236,.9)'; g.fillStyle = 'rgba(240,239,236,.9)'; }
  }
  g.fillStyle = 'rgba(255,238,190,.95)';
  for (const s of air) if (Math.abs(s.y - row) < 2) g.fillRect(s.x * sx - 1, top0 + 4 + ((s.y * 37) % 1) * (top1 - top0 - 8), 2.5, 2.5);
  g.font = '11px system-ui'; g.fillStyle = 'rgba(240,239,236,.85)';
  g.fillText(`Cutaway through the first vent's row (y = ${row}): surface layer`, 6, 13); g.fillText('floor layer (where the cells live)', 6, bot0 - 4);
  g.fillText('orange: rising · blue: sinking · arrows: current · pale dots: spores aloft', 6, Hd - 6);
}
function chemOverlayPrep() {
  const sh = P.chshow; if (cutCv && sh !== 'cut') cutCv.style.display = 'none'; if (sh === 'off') return false;
  const rich = Math.max(1, P.chrich), n = cw * chh;
  if (sh === 'sflow' || sh === 'upw' || sh === 'sheat' || sh === 'cut') {
    const ac = (sh === 'sflow' || sh === 'upw') ? airCount() : null;
    for (let c = 0; c < n; c++) {
      let r = 0, gg = 0, b = 0;
      if (sh === 'sflow') { const u = ux[c], v = uy[c], s = Math.min(1, Math.hypot(u, v) * 2.4), a = Math.atan2(v, u); r = (128 + 127 * Math.cos(a)) * s * .8; gg = (128 + 127 * Math.cos(a - 2.094)) * s * .8; b = (128 + 127 * Math.cos(a + 2.094)) * s * .8; }
      else if (sh === 'upw') { const w = Math.max(-1, Math.min(1, wup[c] * 25)); if (w > 0) { r = 255 * w; gg = 120 * w; b = 30 * w; } else { r = 40 * -w; gg = 110 * -w; b = 255 * -w; } }
      else { const u = Math.max(0, Math.min(1, sh === 'sheat' ? tsurf[c] : temp[c])); r = 255 * Math.min(1, u * 2.2) * .8; gg = 255 * (u < .5 ? u * 1.4 : Math.max(0, 1.2 - u * 1.4)) * .8; b = 255 * Math.max(0, 1 - u * 1.8) * .8; }
      if (ac && ac[c]) { const k = Math.min(1, ac[c] / 4); r += (255 - r) * k; gg += (238 - gg) * k; b += (190 - b) * k; }
      chemRGB[c * 3] = r; chemRGB[c * 3 + 1] = gg; chemRGB[c * 3 + 2] = b;
    }
    if (sh === 'cut') { if (typeof g3Ready === 'function' && g3Ready()) drawCut3(); else drawCut(); }
    return true;
  }
  if (sh === 'water') {
    for (let c = 0; c < n; c++) { const u = Math.min(1, wat[c] / P.wrain); chemRGB[c * 3] = 30 * u; chemRGB[c * 3 + 1] = 110 * u; chemRGB[c * 3 + 2] = 230 * u; }
  } else if (sh === 'co2') {
    for (let c = 0; c < n; c++) { const u = Math.min(1, co2[c] / (2 * Math.max(.5, P.co2air))); chemRGB[c * 3] = 170 * u; chemRGB[c * 3 + 1] = 170 * u; chemRGB[c * 3 + 2] = 150 * u; }
  } else if (sh === 'o2') {
    for (let c = 0; c < n; c++) { const u = Math.min(1, o2[c] / 2); chemRGB[c * 3] = 60 * u; chemRGB[c * 3 + 1] = 230 * u; chemRGB[c * 3 + 2] = 220 * u; }
  } else if (sh === 'energy') {
    for (let c = 0; c < n; c++) { const u = Math.min(1, en[c] / 3); chemRGB[c * 3] = 255 * u * .8; chemRGB[c * 3 + 1] = 190 * u * .8; chemRGB[c * 3 + 2] = 60 * u * .8; }
  } else if (sh === 'flow') {
    for (let c = 0; c < n; c++) { const u = fx[c], v = fy[c], s = Math.min(1, Math.hypot(u, v) * 2.4), a = Math.atan2(v, u); chemRGB[c * 3] = (128 + 127 * Math.cos(a)) * s * .8; chemRGB[c * 3 + 1] = (128 + 127 * Math.cos(a - 2.094)) * s * .8; chemRGB[c * 3 + 2] = (128 + 127 * Math.cos(a + 2.094)) * s * .8; }
  } else if (sh === 'sig') {
    for (let c = 0; c < n; c++) { const u = Math.max(0, Math.min(1, sig[c])), q = Math.min(1, u / Math.max(.05, P.qthr)) * .8; const hot = u >= P.qthr; chemRGB[c * 3] = (hot ? 255 : 40) * q; chemRGB[c * 3 + 1] = (hot ? 200 : 140) * q; chemRGB[c * 3 + 2] = (hot ? 60 : 255) * q; }
  } else if (sh === 'heat') {
    for (let c = 0; c < n; c++) {
      const u = Math.max(0, Math.min(1, temp[c])), r = 255 * Math.min(1, u * 2.2), g = 255 * (u < .5 ? u * 1.4 : Math.max(0, 1.2 - u * 1.4)), b = 255 * Math.max(0, 1 - u * 1.8);
      chemRGB[c * 3] = r * .8; chemRGB[c * 3 + 1] = g * .8; chemRGB[c * 3 + 2] = b * .8;
    }
  } else if (sh === 'all') {
    for (let c = 0; c < n; c++) {
      let best = -1, bv = 0; const o = c << 4;
      for (let k = 0; k < NP; k++) { const v = chem[o + k] / ABUND[k]; if (v > bv) { bv = v; best = k; } }
      const q = best < 0 ? 0 : Math.min(1, bv / (rich * 1.1)) * .8;
      chemRGB[c * 3] = best < 0 ? 0 : SPRGB[best * 3] * q; chemRGB[c * 3 + 1] = best < 0 ? 0 : SPRGB[best * 3 + 1] * q; chemRGB[c * 3 + 2] = best < 0 ? 0 : SPRGB[best * 3 + 2] * q;
    }
  } else {
    const k = +sh, sc = 1 / (rich * ABUND[k] * 1.3);
    for (let c = 0; c < n; c++) {
      const q = Math.min(1, chem[(c << 4) + k] * sc) * .9;
      chemRGB[c * 3] = SPRGB[k * 3] * q; chemRGB[c * 3 + 1] = SPRGB[k * 3 + 1] * q; chemRGB[c * 3 + 2] = SPRGB[k * 3 + 2] * q;
    }
  }
  return true;
}

// ---------------- what a compound is, for the inspector
const SUPN = ['', '', '²', '³'];
const ROLEN = ['survival with 1 neighbour', 'survival with 2', 'with 3', 'with 4', 'with 5', 'with 6', 'with 7', 'with 8'];
function roleText(k, e) {
  if (k < 8 && !P.lifeRule) return 'a building block: costs molecules, does nothing by itself';
  if (k < 8) return ['', 'survives with ' + (k + 1) + ' neighbours', 'gives birth into squares with ' + (k + 1) + ' neighbours', 'survives with ' + (k + 1) + ' and gives birth into squares with ' + (k + 1)][e];
  if (k === 8) return ['', 'moves, wandering', 'moves, leaning to the light', 'moves, climbing the light'][e];
  if (k === 9) return ['', 'writes itself into neighbours, weakly', 'writes itself into neighbours', 'writes itself into neighbours, strongly'][e];
  if (k === 10) return ['', 'uses 20% less light', 'uses 38% less light', 'uses 54% less light'][e];
  if (k === 11) return ['', 'dies by chance 40% less', 'dies by chance 70% less', 'dies by chance 90% less'][e];
  if (k === 12) return ['', 'copies with 40% fewer errors', 'copies with 65% fewer errors', 'copies with 85% fewer errors'][e];
  if (k === 13) return ['', 'prefers warmer water (0.45)', 'prefers warmer water (0.60)', 'prefers hot water (0.75)'][e];
  return 'inert: does nothing, costs molecules, marks the lineage';
}
function compoundNumber(g) { let v = 1n; for (let k = 0; k < NP; k++) { const e = EX(g, k); if (e) v *= BigInt(PR[k]) ** BigInt(e); } return v; }
function bigText(v) { const t = v.toString(); return t.length <= 12 ? t : t[0] + '.' + t.slice(1, 4) + 'e' + (t.length - 1); }
// how a compound spreads: a spore can be born beside a single parent, so one lone cell can seed open ground and the colony leaps;
// a rhizome is only ever born beside company (SPORE_N + 1 or more living neighbours), so it creeps outward along what already lives. Change SPORE_N to move the line.
const STRAT = {spore: 'spore', rhizome: 'rhizome', none: 'sterile'};
const SPORE_N = 1, SPORE_MASK = (1 << (SPORE_N + 1)) - 2;
function strategy(g) { if (!P.lifeRule) return 'rhizome'; const b = B(g); return (b & SPORE_MASK) ? 'spore' : (b & 0x1fe) ? 'rhizome' : 'none'; }
// what a cell is doing right now, not just what its genome allows: a quorum cell in a crowd gives up births into squares with few neighbours
function strategyAt(i) {
  let b = B(gen[i]); const xe = xg[i] & 3;
  if (xe && sig[cmap[i]] >= P.qthr) b &= ~((1 << (xe + 1)) - 2);
  return (b & SPORE_MASK) ? 'spore' : (b & 0x1fe) ? 'rhizome' : 'none';
}
function costOf(g) { let s = 0; for (let k = 0; k < NP; k++) s += EX(g, k); return s; }
function compoundHtml(g, i) {
  const c = cmap[i] << 4, u = P.chunit, T = temp[cmap[i]];
  const rows = []; let can = true;
  for (let k = 0; k < NP; k++) {
    const e = EX(g, k); if (!e) continue;
    const have = chem[c + k], need = e * u; if (have < need) can = false;
    rows.push(`<div><span class="sw" style="display:inline-block;background:${spCss(k)}"></span> <b>${PR[k]}${SUPN[e]}</b> · ${roleText(k, e)}${P.chemOn ? ` <span style="color:var(--muted)">(needs ${need}, here ${have.toFixed(1)})</span>` : ''}</div>`);
  }
  const qe = xg[i] & 3, qline = qe ? `<div><span class="sw" style="display:inline-block;background:#e8b04a"></span> <b>59${SUPN[qe]}</b> · quorum gene: where the signal is at or above ${P.qthr.toFixed(2)} (here ${sig[cmap[i]].toFixed(2)}) it is not born into squares with ${qe} or fewer neighbours, and it uses ${Math.round(100 * P.qsave * qe)}% less light there.</div>` : '';
  const xs = xg[i], pe = (xs >> 2) & 3, se = (xs >> 4) & 3, de = (xs >> 6) & 3, ge = (xs >> 8) & 3, he = (xs >> 10) & 3, ae = (xs >> 12) & 3, pe2 = (xs >> 14) & 3;
  const xline = (pe2 ? `<div><span class="sw" style="display:inline-block;background:#f0e6c8"></span> <b>89${SUPN[pe2]}</b> · spore-forming: when it starves or its ground dries out it may turn into a spore (chance ${Math.round(100 * P.sporeRate * pe2)}% a tick).</div>` : '') + (ae ? `<div><span class="sw" style="display:inline-block;background:#c9a0dc"></span> <b>83${SUPN[ae]}</b> · adhesion: a free form of cells carrying this can become a body, with chance ${(100 * P.nucleate * ae).toFixed(0)}% per look at it.</div>` : '') + (he ? `<div><span class="sw" style="display:inline-block;background:#b08a5a"></span> <b>79${SUPN[he]}</b> · heterotroph: when the light here runs short it takes up the energy molecule from the water (up to ${(.1 * he).toFixed(2)} a step, keeping ${Math.round(100 * P.eeff)}% of it); the water here holds ${en[cmap[i]].toFixed(2)}.</div>` : '') + (ge ? `<div><span class="sw" style="display:inline-block;background:#6fb5e8"></span> <b>73${SUPN[ge]}</b> · storage: it banks spare light, up to ${(P.rbase + P.rcap * ge).toFixed(2)}; it holds ${rsv[i].toFixed(2)} now, and draws on it when the light here runs out.</div>` : '') + (pe ? `<div><span class="sw" style="display:inline-block;background:#8fd16a"></span> <b>61${SUPN[pe]}</b> · producer: in a crowd it secretes the molecules of its own compound, and pays ${(P.prodCost * pe).toFixed(3)} light each time.</div>` : '') + (se ? `<div><span class="sw" style="display:inline-block;background:#d98bd6"></span> <b>67${SUPN[se]}</b> · recombination: when different parents meet, the chance they mix their codes is ${Math.min(100, Math.round(100 * P.fusion * (1 + 1.5 * se)))}%.</div>` : '') + (de ? `<div><span class="sw" style="display:inline-block;background:#e0675a"></span> <b>71${SUPN[de]}</b> · predator: it bites a neighbour of another lineage with chance ${Math.round(100 * P.predRate * de)}% a tick, if it also carries the heterotroph gene, and keeps ${Math.round(100 * P.predGain)}% of the energy in what it eats.</div>` : '');
  return cellSvg(i) + seqHtml(i) + `<div>${dor[i] ? 'It is a <b>spore</b> now: dormant, it pays almost nothing to live, cannot give birth, stands drying and heat, and drifts with the current. It wakes when the light and water come back.' : ''}</div><div>Compound <b>${bigText(compoundNumber(g))}</b> = ${formula(g).replace(/·/g, ' · ')}. A copy takes ${(costOf(g) * u).toFixed(costOf(g) * u % 1 ? 2 : 0)} molecules.${P.chemOn ? (can ? ' The ground here could build another.' : ' The ground here is short of something it needs.') : ''}</div>${P.env !== 'even' ? `<div>The water here is ${T.toFixed(2)}; this compound is ${Math.round(100 * thermFit(g, T))}% suited to it.</div>` : ''}${rows.join('')}${qline}${xline}`;
}
function chemNote(i) {
  const c = cmap[i] << 4, parts = [];
  for (let k = 0; k < NP; k++) parts.push(`<span style="color:${spCss(k)}">${PR[k]}</span> ${chem[c + k].toFixed(0)}`);
  return 'Molecules here: ' + parts.join(' · ') + (P.env !== 'even' ? `<br>Water ${temp[cmap[i]].toFixed(2)}` : '');
}

// ---------------- the chemistry panel
function chemPanel() {
  const ei = $('envinfo'); if (ei) ei.textContent = P.env === 'even' ? 'Light and heat are constant.' : `Daylight ${Math.round(100 * envSun)}% · the water averages ${envTemp.toFixed(2)}${vents.length ? ' · ' + vents.length + ' vents or springs' : ''}`;
  const el = $('chpanel'); if (!el) return;
  let dN = 0, dA = 0; for (let i = 0; i < N; i += 3) if (alive[i]) { dA++; if (dor[i]) dN++; }
  const use = new Float32Array(NP), mean = new Float32Array(NP), capm = new Float32Array(NP); let pop = 0;
  for (let i = 0; i < N; i += 3) if (alive[i]) { pop++; const g = gen[i]; for (let k = 0; k < NP; k++) if ((g >>> (2 * k)) & 3) use[k]++; }
  const n = cw * chh;
  for (let c = 0; c < n; c++) for (let k = 0; k < NP; k++) { mean[k] += chem[(c << 4) + k]; capm[k] += chemCap[(c << 4) + k]; }
  // the ladder: how much variety and structure the living world holds right now
  let cxHtml = '';
  { const lin = new Set(), rules = new Map(), qn = [0, 0, 0, 0], gn = [0, 0, 0, 0, 0, 0, 0, 0]; let rs = 0, rn = 0; let tot = 0, eSp = 0, eN = 0, iSp = 0, iN = 0, qCrowd = 0, qAll = 0;
    for (let i = 0; i < N; i += 3) { if (!alive[i]) continue; tot++; const g = gen[i]; lin.add(g >>> 28); const r = g & 65535; rules.set(r, (rules.get(r) || 0) + 1); const e = xg[i] & 3; qn[e]++; for (let q = 0; q < 8; q++) if ((xg[i] >> (2 * q)) & 3) gn[q]++; if ((xg[i] >> 8) & 3) { rn++; rs += rsv[i] / (P.rbase + P.rcap * ((xg[i] >> 8) & 3)); }
      if (e) { qAll++; if (sig[cmap[i]] >= P.qthr) qCrowd++; }
      const x = i % W, y = (i / W) | 0; let nb = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) if ((dx || dy) && alive[((y + dy + H) % H) * W + ((x + dx + W) % W)]) nb++;
      }
    let kinds = 0; for (const v of rules.values()) if (v >= .01 * tot) kinds++;
    const pc = (a, b) => b ? Math.round(100 * a / b) + '%' : '–';
    cxHtml = `<div style="margin-bottom:6px;color:var(--muted)">Variety: <b>${lin.size}</b> lineages · <b>${kinds}</b> rules each held by 1% or more · genes carried: quorum <b>${pc(gn[0], tot)}</b> · producer <b>${pc(gn[1], tot)}</b> · recombination <b>${pc(gn[2], tot)}</b> · predator <b>${pc(gn[3], tot)}</b> · heterotroph <b>${pc(gn[5], tot)}</b> · adhesion <b>${pc(gn[6], tot)}</b> · spore-forming <b>${pc(gn[7], tot)}</b>${bodies.size ? ' · bodies <b>' + bodies.size + '</b>' : ''}${qAll ? ' (' + pc(qCrowd, qAll) + ' of the quorum cells are in a crowd right now)' : ''}<br>Energy molecule: <b>${(en.reduce((a, b) => a + b, 0) / en.length).toFixed(1)}</b> a square on average · cells have taken up <b>${enTaken.toFixed(0)}</b> and kept <b>${enTaken ? Math.round(100 * enGot / enTaken) : 0}%</b> of it${P.rxn ? `<br>Reactions: water <b>${avgF(wat)}</b> · CO₂ <b>${avgF(co2)}</b> · O₂ <b>${avgF(o2)}</b> a square · <b>${enTaken ? Math.round(100 * enAer / enTaken) : 0}%</b> of the sugar taken up was burned with oxygen, the rest fermented` : ''}</div>`; }
  el.innerHTML = cxHtml + olfPanel() + specPanel() + seqPanel() + ccPanel() + `<div style="margin-bottom:6px">Dormant cells: <b>${dA ? Math.round(100 * dN / dA) : 0}%</b> of the living</div>` + PR.map((p, k) => {
    const lvl = capm[k] ? Math.min(100, Math.round(100 * mean[k] / capm[k])) : 0, u = pop ? Math.round(100 * use[k] / pop) : 0;
    return `<div class="chrow"><span class="sw" style="background:${spCss(k)}"></span><b>${p}</b><span class="chbar"><i style="width:${lvl}%;background:${spCss(k)}"></i></span><span style="color:var(--muted)">${lvl}% of full · in ${u}% of cells</span></div>`;
  }).join('');
}

// ---------------- defence against invaders
// kin: a cell counts neighbours of its own lineage in full and strangers at a fraction (the lineage is the inert primes 43, 47, 53)
function kinCount(g, nb, n, w) {
  const l = g >>> 28; let kin = 0;
  for (let k = 0; k < 8; k++) { const j = nb[k]; if (alive[j] && (gen[j] >>> 28) === l) kin++; }
  return kin + Math.round((n - kin) * w);
}
// territory: the lineage that fills a chemistry square marks it; a foreign child is less likely to be born there
function fieldStep() {                                  // one pass over the living: how dense each square is, and who holds it
  dens.fill(0); const vote = P.terr > 0;
  if (vote) for (let c = 0; c < tstr.length; c++) tstr[c] *= .9;
  for (let i = 0; i < N; i++) {
    if (!alive[i]) continue;
    const c = cmap[i], l = gen[i] >>> 28; dens[c]++;
    if (!vote) continue;
    if (tlin[c] === l) { if (tstr[c] < 16) tstr[c] += 1; }
    else if (tstr[c] > 1) tstr[c] -= 1;
    else { tlin[c] = l; tstr[c] = 1; }
  }
}
// signalling: every living cell gives off a signal into its chemistry square; it spreads to the neighbouring squares and fades, so each square holds a smoothed density.
// A cell with the quorum gene (the prime 59) reads it: where the signal is at or above the quorum level, it stops giving birth into squares with few neighbours and spends less light.
function energyStep() {                                  // the energy molecule: living cells leak it, it spreads, rides the current, and slowly decays
  if (P.current > 0 && P.env !== 'even') { advect(en, enTmp, 1); [en, enTmp] = [enTmp, en]; }
  const D = .2, n = cw * chh, lk = P.eleak;
  const dq = P.env === 'dish' && dishSq && dishSq.length === n ? dishSq : null;
  for (let y = 0; y < chh; y++) {
    const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) {
      const xm = (x - 1 + cw) % cw, xp = (x + 1) % cw, c = y0 + x, s = en[c];
      if (dq && !dq[c]) { enTmp[c] = 0; continue; }
      const eL = dq && !dq[y0 + xm] ? s : en[y0 + xm], eR = dq && !dq[y0 + xp] ? s : en[y0 + xp], eU = dq && !dq[ym + x] ? s : en[ym + x], eD = dq && !dq[yp + x] ? s : en[yp + x];
      const ww = P.rxn ? Math.min(1, wat[c] / P.wrain) : 1, v = s + D * ww * (.25 * (eL + eR + eU + eD) - s), d = P.env === 'dish' ? 0 : v * P.edecay;   // the plate is sterile: its sugar does not rot
      enTmp[c] = v - d;
      if (P.rxn) { co2[c] += d; const a = Math.min(d, o2[c]); o2[c] -= a; wat[c] += a * P.wfix; OLF.co2L += d; OLF.watL += a * P.wfix; }    // sugar left in the water rots back to CO2, using oxygen if there is any
    }
  }
  [en, enTmp] = [enTmp, en];
  if (lk > 0) for (let i = 0; i < N; i++) if (alive[i] && light[i] > lk && (!P.rxn || co2[cmap[i]] >= lk)) { light[i] -= lk; en[cmap[i]] += lk; enMade += lk; if (P.rxn) { const s = cmap[i]; co2[s] -= lk; o2[s] += lk; wat[s] -= lk * P.wfix; } }   // photosynthesis: CO2 + water + light -> sugar + O2   // the leak is paid for in light, so energy is never made from nothing
}
function sigStep() {
  if (P.current > 0 && P.env !== 'even') { advect(sig, sigTmp, 1); [sig, sigTmp] = [sigTmp, sig]; }
  const D = P.sigspread, R = .35;
  for (let y = 0; y < chh; y++) {
    const ym = ((y - 1 + chh) % chh) * cw, y0 = y * cw, yp = ((y + 1) % chh) * cw;
    for (let x = 0; x < cw; x++) {
      const xm = (x - 1 + cw) % cw, xp = (x + 1) % cw, c = y0 + x, s = sig[c];
      sigTmp[c] = s + D * (.25 * (sig[y0 + xm] + sig[y0 + xp] + sig[ym + x] + sig[yp + x]) - s) + R * (dens[c] / 16 - s);
    }
  }
  [sig, sigTmp] = [sigTmp, sig];
}
function foreignBlocked(c, g) {
  const t = tstr[c]; if (t < 1 || tlin[c] === (g >>> 28)) return false;
  return rng() < P.terr * Math.min(1, t / 8);
}


// ---------------- click a form: highlight it
// A form is a connected cluster of living cells. Clicking one outlines its exact cells, names it, marks other copies of the same shape, and follows it as it moves.
let sel = null;                                          // {seed, h, n, x, y}
function floodForm(seed) {                               // the cluster the seed belongs to: indices and unwrapped coordinates
  const idxs = [seed], xs = [seed % W], ys = [(seed / W) | 0], mark = new Set([seed]);
  for (let q = 0; q < idxs.length && idxs.length <= 800; q++) {
    const x = xs[q], y = ys[q];
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      if (!dx && !dy) continue;
      const X = x + dx, Y = y + dy, j = ((Y % H + H) % H) * W + ((X % W + W) % W);
      if (alive[j] && !mark.has(j)) { mark.add(j); idxs.push(j); xs.push(X); ys.push(Y); }
    }
  }
  return {idxs, xs, ys};
}
function shapeHash(xs, ys) {                             // the same hash the census uses, so the form's name matches
  let minx = 1e9, miny = 1e9; for (let k = 0; k < xs.length; k++) { if (xs[k] < minx) minx = xs[k]; if (ys[k] < miny) miny = ys[k]; }
  const pts = []; for (let k = 0; k < xs.length; k++) pts.push((xs[k] - minx) * 1024 + (ys[k] - miny));
  pts.sort((a, b) => a - b);
  let h = 2166136261; for (const p of pts) { h ^= p; h = Math.imul(h, 16777619) >>> 0; }
  return h;
}
function selectForm(i) {
  sel = null; if (!alive[i]) return;
  const f = floodForm(i); if (f.idxs.length > 800 || f.idxs.length < 3) return;
  sel = {seed: i, h: shapeHash(f.xs, f.ys), n: f.idxs.length, x: i % W, y: (i / W) | 0};
}
function reseedSel() {                                   // the form moved or changed: find the nearest cluster of the same shape
  let best = null, bd = 1e9;
  for (const c of comps) { if (c.h !== sel.h) continue; const dx = Math.min(Math.abs(c.x - sel.x), W - Math.abs(c.x - sel.x)), dy = Math.min(Math.abs(c.y - sel.y), H - Math.abs(c.y - sel.y)), d = dx * dx + dy * dy; if (d < bd) { bd = d; best = c; } }
  if (!best) { sel = null; return; }
  for (let y = best.y; y < best.y + best.hh; y++) for (let x = best.x; x < best.x + best.w; x++) {
    const j = ((y % H + H) % H) * W + ((x % W + W) % W);
    if (alive[j]) { const f = floodForm(j); if (f.idxs.length === sel.n && shapeHash(f.xs, f.ys) === sel.h) { sel.seed = j; return; } }
  }
  sel = null;
}
function drawSel(ox, oy, s) {
  if (!sel) return;
  if (!alive[sel.seed]) { reseedSel(); if (!sel) return; }
  const f = floodForm(sel.seed); if (f.idxs.length > 800) { sel = null; return; }
  if (shapeHash(f.xs, f.ys) !== sel.h) { reseedSel(); if (!sel) return; }
  const fm = forms.get(sel.h), pulse = .45 + .2 * Math.sin(performance.now() / 220), z = Math.max(s, 3);
  // other copies of the same shape, dimly
  ctx.strokeStyle = 'rgba(255,225,74,.55)'; ctx.lineWidth = 1;
  let others = 0;
  for (const c of comps) { if (c.h !== sel.h) continue; if (sel.x >= c.x && sel.x < c.x + c.w && sel.y >= c.y && sel.y < c.y + c.hh && alive[sel.seed]) { /* this one */ }
    const mine = f.idxs.some(j => { const x = j % W, y = (j / W) | 0; return x >= c.x && x < c.x + c.w && y >= c.y && y < c.y + c.hh; });
    if (mine) continue; others++; ctx.strokeRect(ox + c.x * s - 2, oy + c.y * s - 2, c.w * s + 4, c.hh * s + 4); }
  // the form itself
  let top = f.idxs[0], tx = 1e9, ty = 1e9;
  ctx.fillStyle = `rgba(255,225,74,${pulse})`; ctx.strokeStyle = 'rgba(255,240,150,.95)'; ctx.lineWidth = 1.5;
  for (const j of f.idxs) { const x = j % W, y = (j / W) | 0, X = ox + x * s + s / 2 - z / 2, Y = oy + y * s + s / 2 - z / 2; ctx.fillRect(X, Y, z, z); if (s >= 6) ctx.strokeRect(X, Y, z, z); if (y < ty || (y === ty && x < tx)) { ty = y; tx = x; top = j; } }
  sel.x = tx; sel.y = ty;
  const label = `${fm && fm.named ? fm.name : 'an unnamed shape'} · ${f.idxs.length} cells${others ? ' · ' + others + ' more like it' : ''}`;
  ctx.font = '12px system-ui'; ctx.textAlign = 'left'; const lx = ox + tx * s, ly = oy + ty * s - 8, w = ctx.measureText(label).width + 10;
  ctx.fillStyle = 'rgba(20,18,10,.8)'; ctx.fillRect(lx - 3, ly - 12, w, 17); ctx.fillStyle = '#ffe14a'; ctx.fillText(label, lx + 2, ly);
}


// ---------------- the extended genes beyond the quorum gene
// xg bits: 0-1 quorum (59), 2-3 producer (61), 4-5 recombination (67), 6-7 predator (71)
let XSLOTS = [0], eaten = 0;
function xslots() { XSLOTS = [0]; if (P.gProd) XSLOTS.push(1); if (P.gSex) XSLOTS.push(2); if (P.gPred) XSLOTS.push(3); if (P.gHet) XSLOTS.push(5); if (P.gAdh) XSLOTS.push(6); if (P.gSpore) XSLOTS.push(7); }
// producers: in a crowd (signal at or above the quorum level) a producer puts the molecules of its own compound into its square, for light
function produce() {
  if (!P.chemOn) return;
  const rate = P.prodRate, cost = P.prodCost, fl = P.floor;
  for (let i = 0; i < N; i++) {
    const pe = (xg[i] >> 2) & 3; if (!pe || !alive[i]) continue;
    const c = cmap[i]; if (sig[c] < P.qthr) continue;
    const g = gen[i], o = c << 4;
    for (let k = 0; k < NP; k++) { const ex = (g >>> (2 * k)) & 3; if (ex) { const q = o + k, take = Math.min(rate * pe * ex, Math.max(0, chemCap[q] - chem[q]), en[c]); if (take > 0) { en[c] -= take; chem[q] += take; OLF.minL += take; } } }   // built out of sugar (the carbon source): matter is not made from energy
    if (fl) light[i] -= cost * pe;
  }
}

// the cell layer, opened: a drawing of one cell from its actual state. Membrane (thicker when dormant), its coat (when
// clumps are made by cells), its working domains as folds labelled with what they do, the molecules of its square with
// arrows for its reactions, its bonds to sticky neighbours, and its light. Organelles will be drawn here as they are built.
function cellSvg(i) {
  if (i == null || !alive[i]) return '';
  const W0 = 320, H0 = 210, cx = 160, cy = 104, R = 62, ink = 'var(--ink)', mu = 'var(--muted)', acc = 'var(--accent)';
  const parts = []; const t = (x, y, s, o = '') => parts.push(`<text x="${x}" y="${y}" font-size="11" fill="${o || ink}" text-anchor="middle">${s}</text>`);
  // coat and membrane
  const x0 = i % W, y0 = (i / W) | 0, ct = typeof coat !== 'undefined' && coat.length === N ? coat[i] : 0;
  if (P.cellClumps && ct > 0) parts.push(`<circle cx="${cx}" cy="${cy}" r="${R + 2 + Math.min(4, ct * 8)}" fill="none" stroke="${ct >= P.coatMin ? acc : mu}" stroke-opacity=".3" stroke-width="${Math.min(8, 1 + ct * 10)}"/>`);
  // bonds: lines toward each sticky neighbour of the same clump
  for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { if (!dx && !dy) continue; const j = ((y0 + dy + H) % H) * W + ((x0 + dx + W) % W);
    if (!alive[j]) continue; const same = body[i] && body[j] === body[i], a = Math.atan2(dy, dx);
    parts.push(`<line x1="${cx + R * Math.cos(a)}" y1="${cy + R * Math.sin(a)}" x2="${cx + (R + 20) * Math.cos(a)}" y2="${cy + (R + 20) * Math.sin(a)}" stroke="${same ? acc : mu}" stroke-width="${same ? 3 : 1}" stroke-dasharray="${same ? '' : '3 3'}"/>`); }
  parts.push(`<circle cx="${cx}" cy="${cy}" r="${R}" fill="var(--surface)" stroke="${ink}" stroke-width="${dor[i] ? 5 : 1.5}" ${dor[i] ? 'stroke-dasharray="6 3"' : ''}/>`);
  // domains as folds inside the membrane
  let doms = [];
  if (P.seqOn && slen.length === N && slen[i]) { infold(seq, i * SL, slen[i]);
    for (let d = 0; d < dN && doms.length < 6; d++) { const b = rxOf(d); if (sAd[d]) { doms.push({lab: `adaptor ${dQ[d] & 15}→${dO[d] & 15}`, st: 1, ok: true, len: dB[d] - dA[d] + 1, ad: 1}); continue; } doms.push({lab: P.rxDom ? ((b & 15) === ((b >> 4) ^ 8) && P.cellClumps && P.sugarCoat > 0 ? 'sugar→coat' : `${MONO[b >> 4]}→${MONO[b & 15]}`) : CATN[dK[d]], st: dS[d], ok: dS[d] >= P.domMin, len: dB[d] - dA[d] + 1}); } }
  doms.forEach((d, k) => { const a = -Math.PI / 2 + (k + .5) * 2 * Math.PI / Math.max(1, doms.length), r = doms.length > 1 ? R * .5 : 0, x = cx + r * Math.cos(a), y = cy + r * Math.sin(a), rr = 8 + Math.min(10, d.len);
    parts.push(`<path d="M${x - rr} ${y + 6} Q${x} ${y - rr * 1.6} ${x + rr} ${y + 6}" fill="none" stroke="${d.ad ? '#D85A30' : d.ok ? acc : mu}" stroke-width="${1 + d.st}" ${d.ad ? 'stroke-dasharray="4 2"' : ''}/>`);
    t(x, y + 18, d.lab + (d.st > 1 ? ' ×' + d.st : ''), d.ok ? '' : mu); });
  if (!doms.length) t(cx, cy + 4, 'no working folds', mu);
  // the square's molecules, around the edge; arrows where this cell's reactions run
  if (P.chemOn) { const c = cmap[i] << 4, top = [...Array(16).keys()].sort((a, b) => chem[c + b] - chem[c + a]).slice(0, 6), mx = Math.max(1e-6, chem[c + top[0]]);
    const tk = new Set(), mk = new Set(); if (P.rxDom && rx[i]) for (let q = 0; q < 4; q++) { const v = (rx[i] >>> (8 * q)) & 255; if (!v) break; if ((v & 15) === ((v >> 4) ^ 8) && P.cellClumps && P.sugarCoat > 0) continue; tk.add(v >> 4); mk.add(v & 15); }
    const show = [...new Set([...tk, ...mk, ...top])].slice(0, 7);
    show.forEach((k, q) => { const x = 18, y = 20 + q * 26, rr = 3 + 8 * Math.sqrt(chem[c + k] / mx); parts.push(`<circle cx="${x}" cy="${y}" r="${rr}" fill="${spCss(k)}" fill-opacity=".8"/>`);
      t(x + 18, y + 4, MONO[k], mu); if (tk.has(k) || mk.has(k)) t(x + 48, y + 4, tk.has(k) && mk.has(k) ? 'takes, makes' : tk.has(k) ? 'it takes' : 'it makes', acc); });
    t(34, H0 - 4, 'in its square', mu); }
  // light
  const L = Math.max(0, Math.min(2, light[i])); parts.push(`<rect x="${W0 - 24}" y="20" width="10" height="160" fill="none" stroke="${mu}"/><rect x="${W0 - 24}" y="${20 + 160 * (1 - L / 2)}" width="10" height="${160 * L / 2}" fill="#e8b04a"/>`); t(W0 - 19, H0 - 4, 'light', mu);
  if (body[i]) t(cx, 14, `in clump #${body[i]}${P.cellClumps ? ` · coat ${ct.toFixed(2)}${ct >= P.coatMin ? ', sticky' : ''}` : ''}`, mu);
  else if (dor[i]) t(cx, 14, 'dormant', mu);
  return `<svg viewBox="0 0 ${W0} ${H0}" style="width:100%;max-width:340px;display:block;margin:4px 0" role="img" aria-label="Drawing of this cell">${parts.join('')}</svg>`;
}
