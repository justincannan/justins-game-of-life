import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, (n, old[:80])
    s = s.replace(old, new)


# ------------------------------------------------------------------ CSS
rep(r'''.insp div{font-size:12px;padding:2px 0}
</style></head><body>''', r'''.insp div{font-size:12px;padding:2px 0}
/* overlays on the stage */
.hud{max-width:calc(100% - 230px)}
.topbtns{position:absolute;right:10px;top:10px;display:flex;gap:6px}
.fade{transition:opacity .4s}
.app.idle .fade{opacity:0;pointer-events:none}
.dock{display:none;position:absolute;left:50%;bottom:10px;transform:translateX(-50%);max-width:calc(100% - 150px);
background:rgba(20,20,19,.86);border-radius:10px;padding:4px 8px}
.app.focus .dock{display:block}
.dock .row{justify-content:center;margin:4px 0}
.dock label{display:inline-flex;gap:6px;align-items:center;font-size:12px;color:#c3c2b7}
.dock input[type=range]{width:90px}
.dock output{min-width:28px;text-align:right;font-variant-numeric:tabular-nums;color:#f0efec}
.dock .lightonly{display:none}
.stage[data-mode=light] .dock .lightonly,.stage[data-mode=shade] .dock .lightonly,.stage[data-mode=wipe] .dock .lightonly{display:inline-flex}
.sepv{width:1px;height:20px;background:rgba(255,255,255,.22);margin:0 2px}
.inspfloat{display:none;position:absolute;left:10px;top:44px;width:min(300px,calc(100% - 20px));max-height:60%;overflow:auto;
background:rgba(20,20,19,.9);color:#f0efec;border-radius:8px;padding:6px 10px;font-size:12px}
.app.focus .inspfloat.show{display:block}
.inspfloat .x{float:right;padding:0 7px;margin-left:6px}
/* menu hidden: the world takes the whole window */
.app.focus{grid-template-columns:minmax(0,1fr);height:100vh;height:100dvh}
.app.focus .side{display:none}
.app.focus .stage{height:100vh;height:100dvh}
.chrow{display:grid;grid-template-columns:12px 22px 70px 1fr;gap:6px;align-items:center;font-size:11px;padding:1px 0}.chbar{height:6px;background:var(--grid);border-radius:3px;overflow:hidden}.chbar i{display:block;height:100%}
</style></head><body>''')

# ------------------------------------------------------------------ HTML: stage overlays
rep('<div class="stage" id="stage">', '<div class="stage" id="stage" data-mode="inspect">')
rep('<div class="hud" id="hud"></div>', '<div class="hud fade" id="hud"></div>')
rep('<div class="zoom">', '<div class="zoom fade">')
rep(r'''<button id="zfit">Fit</button></div>
 </div>
 <div class="side">''', r'''<button id="zfit">Fit</button></div>
  <div class="topbtns fade"><button id="btnMenu" title="Hide the menu (H)">Hide menu</button><button id="btnFs" title="Full screen (F)">Fullscreen</button></div>
  <div class="dock fade" id="dock">
   <div class="row"><button id="dPlay">Pause</button><span class="sepv"></span>
    <button data-tool="inspect" aria-pressed="true" title="Inspect (1)">Inspect</button><button data-tool="paint" aria-pressed="false" title="Paint (2)">Paint</button>
    <button data-tool="erase" aria-pressed="false" title="Erase (3)">Erase</button><button data-tool="light" aria-pressed="false" title="Draw light (4)">Light</button>
    <button data-tool="shade" aria-pressed="false" title="Draw shade (5)">Shade</button><button data-tool="wipe" aria-pressed="false" title="Wipe drawn light (6)">Wipe light</button></div>
   <div class="row">
    <label class="lightonly">Size <input type="range" data-p="lsize" min="1" max="24" value="6"><output></output></label>
    <label class="lightonly">Strength <input type="range" data-p="lstrength" min="0.1" max="4" step="0.1" value="1.5"><output></output></label></div>
  </div>
  <div class="inspfloat" id="inspFloat"><button class="x" aria-label="Close">×</button><div class="insp" id="inspFloatBody"></div></div>
 </div>
 <div class="side">''')

rep('<title>Codes as Rules</title>', "<title>Justin's Game of Life</title>")
rep('<h1>Codes as rules</h1>', "<h1>Justin's Game of Life</h1>")

rep('<option value="soup">Mixed soup</option>', '<option value="organism">One organism</option><option value="soup">Mixed soup</option>')
rep('<button id="reset">Reset</button></div>', '<select id="soupshape" aria-label="Shape of the start"><option value="ring">Ring</option><option value="disc">Disc</option><option value="cross">Cross</option><option value="diamond">Diamond</option><option value="band">Band</option></select><button id="reset">Reset</button></div>')
# reset: shape and organism
rep("    for (let k = 0; k < 24; k++) {", "    for (let k = 0; k < (org ? 1 : 24); k++) {")
rep("if (mode === 'life' || (mode === 'soup' && k < 8)) g =", "if (mode === 'life' || org || (mode === 'soup' && k < 8)) g =")
rep("'A new world: 24 codes in patches. ' +", "(mode === 'organism' ? 'A new world with one organism. ' : 'A new world: 24 codes in patches. ') +")
rep(": mode === 'life' ? 'All carry B3/S23, with different tags.'", ": mode === 'organism' ? 'It carries B3/S23 and copies itself, with errors.' : mode === 'life' ? 'All carry B3/S23, with different tags.'")

rep('<input type="checkbox" id="bodiesOn" checked>', '<input type="checkbox" id="bodiesOn">')
rep('Copy errors (per bit)<input type="range" id="mu" min="0" max="0.02" step="0.0005" value="0.002">', 'Copy errors (per prime)<input type="range" id="mu" min="0" max="0.04" step="0.0005" value="0.004">')
rep("mu:0.002,", "mu:0.004,")
rep('  <label class="sl">Chance death<input type="range" id="death" min="0" max="0.02" step="0.001" value="0.002"><output></output></label>',
    '  <label class="sl">Chance death<input type="range" id="death" min="0" max="0.02" step="0.001" value="0.002"><output></output></label>\n'
    '  <label class="sl">Hop rate (motile cells)<input type="range" id="hop" min="0" max="1" step="0.05" value="0.3"><output></output></label>\n'
    '  <label class="sl">Light per hop<input type="range" id="hopcost" min="0" max="0.3" step="0.005" value="0.2"><output></output></label>\n'
    '  <p id="hopinfo" style="color:var(--muted);margin:2px 0 8px"></p>\n'
    '  <div class="row"><button class="resetRules" title="Put every rate, cost and chemistry setting back to its starting value">Reset rules</button></div>')
rep("[alive, nalive] = [nalive, alive]; [gen, ngen] = [ngen, gen]; [changed, nchanged] = [nchanged, changed];", "[alive, nalive] = [nalive, alive]; [gen, ngen] = [ngen, gen]; [changed, nchanged] = [nchanged, changed];\n  hopPass();")
rep("const t = TAG(gen[i]); const v = (tg.get(t) || 0) + 1;", "const t = TAG(gen[i]) >> 4; const v = (tg.get(t) || 0) + 1;")
rep("pool.push(g); reg(g, null, 'chance');", "if (mode === 'organism') g = (g & ~(15 << 22)) >>> 0;   // the first organism is sessile; hopping has to evolve\n      pool.push(g); reg(g, null, 'chance');")

rep('<input type="checkbox" id="showLight">', '<input type="checkbox" id="showLight" checked>')
rep('<input type="checkbox" id="showForms" checked>', '<input type="checkbox" id="showForms">')
rep('  <div class="row" role="group" aria-label="Click tool">', '  <label class="sl">Start size<input type="range" id="soupsize" min="5" max="100" step="1" value="80"><output>80</output></label>\n  <div class="row" role="group" aria-label="Click tool">')

# ------------------------------------------------------------------ HTML: side panel
rep('<button data-tool="erase" aria-pressed="false">Erase</button></div>', r'''<button data-tool="erase" aria-pressed="false">Erase</button>
   <button data-tool="light" aria-pressed="false">Light</button><button data-tool="shade" aria-pressed="false">Shade</button>
   <button data-tool="wipe" aria-pressed="false">Wipe light</button></div>
  <div class="card" id="lightopts">
   <p style="margin-top:0"><b>Light</b> lays down lamps that keep the light up, so a crowd can't starve there. <b>Shade</b> keeps light out: nothing lives or is born there.
   <b>Wipe light</b> removes both. Drawn light survives Reset.</p>
   <label class="sl">Light brush size<input type="range" data-p="lsize" min="1" max="24" value="6"><output></output></label>
   <label class="sl">Lamp strength<input type="range" data-p="lstrength" min="0.1" max="4" step="0.1" value="1.5"><output></output></label>
   <div class="row"><button id="clearLight">Clear drawn light</button></div>
   <p id="lighthint" style="color:var(--muted)"></p>
   <p style="color:var(--muted)">Keys: H menu · F full screen · I heat vision · Space pause · 1–6 tools · [ ] brush size. Shift-drag or right-drag pans with any tool.</p>
  </div>''')

# ------------------------------------------------------------------ JS: state
rep('showLight:false, showFolds:false, showForms:true,', 'showLight:true, showFolds:false, showForms:false,')
rep('bodiesOn:true, nucleate:0.03, bodyCost:0.004, bmu:0.01};',
    "bodiesOn:false, nucleate:0.03, bodyCost:0.004, bmu:0.01,\n"
    "  lsize:6, lstrength:1.5};")

rep('const W = 256, H = 256, N = W * H;', 'let W = 256, H = 256, N = W * H;   // the world is sized to the window (allocWorld)')
rep('const light = new Float32Array(N), lightTmp = new Float32Array(N);', 'let light = new Float32Array(N), lightTmp = new Float32Array(N);')
rep('const bmark = new Uint8Array(N);', 'let bmark = new Uint8Array(N);')
rep('const seen = new Uint8Array(N);', 'let seen = new Uint8Array(N);')
rep("const octx = off.getContext('2d'), img = octx.createImageData(W, H);", "const octx = off.getContext('2d'); let img = octx.createImageData(W, H);")
rep('const folded = new Uint8Array(N);',
    "let folded = new Uint8Array(N);\n"
    "// light you draw: a lamp (>0) keeps the light at least that high; a shade (<0) keeps it out\n"
    "let lamp = new Float32Array(N);\nlet lampCount = 0;\n"
    "let zmap = new Uint8Array(N);   // which zone each cell is in\n"
    "let hopm = new Uint8Array(N), motileN = 0;\n"
    "const ZRG = new Float32Array(16), ZCOST = new Float32Array(16), ZMU = new Float32Array(16), ZCON = new Float32Array(16), ZFU = new Float32Array(16),\n"
    "  ZDEATH = new Float32Array(16), ZBIRTH = new Float32Array(16), ZMARGIN = new Float32Array(16); let ZCONMAX = 0;")

# step(): every zone has its own climate
rep("  const fl = P.floor, cost = P.cost, rg = P.regrow, mu = P.mu, fu = P.fusion, fo = P.foldOn;",
    "  zoneRecalc();\n  const fl = P.floor, fo = P.foldOn;")
rep("    for (let i = 0; i < N; i++) { light[i] += rg * (1 - light[i]); if (alive[i]) { light[i] -= cost; if (light[i] < 0) light[i] = -1e-6; } }",
    "    for (let i = 0; i < N; i++) { const z = zmap[i]; light[i] += ZRG[z] * (1 - light[i]); if (alive[i]) { light[i] -= ZCOST[z]; if (light[i] < 0) light[i] = -1e-6; } }")
rep("  const margin = 2 * cost + rg;\n", "")
rep("const xm = (x - 1 + W) % W, xp = (x + 1) % W, i = y0 + x;", "const xm = (x - 1 + W) % W, xp = (x + 1) % W, i = y0 + x, zi = zmap[i];")
rep("if (fo && !(alive[i] && P.death > 0) &&", "if (fo && !(alive[i] && (ZDEATH[zi] > 0 || envOn)) &&")
rep("(!fl || light[i] >= margin)) {", "(!fl || light[i] >= ZMARGIN[zi])) {")
rep("&& !(P.death > 0 && rng() < P.death);", "&& !(ZDEATH[zi] > 0 && rng() < ZDEATH[zi]);")
rep("} else if (n > 0 && (!fl || light[i] >= cost)) {", "} else if (n > 0 && (!fl || light[i] >= ZCOST[zi])) {")
rep("(!fl || light[j] >= P.birth)) { cand[c] = gen[j];", "(!fl || light[j] >= ZBIRTH[zi])) { cand[c] = gen[j];")
rep("if (mixed && rng() < fu) {", "if (mixed && rng() < ZFU[zi]) {")
rep("if (fl && pj >= 0) light[pj] -= P.birth;", "if (fl && pj >= 0) light[pj] -= ZBIRTH[zi];")
rep("if (mu > 0) for (let bit = 0; bit < 32; bit++) if (rng() < mu) {", "if (ZMU[zi] > 0) for (let bit = 0; bit < 32; bit++) if (rng() < ZMU[zi]) {")
rep("if (P.contagion > 0) for (let i = 0; i < N; i++) {", "if (ZCONMAX > 0) for (let i = 0; i < N; i++) {")
rep("rng() >= k / 15 * P.contagion) continue;", "rng() >= k / 15 * ZCON[zmap[i]]) continue;")
rep("if (P.floor) light[i] -= P.cost;\n  }", "if (P.floor) light[i] -= ZCOST[zmap[i]];\n  }")

# reset(): the soup is an ellipse that scales with the world
rep("    const r0 = 70;\n", "    const org = mode === 'organism', shape = document.getElementById('soupshape').value, ps = 12;\n    const sz = +document.getElementById('soupsize').value / 100, rx = org ? Math.max(7, Math.round(sz * 20)) : Math.round(W * .5 * sz), ry = org ? Math.max(7, Math.round(sz * 20)) : Math.round(H * .5 * sz);\n    const inShape = (u, v) => { const r2 = u * u + v * v; return shape === 'ring' ? r2 <= 1 && r2 >= .3 : shape === 'disc' ? r2 <= 1 : shape === 'cross' ? Math.abs(u) < .3 || Math.abs(v) < .3 : shape === 'diamond' ? Math.abs(u) + Math.abs(v) <= 1 : Math.abs(v) < .35; };\n")
rep("""    for (let y = -r0; y < r0; y++) for (let x = -r0; x < r0; x++) {
      if (x * x + y * y > r0 * r0 || rng() > .32) continue;""", """    for (let y = -ry; y < ry; y++) for (let x = -rx; x < rx; x++) {
      if (!inShape(x / rx, y / ry) || rng() > (org ? .42 : .32)) continue;""")
rep("const k = (Math.floor((x + r0) / 12) * 7 + Math.floor((y + r0) / 12) * 3) % pool.length;",
    "const k = (Math.floor((x + rx) / ps) * 7 + Math.floor((y + ry) / ps) * 3) % pool.length;")

# step(): lamps and shades hold the light field
rep('''    for (let i = 0; i < N; i++) { const z = zmap[i]; light[i] += ZRG[z] * (1 - light[i]); if (alive[i]) { light[i] -= ZCOST[z]; if (light[i] < 0) light[i] = -1e-6; } }''',
    '''    for (let i = 0; i < N; i++) { const z = zmap[i]; light[i] += ZRG[z] * (1 - light[i]); if (alive[i]) { light[i] -= ZCOST[z]; if (light[i] < 0) light[i] = -1e-6; } }
    // drawn light: lamps hold the light up, shades keep it out (a cell with no light dies, and none is born)
    if (lampCount) for (let i = 0; i < N; i++) { const L = lamp[i]; if (L > 0) { if (light[i] < L) light[i] = L; } else if (L < 0) light[i] = -1e-6; }''')

# one world, the size of the window: the view can't zoom out past it, and pans only within it
rep("function fit() { const r = view.getBoundingClientRect(); cam = {x: W / 2, y: H / 2, s: Math.max(1, Math.min(r.width, r.height) / W)}; }",
    """let lastFit = 0;
const minZoom = () => fitScale();                          // fully zoomed out, the world still fills the window
const fitScale = () => { const r = view.getBoundingClientRect(); return Math.max(.2, Math.max(r.width / W, r.height / H)); };   // cover, not contain
function fit() { cam = {x: W / 2, y: H / 2, s: fitScale()}; lastFit = cam.s; }
function clampCam() {
  const r = view.getBoundingClientRect(), s = cam.s = Math.max(minZoom(), Math.min(60, cam.s)), hw = r.width / (2 * s), hh = r.height / (2 * s);
  cam.x = hw * 2 >= W ? W / 2 : Math.max(hw, Math.min(W - hw, cam.x));
  cam.y = hh * 2 >= H ? H / 2 : Math.max(hh, Math.min(H - hh, cam.y));
}""")
rep("  const r = view.getBoundingClientRect(), s = cam.s;\n  ctx.fillStyle = '#050505'; ctx.fillRect(0, 0, r.width, r.height);",
    "  const r = view.getBoundingClientRect(); clampCam(); const s = cam.s;\n  ctx.fillStyle = '#050505'; ctx.fillRect(0, 0, r.width, r.height);")
rep("""  const tx0 = Math.floor(-ox / (W * s)), tx1 = Math.floor((r.width - ox) / (W * s)), ty0 = Math.floor(-oy / (H * s)), ty1 = Math.floor((r.height - oy) / (H * s));
  for (let ty = ty0; ty <= ty1; ty++) for (let tx = tx0; tx <= tx1; tx++) ctx.drawImage(off, ox + tx * W * s, oy + ty * H * s, W * s, H * s);""",
    """  const tx0 = 0, tx1 = 0, ty0 = 0, ty1 = 0;                   // one copy of the world, not a tiling
  ctx.drawImage(off, ox, oy, W * s, H * s);
  drawZones(ox, oy, s);""")
rep("const ns = Math.max(.5, Math.min(60, cam.s * f));", "const ns = Math.max(minZoom(), Math.min(60, cam.s * f));")
rep("document.getElementById('zout').onclick = () => cam.s = Math.max(.5, cam.s / 1.6);", "document.getElementById('zout').onclick = () => cam.s = Math.max(minZoom(), cam.s / 1.6);")
rep("document.getElementById('reset').onclick = () => { reset(document.getElementById('seedmode').value); };",
    "document.getElementById('reset').onclick = () => { sizeWorld(false); reset(document.getElementById('seedmode').value); };")

# the inspector says which zone a cell is in
rep("if (!alive[i]) { el.innerHTML = `<div>Cell", "if (!alive[i]) { el.innerHTML = `<div>${zoneNote(i)}</div><div>Cell")
rep("el.innerHTML = `<div><span class=\"sw\" style=\"display:inline-block;background:${tagCss(g)}\"></span> <b>Code", "el.innerHTML = `<div>${zoneNote(i)}</div><div><span class=\"sw\" style=\"display:inline-block;background:${tagCss(g)}\"></span> <b>Code")

# render: drawn light
rep("} else if (P.showLight) { const L = Math.max(0, light[i]); d[p] = 8; d[p + 1] = 14 + 30 * L; d[p + 2] = 20 + 70 * L; }",
    '''} else if (lamp[i] !== 0) {
      const lp = lamp[i], q = P.showLight ? 1 : .35;
      if (lp > 0) { const u = Math.min(1, lp / 3); d[p] = (70 + 150 * u) * q; d[p + 1] = (50 + 100 * u) * q; d[p + 2] = (10 + 20 * u) * q; }
      else { d[p] = 70 * q; d[p + 1] = 18 * q; d[p + 2] = 90 * q; }
    } else if (P.showLight) { const L = Math.max(0, light[i]); d[p] = 8; d[p + 1] = 14 + 30 * L; d[p + 2] = 20 + 70 * L; }''')

# render: the light brush ring (drawn just before the HUD text)
rep("document.getElementById('hud').textContent = `tick ${tick}",
    '''  // the light brush
  if (hover && isLightTool(tool)) {
    const [hx, hy] = toCell(hover.x, hover.y);
    ctx.strokeStyle = tool === 'light' ? 'rgba(255,214,110,.95)' : tool === 'shade' ? 'rgba(180,120,255,.95)' : 'rgba(255,255,255,.8)';
    ctx.lineWidth = 1.5; ctx.setLineDash(tool === 'wipe' ? [4, 3] : []);
    ctx.beginPath(); ctx.arc(ox + (hx + .5) * s, oy + (hy + .5) * s, (P.lsize + .5) * s, 0, 6.2832); ctx.stroke(); ctx.setLineDash([]);
  }
  document.getElementById('hud').textContent = `tick ${tick}''')

# inspector: mirrored into a floating card when the menu is hidden; shows drawn light
rep("function inspect(x, y) {", "function inspect(x, y) { inspectCore(x, y); mirrorInsp(); }\nfunction inspectCore(x, y) {")
rep("is empty. Light ${light[i].toFixed(2)}.</div>", "is empty. Light ${Math.max(0, light[i]).toFixed(2)}.${lampNote(i)}</div>")
rep("<div>Light here ${light[i].toFixed(2)}. ${folded[i]", "<div>Light here ${Math.max(0, light[i]).toFixed(2)}.${lampNote(i)} ${folded[i]")

# pointer handling: light strokes, pan with right/middle/shift in any tool, brush hover
rep("view.addEventListener('pointerdown', e => { view.setPointerCapture(e.pointerId); drag = {x: e.clientX, y: e.clientY, cx: cam.x, cy: cam.y, moved: false}; });",
    '''let hover = null;
view.addEventListener('pointerdown', e => {
  view.setPointerCapture(e.pointerId);
  // any tool pans with the middle or right button, or shift; the light tools lay a stroke from the first touch
  const pan = tool === 'inspect' || e.button === 1 || e.button === 2 || e.shiftKey;
  drag = {x: e.clientX, y: e.clientY, cx: cam.x, cy: cam.y, moved: false, pan, stroke: !pan && isLightTool(tool), last: null};
  hover = {x: e.clientX, y: e.clientY};
  if (drag.stroke) { drag.last = toCell(e.clientX, e.clientY); stamp(drag.last[0], drag.last[1]); }
});
view.addEventListener('pointerleave', () => { hover = null; });
view.addEventListener('contextmenu', e => e.preventDefault());''')
rep('''view.addEventListener('pointermove', e => {
  if (!drag) return;''', '''view.addEventListener('pointermove', e => {
  hover = {x: e.clientX, y: e.clientY};
  if (!drag) return;''')
rep('''  if (drag.moved && tool === 'inspect') { cam.x = drag.cx - dx / cam.s; cam.y = drag.cy - dy / cam.s; }
  else if (drag.moved) apply(e);''', '''  if (drag.stroke) { const c = toCell(e.clientX, e.clientY); strokeTo(drag.last, c); drag.last = c; }
  else if (drag.moved && drag.pan) { cam.x = drag.cx - dx / cam.s; cam.y = drag.cy - dy / cam.s; }
  else if (drag.moved) apply(e);''')
rep("view.addEventListener('pointerup', e => { if (drag && !drag.moved) apply(e); drag = null; });",
    '''view.addEventListener('pointerup', e => { if (drag && !drag.moved && !drag.stroke && (tool === 'inspect' || !drag.pan)) apply(e); drag = null; });
view.addEventListener('pointercancel', () => { drag = null; });''')

# tool buttons, play button
rep('''document.querySelectorAll('[data-tool]').forEach(b => b.onclick = () => {
  tool = b.dataset.tool; document.querySelectorAll('[data-tool]').forEach(x => x.setAttribute('aria-pressed', x === b));
  view.style.cursor = tool === 'inspect' ? 'grab' : 'crosshair';
});''', "document.querySelectorAll('[data-tool]').forEach(b => b.onclick = () => setTool(b.dataset.tool));")
rep("document.getElementById('play').onclick = e => { running = !running; e.target.textContent = running ? 'Pause' : 'Play'; };",
    "document.getElementById('play').onclick = () => setRunning(!running);")

# slider / checkbox lists
rep("for (const id of ['speed', 'mu', 'contagion', 'fusion', 'regrow', 'cost', 'spread', 'birth', 'death', 'nucleate', 'bodyCost']) {",
    "for (const id of ['speed', 'mu', 'contagion', 'fusion', 'regrow', 'cost', 'spread', 'birth', 'death', 'nucleate', 'bodyCost', 'hop', 'hopcost']) {")
rep("for (const id of ['floor', 'foldOn', 'showLight', 'showFolds', 'showForms', 'bodiesOn']) {",
    "for (const id of ['floor', 'foldOn', 'showLight', 'showFolds', 'showForms', 'bodiesOn']) {")
rep("el.onchange = () => { P[id] = el.checked; if (id === 'foldOn' || id === 'floor') changed.fill(1); };",
    "el.onchange = () => { P[id] = el.checked; if (id === 'foldOn' || id === 'floor') changed.fill(1); if (id === 'floor') updateLightHint(); };")

# ------------------------------------------------------------------ compounds and chemistry
rep("""// genome: bits 0-8 survive on n neighbours; 9-17 birth on n; 18-21 contagion strength; 22-31 a neutral tag (colour)
const S = g => g & 511, B = g => (g >>> 9) & 511, K = g => (g >>> 18) & 15, TAG = g => g >>> 22;
function rule(g) {
  let b = '', s = '';
  for (let n = 1; n <= 8; n++) if ((B(g) >> n) & 1) b += n;
  for (let n = 0; n <= 8; n++) if ((S(g) >> n) & 1) s += n;
  return 'B' + b + '/S' + s + (K(g) ? ' · c' + K(g) : '');
}
const LIFE = (1 << 2 | 1 << 3) | ((1 << 3) << 9);   // B3/S23, the classic rule, as one code among many
const randTag = () => Math.floor(rng() * 1024) << 22;
function randomGenome() { return (Math.floor(rng() * 2 ** 22) & ~(1 << 9)) | randTag(); }""",
"""// genome: a compound of the first sixteen primes, kept as its exponent list (two bits per prime, exponents 0-3).
// The number is 2^e0 * 3^e1 * 5^e2 * ...; its factorisation is its rule. Primes 2..19 stand for neighbour counts 1..8
// (exponent 1: survive with that many neighbours; 2: give birth into squares with that many; 3: both).
// 23 motility, 29 contagion, 31 light efficiency, 37 hardiness, 41 proofreading, 43 thermophily (a taste for warm water), 47/53 inert (they mark the lineage).
// Conway's Life, "survive on 2 or 3, born on 3", is 3 x 5^3 = 375.
const PR = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53], NP = 16;
const EX = (g, k) => (g >>> (2 * k)) & 3;
const SURV = new Uint16Array(65536), BIRTHT = new Uint16Array(65536);
for (let v = 0; v < 65536; v++) { let s = 0, b = 0; for (let n = 1; n <= 8; n++) { const e = (v >>> (2 * (n - 1))) & 3; if (e & 1) s |= 1 << n; if (e & 2) b |= 1 << n; } SURV[v] = s; BIRTHT[v] = b; }
const S = g => SURV[g & 65535], B = g => BIRTHT[g & 65535], K = g => EX(g, 9) * 5, LINE = g => g >>> 28, TAG = LINE;
const EFFT = [1, .8, .62, .46], HARDT = [1, .6, .3, .1], PROOFT = [1, .6, .35, .15];
const SUPS = ['', '', '²', '³'];
function formula(g) { let s = ''; for (let k = 0; k < NP; k++) { const e = EX(g, k); if (e) s += (s ? '·' : '') + PR[k] + SUPS[e]; } s = s || '1'; return s.length > 30 ? s.slice(0, 29) + '…' : s; }
function rule(g) {
  let b = '', s = '';
  for (let n = 1; n <= 8; n++) if ((B(g) >> n) & 1) b += n;
  for (let n = 1; n <= 8; n++) if ((S(g) >> n) & 1) s += n;
  return 'B' + b + '/S' + s + ' ' + formula(g);
}
const LIFE = (1 << 2) | (3 << 4);   // 3 x 5^3 = 375: B3/S23, the classic rule, as one compound among many
const randTag = () => (Math.floor(rng() * 16) << 28) >>> 0;
function randomGenome() {
  let g = 0;
  for (let k = 0; k < NP; k++) { const u = rng(); const e = k < 8 ? (u < .5 ? 0 : u < .75 ? 1 : u < .9 ? 2 : 3) : (u < .75 ? 0 : u < .9 ? 1 : u < .97 ? 2 : 3); g |= e << (2 * k); }
  return g >>> 0;
}""")
rep("""// colours: hue from the tag
const TAGRGB = new Uint8Array(1024 * 3);
for (let t = 0; t < 1024; t++) {
  const h = t / 1024 * 360, s = .62, l = .58, k = n => (n + h / 30) % 12, a = s * Math.min(l, 1 - l);
  const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1));
  TAGRGB[t * 3] = f(0) * 255; TAGRGB[t * 3 + 1] = f(8) * 255; TAGRGB[t * 3 + 2] = f(4) * 255;
}
const tagCss = g => { const t = TAG(g) * 3; return `rgb(${TAGRGB[t]},${TAGRGB[t + 1]},${TAGRGB[t + 2]})`; };""",
"""// colours: the hue is the blend of the hues of the primes in the compound (a pure compound is vivid, a mixed one pale);
// the brightness follows the lineage marks. Cached by compound.
const PHC = new Float32Array(16), PHS = new Float32Array(16);
for (let k = 0; k < 16; k++) { const h = (k * 137.508) % 360 * Math.PI / 180; PHC[k] = Math.cos(h); PHS[k] = Math.sin(h); }
const CK = new Uint32Array(65536), CV = new Uint8Array(65536 * 3), COK = new Uint8Array(65536);
function colorSlot(g) {
  const h = Math.imul(g, 2654435761) >>> 16, o = h * 3;
  if (COK[h] && CK[h] === g) return o;
  let x = 0, y = 0, w = 0;
  for (let k = 0; k < 14; k++) { const e = (g >>> (2 * k)) & 3; if (e) { x += e * PHC[k]; y += e * PHS[k]; w += e; } }
  const hue = w ? Math.atan2(y, x) * 180 / Math.PI + 360 : 0, sat = w ? .3 + .55 * Math.hypot(x, y) / w : .05, l = .42 + .22 * (g >>> 28) / 15;
  const a = sat * Math.min(l, 1 - l), f = n => { const q = (n + hue / 30) % 12; return l - a * Math.max(-1, Math.min(q - 3, 9 - q, 1)); };
  CK[h] = g; COK[h] = 1; CV[o] = f(0) * 255; CV[o + 1] = f(8) * 255; CV[o + 2] = f(4) * 255;
  return o;
}
const tagCss = g => { const o = colorSlot(g); return `rgb(${CV[o]},${CV[o + 1]},${CV[o + 2]})`; };""")

# state
rep("lsize:6, lstrength:1.5};", "lsize:6, lstrength:1.5,\n  chemOn:true, chrich:45, chrate:.04, chdiff:.15, chrecyc:.7, chunit:1, chshow:'off', kinw:1, terr:.3, front:.5,\n  view:'normal', env:'pond', dayLen:400, nightDepth:.4, heatDiff:.2, heatRelax:.02, heatHarm:.02, heatLife:.2, ventPower:1, heatChaos:.35, current:.5, qthr:.35, qsave:.15, sigspread:.2, qmut:1, qseed:0, xseed:0, gProd:true, gSex:true, gPred:false, prodRate:.3, prodCost:.03, predRate:.1, predGain:.4};")
rep("let births = 0, deaths = 0, foldedCount = 0, writes = 0;", "let births = 0, deaths = 0, foldedCount = 0, writes = 0, starved = 0, walled = 0, heated = 0;")
rep("births = deaths = foldedCount = writes = 0;", "births = deaths = foldedCount = writes = starved = walled = heated = 0;")

# step: chemistry
rep("  const fl = P.floor, fo = P.foldOn;\n", "  const fl = P.floor, fo = P.foldOn, chemOn = P.chemOn, kw = P.kinw, terrOn = P.terr > 0, fr = P.front, envOn = P.env !== 'even', hh = P.heatHarm; if ((tick & 1) === 0) { if (envOn) envStep(); if (chemOn) chemStep(); fieldStep(); sigStep(); xslots(); produce(); }\n")
rep("if (alive[i]) { light[i] -= ZCOST[z]; if (light[i] < 0) light[i] = -1e-6; } }\n    // drawn light", "if (alive[i]) { light[i] -= ZCOST[z] * EFFT[(gen[i] >>> 20) & 3]; if (light[i] < 0) light[i] = -1e-6; } }\n    // drawn light")
rep("&& !(ZDEATH[zi] > 0 && rng() < ZDEATH[zi]);", "&& !(ZDEATH[zi] > 0 && rng() < ZDEATH[zi] * HARDT[(gen[i] >>> 22) & 3]) && !(envOn && rng() < hh * (1 - thermFit(gen[i], temp[cmap[i]])));")
rep("if (!ok) { nchanged[i] = 1; deaths++; }", "if (!ok) { nchanged[i] = 1; deaths++; if (chemOn) releaseChem(cmap[i] << 4, gen[i]); }")
rep("const m = Math.floor(rng() * 2 ** 32) >>> 0;\n            g = ((a & m) | (b2 & ~m)) >>> 0;", "let m = Math.floor(rng() * 2 ** 32) & 0x55555555; m = (m | (m << 1)) >>> 0;   // crossover falls between primes\n            g = ((a & m) | (b2 & ~m)) >>> 0;")
rep("""          if (fl && pj >= 0) light[pj] -= ZBIRTH[zi];
          nbody[i] = pj >= 0 ? body[pj] : 0;         // a cell born of a body's cell is born into that body
          if (ZMU[zi] > 0) for (let bit = 0; bit < 32; bit++) if (rng() < ZMU[zi]) { g = (g ^ (1 << bit)) >>> 0; if (how === 'copy') how = 'mutant'; }
""", """          if (ZMU[zi] > 0) { const m2 = mutate(g, ZMU[zi] * PROOFT[(parent >>> 24) & 3] * (envOn ? .6 + temp[cmap[i]] : 1)); if (m2 !== g) { g = m2; if (how === 'copy') how = 'mutant'; } }
          // building the child takes the molecules its compound is made of; if the ground here is short of one, nothing is born
          if (terrOn && foreignBlocked(cmap[i], g)) { nalive[i] = 0; ngen[i] = 0; nbody[i] = 0; nchanged[i] = 1; walled++; continue; }
          if (envOn && rng() >= thermFit(g, temp[cmap[i]])) { nalive[i] = 0; ngen[i] = 0; nbody[i] = 0; nchanged[i] = 1; heated++; continue; }
          if (chemOn && !payChem(cmap[i] << 4, g, 1 + fr * (8 - n) / 7)) { nalive[i] = 0; ngen[i] = 0; nbody[i] = 0; nchanged[i] = 1; starved++; continue; }
          if (fl && pj >= 0) light[pj] -= ZBIRTH[zi];
          nbody[i] = pj >= 0 ? body[pj] : 0;         // a cell born of a body's cell is born into that body
""")
rep("const len = 4 + Math.floor(rng() * 9), at = Math.floor(rng() * (32 - len));\n    const mask = (((1 << len) - 1) << at) >>> 0;",
    "const len = 2 + Math.floor(rng() * 5), at = Math.floor(rng() * (17 - len));   // a run of whole primes\n    const mask = ((((1 << (2 * len)) - 1) << (2 * at))) >>> 0;")

# reset
rep("g = (g & ~(15 << 22)) >>> 0;   // the first organism is sessile; hopping has to evolve\n      pool.push(g); reg(g, null, 'chance');",
    "g = g >>> 0; if (mode === 'organism' || mode === 'life') g = setThermo(g); if (mode === 'organism') g = (g & ~(3 << 16)) >>> 0;   // the first organism is sessile; hopping has to evolve\n      pool.push(g); reg(g, null, 'chance');")
rep("  log(mode === 'blank' ? 'A blank world. Paint some cells.'", "  chemInit();\n  log(mode === 'blank' ? 'A blank world. Paint some cells.'")
rep("'It carries B3/S23 and copies itself, with errors.'", "'It is the compound 375 (3·5³), the rule B3/S23, and it copies itself with errors, using up the molecules it is made of.'")

rep("const ok = ((S(gen[i]) >> n) & 1)", "const ok = ((S(gen[i]) >> (kw < 1 ? kinCount(gen[i], nb, n, kw) : n)) & 1)")

rep("light[i] += ZRG[z] * (1 - light[i]);", "light[i] += ZRG[z] * (ltc[cmap[i]] - light[i]);")

rep("  alive.fill(0); gen.fill(0); light.fill(1);", "  envInit(); alive.fill(0); gen.fill(0); light.fill(1);")

# kinship, brush
rep("const t = TAG(gen[i]) >> 4; const v", "const t = LINE(gen[i]); const v")
rep("let brush = LIFE | (512 << 22);", "let brush = (LIFE | (8 << 28)) >>> 0;")

# render
rep("function render() {\n  const d = img.data;", "function render() {\n  const d = img.data, chOv = chemOverlayPrep(), vm = P.view;")
rep("""      const t = TAG(gen[i]) * 3; let f = (P.showFolds && folded[i]) ? .45 : 1;
      d[p] = TAGRGB[t] * f; d[p + 1] = TAGRGB[t + 1] * f; d[p + 2] = TAGRGB[t + 2] * f;""",
"""      if (vm === 'ir') { const q = irIdx(temp[cmap[i]] + .12); d[p] = IRL[q]; d[p + 1] = IRL[q + 1]; d[p + 2] = IRL[q + 2]; }
      else if (vm === 'strat') { const st = strategyAt(i); d[p] = st === 'spore' ? 255 : st === 'rhizome' ? 40 : 120; d[p + 1] = st === 'spore' ? 140 : st === 'rhizome' ? 200 : 120; d[p + 2] = st === 'spore' ? 20 : st === 'rhizome' ? 255 : 120; }
      else { const t = colorSlot(gen[i]); let f = (P.showFolds && folded[i]) ? .45 : 1;
      d[p] = CV[t] * f; d[p + 1] = CV[t + 1] * f; d[p + 2] = CV[t + 2] * f; }""")
rep("    } else if (P.showLight) { const L = Math.max(0, light[i]); d[p] = 8; d[p + 1] = 14 + 30 * L; d[p + 2] = 20 + 70 * L; }",
"""    } else if (vm === 'ir') { const q = irIdx(temp[cmap[i]]); d[p] = IRL[q] * .85; d[p + 1] = IRL[q + 1] * .85; d[p + 2] = IRL[q + 2] * .85; }
    else if (chOv) { const q = cmap[i] * 3, L = P.showLight ? Math.max(0, light[i]) : 0; d[p] = 8 + .7 * chemRGB[q]; d[p + 1] = 10 + 16 * L + .7 * chemRGB[q + 1]; d[p + 2] = 14 + 40 * L + .7 * chemRGB[q + 2]; }
    else if (P.showLight) { const L = Math.max(0, light[i]); d[p] = 8; d[p + 1] = 14 + 30 * L; d[p + 2] = 20 + 70 * L; }""")
rep("births ${births} · deaths ${deaths} · writes ${writes}", "births ${births} · deaths ${deaths} · blocked by chemistry ${starved}, territory ${walled}, temperature ${heated} · writes ${writes}")

# inspector
rep("is empty. Light ${Math.max(0, light[i]).toFixed(2)}.${lampNote(i)}</div>", "is empty. Light ${Math.max(0, light[i]).toFixed(2)}.${lampNote(i)}</div><div>${chemNote(i)}</div>")
rep("<div>Contagion: ${K(g) ? 'it writes itself into neighbours, strength ' + K(g) + ' of 15' : 'none'}. Tag ${TAG(g)}.</div>", "${compoundHtml(g, i)}")
rep("  panels(pop, distinct);\n", "  panels(pop, distinct); chemPanel();\n")

# controls and panel
rep("'hop', 'hopcost']) {", "'hop', 'hopcost', 'chrate', 'chrich', 'chdiff', 'chrecyc', 'chunit', 'kinw', 'terr', 'front', 'dayLen', 'nightDepth', 'heatDiff', 'heatRelax', 'heatHarm', 'heatLife', 'ventPower', 'heatChaos', 'current', 'qthr', 'qsave', 'sigspread', 'qmut', 'prodRate', 'prodCost', 'predRate', 'predGain']) {")
rep("'bodiesOn']) {", "'bodiesOn', 'chemOn', 'gProd', 'gSex', 'gPred']) {")
rep("  <h2>Over time</h2>", r"""  <h2>Environment</h2>
  <p>Light and heat change in time and space. Choose a world: even light and no heat (the old world), a sunlit pond with day, night and drifting clouds, dark cold sea floor lit and warmed only by vents that pour out molecules, or hot springs on land. Water temperature matters to every cell: each compound has a preferred temperature (the prime 43 raises it), and cells away from it die more often and are born less often. Life also warms the water a little.</p>
  <div class="row"><select id="envsel" aria-label="Environment"><option value="even">Even light, no heat (the old world)</option><option value="pond">Sunlit pond</option><option value="vent">Ocean vents</option><option value="springs">Hot springs</option></select><button id="envnew">New vents and clouds</button></div>
  <div class="row"><select id="viewsel" aria-label="View"><option value="normal">View: normal</option><option value="ir">View: heat vision (infrared)</option><option value="strat">View: spores and rhizomes</option></select></div>
  <label class="sl">Day length (ticks)<input type="range" id="dayLen" min="40" max="2000" step="10" value="400"><output></output></label>
  <label class="sl">Night depth<input type="range" id="nightDepth" min="0" max="0.9" step="0.05" value="0.4"><output></output></label>
  <label class="sl">Vent power<input type="range" id="ventPower" min="0" max="2" step="0.1" value="1"><output></output></label>
  <label class="sl">Heat spread<input type="range" id="heatDiff" min="0" max="0.5" step="0.01" value="0.2"><output></output></label>
  <label class="sl">Heat loss to the surroundings<input type="range" id="heatRelax" min="0.002" max="0.2" step="0.002" value="0.02"><output></output></label>
  <label class="sl">Harm from the wrong temperature<input type="range" id="heatHarm" min="0" max="0.3" step="0.005" value="0.02"><output></output></label>
  <label class="sl">Life warms the water<input type="range" id="heatLife" min="0" max="1" step="0.05" value="0.2"><output></output></label>
  <label class="sl">Chaotic heat<input type="range" id="heatChaos" min="0" max="1" step="0.05" value="0.35"><output></output></label>
  <label class="sl">Water current<input type="range" id="current" min="0" max="2" step="0.05" value="0.5"><output></output></label>
  <p style="color:var(--muted)">Chaotic heat drives the ambient water temperature and every vent's strength from a Lorenz system (deterministic, never repeating), makes vents wander slowly, and sets off sudden eruptions. 0 gives the smooth cycles only.</p>
  <p id="envinfo" style="color:var(--muted)"></p>

  <h2>Chemistry</h2>
  <p>The primes are the world's molecules. Each prime (2, 3, 5, 7 …) is a substance in the ground, rich in some places and poor in others. A cell's code is a <b>compound</b>, a product of primes, so its factorisation is its formula: Conway's Life, "born on 3, survive on 2 or 3", is 3 × 5³ = 375. To be born, a cell has to be built from the molecules at that spot, one for each prime in its compound. When a cell dies its molecules are set free again.</p>
  <div class="row"><label><input type="checkbox" id="chemOn" checked> Chemistry on</label><select id="chshow" aria-label="Show a molecule"></select><button id="chmap">New map</button></div>
  <label class="sl">Molecule supply<input type="range" id="chrate" min="0" max="0.2" step="0.005" value="0.04"><output></output></label>
  <label class="sl">Richness of the ground<input type="range" id="chrich" min="4" max="120" step="1" value="45"><output></output></label>
  <label class="sl">Spread of molecules<input type="range" id="chdiff" min="0" max="0.5" step="0.01" value="0.15"><output></output></label>
  <label class="sl">Returned by the dead<input type="range" id="chrecyc" min="0" max="1" step="0.05" value="0.7"><output></output></label>
  <label class="sl">Molecules per exponent<input type="range" id="chunit" min="0.25" max="4" step="0.25" value="1"><output></output></label>
  <p style="margin-bottom:2px"><b>Defence against invaders.</b> A cell counts neighbours of its own lineage in full and strangers at a fraction; a lineage marks the ground it fills, so foreign births are less likely there; and births into open ground cost more molecules.</p>
  <label class="sl">Strangers count as<input type="range" id="kinw" min="0" max="1" step="0.05" value="1"><output></output></label>
  <label class="sl">Territory<input type="range" id="terr" min="0" max="1" step="0.05" value="0.3"><output></output></label>
  <label class="sl">Open-ground birth cost<input type="range" id="front" min="0" max="3" step="0.25" value="0.5"><output></output></label>
  <div class="row"><button class="resetRules" title="Put every rate, cost and chemistry setting back to its starting value">Reset rules</button></div>
  <div class="card" id="chpanel"></div>
  <details><summary>What each prime does</summary><div id="chroles" class="card"></div></details>

  <h2>Over time</h2>""")

rep("""Every living cell carries a short code, and the code is its rule: when it survives, when it gives birth, and how
  hard it writes itself into its neighbours. Newborns copy a parent's code, with errors.""", """Every living cell carries a compound, a product of primes, and its factorisation is its rule: when it survives, when it gives birth,
  whether it moves, how hard it writes itself into its neighbours. Newborns copy a parent's compound, with errors, and are built from the molecules in the ground.""")

# ------------------------------------------------------------------ the extended genome and the quorum gene
rep("let gen = new Uint32Array(N), ngen = new Uint32Array(N);\n", "let gen = new Uint32Array(N), ngen = new Uint32Array(N);\nlet xg = new Uint16Array(N), nxg = new Uint16Array(N);       // the extended genome: genes beyond the 16 primes. Bits 0-1: quorum response (the prime 59)\n")
rep("  envInit(); alive.fill(0); gen.fill(0); light.fill(1);", "  envInit(); alive.fill(0); gen.fill(0); xg.fill(0); nxg.fill(0); light.fill(1);")
rep("      gen[i] = pool[k];\n", "      gen[i] = pool[k]; xg[i] = P.qseed | P.xseed;\n")
rep("alive[i] = 1; gen[i] = brush; body[i] = 0;", "alive[i] = 1; gen[i] = brush; xg[i] = 0; body[i] = 0;")
rep("light[i] -= ZCOST[z] * EFFT[(gen[i] >>> 20) & 3];", "{ let cst = ZCOST[z] * EFFT[(gen[i] >>> 20) & 3]; const xs = xg[i]; if (xs) { const xe = xs & 3; cst *= (1 + .03 * (xe + ((xs >> 2) & 3) + ((xs >> 4) & 3) + ((xs >> 6) & 3))) * (xe && sig[cmap[i]] >= P.qthr ? 1 - P.qsave * xe : 1); } light[i] -= cst; }")
rep("nalive[i] = alive[i]; ngen[i] = gen[i]; nbody[i] = body[i]; folded[i] = 1;", "nalive[i] = alive[i]; ngen[i] = gen[i]; nxg[i] = xg[i]; nbody[i] = body[i]; folded[i] = 1;")
rep("nalive[i] = ok ? 1 : 0; ngen[i] = ok ? gen[i] : 0; nbody[i] = ok ? body[i] : 0;", "nalive[i] = ok ? 1 : 0; ngen[i] = ok ? gen[i] : 0; nxg[i] = xg[i]; nbody[i] = ok ? body[i] : 0;")
rep("if (alive[j] && ((B(gen[j]) >> n) & 1) && (!fl || light[j] >= ZBIRTH[zi])) {", "if (alive[j] && ((B(gen[j]) >> n) & 1) && (!(xg[j] & 3) || n > (xg[j] & 3) || sig[cmap[i]] < P.qthr) && (!fl || light[j] >= ZBIRTH[zi])) {")
rep("let pj = -1; for (let k = 0; k < c; k++) if (cand[k] === parent) { pj = candI[k]; break; }",
    "let pj = -1; for (let k = 0; k < c; k++) if (cand[k] === parent) { pj = candI[k]; break; }\n          let cx = pj >= 0 ? xg[pj] : 0;\n          if (P.qmut > 0 && rng() < ZMU[zi] * P.qmut * XSLOTS.length) { const sh = 2 * XSLOTS[(rng() * XSLOTS.length) | 0], e0 = (cx >> sh) & 3, e1 = e0 === 0 ? 1 : e0 === 3 ? 2 : (rng() < .5 ? e0 - 1 : e0 + 1); cx = (cx & ~(3 << sh)) | (e1 << sh); }")
rep("nalive[i] = 1; ngen[i] = g; nchanged[i] = 1; births++;", "nalive[i] = 1; ngen[i] = g; nxg[i] = cx; nchanged[i] = 1; births++;")
rep("[gen, ngen] = [ngen, gen];", "[gen, ngen] = [ngen, gen]; [xg, nxg] = [nxg, xg];")
rep("  <h2>Over time</h2>", r"""  <h2>Signalling</h2>
  <p>Living cells give off a signal into the ground. It spreads a little and fades, so every place holds a smoothed measure of how crowded it is. The <b>quorum gene</b> (the prime 59) lets a cell read it: where the signal is at or above the quorum level, the cell stops giving birth into squares with few neighbours (a spore turns into a creeper) and spends less light. One cell can therefore act as an explorer at the edge and a settler inside the crowd. The gene starts absent and appears by mutation. Show the signal from the molecule menu.</p>
  <label class="sl">Quorum level<input type="range" id="qthr" min="0.05" max="1" step="0.05" value="0.35"><output></output></label>
  <label class="sl">Light saved when settled<input type="range" id="qsave" min="0" max="0.3" step="0.01" value="0.15"><output></output></label>
  <label class="sl">Signal spread<input type="range" id="sigspread" min="0" max="0.24" step="0.01" value="0.2"><output></output></label>
  <label class="sl">Quorum gene mutation<input type="range" id="qmut" min="0" max="3" step="0.25" value="1"><output></output></label>
  <h2>Over time</h2>""")


# ------------------------------------------------------------------ highlight a clicked form
rep("    // the light brush\n", "  drawSel(ox, oy, s);\n    // the light brush\n")
rep("function inspect(x, y) { inspectCore(x, y); mirrorInsp(); }", "function inspect(x, y) { selectForm(idx(x, y)); inspectCore(x, y); mirrorInsp(); }")
rep("It is part of a <b>${f.name}</b>, a lifted form of ${f.size} cells.` : 'It is not part of a named form.'}", "It is part of a <b>${f.name}</b>, a lifted form of ${f.size} cells (outlined in gold).` : (sel ? 'It is part of a small cluster, outlined in gold; it has no name yet.' : 'It is not part of a named form.')}")


# ------------------------------------------------------------------ producers, recombination, predators
rep("          let mixed = false;\n", "          let mixed = false; let sx = 0; for (let k = 0; k < c; k++) { const e = (xg[candI[k]] >> 4) & 3; if (e > sx) sx = e; }\n")
rep("if (mixed && rng() < ZFU[zi]) {", "if (mixed && rng() < ZFU[zi] * (1 + 1.5 * sx)) {")
rep("births = deaths = foldedCount = writes = starved = walled = heated = 0;", "births = deaths = foldedCount = writes = starved = walled = heated = eaten = 0;")
rep("  [alive, nalive] = [nalive, alive]; [gen, ngen]", """  // predation: a predator eats a neighbour of another lineage, taking its light and setting its molecules free
  if (P.gPred || P.xseed & 192) for (let i = 0; i < N; i++) {
    if (!nalive[i]) continue; const de = (nxg[i] >> 6) & 3; if (!de) continue;
    const x = i % W, y = (i / W) | 0, dx = ((rng() * 3) | 0) - 1, dy = ((rng() * 3) | 0) - 1; if (!dx && !dy) continue;
    const j = ((y + dy + H) % H) * W + ((x + dx + W) % W);
    if (!nalive[j] || (ngen[j] >>> 28) === (ngen[i] >>> 28) || rng() >= P.predRate * de) continue;
    if (chemOn) releaseChem(cmap[j] << 4, ngen[j]);
    nalive[j] = 0; ngen[j] = 0; nbody[j] = 0; nchanged[j] = 1; nchanged[i] = 1; deaths++; eaten++;
    if (fl) light[i] = Math.min(2, light[i] + P.predGain);
  }
  [alive, nalive] = [nalive, alive]; [gen, ngen]""")
rep("blocked by chemistry ${starved}, territory ${walled}, temperature ${heated}", "blocked by chemistry ${starved}, territory ${walled}, temperature ${heated}${eaten ? ', eaten ' + eaten : ''}")
rep("  <h2>Over time</h2>", r"""  <h2>Roles, sex and predation</h2>
  <p>Three more genes in the extended genome. Like the quorum gene they start absent and appear by mutation; each strength 1 to 3 costs a little light to carry.</p>
  <div class="row"><label><input type="checkbox" id="gProd" checked> Producers (61)</label><label><input type="checkbox" id="gSex" checked> Recombination (67)</label><label><input type="checkbox" id="gPred"> Predators (71)</label></div>
  <p style="color:var(--muted)"><b>Producers</b> (a division of labour): in a crowd, a producer secretes the molecules of its own compound into the ground and pays for it in light. The crowd's builders are fed by it, so it is a gift to whoever lives nearby, kin or not.<br><b>Recombination</b> raises the chance that two different parents mix their codes. <b>Predators</b> eat a neighbour of another lineage, gaining its light and freeing its molecules.</p>
  <label class="sl">Producer output<input type="range" id="prodRate" min="0" max="1" step="0.05" value="0.3"><output></output></label>
  <label class="sl">Producer light cost<input type="range" id="prodCost" min="0" max="0.1" step="0.005" value="0.03"><output></output></label>
  <label class="sl">Predator bite chance<input type="range" id="predRate" min="0" max="0.5" step="0.01" value="0.1"><output></output></label>
  <label class="sl">Light gained per bite<input type="range" id="predGain" min="0" max="1" step="0.05" value="0.4"><output></output></label>
  <h2>Over time</h2>""")


# ------------------------------------------------------------------ stage 1: the energy reserve (storage gene, prime 73)
rep("let xg = new Uint16Array(N), nxg = new Uint16Array(N);", "let rsv = new Float32Array(N), nrsv = new Float32Array(N);      // the energy reserve a cell carries: light banked against a dark spell\nlet xg = new Uint16Array(N), nxg = new Uint16Array(N);")
rep("xg.fill(0); nxg.fill(0);", "xg.fill(0); nxg.fill(0); rsv.fill(0); nrsv.fill(0);")
rep("alive[i] = 1; gen[i] = brush; xg[i] = 0; body[i] = 0;", "alive[i] = 1; gen[i] = brush; xg[i] = 0; rsv[i] = 0; body[i] = 0;")
rep("((xs >> 4) & 3) + ((xs >> 6) & 3))) *", "((xs >> 4) & 3) + ((xs >> 6) & 3) + ((xs >> 8) & 3))) *")
rep("light[i] -= cst; } if (light[i] < 0) light[i] = -1e-6; } }",
    """light[i] -= cst; }
      // the reserve: a shortfall is paid from it, a surplus is banked in it, and it leaks a little each tick
      const re = (xg[i] >> 8) & 3, cap = P.rbase + P.rcap * re;
      if (cap > 0 || rsv[i] > 0) {
        let r = rsv[i];
        if (light[i] < 0) { const use = Math.min(-light[i], r); r -= use; light[i] += use; }
        else if (light[i] > P.rthr && r < cap) { const put = Math.min((cap - r) / P.rconv, P.rfill * (light[i] - P.rthr)); r += put * P.rconv; light[i] -= put; }
        r *= 1 - P.rleak; rsv[i] = r > cap ? cap : r;
      }
      if (light[i] < 0) light[i] = -1e-6; } }""")
rep("nxg[i] = xg[i]; nbody[i] = body[i]; folded[i] = 1;", "nxg[i] = xg[i]; nrsv[i] = rsv[i]; nbody[i] = body[i]; folded[i] = 1;")
rep("nxg[i] = xg[i]; nbody[i] = ok ? body[i] : 0;", "nxg[i] = xg[i]; nrsv[i] = ok ? rsv[i] : 0; nbody[i] = ok ? body[i] : 0;")
rep("ngen[i] = g; nxg[i] = cx; nchanged[i] = 1; births++;", "ngen[i] = g; nxg[i] = cx; nrsv[i] = 0; nchanged[i] = 1; births++;")
rep("[xg, nxg] = [nxg, xg];", "[xg, nxg] = [nxg, xg]; [rsv, nrsv] = [nrsv, rsv];")
rep("gPred:false, prodRate:.3,", "gPred:false, gStore:false, rbase:0, rcap:.5, rfill:.06, rthr:.75, rleak:.01, rconv:4, prodRate:.3,")
rep("'prodRate', 'prodCost', 'predRate', 'predGain']) {", "'prodRate', 'prodCost', 'predRate', 'predGain', 'rcap', 'rfill', 'rthr', 'rleak']) {")
rep("'chemOn', 'gProd', 'gSex', 'gPred']) {", "'chemOn', 'gProd', 'gSex', 'gPred', 'gStore']) {")
rep("  <h2>Over time</h2>", r"""  <h2>Energy reserve</h2>
  <p>A cell can bank light it does not need. The <b>storage gene</b> (the prime 73, strength 1 to 3) sets how much it can hold. A cell in the dark, or in a crowd with no light to spare, draws on its reserve before it starves. The reserve leaks a little every tick, so hoarding is not free, and the gene adds to the cost of carrying genes. Children are born with none.</p>
  <div class="row"><label><input type="checkbox" id="gStore"> Storage gene (73)</label></div>
  <label class="sl">Capacity per strength<input type="range" id="rcap" min="0" max="1.5" step="0.05" value="0.5"><output></output></label>
  <label class="sl">Banking rate<input type="range" id="rfill" min="0" max="0.3" step="0.01" value="0.06"><output></output></label>
  <label class="sl">Bank above light<input type="range" id="rthr" min="0.2" max="1" step="0.05" value="0.75"><output></output></label>
  <label class="sl">Leak per tick<input type="range" id="rleak" min="0" max="0.05" step="0.005" value="0.01"><output></output></label>
  <h2>Over time</h2>""")


# ------------------------------------------------------------------ stage 3: the energy molecule and the heterotroph gene (prime 79)
rep("fieldStep(); sigStep(); xslots(); produce(); }", "fieldStep(); sigStep(); energyStep(); xslots(); produce(); }")
rep("((xs >> 6) & 3) + ((xs >> 8) & 3))) *", "((xs >> 6) & 3) + ((xs >> 8) & 3) + ((xs >> 10) & 3))) *")
rep("      if (light[i] < 0) light[i] = -1e-6; } }", """      if (light[i] < 0) { const he = (xg[i] >> 10) & 3; if (he) {          // a heterotroph covers a shortfall from the energy molecule in the water
          const sq = cmap[i], take = Math.min(en[sq], .1 * he, -light[i] / P.eeff); if (take > 0) { en[sq] -= take; light[i] += take * P.eeff; enTaken += take; enGot += take * P.eeff; } } }
      if (light[i] < 0) light[i] = -1e-6; } }""")
rep("gStore:false, rbase:0,", "gStore:false, gHet:true, eleak:.01, ebody:.2, eeff:.4, edecay:.02, rbase:0,")
rep("'rcap', 'rfill', 'rthr', 'rleak']) {", "'rcap', 'rfill', 'rthr', 'rleak', 'eleak', 'ebody', 'eeff']) {")
rep("'gPred', 'gStore']) {", "'gPred', 'gStore', 'gHet']) {")
rep("  <h2>Over time</h2>", r"""  <h2>Energy molecule</h2>
  <p>Living cells leak a little energy into the water and dead cells set free what they held. It spreads, rides the current, and slowly decays. A <b>heterotroph gene</b> (the prime 79, strength 1 to 3) lets a cell that has run short of light take the energy up from the water instead, but it keeps only part of what it takes; the rest is lost, which is why each step along a food chain passes on less. Show it with <i>Show: energy molecule</i>.</p>
  <div class="row"><label><input type="checkbox" id="gHet" checked> Heterotroph gene (79)</label></div>
  <label class="sl">Leak per living cell<input type="range" id="eleak" min="0" max="0.05" step="0.005" value="0.01"><output></output></label>
  <label class="sl">Released at death<input type="range" id="ebody" min="0" max="0.6" step="0.05" value="0.2"><output></output></label>
  <label class="sl">Kept when absorbed<input type="range" id="eeff" min="0.05" max="1" step="0.05" value="0.4"><output></output></label>
  <h2>Over time</h2>""")


# ------------------------------------------------------------------ stage 4: graded predation, decomposers, births on the energy molecule
rep("    if (!nalive[i]) continue; const de = (nxg[i] >> 6) & 3; if (!de) continue;", "    if (!nalive[i]) continue; const de = (nxg[i] >> 6) & 3, hx = (nxg[i] >> 10) & 3; if (!de || !hx) continue;     // a predator is a heterotroph that bites")
rep("    if (fl) light[i] = Math.min(2, light[i] + P.predGain);", "    { const sq = cmap[j], take = Math.min(en[sq], P.ebody); en[sq] -= take; enTaken += take; const gain = take * P.predGain; enGot += gain; if (fl) light[i] = Math.min(2, light[i] + gain); }")
rep("} else if (n > 0 && (!fl || light[i] >= ZCOST[zi])) {", "} else if (n > 0 && (!fl || light[i] >= ZCOST[zi] || en[cmap[i]] * P.eeff >= ZCOST[zi])) {")
rep("(!fl || light[j] >= ZBIRTH[zi])", "(!fl || ((light[i] >= ZCOST[zi] || ((xg[j] >> 10) & 3)) && (light[j] >= ZBIRTH[zi] || (((xg[j] >> 10) & 3) && en[cmap[i]] * P.eeff >= ZBIRTH[zi]))))")
rep("if (fl && pj >= 0) light[pj] -= ZBIRTH[zi];", "if (fl && pj >= 0) { if (light[pj] >= ZBIRTH[zi]) light[pj] -= ZBIRTH[zi]; else { const sq = cmap[i], tk = Math.min(en[sq], ZBIRTH[zi] / P.eeff); en[sq] -= tk; enTaken += tk; enGot += tk * P.eeff; } }")
rep("Light gained per bite", "Share of prey energy kept")


# ------------------------------------------------------------------ stage 5: the adhesion gene (prime 83) and bodies that form from it
rep("if (P.bodiesOn && bodies.size) poolLight();", "if ((P.bodiesOn || P.gAdh) && bodies.size) poolLight();")
rep("  if (!P.bodiesOn) return;", "  if (!P.bodiesOn && !P.gAdh) return;")
rep("  if (P.bodiesOn && bodies.size) {", "  if ((P.bodiesOn || P.gAdh) && bodies.size) {")
rep("if (ts / comp.length < .6 || rng() >= P.nucleate) continue;", "let ma = 0; for (const i of comp) ma += (xg[i] >> 12) & 3; ma /= comp.length;     // how strongly its cells stick together\n    if (ts / comp.length < .6 || rng() >= (P.gAdh ? P.nucleate * ma : P.nucleate)) continue;")
rep("((xs >> 8) & 3) + ((xs >> 10) & 3))) *", "((xs >> 8) & 3) + ((xs >> 10) & 3) + ((xs >> 12) & 3))) *")
rep("gStore:false, gHet:true,", "gStore:false, gHet:true, gAdh:false,")
rep("'rleak', 'eleak', 'ebody', 'eeff']) {", "'rleak', 'eleak', 'ebody', 'eeff']) {")
rep("'gStore', 'gHet']) {", "'gStore', 'gHet', 'gAdh']) {")
rep("  <h2>Over time</h2>", r"""  <h2>Sticking together</h2>
  <p>The <b>adhesion gene</b> (the prime 83, strength 1 to 3) makes the cells of a lineage cling. A free form whose cells carry it can become a body, and the stronger the gene, the likelier. A cell born beside a body's cell is born into that body, so a clump that sticks goes on as one unit, pooling light inside. Carrying the gene costs a little light. With the gene on, bodies form only from it; the Bodies box above keeps the older chance-based forming.</p>
  <div class="row"><label><input type="checkbox" id="gAdh"> Adhesion gene (83)</label></div>
  <h2>Over time</h2>""")


# ------------------------------------------------------------------ stage 6: reactions (photosynthesis, respiration, fermentation, water)
rep("energyStep(); xslots();", "energyStep(); rxnStep(); xslots();")
rep("const sq = cmap[i], take = Math.min(en[sq], .1 * he, -light[i] / P.eeff); if (take > 0) { en[sq] -= take; light[i] += take * P.eeff; enTaken += take; enGot += take * P.eeff; }", "light[i] += burn(cmap[i], -light[i], .1 * he, P.eeff);")
rep("{ const sq = cmap[j], take = Math.min(en[sq], P.ebody); en[sq] -= take; enTaken += take; const gain = take * P.predGain; enGot += gain; if (fl) light[i] = Math.min(2, light[i] + gain); }", "{ const gain = burn(cmap[j], 1e9, P.ebody, P.predGain); if (fl) light[i] = Math.min(2, light[i] + gain); }")
rep("!(envOn && rng() < hh * (1 - thermFit(gen[i], temp[cmap[i]])));", "!(envOn && rng() < hh * (1 - thermFit(gen[i], temp[cmap[i]]))) && !(P.rxn && dryKill(i, n));")
rep("          if (chemOn && !payChem(cmap[i] << 4, g, 1 + fr * (8 - n) / 7))", "          if (P.rxn && fl && pj >= 0 && (wat[cmap[i]] < P.wcell || (light[pj] >= ZBIRTH[zi] && co2[cmap[i]] < ZBIRTH[zi]))) { nalive[i] = 0; ngen[i] = 0; nbody[i] = 0; nchanged[i] = 1; starved++; carbonless++; continue; }\n          if (chemOn && !payChem(cmap[i] << 4, g, 1 + fr * (8 - n) / 7))")
rep("if (fl && pj >= 0) { if (light[pj] >= ZBIRTH[zi]) light[pj] -= ZBIRTH[zi]; else { const sq = cmap[i], tk = Math.min(en[sq], ZBIRTH[zi] / P.eeff); en[sq] -= tk; enTaken += tk; enGot += tk * P.eeff; } }",
    "if (fl && pj >= 0) { const sq = cmap[i]; if (light[pj] >= ZBIRTH[zi]) { light[pj] -= ZBIRTH[zi]; if (P.rxn) { co2[sq] -= ZBIRTH[zi]; o2[sq] += ZBIRTH[zi]; wat[sq] -= ZBIRTH[zi] * P.wfix; } }   // a child's body is carbon fixed from CO2, giving off O2\n            else { burn(sq, ZBIRTH[zi], 1e9, P.eeff); if (P.rxn) co2[sq] = Math.max(0, co2[sq] - ZBIRTH[zi]); }\n            if (P.rxn) wat[sq] -= P.wcell; }")
rep("births = deaths = foldedCount = writes = starved = walled = heated = eaten = 0;", "births = deaths = foldedCount = writes = starved = walled = heated = eaten = 0; dried = carbonless = 0;")
rep("${eaten ? ', eaten ' + eaten : ''}", "${eaten ? ', eaten ' + eaten : ''}${P.rxn ? ', no carbon or water ' + carbonless + ', dried ' + dried : ''}")
rep("gHet:true, gAdh:false,", "gHet:true, gAdh:false, rxn:false, co2air:4, gasx:.01, vco2:.05, o2sink:.002, ferm:.3, evap:.02, rain:.005, wrain:2, wcell:.05, wfix:.2, wdry:.5, dryHarm:.02,")
rep("'rleak', 'eleak', 'ebody', 'eeff']) {", "'rleak', 'eleak', 'ebody', 'eeff', 'co2air', 'gasx', 'ferm', 'evap', 'rain', 'dryHarm']) {")
rep("'gStore', 'gHet', 'gAdh']) {", "'gStore', 'gHet', 'gAdh', 'rxn']) {")
rep("  <h2>Over time</h2>", r"""  <h2>Reactions</h2>
  <p>Switch on real reactions in place of the bare energy bookkeeping. The water holds <b>carbon dioxide</b>, <b>oxygen</b> and <b>water</b> itself, and the energy molecule becomes <b>sugar</b>. When a cell builds a child or leaks sugar it fixes carbon: CO₂ + water + light → sugar + O₂. A heterotroph, a predator or rot burns sugar: with oxygen, sugar + O₂ → CO₂ + water at full yield; without it, it ferments, sugar → CO₂, at a lower yield. The world starts with no oxygen, so the first consumers ferment. Every child takes a little water and every death gives it back; water also carries the molecules, so dry ground slows them. Heat dries the water and rain refills it; a cell in dry ground may dry out and die, cells at an edge sooner, and a body shelters its cells. Vents breathe out CO₂. Show each with the <i>Show</i> menu.</p>
  <div class="row"><label><input type="checkbox" id="rxn"> Reactions</label></div>
  <label class="sl">CO₂ in the air<input type="range" id="co2air" min="0" max="10" step="0.5" value="4"><output></output></label>
  <label class="sl">Exchange with the air<input type="range" id="gasx" min="0" max="0.05" step="0.0025" value="0.01"><output></output></label>
  <label class="sl">Fermenting yield<input type="range" id="ferm" min="0" max="1" step="0.05" value="0.3"><output></output></label>
  <label class="sl">Evaporation<input type="range" id="evap" min="0" max="0.1" step="0.005" value="0.02"><output></output></label>
  <label class="sl">Rain<input type="range" id="rain" min="0" max="0.05" step="0.0025" value="0.005"><output></output></label>
  <label class="sl">Drying harm<input type="range" id="dryHarm" min="0" max="0.2" step="0.005" value="0.02"><output></output></label>
  <h2>Over time</h2>""")


# ------------------------------------------------------------------ drying that bites (seasons) and stage 7: the current carries loose cells
rep("  hopPass();\n", "  hopPass(); driftPass();\n")
rep("rxn:false, co2air:4,", "drift:.3, seasonLen:1500, drySeason:.7, rxn:false, co2air:4,")
rep("evap:.02, rain:.005,", "evap:.03, rain:.005,")
rep('id="evap" min="0" max="0.1" step="0.005" value="0.02"', 'id="evap" min="0" max="0.1" step="0.005" value="0.03"')
rep('  <label class="sl">Drying harm<input', '  <label class="sl">Season length<input type="range" id="seasonLen" min="0" max="5000" step="100" value="1500"><output></output></label>\n  <label class="sl">Dry season<input type="range" id="drySeason" min="0" max="1" step="0.05" value="0.7"><output></output></label>\n  <label class="sl">Drying harm<input')
rep('<label class="sl">Water current<input type="range" id="current" min="0" max="2" step="0.05" value="0.5"><output></output></label>', '<label class="sl">Water current<input type="range" id="current" min="0" max="2" step="0.05" value="0.5"><output></output></label>\n  <label class="sl">Current carries loose cells<input type="range" id="drift" min="0" max="2" step="0.05" value="0.3"><output></output></label>')
rep("'gasx', 'ferm', 'evap', 'rain', 'dryHarm']) {", "'gasx', 'ferm', 'evap', 'rain', 'dryHarm', 'seasonLen', 'drySeason', 'drift']) {")
rep("${P.rxn ? ', no carbon or water ' + carbonless + ', dried ' + dried : ''}", "${P.rxn ? ', no carbon or water ' + carbonless + ', dried ' + dried + (P.env !== 'even' && P.seasonLen > 0 ? (rxSeason < .5 ? ' · dry season' : ' · wet season') : '') : ''}${drifted ? ' · drifting ' + drifted : ''}")


# ------------------------------------------------------------------ tidy: the old chance-made bodies and the light reserve are gone; adhesion and predators are on
rep('   <label><input type="checkbox" id="bodiesOn"> Bodies</label></div>', '</div>')
rep('  bodiesOn:false, nucleate:0.03,', '  nucleate:0.03,')
rep('if ((P.bodiesOn || P.gAdh) && bodies.size) poolLight();', 'if (P.gAdh && bodies.size) poolLight();')
rep('  if (!P.bodiesOn && !P.gAdh) return;', '  if (!P.gAdh) return;')
rep('  if ((P.bodiesOn || P.gAdh) && bodies.size) {', '  if (P.gAdh && bodies.size) {')
rep('rng() >= (P.gAdh ? P.nucleate * ma : P.nucleate)', 'rng() >= P.nucleate * ma')
rep("'showForms', 'bodiesOn', 'chemOn', 'gProd', 'gSex', 'gPred', 'gStore', 'gHet', 'gAdh', 'rxn']", "'showForms', 'chemOn', 'gProd', 'gSex', 'gPred', 'gHet', 'gAdh', 'rxn']")
rep(", 'rcap', 'rfill', 'rthr', 'rleak', 'eleak',", ", 'eleak',")
rep('  <h2>Energy reserve</h2>\n  <p>A cell can bank light it does not need. The <b>storage gene</b> (the prime 73, strength 1 to 3) sets how much it can hold. A cell in the dark, or in a crowd with no light to spare, draws on its reserve before it starves. The reserve leaks a little every tick, so hoarding is not free, and the gene adds to the cost of carrying genes. Children are born with none.</p>\n  <div class="row"><label><input type="checkbox" id="gStore"> Storage gene (73)</label></div>\n  <label class="sl">Capacity per strength<input type="range" id="rcap" min="0" max="1.5" step="0.05" value="0.5"><output></output></label>\n  <label class="sl">Banking rate<input type="range" id="rfill" min="0" max="0.3" step="0.01" value="0.06"><output></output></label>\n  <label class="sl">Bank above light<input type="range" id="rthr" min="0.2" max="1" step="0.05" value="0.75"><output></output></label>\n  <label class="sl">Leak per tick<input type="range" id="rleak" min="0" max="0.05" step="0.005" value="0.01"><output></output></label>\n', '')
rep('gPred:false, gStore:false, gHet:true, gAdh:false,', 'gPred:true, gHet:true, gAdh:true,')
rep('<input type="checkbox" id="gPred">', '<input type="checkbox" id="gPred" checked>')
rep('<input type="checkbox" id="gAdh">', '<input type="checkbox" id="gAdh" checked>')
rep('With the gene on, bodies form only from it; the Bodies box above keeps the older chance-based forming.', 'How readily bodies form, and what they cost to keep, are set by Bodies forming and Body upkeep above.')

rep("rxn:false, co2air:4,", "rxn:true, co2air:4,")
rep('<input type="checkbox" id="rxn">', '<input type="checkbox" id="rxn" checked>')

rep("  if (P.gAdh && bodies.size) {", "  if (P.showBodies && bodies.size) {")
rep("showLight:true, showFolds:false, showForms:false,", "showLight:true, showFolds:false, showForms:false, showBodies:false,")
rep('<div class="topbtns fade"><button id="btnMenu"', '<div class="topbtns fade"><button id="btnBodies" title="Outline the clumps">Show clumps</button><button id="btnMenu"')
rep("How readily bodies form, and what they cost to keep, are set by Bodies forming and Body upkeep above.", "The cells of a body are held in a shared slime, so a gap of a cell or two does not split it. How readily bodies form, and what they cost to keep, are set by Bodies forming and Body upkeep above. Outline them with Show bodies at the top of the world.")

rep("    light[i] = (1 - sh) * light[i] + sh * s[0] / s[1] - (P.floor ? P.bodyCost : 0);\n  }\n}", """    light[i] = (1 - sh) * light[i] + sh * s[0] / s[1] - (P.floor ? P.bodyCost : 0);
  }
  // a clump also shares the sugar and water in the ground it covers: rich parts feed poor ones, and nothing is lost
  if (P.clumpShare > 0 && (tick & 1) === 0) {
    const sq = new Map();
    for (let i = 0; i < N; i++) { const b = body[i]; if (!b || !alive[i]) continue; let m = sq.get(b); if (!m) sq.set(b, m = new Set()); m.add(cmap[i]); }
    for (const [b, m] of sq) {
      if (m.size < 2) continue; const bo = bodies.get(b); if (!bo) continue; const f = P.clumpShare * (.3 + .7 * BS(bo.code));
      let se = 0, sw = 0; for (const c of m) { se += en[c]; if (P.rxn) sw += wat[c]; } se /= m.size; sw /= m.size;
      for (const c of m) { en[c] += f * (se - en[c]); if (P.rxn) wat[c] += f * (sw - wat[c]); }
    }
  }
}""")
rep("nucleate:0.03,", "nucleate:0.03, clumpShare:.5,")
rep('  <label class="sl">Body upkeep<input', '  <label class="sl">Body sharing<input type="range" id="clumpShare" min="0" max="1" step="0.05" value="0.5"><output></output></label>\n  <label class="sl">Body upkeep<input')
rep("'seasonLen', 'drySeason', 'drift']) {", "'seasonLen', 'drySeason', 'drift', 'clumpShare']) {")

rep("const ok = ((S(gen[i]) >> (kw < 1 ? kinCount(gen[i], nb, n, kw) : n)) & 1)", "const ok = (((S(gen[i]) >> (kw < 1 ? kinCount(gen[i], nb, n, kw) : n)) & 1) || (body[i] && rng() < P.clumpHold))")
rep("nucleate:0.03, clumpShare:.5,", "nucleate:0.03, clumpShare:.5, clumpHold:.5,")
rep('  <label class="sl">Body upkeep<input', '  <label class="sl">Slime holds cells<input type="range" id="clumpHold" min="0" max="1" step="0.05" value="0.5"><output></output></label>\n  <label class="sl">Body upkeep<input')
rep("'drift', 'clumpShare']) {", "'drift', 'clumpShare', 'clumpHold']) {")

rep("o2sink:.002,", "o2sink:.0005, bury:.02, feStart:1.5,")
rep("bodies: bodies.size, inBodies: pop ? Math.round(100 * inBodies / pop) : 0});", "bodies: bodies.size, inBodies: pop ? Math.round(100 * inBodies / pop) : 0, o2: P.rxn ? +(o2.reduce((a, b) => a + b, 0) / o2.length).toFixed(2) : 0});")
rep("['folded', 'Folded (%)']];", "['folded', 'Folded (%)'], ['o2', 'Oxygen (a square)']];")
rep("Vents breathe out CO₂. Show each", "Vents breathe out CO₂. A little sugar is buried in the mud for good, leaving its oxygen behind; iron in the ground rusts and soaks oxygen up until it runs out, so oxygen can rise only slowly, as it did on the early Earth. Show each")

rep("document.getElementById('hud').textContent = `tick", "hudSet(`tick")
rep("· zoom ${s.toFixed(1)}`;", "· zoom ${s.toFixed(1)}`, s);")
rep('<div class="topbtns fade"><button id="btnBodies"', '<div class="topbtns fade"><select id="topview" aria-label="View" title="What to show"></select><button id="btnBodies"')
rep('  <div class="row"><select id="viewsel" aria-label="View">', '  <div class="row" style="display:none"><select id="viewsel" aria-label="View">')
rep('<select id="chshow" aria-label="Show a molecule"></select>', '<select id="chshow" aria-label="Show a molecule" style="display:none"></select>')
rep('   <label><input type="checkbox" id="showFolds"> Show folds</label>', '   <label style="display:none"><input type="checkbox" id="showFolds"> Show folds</label>')
rep(".hud{max-width:calc(100% - 230px)}", ".hud{max-width:calc(100% - 540px)}")
rep("heatChaos:.35, current:.5,", "heatChaos:.35, current:.25, plumeW:.35, crossflow:1, convect:.06, visc:.04, eddies:.2, fdrag:.03,")
rep('<label class="sl">Water current<input type="range" id="current" min="0" max="2" step="0.05" value="0.5"><output></output></label>', '<label class="sl">Water current<input type="range" id="current" min="0" max="2" step="0.05" value="0.5"><output></output></label>\n  <label class="sl">Convection<input type="range" id="convect" min="0" max="0.5" step="0.01" value="0.06"><output></output></label>\n  <label class="sl">Eddies<input type="range" id="eddies" min="0" max="0.6" step="0.01" value="0.2"><output></output></label>')
rep("'drift', 'clumpShare', 'clumpHold']) {", "'drift', 'clumpShare', 'clumpHold', 'convect', 'eddies']) {")

rep('id="current" min="0" max="2" step="0.05" value="0.5"', 'id="current" min="0" max="2" step="0.05" value="0.25"')


# ------------------------------------------------------------------ spores as a state: the spore-forming gene (prime 89)
rep("let rsv = new Float32Array(N), nrsv = new Float32Array(N);", "let rsv = new Float32Array(N), nrsv = new Float32Array(N);\nlet dor = new Uint8Array(N), ndor = new Uint8Array(N);      // a spore: a dormant cell")
rep("xg.fill(0); nxg.fill(0); rsv.fill(0); nrsv.fill(0);", "xg.fill(0); nxg.fill(0); rsv.fill(0); nrsv.fill(0); dor.fill(0); ndor.fill(0);")
rep("xg[i] = 0; rsv[i] = 0;", "xg[i] = 0; rsv[i] = 0; dor[i] = 0;")
rep("nrsv[i] = rsv[i]; nbody[i] = body[i]; folded[i] = 1;", "nrsv[i] = rsv[i]; ndor[i] = dor[i]; nbody[i] = body[i]; folded[i] = 1;")
rep("nrsv[i] = ok ? rsv[i] : 0;", "nrsv[i] = ok ? rsv[i] : 0; ndor[i] = ok ? dor[i] : 0;")
rep("ngen[i] = g; nxg[i] = cx; nrsv[i] = 0; nchanged[i] = 1; births++;", "ngen[i] = g; nxg[i] = cx; nrsv[i] = 0; ndor[i] = 0; nchanged[i] = 1; births++;")
rep("[rsv, nrsv] = [nrsv, rsv];", "[rsv, nrsv] = [nrsv, rsv]; [dor, ndor] = [ndor, dor];")
rep(": 1); } light[i] -= cst; }", ": 1); } light[i] -= dor[i] ? cst * P.sporeCost : cst; }")
rep("((xs >> 12) & 3))) *", "((xs >> 12) & 3) + ((xs >> 14) & 3))) *")
rep("if (alive[j] && ((B(gen[j]) >> n) & 1) &&", "if (alive[j] && !dor[j] && ((B(gen[j]) >> n) & 1) &&")
rep("const ok = (((S(gen[i])", "const ok = (dor[i] || ((S(gen[i])")
rep("rng() < hh * (1 - thermFit(gen[i], temp[cmap[i]])))", "rng() < hh * (dor[i] ? .2 : 1) * (1 - thermFit(gen[i], temp[cmap[i]])))")
rep("hopPass(); driftPass();", "hopPass(); driftPass(); sporePass();")
rep("      else if (vm === 'strat') {", "      else if (vm === 'spore') { if (dor[i]) { d[p] = 255; d[p + 1] = 238; d[p + 2] = 190; } else { const t = colorSlot(gen[i]); d[p] = CV[t] * .22; d[p + 1] = CV[t + 1] * .22; d[p + 2] = CV[t + 2] * .22; } }\n      else if (vm === 'strat') {")
rep("      d[p] = CV[t] * f; d[p + 1] = CV[t + 1] * f; d[p + 2] = CV[t + 2] * f; }", "      if (dor[i]) { d[p] = 150 + CV[t] * .3; d[p + 1] = 145 + CV[t + 1] * .3; d[p + 2] = 135 + CV[t + 2] * .3; } else { d[p] = CV[t] * f; d[p + 1] = CV[t + 1] * f; d[p + 2] = CV[t + 2] * f; } }")
rep("gHet:true, gAdh:true,", "gHet:true, gAdh:true, gSpore:true, sporeRate:.05, sporeLight:.03, wakeLight:.3, wakeRate:.03, sporeCost:.1, sporeDeath:.003,")
rep("'convect', 'eddies']) {", "'convect', 'eddies', 'sporeRate', 'wakeRate']) {")
rep("'gHet', 'gAdh', 'rxn']) {", "'gHet', 'gAdh', 'rxn', 'gSpore']) {")
rep("  <h2>Reactions</h2>", r"""  <h2>Spores</h2>
  <p>A cell with the <b>spore-forming gene</b> (the prime 89, strength 1 to 3) that starves or whose ground dries out may turn into a <b>spore</b>: a dormant cell that pays almost nothing to live, cannot give birth, stands drying and heat far better, and is carried by the current even out of a crowd. A spore wakes when light and water come back. Show them with <i>View: Spores</i>; in the normal view they are pale.</p>
  <div class="row"><label><input type="checkbox" id="gSpore" checked> Spore-forming gene (89)</label></div>
  <label class="sl">Turning into a spore<input type="range" id="sporeRate" min="0" max="0.3" step="0.01" value="0.05"><output></output></label>
  <label class="sl">Waking<input type="range" id="wakeRate" min="0" max="0.2" step="0.005" value="0.03"><output></output></label>
  <h2>Reactions</h2>""")

rep("&& !(P.rxn && dryKill(i, n));", "&& !(P.rxn && dryKill(i, n)) && !(dor[i] && rng() < P.sporeDeath);")

rep("heatDiff:.2,", "heatDiff:.05,")
rep("heatRelax:.02,", "heatRelax:.006,")

rep('id="heatDiff" min="0" max="0.5" step="0.01" value="0.2"', 'id="heatDiff" min="0" max="0.5" step="0.01" value="0.05"')
rep('id="heatRelax" min="0.002" max="0.2" step="0.002" value="0.02"', 'id="heatRelax" min="0.002" max="0.2" step="0.002" value="0.006"')
rep('<label class="sl">Convection<input', '<label class="sl">Cross-current<input type="range" id="crossflow" min="0" max="2" step="0.05" value="1"><output></output></label>\n  <label class="sl">Convection<input')
rep("'convect', 'eddies', 'sporeRate', 'wakeRate']) {", "'convect', 'eddies', 'sporeRate', 'wakeRate', 'crossflow']) {")


# ------------------------------------------------------------------ soma and germ: the clump's code (its nucleus) can set its inner cells to work instead of breed
rep("  BS = c => ((c >>> 9) & 7) / 7, BT = c => (c >>> 12) & 255;", "  BS = c => ((c >>> 9) & 7) / 7, BT = c => (c >>> 12) & 255, BG = c => (c >>> 20) & 3;   // BG: how far its inside cells serve as soma")
rep("pools ${Math.round(BS(c) * 100)}% of its light`;", "pools ${Math.round(BS(c) * 100)}% of its light${P.somaOn && BG(c) ? `; its innermost ${20 * BG(c)}% of cells are soma: they do not breed and pass half their spare light to its outer cells, which breed` : ''}`;")
rep("  // a clump also shares the sugar and water in the ground it covers", """  // soma and germ: in a clump whose code says so, its innermost cells (20, 40 or 60% of them) are soma. They do not
  // breed, and pass part of their spare light to the outer cells, the germ line, which breed into the open ground around it
  if (P.somaOn) {
    if ((tick & 3) === 0) {
      soma.fill(0); somaN = 0; const mem = new Map();
      for (let i = 0; i < N; i++) { const b = body[i]; if (!b || !alive[i]) continue; let m = mem.get(b); if (!m) mem.set(b, m = []); m.push(i); }
      for (const [b, m] of mem) {
        const bo = bodies.get(b); if (!bo || m.length < 6) continue; const k = BG(bo.code); if (!k) continue;
        const ax = m[0] % W, ay = (m[0] / W) | 0; let cx = 0, cy = 0; const rel = m.map(i => { const dx = wrapd(i % W - ax, W), dy = wrapd(((i / W) | 0) - ay, H); cx += dx; cy += dy; return [dx, dy, i]; });
        cx /= m.length; cy /= m.length; rel.sort((p, q) => ((p[0] - cx) ** 2 + (p[1] - cy) ** 2) - ((q[0] - cx) ** 2 + (q[1] - cy) ** 2));
        const ns = Math.floor(m.length * .2 * k); for (let h = 0; h < ns; h++) { soma[rel[h][2]] = 1; somaN++; }
      }
    }
    const give = new Map();
    for (let i = 0; i < N; i++) { const b = body[i]; if (!b || !alive[i]) continue; let g = give.get(b); if (!g) give.set(b, g = [0, 0]);
      if (soma[i]) { const ex = light[i] - P.somaKeep; if (ex > 0) { const t = ex * .5; light[i] -= t; g[0] += t; } } else g[1]++; }
    for (let i = 0; i < N; i++) { if (soma[i] || !body[i] || !alive[i]) continue; const g = give.get(body[i]); if (g && g[0] > 0 && g[1] > 0) light[i] += g[0] / g[1]; }
  } else if (somaN) { soma.fill(0); somaN = 0; }
  // a clump also shares the sugar and water in the ground it covers""")
rep("if (alive[j] && !dor[j] && ((B(gen[j]) >> n) & 1) &&", "if (alive[j] && !dor[j] && !soma[j] && ((B(gen[j]) >> n) & 1) &&")
rep("let dor = new Uint8Array(N), ndor = new Uint8Array(N);", "let dor = new Uint8Array(N), ndor = new Uint8Array(N);\nlet soma = new Uint8Array(N), somaN = 0;               // soma: a clump's working cell that does not breed")
rep("gSpore:true,", "gSpore:true, somaOn:true, somaKeep:.15,")
rep("  <h2>Spores</h2>", r"""  <h2>Soma and germ</h2>
  <p>A clump's code, its nucleus, can set its cells to different work. Where the code calls for it, the clump's innermost cells become <b>soma</b>: they do not breed, and they pass half their spare light to the outer cells, the <b>germ line</b>, which breed into the open ground around the clump. How many cells serve (none, 20, 40 or 60%) is written in the code and mutates when the clump divides or buds, so clumps can evolve toward working insides or away from them.</p>
  <div class="row"><label><input type="checkbox" id="somaOn" checked> Soma and germ</label></div>
  <h2>Spores</h2>""")
rep("'gHet', 'gAdh', 'rxn', 'gSpore']) {", "'gHet', 'gAdh', 'rxn', 'gSpore', 'somaOn']) {")

rep("light[i] -= dor[i] ? cst * P.sporeCost : cst; }", "light[i] -= dor[i] ? cst * P.sporeCost : soma[i] ? cst * P.somaCost : cst; }")
rep("somaOn:true, somaKeep:.15,", "somaOn:true, somaKeep:.15, somaCost:.5,")


# ------------------------------------------------------------------ predators cannot easily swallow a big clump
rep("|| rng() >= P.predRate * de) continue;", "|| rng() >= P.predRate * de) continue;\n    if (nbody[j]) { const bo = bodies.get(nbody[j]); if (bo && bo.size > P.gape && rng() >= P.gape / bo.size) continue; }   // a grazer cannot swallow what is much bigger than it")
rep("somaOn:true, somaKeep:.15, somaCost:.5,", "somaOn:true, somaKeep:.15, somaCost:.5, gape:10,")


# ------------------------------------------------------------------ restart a start that fizzles out
rep("function reset(mode) {\n  envInit();", "function reset(mode, auto) {\n  if (!auto) restarts = 0; lastMode = mode;\n  envInit();")
rep("hopPass(); driftPass(); sporePass();", "hopPass(); driftPass(); sporePass(); earlyCheck();")
rep('<label><input type="checkbox" id="foldOn" checked> Fold quiet regions</label>', '<label><input type="checkbox" id="foldOn" checked> Fold quiet regions</label><label title="If the start dies out in its first 400 ticks, sow a fresh one"><input type="checkbox" id="autoRestart" checked> Restart if it fizzles out</label>')
rep("gape:10,", "gape:10, autoRestart:true,")
rep("'gSpore', 'somaOn']) {", "'gSpore', 'somaOn', 'autoRestart']) {")


# ------------------------------------------------------------------ the line of expression: sequences, copied and infolded into compounds
rep("let mixed = false; let sx = 0;", "let mixed = false, mateG = -1; let sx = 0;")
rep("g = ((a & m) | (b2 & ~m)) >>> 0; parent = a; how = 'fusion';", "g = ((a & m) | (b2 & ~m)) >>> 0; parent = a; how = 'fusion'; mateG = b2;")
rep("if (ZMU[zi] > 0) { const m2 = mutate(g, ZMU[zi] * PROOFT[(parent >>> 24) & 3] * (envOn ? .6 + temp[cmap[i]] : 1)); if (m2 !== g) { g = m2; if (how === 'copy') how = 'mutant'; } }",
    "if (P.seqOn && pj >= 0) { let pb = -1; if (mateG !== -1) for (let k = 0; k < c; k++) if (cand[k] === mateG) { pb = candI[k]; break; }\n            const m2 = seqBirth(i, pj, pb, ZMU[zi] * PROOFT[(parent >>> 24) & 3] * (envOn ? .6 + temp[cmap[i]] : 1)); if (m2 !== g) { g = m2; if (how === 'copy') how = 'mutant'; } }\n          else if (ZMU[zi] > 0) { const m2 = mutate(g, ZMU[zi] * PROOFT[(parent >>> 24) & 3] * (envOn ? .6 + temp[cmap[i]] : 1)); if (m2 !== g) { g = m2; if (how === 'copy') how = 'mutant'; } }")
rep("light[pj] -= ZBIRTH[zi]; if (P.rxn) { co2[sq]", "light[pj] -= ZBIRTH[zi] + (P.seqOn ? P.seqCost * slen[i] : 0); if (P.rxn) { co2[sq]")
rep("const g = ((ngen[j] & ~mask) | (ngen[i] & mask)) >>> 0;", "const g = P.seqOn ? seqTransfer(i, j) : ((ngen[j] & ~mask) | (ngen[i] & mask)) >>> 0;")
rep("dor.fill(0); ndor.fill(0);", "dor.fill(0); ndor.fill(0); if (slen.length !== N) seqAlloc(); slen.fill(0); seqMut = seqNeutral = 0;")
rep("xg[i] = 0; rsv[i] = 0; dor[i] = 0;", "xg[i] = 0; rsv[i] = 0; dor[i] = 0; slen[i] = 0;")
rep("autoRestart:true,", "autoRestart:true, seqOn:true, seqMu:1, seqDup:.02, seqDel:.02, seqCost:.0004,")
rep("'somaOn', 'autoRestart']) {", "'somaOn', 'autoRestart', 'seqOn']) {")
rep("'sporeRate', 'wakeRate', 'crossflow']) {", "'sporeRate', 'wakeRate', 'crossflow', 'seqMu', 'seqDup', 'seqDel', 'seqCost']) {")
rep("  <h2>Soma and germ</h2>", r"""  <h2>Line of expression</h2>
  <p>Each cell carries an ordered <b>sequence</b> of monomers, the 16 molecules, and its compound (its rule) is what the sequence <b>infolds</b> into. Read along the sequence, a monomer that meets its complement, the molecule eight places away, pairs with it, and both are buried; the monomers left unpaired are exposed, and their counts make the compound. A child copies its parent's sequence, or crosses two parents' sequences, with copying errors; now and then a stretch is copied twice, leaving the second copy free to vary, or a stretch is lost. Contagion splices a stretch of one cell's sequence into its neighbour's. A longer sequence costs more light to copy. Many sequences infold into the same compound, so many copying errors change nothing. Click a cell to see its sequence and how it infolds.</p>
  <div class="row"><label><input type="checkbox" id="seqOn" checked> Line of expression</label></div>
  <label class="sl">Copying errors (× the base rate)<input type="range" id="seqMu" min="0" max="20" step="0.5" value="1"><output></output></label>
  <label class="sl">Stretch copied twice<input type="range" id="seqDup" min="0" max="0.2" step="0.005" value="0.02"><output></output></label>
  <label class="sl">Stretch lost<input type="range" id="seqDel" min="0" max="0.2" step="0.005" value="0.02"><output></output></label>
  <label class="sl">Light per monomer copied<input type="range" id="seqCost" min="0" max="0.02" step="0.001" value="0.004"><output></output></label>
  <h2>Soma and germ</h2>""")


# ------------------------------------------------------------------ the infolded pairs at work: eight kinds of enzyme
rep("light[i] -= dor[i] ? cst * P.sporeCost : soma[i] ? cst * P.somaCost : cst; }", "light[i] -= (1 - .1 * CA(i, 0)) * (dor[i] ? cst * P.sporeCost : soma[i] ? cst * P.somaCost : cst); }")
rep("light[i] += burn(cmap[i], -light[i], .1 * he, P.eeff);", "light[i] += burn(cmap[i], -light[i], .1 * he, Math.min(1, P.eeff * (1 + .25 * CA(i, 1))));")
rep("if (chemOn && !payChem(cmap[i] << 4, g, 1 + fr * (8 - n) / 7))", "if (chemOn && !payChem(cmap[i] << 4, g, (1 + fr * (8 - n) / 7) * (P.seqOn ? 1 - .15 * CA(i, 2) : 1)))")
rep("rng() < hh * (dor[i] ? .2 : 1) * (1 - thermFit(gen[i], temp[cmap[i]])))", "rng() < hh * (dor[i] ? .2 : 1) * (1 - .25 * CA(i, 4)) * (1 - thermFit(gen[i], temp[cmap[i]])))")
rep("light[pj] -= ZBIRTH[zi] + (P.seqOn ? P.seqCost * slen[i] : 0);", "light[pj] -= ZBIRTH[zi] * (1 - .1 * CA(pj, 7)) + (P.seqOn ? P.seqCost * slen[i] : 0);")
rep("if (nbody[j]) { const bo = bodies.get(nbody[j]);", "if (rng() < .25 * CA(j, 6)) continue;      // its defence enzyme turns the bite away\n    if (nbody[j]) { const bo = bodies.get(nbody[j]);")
rep("seqOn:true,", "seqOn:true, catOn:true,")
rep("'somaOn', 'autoRestart', 'seqOn']) {", "'somaOn', 'autoRestart', 'seqOn', 'catOn']) {")
rep("  <h2>Soma and germ</h2>", r"""  <h2>Infolded pairs at work</h2>
  <p>The monomers a sequence leaves exposed make its compound, its rule; the pairs it buries do work. A pair of a monomer with its complement is an enzyme of one of eight kinds, by which pair it is: light harvest (lower upkeep), respiration (more from sugar), uptake (fewer molecules to build a child), keeping water, heat tolerance, copying fidelity (fewer copying errors), defence (bites turned away) and building (cheaper births), each up to strength 3. Every monomer that pairs to work no longer counts toward the rule, so a sequence trades rule against work.</p>
  <div class="row"><label><input type="checkbox" id="catOn" checked> Infolded pairs work</label></div>
  <h2>Soma and germ</h2>""")


# ------------------------------------------------------------------ the nucleus regulates its soma cells' expression
rep("soma.fill(0); somaN = 0; const mem = new Map();", "regRestore(); soma.fill(0); somaN = 0; const mem = new Map();")
rep("const ns = Math.floor(m.length * .2 * k); for (let h = 0; h < ns; h++) { soma[rel[h][2]] = 1; somaN++; }",
    "const ns = Math.floor(m.length * .2 * k), rg = P.nucReg && P.seqOn && ((bo.code >>> 26) & 1), sk = (bo.code >>> 22) & 15;\n        for (let h = 0; h < ns; h++) { soma[rel[h][2]] = 1; somaN++; if (rg) regApply(rel[h][2], sk); }")
rep("pass half their spare light to its outer cells, which breed` : ''}`;", "pass half their spare light to its outer cells, which breed${P.nucReg && P.seqOn && ((c >>> 26) & 1) ? `, and it silences the monomer ${MONO[(c >>> 22) & 15]} in them, so they infold without it` : ''}` : ''}`;")
rep("catOn:true,", "catOn:true, nucReg:true,")
rep("'seqOn', 'catOn']) {", "'seqOn', 'catOn', 'nucReg']) {")
rep('  <div class="row"><label><input type="checkbox" id="somaOn" checked> Soma and germ</label></div>', '  <p>The nucleus can also regulate what its soma cells express. Where its code says so, it silences one kind of monomer in them: they infold without it, so their rule and their enzymes change while they serve. Their sequence is untouched, so a cell that leaves the clump, and every child, expresses all of it again.</p>\n  <div class="row"><label><input type="checkbox" id="somaOn" checked> Soma and germ</label><label><input type="checkbox" id="nucReg" checked> The nucleus regulates its soma</label></div>')


# ------------------------------------------------------------------ open, lift and fold as readouts
rep("hopPass(); driftPass(); sporePass(); earlyCheck();", "hopPass(); driftPass(); sporePass(); earlyCheck(); if ((tick & 1) === 0) olfStep();")
rep("dor.fill(0); ndor.fill(0);", "dor.fill(0); ndor.fill(0); olfReset();")
# ------------------------------------------------------------------ two layers: a floor layer and a surface layer (env.js: fluidStep2, heat2, sporeAir)
rep("fdrag:.03,", "fdrag:.03, twoLayer:true, buoy:40, sdrag:.005, vmix:.02, wheat:4, floorRelax:1, airLoss:1, shear:.01, coriolis:0, tide:0, sporeLift:.3, settle:.02, airMax:3000, water3d:true, nz3:16, buoy3:.012, drag3:.01, jac3:30, vdiff3:.15,")
rep('<label class="sl">Cross-current<input', '''<div class="row"><label><input type="checkbox" id="water3d" checked> 3D water on the GPU</label> <span id="g3status" style="color:var(--muted);font-size:12px"></span></div>
  <p>3D water: a grid of the chemistry squares across and several levels deep, run on the graphics card (WebGPU). Warm water rises through the levels, spreads at the surface and sinks where it is cool. Without a GPU, or while it starts, the two-layer model runs instead.</p>
  <label class="sl">3D buoyancy<input type="range" id="buoy3" min="0" max="0.04" step="0.001" value="0.012"><output></output></label>
  <label class="sl">3D drag<input type="range" id="drag3" min="0" max="0.1" step="0.002" value="0.01"><output></output></label>
  <label class="sl">3D vertical mixing<input type="range" id="vdiff3" min="0" max="1" step="0.05" value="0.15"><output></output></label>
  <label class="sl">3D levels<input type="range" id="nz3" min="4" max="32" step="1" value="16"><output></output></label>
  <div class="row"><label><input type="checkbox" id="twoLayer" checked> Two layers: a floor and a surface</label></div>
  <p>With two layers, warm water rises from the floor into the surface layer and spreads, and cool water sinks and returns along the floor; the cross-current is then unused, and the tide pushes both layers. Spores can ride the rising water and settle far away.</p>
  <label class="sl">Mixing between layers<input type="range" id="vmix" min="0" max="0.2" step="0.005" value="0.02"><output></output></label>
  <label class="sl">Drag between layers<input type="range" id="shear" min="0" max="0.1" step="0.005" value="0.01"><output></output></label>
  <label class="sl">Turning (Coriolis)<input type="range" id="coriolis" min="-0.05" max="0.05" step="0.005" value="0"><output></output></label>
  <label class="sl">Tide<input type="range" id="tide" min="0" max="2" step="0.05" value="0"><output></output></label>
  <label class="sl">Spores lifted<input type="range" id="sporeLift" min="0" max="1" step="0.05" value="0.3"><output></output></label>
  <label class="sl">Spores settling<input type="range" id="settle" min="0" max="0.3" step="0.01" value="0.02"><output></output></label>
  <label class="sl">Cross-current<input''')
rep("'seqMu', 'seqDup', 'seqDel', 'seqCost']) {", "'seqMu', 'seqDup', 'seqDel', 'seqCost', 'vmix', 'shear', 'coriolis', 'tide', 'sporeLift', 'settle', 'buoy3', 'drag3', 'nz3', 'vdiff3']) {")
rep("'seqOn', 'catOn', 'nucReg']) {", "'seqOn', 'catOn', 'nucReg', 'twoLayer', 'water3d']) {")
# the 3D view (view3d.js): a button on the world, beside the View menu
rep('<button id="btnBodies"', '<button id="btn3d" title="A 3D view of the water and the floor, rendered on the GPU">3D view</button><button id="btnBodies"')
rep("water3d:true, nz3:16,", "view3d:false, water3d:true, nz3:16, cellLift:.05, aloftDeath:.004, sinkSpore:.006, sinkCell:.016, settle3:.08,")
rep('  <label class="sl">Spores settling<input', '  <label class="sl">Loose cells carried<input type="range" id="cellLift" min="0" max="1" step="0.01" value="0.05"><output></output></label>\n  <label class="sl">Spores settling<input')
rep("'buoy3', 'drag3', 'nz3', 'vdiff3']) {", "'buoy3', 'drag3', 'nz3', 'vdiff3', 'cellLift']) {")


# ------------------------------------------------------------------ species as a readout
rep("if ((tick & 1) === 0) olfStep();", "if ((tick & 1) === 0) olfStep(); if (tick % 100 === 0) specStep();")
rep("o2: P.rxn ? +(o2.reduce((a, b) => a + b, 0) / o2.length).toFixed(2) : 0});", "o2: P.rxn ? +(o2.reduce((a, b) => a + b, 0) / o2.length).toFixed(2) : 0, species: specStat.n});")
rep("['o2', 'Oxygen (a square)']];", "['o2', 'Oxygen (a square)'], ['species', 'Species (sequence clusters)']];")
rep("dor.fill(0); ndor.fill(0); olfReset();", "dor.fill(0); ndor.fill(0); olfReset(); species = []; nextSpecies = 1; specStat = {n: 0, est: 0, within: 0, between: 0, niches: 0, sampled: 0, div: 0};")
rep("catOn:true, nucReg:true,", "catOn:true, nucReg:true, specThr:.5,")


# ------------------------------------------------------------------ mating compatibility
rep("g = ((a & m) | (b2 & ~m)) >>> 0; parent = a; how = 'fusion'; mateG = b2;", "if (P.seqOn && P.mateThr > 0 && !mateOK(cand, candI, c, a, b2)) { g = a; parent = a; }      // too unlike to mate: a plain copy instead\n            else { g = ((a & m) | (b2 & ~m)) >>> 0; parent = a; how = 'fusion'; mateG = b2; }")
rep("specThr:.5,", "specThr:.5, mateThr:0,")

# ------------------------------------------------------------------ sliders for mating and homology; contagion needs a matching stretch
rep("mateThr:0,", "mateThr:0, hgtHom:0,")
rep('  <label class="sl">Light per monomer copied<input type="range" id="seqCost" min="0" max="0.02" step="0.001" value="0.004"><output></output></label>',
    '  <label class="sl">Light per monomer copied<input type="range" id="seqCost" min="0" max="0.02" step="0.001" value="0.004"><output></output></label>\n  <label class="sl">Likeness needed to mate (0 = any)<input type="range" id="mateThr" min="0" max="1" step="0.05" value="0"><output></output></label>\n  <label class="sl">Matching monomers needed for contagion (0 = none)<input type="range" id="hgtHom" min="0" max="6" step="1" value="0"><output></output></label>')
rep("'buoy3', 'drag3', 'nz3', 'vdiff3', 'cellLift']) {", "'buoy3', 'drag3', 'nz3', 'vdiff3', 'cellLift', 'mateThr', 'hgtHom']) {")
rep("dor.fill(0); ndor.fill(0); olfReset();", "dor.fill(0); ndor.fill(0); olfReset(); hgtTried = hgtFailed = 0; mateTried = mateRefused = 0;")

# ------------------------------------------------------------------ domains: nested folds as working units
rep("mateThr:0, hgtHom:0,", "mateThr:0, hgtHom:0, domOn:true, domDup:.01, domHGT:false, domMin:1,")
rep('  <label class="sl">Matching monomers needed for contagion (0 = none)<input',
    '  <div class="row"><label title="A pair and everything folded inside it work as one unit, named by the outer pair"><input type="checkbox" id="domOn" checked> Domains</label><label title="Contagion moves one whole domain instead of a random stretch"><input type="checkbox" id="domHGT"> Contagion moves whole domains</label></div>\n  <label class="sl" title="1 = a single pair works on its own; 2 or more = a fold must hold that many same-kind pairs to be stable">Pairs a domain needs to work<input type="range" id="domMin" min="1" max="3" step="1" value="1"><output></output></label>\n  <label class="sl">Whole domain copied twice<input type="range" id="domDup" min="0" max="0.1" step="0.005" value="0.01"><output></output></label>\n  <label class="sl">Matching monomers needed for contagion (0 = none)<input')
rep("'cellLift', 'mateThr', 'hgtHom']) {", "'cellLift', 'mateThr', 'hgtHom', 'domDup', 'domMin']) {")
rep("'twoLayer', 'water3d']) {", "'twoLayer', 'water3d', 'domOn', 'domHGT']) {")
rep("hgtTried = hgtFailed = 0; mateTried", "hgtTried = hgtFailed = 0; domDupN = 0; mateTried")

# ------------------------------------------------------------------ reactions from shape: domains convert molecules (replaces the named enzyme jobs)
rep("domHGT:false, domMin:1,", "domHGT:false, domMin:1, rxDom:true, rxRate:.2, rxE:.08, rxGround:true,")
rep("light[i] -= (1 - .1 * CA(i, 0)) * (", "if (P.rxDom && rx[i] && !dor[i]) domReact(i);\n      light[i] -= (1 - .1 * CA(i, 0)) * (")
rep('<input type="checkbox" id="domHGT"> Contagion moves whole domains</label></div>',
    '<input type="checkbox" id="domHGT"> Contagion moves whole domains</label><label title="Each domain turns one molecule into another, set by its shape; the eight named enzyme jobs are switched off"><input type="checkbox" id="rxDom" checked> Domains run reactions</label><label title="With reactions on, the ground re-forms only low-energy molecules; high-energy ones come from vents and the dead"><input type="checkbox" id="rxGround" checked> Energy only from vents and the dead</label></div>\n  <label class="sl">Reaction rate<input type="range" id="rxRate" min="0" max="0.3" step="0.01" value="0.05"><output></output></label>\n  <label class="sl">Light per step down the molecule ladder<input type="range" id="rxE" min="0" max="0.1" step="0.005" value="0.02"><output></output></label>')
rep("'hgtHom', 'domDup', 'domMin']) {", "'hgtHom', 'domDup', 'domMin', 'rxRate', 'rxE']) {")
rep("'water3d', 'domOn', 'domHGT']) {", "'water3d', 'domOn', 'domHGT', 'rxDom', 'rxGround']) {")
rep("domDupN = 0; mateTried", "domDupN = 0; rxRun = rxGain = rxCost = 0; mateTried")

# ------------------------------------------------------------------ clumps made by their cells: the clump code is retired (step 2)
rep("rxE:.08, rxGround:true,", "rxE:.08, rxGround:true, cellClumps:true, coatFrac:.3, coatDecay:.02, coatMin:.2, clumpMin:4,")
rep("function bodyCensus() {\n  if (!P.gAdh) return;", "function bodyCensus() {\n  if (!P.gAdh) return;\n  if (P.cellClumps) return cellClumpCensus();")
rep("sh * s[0] / s[1] - (P.floor ? P.bodyCost : 0);", "sh * s[0] / s[1] - (P.floor && !P.cellClumps ? P.bodyCost : 0);")
rep("<div>The body's code: ${bodyText(bo.code)}.</div>", "<div>${P.cellClumps ? `It has no code of its own: its cells hold together because what their reactions make coats them. It ${bo.how === 'splitting' ? 'split off #' + bo.parents[0] : 'formed from free cells'}.` : `The body's code: ${bodyText(bo.code)}.`}</div>")
rep('<input type="checkbox" id="rxGround" checked> Energy only from vents and the dead</label></div>',
    '<input type="checkbox" id="rxGround" checked> Energy only from vents and the dead</label><label title="A clump is just cells that stick: part of what a cell\'s reactions make stays on its surface, and larger molecules stick more. The clump has no code of its own"><input type="checkbox" id="cellClumps" checked> Clumps made by their cells</label></div>\n  <label class="sl">Share of a product kept as coat<input type="range" id="coatFrac" min="0" max="1" step="0.05" value="0.3"><output></output></label>\n  <label class="sl">Coat needed to stick<input type="range" id="coatMin" min="0.02" max="1" step="0.02" value="0.2"><output></output></label>')
rep("'domMin', 'rxRate', 'rxE']) {", "'domMin', 'rxRate', 'rxE', 'coatFrac', 'coatMin']) {")
rep("'rxDom', 'rxGround']) {", "'rxDom', 'rxGround', 'cellClumps']) {")
rep("rxRun = rxGain = rxCost = 0; mateTried", "rxRun = rxGain = rxCost = 0; ccStat = {formed: 0, split: 0, merged: 0, fromFree: 0, fromSplit: 0, rel: null, relN: 0}; coat.fill(0); mateTried")

# ------------------------------------------------------------------ the matrix: what clumps get for their coats, and what size costs
rep("coatMin:.2, clumpMin:4,", "coatMin:.2, clumpMin:4, mxRetain:.5, mxLeak:.05, sinkSize:200,")
rep("if (!ok) { nchanged[i] = 1; deaths++; if (chemOn) releaseChem(cmap[i] << 4, gen[i]); }", "if (!ok) { nchanged[i] = 1; deaths++; if (chemOn) releaseChem(cmap[i] << 4, gen[i], P.cellClumps ? body[i] : 0); }")
rep("if (chemOn && !payChem(cmap[i] << 4, g, (1 + fr * (8 - n) / 7) * (P.seqOn ? 1 - .15 * CA(i, 2) : 1))) {", "if (chemOn && !payChem(cmap[i] << 4, g, (1 + fr * (8 - n) / 7) * (P.seqOn ? 1 - .15 * CA(i, 2) : 1), P.cellClumps && pj >= 0 ? body[pj] : 0)) {")
rep("light[i] += ZRG[z] * (ltc[cmap[i]] - light[i]);", "light[i] += ZRG[z] * (ltc[cmap[i]] * (P.cellClumps && body[i] ? clumpShade(i) : 1) - light[i]);")
rep('<input type="range" id="coatMin" min="0.02" max="1" step="0.02" value="0.2"><output></output></label>',
    '<input type="range" id="coatMin" min="0.02" max="1" step="0.02" value="0.2"><output></output></label>\n  <label class="sl" title="Share of what a clump\'s cells make, and of what its dead release, that the matrix keeps for the clump">Kept by the matrix<input type="range" id="mxRetain" min="0" max="1" step="0.05" value="0.5"><output></output></label>\n  <label class="sl" title="A clump of this many cells gets half its light: its cells shade each other and it sinks">Clump size at half light<input type="range" id="sinkSize" min="10" max="1000" step="10" value="200"><output></output></label>')
rep("'rxE', 'coatFrac', 'coatMin']) {", "'rxE', 'coatFrac', 'coatMin', 'mxRetain', 'sinkSize']) {")
rep("ccStat = {formed: 0, split: 0, merged: 0, fromFree: 0, fromSplit: 0, rel: null, relN: 0}; coat.fill(0);", "ccStat = {formed: 0, split: 0, merged: 0, fromFree: 0, fromSplit: 0, rel: null, relN: 0}; coat.fill(0); mxPool.clear();")

# ------------------------------------------------------------------ the coat can be made from sugar (12 November)
rep("mxRetain:.5, mxLeak:.05, sinkSize:200,", "mxRetain:.5, mxLeak:.05, sinkSize:200, sugarCoat:.02, sugarKeep:.3, clumpReach:3,")
rep("if (!ok) { nchanged[i] = 1; deaths++; if (chemOn) releaseChem(cmap[i] << 4, gen[i], P.cellClumps ? body[i] : 0); }", "if (!ok) { nchanged[i] = 1; deaths++; if (chemOn) releaseChem(cmap[i] << 4, gen[i], P.cellClumps ? body[i] : 0); if (coat[i]) { coatReturn(i, 1); coat[i] = 0; } }")
rep('Clump size at half light<input type="range" id="sinkSize" min="10" max="1000" step="10" value="200"><output></output></label>',
    'Clump size at half light<input type="range" id="sinkSize" min="10" max="1000" step="10" value="200"><output></output></label>\n  <label class="sl" title="A fold that pairs a monomer with its complement chains the cell\'s own sugar into coat, this much light a tick for each unit of strength">Sugar chained into coat<input type="range" id="sugarCoat" min="0" max="0.1" step="0.005" value="0.02"><output></output></label>')
rep("'coatMin', 'mxRetain', 'sinkSize']) {", "'coatMin', 'mxRetain', 'sinkSize', 'sugarCoat']) {")
rep("coat.fill(0); mxPool.clear();", "coat.fill(0); mxPool.clear(); coatMade = 0;")

# ------------------------------------------------------------------ regulation from chemistry: product inhibition (12 November)
rep("sugarCoat:.02, sugarKeep:.3, clumpReach:3,", "sugarCoat:.02, sugarKeep:.3, clumpReach:3, rxInhib:true,")
rep('<input type="checkbox" id="cellClumps" checked> Clumps made by their cells</label></div>', '<input type="checkbox" id="cellClumps" checked> Clumps made by their cells</label><label title="A reaction slows as its product builds up around the cell, in its square and in its clump\'s matrix"><input type="checkbox" id="rxInhib" checked> Products slow their own reactions</label></div>')
rep("'rxGround', 'cellClumps']) {", "'rxGround', 'cellClumps', 'rxInhib']) {")

# ------------------------------------------------------------------ the inner sum weighted by depth (12 November, option A)
rep("clumpReach:3, rxInhib:true,", "clumpReach:3, rxInhib:true, depthW:true,")

# ------------------------------------------------------------------ adaptors: the code read by its own products (12 November)
rep("rxInhib:true, depthW:true,", "rxInhib:true, depthW:true, adapt:true,")
rep('<input type="checkbox" id="rxInhib" checked> Products slow their own reactions</label></div>', '<input type="checkbox" id="rxInhib" checked> Products slow their own reactions</label><label title="Domains at the head of a sequence, before its first unpaired monomer, rewrite the cell\'s reading code instead of running reactions"><input type="checkbox" id="adapt" checked> Adaptors: cells rewrite their reading code</label></div>')
rep("'cellClumps', 'rxInhib']) {", "'cellClumps', 'rxInhib', 'adapt']) {")
rep("coat.fill(0); mxPool.clear(); coatMade = 0;", "coat.fill(0); mxPool.clear(); coatMade = 0; codeChg = codeBirths = 0;")

# ------------------------------------------------------------------ gliding on slime, and the dish world (12 November)
rep("depthW:true, adapt:true,", "depthW:true, adapt:true, glide:.1, glideCost:.05, dishFood:.5, dishLight:.1,")
rep("hopPass(); driftPass(); sporePass();", "hopPass(); glidePass(); driftPass(); sporePass();")
rep("  chemInit();\n  log(mode === 'blank'", "  chemInit(); dishSetup();\n  log(mode === 'blank'")
rep('<option value="springs">Hot springs</option>', '<option value="springs">Hot springs</option><option value="dish">Dish: dark, still, food laid once</option>')
rep('<input type="checkbox" id="adapt" checked> Adaptors: cells rewrite their reading code</label></div>', '<input type="checkbox" id="adapt" checked> Adaptors: cells rewrite their reading code</label></div>\n  <label class="sl" title="Chance a tick that a fully coated cell creeps into an empty neighbouring place, spending coat as slime">Gliding on slime<input type="range" id="glide" min="0" max="0.5" step="0.01" value="0.1"><output></output></label>\n  <label class="sl" title="In the dish: the food (p) laid down once, as a share of the ground\'s richness">Food in the dish<input type="range" id="dishFood" min="0.05" max="2" step="0.05" value="0.5"><output></output></label>')
rep("'mxRetain', 'sinkSize', 'sugarCoat']) {", "'mxRetain', 'sinkSize', 'sugarCoat', 'glide', 'dishFood']) {")

# ------------------------------------------------------------------ the Game of Life rule removed (13 November, option 2)
# With lifeRule off a cell divides when it has stored the energy for a child and there is an empty place beside it, at
# most once a tick, and it dies only of real causes (starvation, chance, heat, drying, predation). The primes 2 to 19
# are then ordinary building blocks. The rule is kept as a switch, for comparison.
rep("glide:.1, glideCost:.05, dishFood:.5, dishLight:.1,", "glide:.1, glideCost:.05, dishFood:.5, dishLight:.1, lifeRule:false,")
rep("fl = P.floor, fo = P.foldOn,", "fl = P.floor, fo = P.foldOn && P.lifeRule,")
rep("function step() {\n  tick++;", "function step() {\n  tick++; if (!divT || divT.length !== N) divT = new Int32Array(N).fill(-1);")
rep("const ok = (dor[i] || ((S(gen[i]) >> (kw < 1 ? kinCount(gen[i], nb, n, kw) : n)) & 1)", "const ok = (dor[i] || !P.lifeRule || ((S(gen[i]) >> (kw < 1 ? kinCount(gen[i], nb, n, kw) : n)) & 1)")
rep("!soma[j] && ((B(gen[j]) >> n) & 1)", "!soma[j] && (P.lifeRule ? ((B(gen[j]) >> n) & 1) : divTgt[j] === i && divT[j] !== tick)")
rep("nchanged.fill(0); births = deaths = foldedCount", "if (!P.lifeRule) divPick(); nchanged.fill(0); births = deaths = foldedCount")
rep("let mixed = false, mateG = -1;", "let pjSel = -1, mixed = false, mateG = -1;")
rep("""            // dominance: the code most of the would-be parents carry
""", """            // with no Life rule: any neighbour ready to divide may take the place, each as likely as the next
            if (!P.lifeRule) { const k = (rng() * c) | 0; g = cand[k]; parent = g; pjSel = candI[k]; } else {
            // dominance: the code most of the would-be parents carry
""")
rep("            g = best; parent = best;\n          }", "            g = best; parent = best; }\n          }")
rep("let pj = -1; for (let k = 0; k < c; k++) if (cand[k] === parent) { pj = candI[k]; break; }", "let pj = pjSel; if (pj < 0) for (let k = 0; k < c; k++) if (cand[k] === parent) { pj = candI[k]; break; } if (pj >= 0) divT[pj] = tick;")
rep("  return 'B' + b + '/S' + s + ' ' + formula(g);", "  return P.lifeRule ? 'B' + b + '/S' + s + ' ' + formula(g) : formula(g);")
rep("""   <div>It is born where a dead cell has""", """   <div${P.lifeRule ? '' : ' style="display:none"'}>It is born where a dead cell has""")
rep('<input type="checkbox" id="adapt" checked> Adaptors: cells rewrite their reading code</label></div>', '<input type="checkbox" id="adapt" checked> Adaptors: cells rewrite their reading code</label><label title="Conway\'s rule, kept for comparison: the primes 2 to 19 say with how many neighbours a cell survives and is born. Off, a cell divides when it has the energy and there is room, and dies only of real causes"><input type="checkbox" id="lifeRule"> Game of Life rule (for comparison)</label></div>')
rep("'cellClumps', 'rxInhib', 'adapt']) {", "'cellClumps', 'rxInhib', 'adapt', 'lifeRule']) {")

# the dish is dim: its light was never applied, because the dish runs as an even world and skips envStep (fixed 13 November)
rep("dishFood:.5, dishLight:.1, lifeRule:false,", "dishFood:.5, dishLight:0, lifeRule:false, dishSugar:5, dishAir:.5, dishUpkeep:.24, dishR:.95,")
rep("if ((tick & 1) === 0) { if (envOn) envStep();", "if ((tick & 1) === 0) { if (envOn) envStep(); else if (P.env === 'dish' && ltc[0] !== P.dishLight) ltc.fill(P.dishLight);")

# the dish is a round plate with a rim (13 November, your note): nothing is born, glides or hops beyond it
rep("} else if (n > 0 && (!fl || light[i] >= ZCOST[zi]", "} else if (n > 0 && !dishBlocked(i) && (!fl || light[i] >= ZCOST[zi]")
rep("} else if (lamp[i] !== 0) {\n      const lp = lamp[i]", "} else if (dishOut(i)) { d[p] = 34; d[p + 1] = 33; d[p + 2] = 40;     // beyond the rim of the plate\n    } else if (lamp[i] !== 0) {\n      const lp = lamp[i]")

# the opening paragraph no longer says the compound is a survival rule (13 November)
rep("its factorisation is its rule: when it survives, when it gives birth,\n  whether it moves,", "its factorisation says what the cell is made of and what it can do: whether it moves,")

# in the dish, dormant cells are long-lived (13 November): they die at P.dishDormDeath of the usual rate
rep("&& !(dor[i] && rng() < P.sporeDeath);", "&& !(dor[i] && rng() < P.sporeDeath * (P.env === 'dish' ? P.dishDormDeath : 1));")
rep("dishUpkeep:.24, dishR:.95,", "dishUpkeep:.24, dishR:.95, dishDorm:true, dishDormDeath:.1,")

# inactive cells and remains in the dish (13 November): a starving cell that carries the dormancy gene stops instead of
# dying, and an inactive cell does not starve; a cell that dies leaves remains that hold its place and break down slowly
rep("dishDorm:true, dishDormDeath:.1,", "dishDorm:true, dishDormDeath:.1, dishLysis:.002,")
rep("        const ok = (dor[i] || !P.lifeRule", "        if (fl && !dor[i] && light[i] < 0 && P.env === 'dish' && ((xg[i] >> 14) & 3)) { dor[i] = 1; light[i] = 0; }   // in the dish a starving cell goes still\n        const ok = (dor[i] || !P.lifeRule")
rep("&& (!fl || light[i] >= 0) &&", "&& (!fl || light[i] >= 0 || (dor[i] && P.env === 'dish')) &&")
rep("if (!ok) { nchanged[i] = 1; deaths++;", "if (!ok) { nchanged[i] = 1; deaths++; if (P.env === 'dish' && husk) { husk[i] = 1; if (!huskG || huskG.length !== N) huskG = new Int32Array(N); huskG[i] = gen[i]; }")
rep("hopPass(); glidePass();", "dishTick(); hopPass(); glidePass();")
rep("} else if (dishOut(i)) { d[p] = 34; d[p + 1] = 33; d[p + 2] = 40;     // beyond the rim of the plate", "} else if (dishOut(i)) { d[p] = 34; d[p + 1] = 33; d[p + 2] = 40;     // beyond the rim of the plate\n    } else if (P.env === 'dish' && husk && husk[i] > 0) { const h = .35 + .65 * husk[i]; d[p] = 120 * h; d[p + 1] = 104 * h; d[p + 2] = 80 * h;   // remains")

# the dish as populations, with patches that open to single cells (13 November, Justin's decision)
rep("dishDormDeath:.1, dishLysis:.002,", "dishDormDeath:.1, dishLysis:.002, dishPop:false, popSugar:5, popSoft:.02,")
rep("function step() {\n  tick++;", "function step() {\n  if (popActive()) { popStep(); return; }\n  tick++;")
rep("  for (let i = 0; i < N; i++) {\n    const p = i * 4;\n    if (alive[i]) {", "  if (popActive()) popDraw(d); else for (let i = 0; i < N; i++) {\n    const p = i * 4;\n    if (alive[i]) {")
rep("function inspect(x, y) {", "function inspect(x, y) { if (popActive()) { popOpen(x, y); return; }")
rep('<option value="dish">Dish: dark, still, food laid once</option>', '<option value="dish">Dish: dark, still, food laid once</option><option value="dishpop">Dish, cells counted as populations</option>')

# the chemistry audit, part 1 (13 November): matter is conserved. Births no longer charge a lonely cell extra (a Life-rule
# leftover, kept only with the rule on); in the dish the remains hold a dead cell's compound until they break down;
# contagion pays for what it rewrites
rep("(1 + fr * (8 - n) / 7)", "(P.lifeRule ? 1 + fr * (8 - n) / 7 : 1)")
rep("if (chemOn) releaseChem(cmap[i] << 4, gen[i], P.cellClumps ? body[i] : 0);", "if (chemOn && !(P.env === 'dish' && husk)) releaseChem(cmap[i] << 4, gen[i], P.cellClumps ? body[i] : 0);")
rep("    reg(g, ngen[j], 'contagion'); ngen[j] = g;", "    if (chemOn && !swapChem(cmap[j] << 4, ngen[j], g)) continue;\n    reg(g, ngen[j], 'contagion'); ngen[j] = g;")
# fix (15 November, report 22 section 6): a contagion the cell cannot pay for is undone, sequence and program too, as uptake does
rep("    if (chemOn && !swapChem(cmap[j] << 4, ngen[j], g)) continue;", "    if (chemOn && !swapChem(cmap[j] << 4, ngen[j], g)) { if (P.seqOn) seqTransferUndo(j); continue; }")

# the chemistry audit, part 2 (13 November): energy. The reserve gives back what was put in, not rconv times as much
rep("if (light[i] < 0) { const use = Math.min(-light[i], r); r -= use; light[i] += use; }", "if (light[i] < 0) { const use = Math.min(-light[i], r / P.rconv); r -= use * P.rconv; light[i] += use; }")

# the vent retuned after the energy audit (13 November): vents twice as strong, the slider's range widened to match
rep("heatLife:.2, ventPower:1, heatChaos", "heatLife:.2, ventPower:2, rxKm:1, heatChaos")
rep('id="ventPower" min="0" max="2" step="0.1" value="1"', 'id="ventPower" min="0" max="4" step="0.1" value="2"')

# short chains in the ground (13 November, Justin's decision): fragments released at death, broken down, catalysing,
# taken up by homologous replacement
rep("dishPop:false, popSugar:5, popSoft:.02,", "dishPop:false, popSugar:5, popSoft:.02, fragOn:true, fragRel:.3, fragDecay:.0005, fragCat:.5, fragUp:.02,")
rep("if (chemOn && !(P.env === 'dish' && husk)) releaseChem(cmap[i] << 4, gen[i], P.cellClumps ? body[i] : 0);", "if (chemOn && !(P.env === 'dish' && husk)) releaseChem(cmap[i] << 4, gen[i], P.cellClumps ? body[i] : 0); if (chemOn) fragRelease(i);")
rep("dishTick(); hopPass(); glidePass();", "dishTick(); if ((tick & 7) === 0) fragStep(); hopPass(); glidePass();")
rep('<input type="checkbox" id="lifeRule"> Game of Life rule (for comparison)</label>', '<input type="checkbox" id="lifeRule"> Game of Life rule (for comparison)</label><label title="Dying cells release fragments of their line of expression into the ground; fragments break down, may catalyse their reaction, and may be taken up by cells"><input type="checkbox" id="fragOn" checked> Fragments in the ground</label>')
rep("'cellClumps', 'rxInhib', 'adapt', 'lifeRule']) {", "'cellClumps', 'rxInhib', 'adapt', 'lifeRule', 'fragOn']) {")

# heterotrophs store energy from sugar (13 November, at your agreement): when sugar is about, an eating cell also tops up
# its store towards hetStore, at most hetFill × its gene strength a tick, within its uptake limit. Without this a dish cell
# only ever covered each tick's shortfall, so its store ran down like a clock and going still did not follow the sugar.
# A dormant cell tops up at a quarter of the rate, so food returning can wake it.
rep("""      if (light[i] < 0) { const he = (xg[i] >> 10) & 3; if (he) {          // a heterotroph covers a shortfall from the energy molecule in the water
          light[i] += burn(cmap[i], -light[i], .1 * he, Math.min(1, P.eeff * (1 + .25 * CA(i, 1)))); } }""", """      { const he = (xg[i] >> 10) & 3;          // a heterotroph covers a shortfall from the energy molecule in the water, and stores some when it can
        if (he) { const fill = P.hetStore > light[i] ? Math.min(P.hetStore - Math.max(0, light[i]), P.hetFill * he * (dor[i] ? .25 : 1)) : 0, want = Math.max(0, -light[i]) + fill;
          if (want > 0) light[i] += burn(cmap[i], want, .1 * he, Math.min(1, P.eeff * (1 + .25 * CA(i, 1)))); } }""")
rep("fragDecay:.0005, fragCat:.5, fragUp:.02,", "fragDecay:.0005, fragCat:.5, fragUp:.02, hetStore:.4, hetFill:.02, fragJoin:.3, fragLig:2, fragCopy:.05, fragErr:.02, absorb:1,")

# ambient light and stored energy separated (13 November; the coding session's finding). One array, light, held both the
# light at an empty place and a cell's stored energy, so a newborn inherited the place's light, unpaid; stored energy
# spread between cells and into empty places; and in the dark dish a cell's store relaxed towards 0, a leak of 2% a tick.
# Now amb holds the ambient light: it relaxes towards the sun's level (ltc) and spreads, so crowds still shade one another.
# A cell absorbs from it, using it up; its store never leaks into the dark. A daughter gets half of what its parent has
# left after paying for the birth, and nothing from the place.
rep("tick++; if (!divT || divT.length !== N) divT = new Int32Array(N).fill(-1);", "tick++; if (!divT || divT.length !== N) divT = new Int32Array(N).fill(-1); if (!amb || amb.length !== N) amb = new Float32Array(N).fill(1);")
rep("seqMut = seqNeutral = 0; light.fill(1);", "seqMut = seqNeutral = 0; light.fill(1); if (amb && amb.length === N) amb.fill(1);")
rep("lightTmp[i] = (1 - df) * light[i] + df * .25 * (light[y0 + (x - 1 + W) % W] + light[y0 + (x + 1) % W] + light[ym + x] + light[yp + x]); } }\n      light.set(lightTmp);", "lightTmp[i] = (1 - df) * amb[i] + df * .25 * (amb[y0 + (x - 1 + W) % W] + amb[y0 + (x + 1) % W] + amb[ym + x] + amb[yp + x]); } }\n      amb.set(lightTmp);")
rep("light[i] += ZRG[z] * (ltc[cmap[i]] * (P.cellClumps && body[i] ? clumpShade(i) : 1) - light[i]); if (alive[i]) {", "amb[i] += ZRG[z] * (ltc[cmap[i]] * (P.cellClumps && body[i] ? clumpShade(i) : 1) - amb[i]); if (alive[i]) { { const ab = P.absorb * Math.max(0, Math.min(amb[i], amb[i] - Math.max(0, light[i]))); light[i] += ab; amb[i] -= ab; }")
rep("} else if (n > 0 && !dishBlocked(i) && (!fl || light[i] >= ZCOST[zi]", "} else if (n > 0 && !dishBlocked(i) && (!fl || amb[i] >= ZCOST[zi]")
rep("nalive[i] = 1; ngen[i] = g; nxg[i] = cx; nrsv[i] = 0; ndor[i] = 0; nchanged[i] = 1; births++;", "if (pj >= 0) { const h = Math.max(0, light[pj]) * .5; light[pj] -= h; light[i] = h; } else light[i] = 0;   // the daughter gets half of what the parent has left\n          nalive[i] = 1; ngen[i] = g; nxg[i] = cx; nrsv[i] = 0; ndor[i] = 0; nchanged[i] = 1; births++;")
rep("else if (P.showLight) { const L = Math.max(0, light[i]);", "else if (P.showLight) { const L = Math.max(0, amb ? amb[i] : light[i]);")
rep("else if (chOv) { const q = cmap[i] * 3, L = P.showLight ? Math.max(0, light[i]) : 0;", "else if (chOv) { const q = cmap[i] * 3, L = P.showLight ? Math.max(0, amb ? amb[i] : light[i]) : 0;")

# a parent divides only when its daughter gets a fair start (13 November, health check): its store must cover the birth
# and leave divKeep for each of the two (real bacteria grow before they split). With divKeep 0 the old rule holds
rep("(light[j] >= ZBIRTH[zi] || (((xg[j] >> 10) & 3) && en[cmap[i]] * P.eeff >= ZBIRTH[zi]))", "(light[j] >= ZBIRTH[zi] + (P.seqOn ? P.seqCost * slen[j] : 0) + 2 * P.divKeep || (((xg[j] >> 10) & 3) && light[j] >= (P.seqOn ? P.seqCost * slen[j] : 0) + 2 * P.divKeep && en[cmap[i]] * P.eeff >= ZBIRTH[zi]))")
rep("absorb:1,", "absorb:1, divKeep:0,")

# the health check's two corrections, made defaults (13 November): copying a sequence costs a tenth of what it did (real
# genome copying is a small part of a division's cost), and a parent divides only when each of the two can start with divKeep
rep("absorb:1, divKeep:0,", "absorb:1, divKeep:.1, restartWindow:3000, restartQuiet:300, restartGrow:1000,")

rep('id="seqCost" min="0" max="0.02" step="0.001" value="0.004"', 'id="seqCost" min="0" max="0.004" step="0.0001" value="0.0004"')

# the birth's payment follows the gate (13 November, the coding session's item b): a parent pays from its store only when
# its store covers the birth, the sequence and divKeep for each of the two; otherwise (a heterotroph admitted because the
# square's sugar can pay) the birth is paid from sugar, and only the sequence from the store
rep("if (fl && pj >= 0) { const sq = cmap[i]; if (light[pj] >= ZBIRTH[zi]) {", "if (fl && pj >= 0) { const sq = cmap[i]; if (light[pj] >= ZBIRTH[zi] + (P.seqOn ? P.seqCost * slen[pj] : 0) + 2 * P.divKeep) {")
rep("            else { burn(sq, ZBIRTH[zi], 1e9, P.eeff); if (P.rxn) co2[sq] = Math.max(0, co2[sq] - ZBIRTH[zi]); }", "            else { burn(sq, ZBIRTH[zi], 1e9, P.eeff); if (P.rxn) co2[sq] = Math.max(0, co2[sq] - ZBIRTH[zi]); light[pj] -= P.seqOn ? P.seqCost * slen[i] : 0; }")

# light rebalanced and vents darkened (13 November, at your go-ahead): light returns to a place at 0.15 a tick, so a covered
# patch in full sun earns about twice a cell's upkeep (it was 0.02, a quarter of the upkeep); the deep sea is dark but for
# the vents' dim glow (ventGlow)
rep("restartWindow:3000, restartQuiet:300, restartGrow:1000,", "restartWindow:3000, restartQuiet:300, restartGrow:1000, ventGlow:.05,")

rep("regrow:0.02, cost:0.08,", "regrow:0.15, cost:0.08,")

rep('id="regrow" min="0.005" max="0.2" step="0.005" value="0.02"', 'id="regrow" min="0.005" max="0.4" step="0.005" value="0.15"')

# the chemistry retuned so chemistry can pay (13 November, Justin's choice, option 3): upkeep an eighth (cost 0.01; 0.02 founded vent life in only 2 of 6 starts), enzymes
# four times faster at the same 40% efficiency (rxRate 0.2, rxE 0.08), light return rescaled to keep the lit worlds'
# balance (regrow 0.02), and the vents dark but for a dim glow (ventGlow 0.05). The dish's own upkeep is unchanged:
# dishUpkeep scaled up eightfold, so cost × dishUpkeep stays 0.0024
rep("regrow:0.15, cost:0.08,", "regrow:0.02, cost:0.01,")
rep('id="regrow" min="0.005" max="0.4" step="0.005" value="0.15"', 'id="regrow" min="0.005" max="0.2" step="0.005" value="0.02"')
rep('id="cost" min="0.005" max="0.2" step="0.005" value="0.08"', 'id="cost" min="0.001" max="0.1" step="0.001" value="0.01"')
rep('id="rxRate" min="0" max="0.3" step="0.01" value="0.05"', 'id="rxRate" min="0" max="0.6" step="0.01" value="0.2"')
rep('id="rxE" min="0" max="0.1" step="0.005" value="0.02"', 'id="rxE" min="0" max="0.24" step="0.005" value="0.08"')

# the visiting order (Justin, 14 November): the feeding loop and the birth scan visit places in a random order each tick,
# drawn with the page's seeded rng, so no row or column gets first claim on a square's shared stores (report 08's streaks;
# the dish colony's lean towards the top). P.randOrder = false restores row-by-row order.
rep("    for (let i = 0; i < N; i++) { const z = zmap[i]; amb[i] += ZRG[z]",
    "    visitOrder(); for (let vk = 0; vk < N; vk++) { const i = VORD[vk]; const z = zmap[i]; amb[i] += ZRG[z]")
rep('''for (let y = 0; y < H; y++) {
    const ym = ((y - 1 + H) % H) * W, y0 = y * W, yp = ((y + 1) % H) * W;
    for (let x = 0; x < W; x++) {
      const xm = (x - 1 + W) % W, xp = (x + 1) % W, i = y0 + x, zi = zmap[i];''',
    '''if (!VORD || VORD.length !== N) visitOrder();
  for (let vk = 0; vk < N; vk++) { const i = VORD[vk], y = (i / W) | 0, x = i - y * W;
    const ym = ((y - 1 + H) % H) * W, y0 = y * W, yp = ((y + 1) % H) * W;
    {
      const xm = (x - 1 + W) % W, xp = (x + 1) % W, zi = zmap[i];''')
rep("dishLysis:.002,", "dishLysis:.002, randOrder:true, springZone:true, springFlow:.3, springSrc:4, springRain:.0001, pondInflow:4, pigment:true, pigSat:.05, pigBase:0, virOn:true, virUp:.05, virCopy:.5, virE:.01, virBurst:12, detOn:true, detBreak:.05, detLeach:.001, detRot:.002, geneDup:.005, geneDel:.005, geneHGT:.1, virInteg:.02,")

# light use depends on a fold (Justin's queue, 15 November): with P.pigment, a cell absorbs light only as far as it holds a
# pigment, one of the four costliest molecules (kinds 12-15, the top of the ladder) kept in its coat, which it makes with its own domains.
rep("{ const ab = P.absorb * Math.max(", "{ const ab = P.absorb * (P.pigment ? pigOf(i) : 1) * Math.max(")

# viruses (Justin's queue, 15 November; virStep in env.js): a cell marked to burst dies; a newborn inherits half its parent's copies
rep("&& !(dor[i] && rng() < P.sporeDeath * (P.env === 'dish' ? P.dishDormDeath : 1));", "&& !(dor[i] && rng() < P.sporeDeath * (P.env === 'dish' ? P.dishDormDeath : 1)) && !(VIR.kill && VIR.kill[i]);")
rep("nalive[i] = 1; ngen[i] = g; nxg[i] = cx; nrsv[i] = 0; ndor[i] = 0; nchanged[i] = 1; births++;", "nalive[i] = 1; ngen[i] = g; nxg[i] = cx; nrsv[i] = 0; ndor[i] = 0; nchanged[i] = 1; births++; virBorn(i, pj); pigBorn(i, pj);")

rep("if ((tick & 7) === 0) fragStep();", "if ((tick & 7) === 0) { fragStep(); virStep(); }")

# the decay economy (Justin, 15 November): a dead cell's stored energy becomes remains (detritus) in its square, which
# heterotrophs break down into sugar (detStep in env.js)
rep("if (chemOn) fragRelease(i); if (coat[i]) { coatReturn(i, 1); coat[i] = 0; } }", "if (chemOn) fragRelease(i); if (coat[i]) { coatReturn(i, 1); coat[i] = 0; } detDie(i); }")
rep("if ((tick & 7) === 0) { fragStep(); virStep(); }", "if ((tick & 7) === 0) { fragStep(); virStep(); } detStep();")

# stage 1 of the genome (Justin, 15 November; design/genome_stage1.md): the line is divided into genes by runs of 4
# identical monomers; each gene folds on its own (infold in env.js; the old one becomes infoldGene); up to 4 reactions
# per gene and 8 per cell (rx and rx2); the line may be 256 long

# the chemistry code goes in before the wiring
GPU = (open(sys.argv[7], encoding='utf-8').read() + '\n') if len(sys.argv) > 7 else ''   # gpu3d.js, optional: before env.js, which reads G3
VIEW = ('\n' + open(sys.argv[8], encoding='utf-8').read()) if len(sys.argv) > 8 else ''   # view3d.js, optional: after the UI wiring
CH = open(sys.argv[4], encoding='utf-8').read() + '\n' + GPU + open(sys.argv[5], encoding='utf-8').read() + '\n' + open(sys.argv[6], encoding='utf-8').read() + VIEW

# ------------------------------------------------------------------ the big new block + init
NEW = open(sys.argv[3], encoding='utf-8').read().replace('//@@CHEMUI@@', CH)
rep('''addEventListener('resize', resize);
resize(); fit(); reset('soup');''', NEW)


# ------------------------------------------------------------------ the user-facing word is "clump": cells that stick together are not a body
import re as _re
_WMAP = {'body':'clump','bodies':'clumps','Body':'Clump','Bodies':'Clumps','BODY':'CLUMP','BODIES':'CLUMPS',
         'spore':'dormant cell','spores':'dormant cells','Spore':'Dormant cell','Spores':'Dormant cells'}   # spores are dormant cells (12 November)
def _word(t):
    return _re.sub(r'\b(body|bodies|Body|Bodies|spores|spore|Spores|Spore)\b', lambda m: _WMAP[m.group(0)], t)
def clumpify(src):
    out = []; i = 0; n = len(src)
    def html_text(seg):                      # replace only between tags, never inside a tag
        parts = _re.split(r'(<style>.*?</style>)', seg, flags=_re.S)    # style sheets are left alone
        return ''.join(p if p.startswith('<style>') else _re.sub(r'>([^<]*)', lambda m: '>' + _word(m.group(1)), p) for p in parts)
    while i < n:
        a = src.find('<script>', i)
        if a < 0: out.append(html_text(src[i:])); break
        out.append(html_text(src[i:a + 8])); b = src.find('</script>', a); js = src[a + 8:b]
        out.append(js_strings(js)); i = b
    return ''.join(out)
def js_strings(js):
    out = []; i = 0; n = len(js); stack = []      # stack of template depths: brace counts inside ${ }
    while i < n:
        c = js[i]
        if stack and stack[-1] >= 0:             # in code inside ${...}
            pass
        if c == '/' and i + 1 < n and js[i + 1] == '/' and not (stack and stack[-1] == -1):
            e = js.find('\n', i); e = n if e < 0 else e; out.append(js[i:e]); i = e; continue
        if c == '/' and i + 1 < n and js[i + 1] == '*':
            e = js.find('*/', i) + 2; out.append(js[i:e]); i = e; continue
        if c == '/' and not (i + 1 < n and js[i + 1] in '/*'):
            k = len(out) - 1
            while k >= 0 and out[k] in ' \t\n': k -= 1
            if k < 0 or out[k][-1] in '(,=:[!&|?{};+-*%<>~^':     # a regular expression literal: copy it as it is
                j = i + 1; inc = False
                while True:
                    d = js[j]
                    if d == '\\': j += 2; continue
                    if d == '[': inc = True
                    elif d == ']': inc = False
                    elif d == '/' and not inc: break
                    j += 1
                out.append(js[i:j + 1]); i = j + 1; continue
        if c in "'\"":
            j = i + 1
            while js[j] != c: j += 2 if js[j] == '\\' else 1
            lit = js[i + 1:j]
            out.append(c + (lit if lit in ('body', 'bodies', 'spore', 'spores') else _word(lit)) + c); i = j + 1; continue
        if c == '`' or (c == '}' and stack and stack[-1] == 0):
            if c == '}': stack.pop()
            j = i + 1; seg = []
            while True:
                d = js[j]
                if d == '\\': seg.append(js[j:j + 2]); j += 2; continue
                if d == '`': break
                if d == '$' and js[j + 1] == '{': break
                seg.append(d); j += 1
            out.append(c + _word(''.join(seg)))
            if js[j] == '`': out.append('`'); i = j + 1
            else: out.append('${'); stack.append(0); i = j + 2
            continue
        if stack:
            if c == '{': stack[-1] += 1
            elif c == '}': stack[-1] -= 1
        out.append(c); i += 1
    return ''.join(out)
# the dish is calm like the even world: no currents, no heat
s = s.replace("P.env === 'even'", "(P.env === 'even' || P.env === 'dish')").replace("P.env !== 'even'", "(P.env !== 'even' && P.env !== 'dish')")
_before = s
s = clumpify(s)

# stage 1 of the genome: every place that stores a cell's reactions stores the second word too
import re as _re
s = _re.sub(r"\brx\[(\w+)\] = lastRx; rxStr\[\1\] = lastRxS;", r"rx[\1] = lastRx; rxStr[\1] = lastRxS; rx2[\1] = lastRx2; rxStr2[\1] = lastRxS2;", s)
for a, b in [("slen = new Uint8Array(N)", "slen = new Uint16Array(N)"), ("slen = new Uint8Array(1)", "slen = new Uint16Array(1)"),
             ("rx = new Uint32Array(N); rxStr = new Uint8Array(N);", "rx = new Uint32Array(N); rxStr = new Uint8Array(N); rx2 = new Uint32Array(N); rxStr2 = new Uint8Array(N);"),
             ("    if (g === ngen[j]) continue;\n    if (chemOn && !swapChem(", "    if (g === ngen[j]) { if (P.seqOn) sameCompN++; continue; }   // same compound: nothing to pay, so the new sequence stays (Justin, 16 November: keep and count)\n    if (chemOn && !swapChem("),
             ("seq.copyWithin(b * SL, a * SL, a * SL + SL);", "seq.copyWithin(b * SL, a * SL, a * SL + slen[a]);"),
             ("rx[b] = rx[a]; rx[a] = 0; rxStr[b] = rxStr[a];", "rx[b] = rx[a]; rx[a] = 0; rxStr[b] = rxStr[a]; rx2[b] = rx2[a]; rx2[a] = 0; rxStr2[b] = rxStr2[a];"),
             ("tuRx = rx[j]; tuRxS = rxStr[j];", "tuRx = rx[j]; tuRxS = rxStr[j]; tuRx2 = rx2[j]; tuRxS2 = rxStr2[j];"),
             ("rx[j] = tuRx; rxStr[j] = tuRxS;", "rx[j] = tuRx; rxStr[j] = tuRxS; rx2[j] = tuRx2; rxStr2[j] = tuRxS2;"),
             ("let tuJ = -1, tuB = 0, tuLen = 0, tuCat = 0, tuRx = 0, tuRxS = 0, tuCH = 0;", "let tuJ = -1, tuB = 0, tuLen = 0, tuCat = 0, tuRx = 0, tuRxS = 0, tuCH = 0, tuRx2 = 0, tuRxS2 = 0;"),
             ("rx: rx[i], rs: rxStr[i],", "rx: rx[i], rs: rxStr[i], rx2: rx2[i], rs2: rxStr2[i],"),
             ("rx[i] = s.rx || 0; rxStr[i] = s.rs || 0;", "rx[i] = s.rx || 0; rxStr[i] = s.rs || 0; rx2[i] = s.rx2 || 0; rxStr2[i] = s.rs2 || 0;")]:
    c = s.count(a); assert c >= 1, ('genome stage 1: not found', a); s = s.replace(a, b)
open(dst, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(s), 'chars')
