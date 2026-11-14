import sys, json
from playwright.sync_api import sync_playwright
url = 'file://' + sys.argv[1]; shots = sys.argv[2]
errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    pg.on('console', lambda m: errors.append('console.' + m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
    pg.goto(url); pg.wait_for_timeout(2500)
    print('world', pg.evaluate("() => ({W, H, N, zones: Z.n, cam, ready: SYready, zm: Array.from(new Set(zmap)).length})"))
    pg.screenshot(path=shots + '/a_default.png')
    # zones differ
    pg.wait_for_timeout(3000)
    print('step', pg.evaluate("() => ({tick, pop: series[series.length-1] && series[series.length-1].pop})"))
    # music with synth
    pg.click('#musicBtn'); pg.wait_for_timeout(300)
    pg.evaluate("""() => { const c = SY.ctx(), an = c.createAnalyser(); an.fftSize = 2048; window.__sim = an;
      const fr = synthFrame.contentWindow; }""")
    pg.evaluate("""() => { window.__peak = 0; const an = SY.ctx().createAnalyser(); an.fftSize = 2048;
      // tap the destination-side: use a script processor on the context via the synth's capture instead
      window.__h = SY.capture({source:'all', startAt: SY.ctx().currentTime, seconds: 3, name: 'probe', done: (id,msg)=>{ window.__probe = [id,msg]; }}); }""")
    pg.wait_for_timeout(6000)
    print('music', pg.evaluate("() => ({on: M.on, state: SY.state(), steps: M.stepN, info: document.getElementById('minfo').textContent, probe: window.__probe})"))
    pg.screenshot(path=shots + '/b_music.png')
    # loop record, one quarter sweep
    pg.select_option('#reclen', '0.25'); pg.click('#recBtn'); pg.wait_for_timeout(500)
    print('rec msg', pg.evaluate("() => document.getElementById('recmsg').textContent"))
    pg.wait_for_timeout(9000)
    print('loops', pg.evaluate("() => ({list: document.getElementById('looplist').innerText, msg: document.getElementById('recmsg').textContent, samples: SY.samples()})"))
    # layer it
    if pg.locator('#looplist button[data-act=layer]').count():
        pg.click('#looplist button[data-act=layer]'); pg.wait_for_timeout(1500)
        print('layer', pg.evaluate("() => M.layers.size"))
    # open synth
    pg.keyboard.press('s'); pg.wait_for_timeout(800)
    pg.screenshot(path=shots + '/c_synth.png')
    print('synth open', pg.evaluate("() => document.body.classList.contains('synthopen')"))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    print('closed', pg.evaluate("() => !document.body.classList.contains('synthopen')"))
    # zoom out limit + pan clamp
    for i in range(6): pg.click('#zout')
    pg.wait_for_timeout(200)
    print('cam', pg.evaluate("() => ({cam, fit: fitScale()})"))
    # resize window
    pg.set_viewport_size({'width': 900, 'height': 900}); pg.wait_for_timeout(900)
    print('resized', pg.evaluate("() => ({W, H, cam})"))
    pg.screenshot(path=shots + '/d_resized.png')
    # hide menu
    pg.keyboard.press('h'); pg.wait_for_timeout(900)
    print('menu hidden', pg.evaluate("() => ({W, H, cam})"))
    pg.screenshot(path=shots + '/e_hidden.png')
    # zones distinct: compare pop per zone
    print('zone pops', pg.evaluate("() => { const c = new Array(Z.n).fill(0); for (let i=0;i<N;i++) if (alive[i]) c[zmap[i]]++; return c; }"))
    # type to play
    pg.keyboard.press('h'); pg.check('#typeplay'); pg.keyboard.down('a'); pg.wait_for_timeout(300); pg.keyboard.up('a')
    print('errors:', errors[:12])
    b.close()
