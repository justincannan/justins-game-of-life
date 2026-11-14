import sys, json, time
from playwright.sync_api import sync_playwright

url = 'file://' + sys.argv[1]
shots = sys.argv[2]
errors = []

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True,
                          args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    pg.on('console', lambda m: errors.append('console.' + m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
    pg.goto(url)
    pg.wait_for_timeout(1500)
    pg.screenshot(path=shots + '/1_default.png')

    # ---- music
    pg.click('#musicBtn')
    pg.wait_for_timeout(300)
    # tap the master bus so we can tell silence from sound
    pg.evaluate("""() => { const an = M.ac.createAnalyser(); an.fftSize = 2048; M.master.connect(an); window.__an = an; window.__peak = 0;
      setInterval(() => { const d = new Float32Array(2048); an.getFloatTimeDomainData(d); let m = 0; for (const v of d) m = Math.max(m, Math.abs(v)); window.__peak = Math.max(window.__peak, m); }, 50); }""")
    pg.wait_for_timeout(6000)
    st = pg.evaluate("() => ({on: M.on, state: M.ac.state, steps: M.stepN, peak: window.__peak, info: document.getElementById('minfo').textContent, pop: series[series.length-1].pop, bodies: bodies.size})")
    print('music:', json.dumps(st))
    pg.screenshot(path=shots + '/2_music.png')

    # change scale / key / tempo while playing
    pg.select_option('#mscale', 'Dorian'); pg.select_option('#mroot', '9')
    pg.evaluate("() => { const e = document.getElementById('mtempo'); e.value = 12; e.dispatchEvent(new Event('input')); }")
    pg.wait_for_timeout(2500)
    print('after change:', pg.evaluate("() => document.getElementById('minfo').textContent"))

    # ---- light: draw a stroke with the Light tool, then shade
    pg.keyboard.press('4')
    print('tool', pg.evaluate("() => [tool, stage.dataset.mode, P.showLight]"))
    box = pg.locator('#view').bounding_box()
    cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    pg.mouse.move(cx - 200, cy - 150); pg.mouse.down()
    for k in range(12):
        pg.mouse.move(cx - 200 + k * 30, cy - 150 + k * 6)
    pg.mouse.up()
    pg.keyboard.press('5')
    pg.mouse.move(cx + 100, cy + 100); pg.mouse.down(); pg.mouse.move(cx + 200, cy + 100, steps=6); pg.mouse.up()
    pg.mouse.move(cx, cy + 50)   # leave the brush ring visible
    pg.wait_for_timeout(600)
    print('lamps:', pg.evaluate("() => { let l = 0, s = 0; for (let i = 0; i < N; i++) { if (lamp[i] > 0) l++; else if (lamp[i] < 0) s++; } return {lampCount, l, s}; }"))
    pg.screenshot(path=shots + '/3_light.png')

    # shade really kills: put living cells on a shade
    res = pg.evaluate("""() => { tool = 'paint'; const x0 = 20, y0 = 20; for (let dy = 0; dy < 3; dy++) for (let dx = 0; dx < 3; dx++) { const i = idx(x0+dx, y0+dy); alive[i] = 1; gen[i] = LIFE; changed[i] = 1; }
      tool = 'shade'; stamp(21, 21); const before = alive[idx(21,21)]; for (let k = 0; k < 4; k++) step(); return {before, after: alive[idx(21,21)]}; }""")
    print('shade kill:', res)
    res = pg.evaluate("""() => { tool = 'light'; stamp(200, 40); const i = idx(200,40); for (let k = 0; k < 30; k++) step(); return {lampLevel: lamp[i], light: light[i]}; }""")
    print('lamp holds:', res)
    pg.keyboard.press('1')

    # ---- hide menu
    pg.keyboard.press('h')
    pg.wait_for_timeout(700)
    print('focus:', pg.evaluate("() => [app.classList.contains('focus'), getComputedStyle(document.querySelector('.side')).display, view.getBoundingClientRect().width, cam.s]"))
    pg.screenshot(path=shots + '/4_hidden.png')
    # inspect in hidden mode -> floating card
    pg.mouse.click(cx, cy)
    pg.wait_for_timeout(300)
    print('float shown:', pg.evaluate("() => inspFloat.classList.contains('show')"))
    pg.keyboard.press('4')
    pg.mouse.move(cx - 50, cy + 80)
    pg.wait_for_timeout(300)
    pg.screenshot(path=shots + '/5_hidden_light_tool.png')
    pg.wait_for_timeout(4200)
    print('idle:', pg.evaluate("() => app.classList.contains('idle')"))
    pg.screenshot(path=shots + '/6_idle.png')
    pg.mouse.move(cx + 5, cy + 90)
    pg.wait_for_timeout(500)
    print('woke:', pg.evaluate("() => !app.classList.contains('idle')"))

    # ---- fullscreen (needs a gesture; click the button)
    pg.click('#btnFs')
    pg.wait_for_timeout(800)
    print('fs:', pg.evaluate("() => ({fs: !!document.fullscreenElement, focus: app.classList.contains('focus'), label: btnFs.textContent})"))
    pg.keyboard.press('f')
    pg.wait_for_timeout(800)
    print('fs exit:', pg.evaluate("() => ({fs: !!document.fullscreenElement, focus: app.classList.contains('focus'), label: btnFs.textContent})"))
    pg.keyboard.press('h')
    pg.wait_for_timeout(400)
    print('menu back:', pg.evaluate("() => app.classList.contains('focus')"))

    # ---- reset keeps drawn light; pan with shift in light tool
    pg.evaluate("() => reset('soup')")
    print('lamps after reset:', pg.evaluate("() => lampCount"))
    c0 = pg.evaluate("() => [cam.x, cam.y]")
    pg.keyboard.press('4')
    pg.keyboard.down('Shift'); pg.mouse.move(cx, cy); pg.mouse.down(); pg.mouse.move(cx + 60, cy + 40, steps=5); pg.mouse.up(); pg.keyboard.up('Shift')
    print('pan moved:', c0, pg.evaluate("() => [cam.x, cam.y]"))

    # music off
    pg.click('#musicBtn')
    pg.wait_for_timeout(500)
    print('music off:', pg.evaluate("() => M.on"))
    b.close()

print('ERRORS:', json.dumps(errors, indent=1) if errors else 'none')
