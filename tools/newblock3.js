// ---------------- light you draw: lamps hold the light up, shades keep it out
function isLightTool(t) { return t === 'light' || t === 'shade' || t === 'wipe'; }
function lampNote(i) { return lamp[i] > 0 ? ` A lamp holds the light here at ${lamp[i].toFixed(1)}.` : lamp[i] < 0 ? ' A shade keeps it dark.' : ''; }
function stamp(cx, cy) {
  const r = P.lsize, r2 = r * r + r, v = tool === 'light' ? P.lstrength : tool === 'shade' ? -1 : 0;
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
    if (dx * dx + dy * dy > r2) continue;
    const i = idx(cx + dx, cy + dy);
    lampCount += (v !== 0 ? 1 : 0) - (lamp[i] !== 0 ? 1 : 0);
    lamp[i] = v; changed[i] = 1;                      // wake the folded region around it
    if (v > 0 && light[i] < v) light[i] = v; else if (v < 0) light[i] = -1e-6;   // visible at once, even when paused
  }
}
function strokeTo(a, b) {                               // fill the gap between two pointer samples
  const n = Math.max(Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1])), st = Math.max(1, P.lsize >> 1);
  for (let k = st; k < n; k += st) stamp(Math.round(a[0] + (b[0] - a[0]) * k / n), Math.round(a[1] + (b[1] - a[1]) * k / n));
  if (n) stamp(b[0], b[1]);
}
function updateLightHint() {
  document.getElementById('lighthint').textContent = P.floor ? '' :
    'Light is switched off, so lamps and shades do nothing yet. Tick "Light (a floor)".';
}
document.getElementById('clearLight').onclick = () => { lamp.fill(0); lampCount = 0; changed.fill(1); };

// ---------------- the world is as large as the window
const PX_OUT = 1.3;
function worldDims() {
  const r = view.getBoundingClientRect(), w = Math.max(200, r.width), h = Math.max(200, r.height);
  const px = PX_OUT;                                              // pixels per cell when fully zoomed out: the world covers the window
  return [Math.max(96, Math.round(w / px / 4) * 4), Math.max(96, Math.round(h / px / 2) * 2)];   // columns in fours: the playhead reads four at a time
}
function allocWorld(nw, nh, keep) {
  const o = {alive, gen, xg, rsv, dor, light, body, lamp}, oW = W, oH = H;
  W = nw; H = nh; N = W * H;
  alive = new Uint8Array(N); nalive = new Uint8Array(N); gen = new Uint32Array(N); ngen = new Uint32Array(N); xg = new Uint16Array(N); nxg = new Uint16Array(N); rsv = new Float32Array(N); nrsv = new Float32Array(N); dor = new Uint8Array(N); ndor = new Uint8Array(N); soma = new Uint8Array(N); cH = new Uint32Array(N); coat = new Float32Array(N); rxAct = new Float32Array(N); seq = new Uint8Array(N * SL); slen = new Uint8Array(N); cat = new Uint16Array(N); rx = new Uint32Array(N); rxStr = new Uint8Array(N); regd = new Uint8Array(N); regList.length = 0;
  light = new Float32Array(N).fill(1); lightTmp = new Float32Array(N); changed = new Uint8Array(N).fill(1); nchanged = new Uint8Array(N);
  folded = new Uint8Array(N); lamp = new Float32Array(N); body = new Int32Array(N); nbody = new Int32Array(N);
  bmark = new Uint8Array(N); seen = new Uint8Array(N); zmap = new Uint8Array(N); hopm = new Uint8Array(N);
  off.width = W; off.height = H; img = octx.createImageData(W, H); comps = [];
  if (keep) {                                                      // what was there stays, centred; the rest is new empty ground
    const ox = Math.floor((W - oW) / 2), oy = Math.floor((H - oH) / 2);
    for (let y = 0; y < oH; y++) { const ty = y + oy; if (ty < 0 || ty >= H) continue;
      for (let x = 0; x < oW; x++) { const tx = x + ox; if (tx < 0 || tx >= W) continue; const a = y * oW + x, b = ty * W + tx;
        alive[b] = o.alive[a]; gen[b] = o.gen[a]; xg[b] = o.xg[a]; rsv[b] = o.rsv[a]; dor[b] = o.dor[a]; light[b] = o.light[a]; body[b] = o.body[a]; lamp[b] = o.lamp[a]; } }
  }
  lampCount = 0; for (let i = 0; i < N; i++) if (lamp[i] !== 0) lampCount++;
  chemAlloc();
  layoutZones();
}
function sizeWorld(keep) {
  const [nw, nh] = worldDims(); if (nw === W && nh === H) return false;
  allocWorld(nw, nh, keep); fit(); return true;
}


// ---------------- motility: a cell can hop into an empty neighbouring square if its code says so
// the prime 23 in a compound makes a cell motile; its exponent says how strongly it climbs the light (1 wanders)
function hopPass() {
  const rate = P.hop; motileN = 0; let livingN = 0; if (!(rate > 0)) return;
  hopm.fill(0); const fl = P.floor, hc = P.hopcost; let hops = 0;
  for (let y = 0; y < H; y++) {
    const ym = ((y - 1 + H) % H) * W, y0 = y * W, yp = ((y + 1) % H) * W;
    for (let x = 0; x < W; x++) {
      const i = y0 + x; if (!alive[i]) continue; livingN++; const g = gen[i], me = (g >>> 16) & 3; if (!me) continue; motileN++;
      if (fl) light[i] -= hc * .4;                 // being able to move costs a little every tick
      if (hopm[i] || rng() >= rate) continue;
      const xm = (x - 1 + W) % W, xp = (x + 1) % W, nb = [ym + xm, ym + x, ym + xp, y0 + xm, y0 + xp, yp + xm, yp + x, yp + xp];
      let n = 0; for (let k = 0; k < 8; k++) n += alive[nb[k]];
      const t = me - 1; let best = -1, bs = -1e9;
      for (let k = 0; k < 8; k++) {
        const j = nb[k]; if (alive[j] || hopm[j] || dishBlocked(j) || (fl && (amb ? amb[j] : light[j]) < hc)) continue;
        const sc = (fl ? t * 3 * (amb ? amb[j] : light[j]) : 0) + rng(); if (sc > bs) { bs = sc; best = j; }   // a hop seeks the brighter place (ambient light)
      }
      if (best < 0) continue;
      alive[best] = 1; gen[best] = g; xg[best] = xg[i]; rsv[best] = rsv[i]; rsv[i] = 0; dor[best] = dor[i]; dor[i] = 0; if (P.seqOn) moveSeq(i, best); alive[i] = 0; gen[i] = 0; body[best] = body[i]; body[i] = 0; hopm[best] = 1;
      light[best] = light[i] - (fl ? hc : 0); light[i] = 0; virMove(i, best);   // the cell takes its store with it, paying for the hop
      changed[i] = 1; changed[best] = 1; hops++;
    }
  }
  if (tick % 20 === 0) { document.getElementById('hopinfo').textContent = `${motileN} motile cells (${livingN ? Math.round(100 * motileN / livingN) : 0}% of the living) · ${hops} hops last tick`; }
}

// ---------------- zones: each has its own climate and its own instrument
const ZLAYOUTS = [[1, 1]];                                        // one world, one climate
const Z = {cc: 1, rr: 1, n: 1, list: [], distinct: true, show: true, layout: 0};
const ONE = {rg: 1, cost: 1, mu: 1, con: 1, fu: 1, death: 1, birth: 1};
const CL_RANGE = {rg: [.4, 2.2], cost: [.6, 1.8], mu: [.3, 5], con: [.2, 3], fu: [.3, 2], death: [.3, 4], birth: [.7, 1.4]};
const CL_WORDS = {rg: ['Lush', 'Arid'], cost: ['Costly', 'Cheap'], mu: ['Mutagenic', 'Stable'], con: ['Viral', 'Sealed'], fu: ['Fusing', 'Pure'], death: ['Frail', 'Hardy'], birth: ['Dear', 'Fertile']};
const CL_LABEL = {rg: 'light', cost: 'cost', mu: 'mutation', con: 'contagion', fu: 'fusion', death: 'fragility', birth: 'birth cost'};
function newClimate() {
  const c = {}; for (const k in CL_RANGE) { const [a, b] = CL_RANGE[k]; c[k] = Math.exp(Math.log(a) + rng() * (Math.log(b) - Math.log(a))); }
  return c;
}
function nameClimate(c) {
  let best = 'rg', bv = -1; for (const k in c) { const v = Math.abs(Math.log(c[k]) / Math.log(CL_RANGE[k][c[k] >= 1 ? 1 : 0])); if (v > bv) { bv = v; best = k; } }
  return CL_WORDS[best][c[best] >= 1 ? 0 : 1];
}
function newZone(k) { const cl = newClimate(); return {hue: (k * 67 + 15) % 360, cl, name: nameClimate(cl), glow: 0}; }
function climateText(z) {
  const out = []; for (const k in CL_LABEL) if (Math.abs(Math.log(z.cl[k])) > .15) out.push(`${CL_LABEL[k]} ×${z.cl[k].toFixed(1)}`);
  return out.join(', ') || 'average climate';
}
function zoneRecalc() {
  ZCONMAX = 0;
  for (let z = 0; z < Z.n; z++) {
    const c = Z.distinct && Z.n > 1 ? Z.list[z].cl : ONE;
    ZRG[z] = Math.min(.6, P.regrow * c.rg); ZCOST[z] = P.cost * c.cost * (P.env === 'dish' ? P.dishUpkeep : 1); ZMU[z] = P.mu * c.mu; ZCON[z] = P.contagion * c.con;
    ZFU[z] = Math.min(1, P.fusion * c.fu); ZDEATH[z] = Math.min(.5, P.death * c.death); ZBIRTH[z] = P.birth * c.birth;
    ZMARGIN[z] = 2 * ZCOST[z] + ZRG[z]; if (ZCON[z] > ZCONMAX) ZCONMAX = ZCON[z];
  }
}
function layoutZones() {
  let [cc, rr] = ZLAYOUTS[Z.layout]; if (H > W * 1.2 && cc > rr) [cc, rr] = [rr, cc];   // a tall window gets tall zones
  Z.cc = cc; Z.rr = rr; Z.n = cc * rr;
  while (Z.list.length < Z.n) Z.list.push(newZone(Z.list.length));
  for (let y = 0; y < H; y++) { const zy = Math.min(rr - 1, Math.floor(y * rr / H)), row = y * W;
    for (let x = 0; x < W; x++) zmap[row + x] = zy * cc + Math.min(cc - 1, Math.floor(x * cc / W)); }
  zoneRecalc(); changed.fill(1);
}
function zoneNote(i) {
  if (Z.n < 2) return '';
  const z = Z.list[zmap[i]];
  return `<b>Zone ${zmap[i] + 1}, ${z.name}</b>. ${Z.distinct ? climateText(z) : 'Same climate everywhere.'}`;
}
function drawZones(ox, oy, s) {
  if (!Z.show || Z.n < 2) return;
  ctx.save(); ctx.font = '12px system-ui'; ctx.textAlign = 'left';
  for (let z = 0; z < Z.n; z++) {
    const zn = Z.list[z], zx = z % Z.cc, zy = (z / Z.cc) | 0, gl = zn.glow || 0; zn.glow = 0;
    const x0 = ox + Math.ceil(zx * W / Z.cc) * s, x1 = ox + Math.ceil((zx + 1) * W / Z.cc) * s, y0 = oy + Math.ceil(zy * H / Z.rr) * s, y1 = oy + Math.ceil((zy + 1) * H / Z.rr) * s;
    ctx.fillStyle = `hsla(${zn.hue},70%,55%,${.04 + .1 * gl})`; ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
    ctx.strokeStyle = `hsla(${zn.hue},70%,70%,${.3 + .5 * gl})`; ctx.lineWidth = 1 + gl; ctx.setLineDash([6, 4]);
    ctx.strokeRect(x0 + .5, y0 + .5, x1 - x0 - 1, y1 - y0 - 1);
    if (s < 12 && x1 - x0 > 90) {
      const lx = Math.max(x0, 0) + 8, ly = Math.max(y0, 0) + 16;
      ctx.setLineDash([]); ctx.fillStyle = `hsla(${zn.hue},70%,84%,.92)`; ctx.fillText(`${z + 1} · ${zn.name}${Z.distinct ? '' : ''}`, lx, ly);
    }
  }
  ctx.restore();
}


const $ = id => document.getElementById(id);
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

// ---------------- tools, play, menu, full screen
const app = document.querySelector('.app'), stage = document.getElementById('stage');
const btnMenu = document.getElementById('btnMenu'), btnFs = document.getElementById('btnFs');
const inspFloat = document.getElementById('inspFloat'), inspFloatBody = document.getElementById('inspFloatBody');
const TOOL_KEYS = ['inspect', 'paint', 'erase', 'light', 'shade', 'wipe'];
let lightShown = false, idleT = 0, menuBeforeFs = false;

function setTool(name) {
  tool = name;
  document.querySelectorAll('[data-tool]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.tool === name)));
  view.style.cursor = name === 'inspect' ? 'grab' : 'crosshair';
  stage.dataset.mode = name;
  // you can't draw what you can't see: show the light the first time a light tool is picked
  if (isLightTool(name) && !lightShown) { lightShown = true; P.showLight = true; document.getElementById('showLight').checked = true; }
  updateLightHint();
}
function setRunning(v) {
  running = v;
  for (const id of ['play', 'dPlay']) document.getElementById(id).textContent = running ? 'Pause' : 'Play';
}
document.getElementById('dPlay').onclick = () => setRunning(!running);

function wake() {                                       // with the menu hidden, the overlays fade after a few quiet seconds
  app.classList.remove('idle'); clearTimeout(idleT);
  if (app.classList.contains('focus')) idleT = setTimeout(() => { if (!drag) app.classList.add('idle'); }, 3500);
}
function setMenu(hidden) {
  app.classList.toggle('focus', hidden);
  btnMenu.textContent = hidden ? 'Show menu' : 'Hide menu';
  if (!hidden) inspFloat.classList.remove('show');
  wake();
}
function mirrorInsp() {                                 // with the menu hidden the inspector floats over the world
  if (!app.classList.contains('focus')) return;
  inspFloatBody.innerHTML = document.getElementById('insp').innerHTML; inspFloat.classList.add('show');
}
inspFloat.querySelector('.x').onclick = () => inspFloat.classList.remove('show');
const fsOn = () => !!(document.fullscreenElement || document.webkitFullscreenElement);
async function toggleFs() {
  if (fsOn()) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); return; }
  const el = document.documentElement, req = el.requestFullscreen || el.webkitRequestFullscreen;
  // where full screen isn't available (some phones, or a frame that doesn't allow it), at least hide or show the menu
  if (!req) { setMenu(!app.classList.contains('focus')); return; }
  try { await req.call(el); } catch (err) { setMenu(!app.classList.contains('focus')); }
}
function onFsChange() {
  if (fsOn()) { menuBeforeFs = app.classList.contains('focus'); setMenu(true); btnFs.textContent = 'Exit fullscreen'; }
  else { setMenu(menuBeforeFs); btnFs.textContent = 'Fullscreen'; }
}
document.addEventListener('fullscreenchange', onFsChange);
document.addEventListener('webkitfullscreenchange', onFsChange);
btnMenu.onclick = () => setMenu(!app.classList.contains('focus'));
btnFs.onclick = toggleFs;
['pointermove', 'pointerdown', 'keydown', 'touchstart'].forEach(ev => addEventListener(ev, wake, {passive: true}));

function bump(key, d) {
  const el = document.querySelector(`[data-p="${key}"]`); if (!el) return;
  el.value = Math.max(+el.min, Math.min(+el.max, +el.value + d)); el.dispatchEvent(new Event('input'));
}

addEventListener('keydown', e => {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const tag = e.target && e.target.tagName, k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
  if (tag === 'SELECT') return;
  if (k === 'h') setMenu(!app.classList.contains('focus'));
  else if (k === 'f') toggleFs();
  else if (k === ' ' && tag !== 'BUTTON' && tag !== 'INPUT') { e.preventDefault(); setRunning(!running); }
  else if (k === 'Escape' && app.classList.contains('focus') && !fsOn()) setMenu(false);
  else if (/^[1-6]$/.test(k)) setTool(TOOL_KEYS[k - 1]);
  else if (k === '[' || k === ']') bump('lsize', k === ']' ? 1 : -1);
});

// light sliders that appear twice (the side panel and the floating dock) stay in step
for (const key of ['lsize', 'lstrength']) {
  const els = [...document.querySelectorAll(`[data-p="${key}"]`)];
  const sync = src => {
    P[key] = +src.value;
    for (const e of els) { e.value = src.value; const o = e.parentElement.querySelector('output'); if (o) o.textContent = src.value; }
  };
  for (const e of els) e.oninput = () => sync(e);
  sync(els[0]);
}
//@@CHEMUI@@
{ const el = document.getElementById('soupsize'), out = el.nextElementSibling; el.oninput = () => { out.textContent = el.value; }; }
// the world follows the window: a bigger or smaller stage (menu hidden, full screen, a dragged edge) re-sizes it, keeping what is there
let rsT = 0;
new ResizeObserver(() => {
  resize(); clearTimeout(rsT);
  rsT = setTimeout(() => {
    const [nw, nh] = worldDims(); if (Math.abs(nw - W) / W < .05 && Math.abs(nh - H) / H < .05) return;
    const wasFit = cam.s <= lastFit * 1.001, oW = W, oH = H;
    allocWorld(nw, nh, true);
    if (wasFit) fit(); else { cam.x += (W - oW) / 2; cam.y += (H - oH) / 2; }
  }, 250);
}).observe(stage);
resize(); { const [nw, nh] = worldDims(); allocWorld(nw, nh, false); } fit(); cam.s = fitScale() * 1.7; reset(document.getElementById('seedmode').value); setTool('inspect');
