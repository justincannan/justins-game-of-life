import sys, json
from playwright.sync_api import sync_playwright
errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    pg.goto('file:///home/claude/out/digital_life.html'); pg.wait_for_timeout(800)
    pg.click('#musicBtn')
    # record every oscillator frequency the engine sets, as cents above C
    pg.evaluate("""() => { window.__f = new Set(); const o = M.ac.createOscillator().constructor.prototype; 
      const d = Object.getOwnPropertyDescriptor(AudioParam.prototype, 'value');
      const orig = AudioParam.prototype.setTargetAtTime;
      const osc = OscillatorNode.prototype; const nc = BaseAudioContext.prototype.createOscillator;
      BaseAudioContext.prototype.createOscillator = function() { const n = nc.call(this); const p = n.frequency; 
        Object.defineProperty(p, 'value', {set(v) { window.__f.add(v); d.set.call(p, v); }, get() { return d.get.call(p); }}); return n; }; }""")
    for tune, scale in [('12', 'Minor pentatonic'), ('24', 'Minor pentatonic'), ('24', 'Rast (neutral 3rd, 7th)'), ('30', 'Minor pentatonic'), ('30', 'Every step'), ('36', 'Bayati (neutral 2nd, 3rd)')]:
        pg.select_option('#mtune', tune); pg.select_option('#mscale', scale)
        pg.evaluate("() => { __f.clear(); }")
        pg.wait_for_timeout(3000)
        r = pg.evaluate("""() => { const fs = [...__f].filter(f => f > 100 && f < 4000); const cents = [...new Set(fs.map(f => Math.round((1200 * Math.log2(f / 440)) % 1200 + 1200) % 1200))].sort((a,b)=>a-b);
          return {n: fs.length, cents: cents.slice(0, 24), info: document.getElementById('minfo').textContent.slice(0, 70), hint: document.getElementById('mhint').textContent.slice(0, 40)}; }""")
        print(tune, scale, json.dumps(r))
    b.close()
print('ERRORS:', errors or 'none')
