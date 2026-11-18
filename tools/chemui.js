// ---------------- chemistry controls
{
  const sel = $('chshow');
  sel.add(new Option('Show: no molecules', 'off')); sel.add(new Option('Show: dominant molecule', 'all')); sel.add(new Option('Show: temperature', 'heat')); sel.add(new Option('Show: signal (quorum)', 'sig')); sel.add(new Option('Show: current (flow)', 'flow')); sel.add(new Option('Show: energy molecule (sugar)', 'energy')); sel.add(new Option('Show: water', 'water')); sel.add(new Option('Show: carbon dioxide', 'co2')); sel.add(new Option('Show: oxygen', 'o2')); sel.add(new Option('Show: surface current', 'sflow')); sel.add(new Option('Show: surface temperature', 'sheat')); sel.add(new Option('Show: rising and sinking water', 'upw')); sel.add(new Option('Show: cutaway', 'cut'));
  PR.forEach((p, k) => sel.add(new Option(`Show: ${p}  (${k < 8 ? 'n=' + (k + 1) : ['motility', 'contagion', 'efficiency', 'hardiness', 'proofreading', 'thermophily', 'inert', 'inert'][k - 8]})`, k)));
  sel.value = P.chshow; sel.onchange = () => { P.chshow = sel.value; };
  $('chroles').innerHTML = PR.map((p, k) => `<div><span class="sw" style="display:inline-block;background:${spCss(k)}"></span> <b>${p}</b> · ` +
    (k < 8 ? `a neighbour count of ${k + 1}: exponent 1 survives with ${k + 1} neighbours, 2 gives birth into squares with ${k + 1}, 3 does both` :
     ['moves (exponent: how strongly it climbs the light)', 'contagion (strength)', 'light efficiency (less light used)', 'hardiness (less death by chance)', 'proofreading (fewer copy errors)', 'prefers warmer water (thermophily)', 'inert', 'inert'][k - 8]) + '</div>').join('');
  for (const id of ['chrich']) $(id).addEventListener('input', () => { chemCapFill(); });
  const vs = $('viewsel'); vs.value = P.view; vs.onchange = () => { P.view = vs.value; };
  document.addEventListener('keydown', e => { if (e.key !== 'i' && e.key !== 'I') return; if (/INPUT|SELECT|TEXTAREA/.test(e.target.tagName) || e.ctrlKey || e.metaKey) return; P.view = P.view === 'ir' ? 'normal' : 'ir'; vs.value = P.view; });
  $('chemOn').addEventListener('change', () => { changed.fill(1); });
  $('chmap').onclick = () => { geoSeed(); chemCapFill(); chem.set(chemCap); changed.fill(1); chemPanel(); };
  const RULE_SL = ['speed', 'mu', 'contagion', 'fusion', 'regrow', 'cost', 'spread', 'birth', 'death', 'hop', 'hopcost', 'nucleate', 'bodyCost', 'chrate', 'chrich', 'chdiff', 'chrecyc', 'chunit', 'kinw', 'terr', 'front', 'dayLen', 'nightDepth', 'heatDiff', 'heatRelax', 'heatHarm', 'heatLife', 'ventPower', 'heatChaos', 'qthr', 'qsave', 'sigspread', 'qmut', 'prodRate', 'prodCost', 'predRate', 'predGain', 'current', 'eleak', 'ebody', 'eeff', 'co2air', 'gasx', 'ferm', 'evap', 'rain', 'dryHarm', 'seasonLen', 'drySeason', 'drift', 'clumpShare', 'clumpHold', 'convect', 'eddies', 'sporeRate', 'wakeRate', 'crossflow', 'seqMu', 'seqDup', 'seqDel', 'seqCost', 'vmix', 'shear', 'coriolis', 'tide', 'sporeLift', 'settle', 'buoy3', 'drag3', 'nz3', 'vdiff3', 'cellLift', 'mateThr', 'hgtHom', 'domDup', 'domMin', 'rxRate', 'rxE', 'coatFrac', 'coatMin', 'mxRetain', 'sinkSize', 'sugarCoat', 'glide', 'dishFood', 'popSugar', 'popSoft'];
  const RULE_CK = ['floor', 'foldOn', 'chemOn', 'gProd', 'gSex', 'gPred', 'gHet', 'gAdh', 'rxn', 'gSpore', 'somaOn', 'autoRestart', 'seqOn', 'catOn', 'nucReg', 'twoLayer', 'water3d', 'domOn', 'domHGT', 'rxDom', 'rxGround', 'cellClumps', 'rxInhib', 'adapt', 'lifeRule', 'fragOn', 'founderModern'];
  const doReset = () => {
    for (const id of RULE_SL) { const el = $(id); el.value = el.defaultValue; el.dispatchEvent(new Event('input')); }
    for (const id of RULE_CK) { const el = $(id); el.checked = el.defaultChecked; el.dispatchEvent(new Event('change')); }
    changed.fill(1);
  };
  document.querySelectorAll('.resetRules').forEach(b => b.onclick = doReset);
}

// ---------------- environment controls
{
  const es = $('envsel'); es.value = P.env;
  es.onchange = () => { P.env = es.value; envInit(); changed.fill(1); if (P.env === 'even') light.fill(1); chemPanel(); };
  $('envnew').onclick = () => { envInit(); chem.set(chemCap); changed.fill(1); chemPanel(); };
}

// ---------------- 3D water: start it when switched on, rebuild its grid when the levels change, and say how it is doing
{
  $('water3d').addEventListener('change', () => { if (P.water3d) { if (!g3Avail()) G3.state = 'none'; else g3Setup(); } });
  $('nz3').addEventListener('change', () => { if (G3.dev) g3Alloc(); });
  const st = $('g3status');
  setInterval(() => {
    st.textContent = !P.water3d ? '' : G3.state === 'ready' ? `running on ${G3.adapter || 'the GPU'}: ${G3.nx}×${G3.ny}×${G3.nz}, ${G3.ms.toFixed(1)} ms a step on the CPU side`
      : G3.state === 'none' ? 'no WebGPU here: the two layers run instead' : G3.state === 'error' ? 'GPU error: the two layers run instead (' + G3.err.slice(0, 80) + ')'
      : G3.state === 'lost' ? 'the GPU was lost: the two layers run instead' : 'starting…';
  }, 1000);
}

{ const b = $('btnBodies'); b.onclick = () => { P.showBodies = !P.showBodies; b.textContent = P.showBodies ? 'Hide clumps' : 'Show clumps'; }; }

// ---------------- one View menu on the world: how the cells look, or what the water holds
{
  const tv = $('topview'), PRN = ['n=1', 'n=2', 'n=3', 'n=4', 'n=5', 'n=6', 'n=7', 'n=8', 'motility', 'contagion', 'efficiency', 'hardiness', 'proofreading', 'thermophily', 'inert', 'inert'];
  const groups = [['Cells', [['v:normal', 'Normal'], ['v:ir', 'Heat vision (infrared)'], ['v:spore', 'Spores']]],
    ['The water', [['c:heat', 'Temperature (floor)'], ['c:flow', 'Current (floor)'], ['c:sheat', 'Temperature (surface)'], ['c:sflow', 'Current (surface), spores aloft'], ['c:upw', 'Rising and sinking water'], ['c:cut', 'Cutaway (side slice)'], ['c:water', 'Water'], ['c:co2', 'Carbon dioxide'], ['c:o2', 'Oxygen'], ['c:energy', 'Sugar'], ['c:sig', 'Quorum signal']]],
    ['Building blocks', [['c:all', 'Most plentiful molecule']].concat(PR.map((p, k) => ['c:' + k, `${p} (${PRN[k]})`]))]];
  tv.innerHTML = groups.map(([g, os]) => `<optgroup label="${g}">` + os.map(([v, t]) => `<option value="${v}">${t}</option>`).join('') + '</optgroup>').join('');
  const cur = () => P.chshow !== 'off' ? 'c:' + P.chshow : 'v:' + (P.view === 'ir' || P.view === 'spore' ? P.view : 'normal');
  if (P.view === 'strat') P.view = 'normal';
  tv.value = cur();
  tv.onchange = () => { const [k, v] = tv.value.split(':'); if (k === 'v') { P.view = v; P.chshow = 'off'; } else { P.view = 'normal'; P.chshow = v; } $('chshow').value = P.chshow; $('viewsel').value = P.view; };
  document.addEventListener('keydown', e => { if ((e.key === 'i' || e.key === 'I') && !/INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) setTimeout(() => { if (P.view === 'ir') P.chshow = 'off'; tv.value = cur(); }, 0); });
  const hd = $('hud'); hd.style.pointerEvents = 'auto'; hd.style.cursor = 'pointer'; hd.onclick = () => { P.hudFull = !P.hudFull; };
}

// ---------------- the menu, tidied (13 November): a compact Start bar at the top, the drawing tools gone, and every
// section folded away under a few headings, in the order: watching, the world, the cell, behaviours, records
{
  const side = document.querySelector('.side'), q = s => document.querySelector(s);
  // the drawing tools are gone: clicking always inspects
  document.querySelectorAll('[data-tool]').forEach(b => { if (b.dataset.tool !== 'inspect') b.remove(); });
  document.querySelectorAll('.side [data-tool="inspect"], .dock [data-tool="inspect"]').forEach(b => { const r = b.parentElement; b.remove(); if (r && r.classList.contains('row') && !r.querySelector('button,select,input')) r.remove(); });
  document.querySelectorAll('.lightonly').forEach(e => e.remove());
  { const lo = $('lightopts'); if (lo) lo.style.display = 'none'; }
  const _setTool = setTool; setTool = () => _setTool('inspect'); setTool('inspect');
  // the Start bar
  const st = document.createElement('div'); st.className = 'card quick';
  const mk = (...els) => { const r = document.createElement('div'); r.className = 'row'; els.forEach(e => e && r.appendChild(e)); st.appendChild(r); return r; };
  const lbl = t => { const s = document.createElement('span'); s.className = 'qlbl'; s.textContent = t; return s; };
  const env = $('envsel'), envRow = env.parentElement;
  { const nb = $('envnew'); nb.textContent = 'Reshuffle'; nb.title = 'New vents and clouds'; }
  { const sp = $('speed').closest('label'); if (sp.firstChild && sp.firstChild.nodeType === 3) sp.firstChild.textContent = 'Speed'; }
  mk(lbl('World'), env, $('envnew'));
  mk(lbl('Start'), $('seedmode'), $('soupshape'));
  const size = $('soupsize').closest('label'), speed = $('speed').closest('label'); size.classList.add('qsl'); speed.classList.add('qsl');
  mk($('play'), $('stepb'), $('reset'));
  mk(speed);
  mk(size);
  { const lr = $('lifeRule').closest('label'); mk(lr); }
  if (envRow && !envRow.querySelector('button,select,input')) envRow.remove();
  side.querySelector('h1').after(st);
  { const ins = q('#insp p'); if (ins) ins.textContent = 'Click a cell to inspect it.'; }
  // fold each section (an h2 and what follows it) into a closed <details>
  const secs = {}; let cur = null;
  for (const el of [...side.children]) {
    if (el.tagName === 'H2') { cur = document.createElement('details'); cur.className = 'sec'; const sm = document.createElement('summary'); sm.textContent = el.textContent; cur.appendChild(sm); secs[el.textContent.toLowerCase()] = cur; el.replaceWith(cur); continue; }
    if (cur && el !== st) cur.appendChild(el);
  }
  const find = k => { for (const t in secs) if (t.startsWith(k)) { const s = secs[t]; delete secs[t]; return s; } return null; };
  const groups = [['Watch', [['inspector', true], ['over time', true]]],
    ['The world', [['environment'], ['rates'], ['chemistry'], ['energy molecule'], ['reactions']]],
    ['The cell', [['line of expression'], ['infolded pairs'], ['sticking together'], ['dormant cells']]],
    ['Behaviours', [['signalling'], ['roles, sex'], ['soma and germ']]],
    ['Records', [['commonest codes'], ['clumps'], ['named forms'], ['chronicle']]]];
  let after = st;
  for (const [g, list] of groups) {
    const h = document.createElement('div'); h.className = 'grp'; h.textContent = g; after.after(h); after = h;
    for (const [k, open] of list) { const s = find(k); if (!s) continue; if (open) s.open = true; after.after(s); after = s; }
  }
  for (const t in secs) { after.after(secs[t]); after = secs[t]; }      // anything not named above keeps its place at the end
  { const ab = document.createElement('details'); ab.className = 'sec'; ab.innerHTML = '<summary>About this page</summary>';
    const intro = side.querySelector(':scope > p'); if (intro) ab.appendChild(intro); after.after(ab); }
  const css = document.createElement('style');
  css.textContent = `.quick{padding:8px 10px}.quick .row{gap:6px;margin:3px 0;flex-wrap:wrap;align-items:center}.quick select{max-width:118px;font-size:12px}.quick button{font-size:12px;padding:3px 8px}
  .qlbl{font-size:11px;color:var(--muted);width:38px}.quick label.qsl{display:flex;gap:6px;align-items:center;font-size:12px;margin:0;flex:1;min-width:150px}.quick label.qsl input{flex:1}
  .grp{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:16px 0 4px}
  details.sec{border-top:1px solid var(--grid);padding:2px 0}details.sec>summary{cursor:pointer;font-weight:600;font-size:14px;padding:6px 0;list-style-position:inside}
  details.sec[open]>summary{margin-bottom:4px}`;
  document.head.appendChild(css);
}

// ---------------- the population dish: its world option, its two dials and the Fold button, in the Start bar
{
  const es = $('envsel'), old = es.onchange;
  es.onchange = () => { const v = es.value; old(); P.dishPop = v === 'dishpop'; if (P.dishPop) P.env = 'dish'; popRow.style.display = P.dishPop ? '' : 'none'; };
  const st = document.querySelector('.quick'), popRow = document.createElement('div'); popRow.style.display = 'none';
  popRow.innerHTML = `<label class="sl qsl" title="Sugar laid in each square of the plate, in divisions' worth">Plate sugar<input type="range" id="popSugar" min="1" max="30" step="0.5" value="5"><output>5</output></label>
   <label class="sl qsl" title="How readily active cells move: on hard agar (0) only where cells and sugar are both plentiful, on soft agar (1) freely">Agar softness<input type="range" id="popSoft" min="0" max="0.3" step="0.005" value="0.02"><output>0.02</output></label>
   <div class="row"><button id="popFold" style="display:none" title="Count the open patch's single cells back into the plate">Fold the patch back</button><span class="qlbl" style="width:auto">Click the plate to open a patch at the scale of single cells.</span></div>`;
  st.appendChild(popRow);
  for (const id of ['popSugar', 'popSoft']) { const el = $(id), out = el.nextElementSibling; el.addEventListener('input', () => { P[id] = +el.value; out.textContent = el.value; }); }
  $('popFold').onclick = () => popFold();
}
