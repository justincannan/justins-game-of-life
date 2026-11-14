// ---------------- 3D water on the GPU (WebGPU compute), with the two-layer CPU model as the fallback
// A coarse 3D grid: the chemistry squares (cw x chh) across, P.nz3 levels deep. Level 0 is the floor, where the cells live; the
// top level is the surface, which gives its heat to the air. Each step: carry velocity and heat along the flow (semi-Lagrangian,
// trilinear), add buoyancy, floor drag, the vents' heat and swirl, the air's cooling, spread heat a little, then make the flow
// mass-conserving with a pressure solve (Jacobi). The floor and surface layers, the upwelling just above the floor, and a side slice
// are read back to the CPU each step, one step late, into fx, fy, temp, ux, uy, tsurf and wup, so the rest of the page is unchanged.
const G3 = {state: 'off', dev: null, nx: 0, ny: 0, nz: 0, V: 0, pend: false, steps: 0, reads: 0, ms: 0, err: '', slice: null, sliceRow: 0, needInit: true, tref: .35, lastRead: null};
const G3WG = 64;
const G3_WGSL = /* wgsl */`
struct Prm { nx: i32, ny: i32, nz: i32, row: i32,
  buoy: f32, tref: f32, fdrag: f32, sdrag: f32,
  rf: f32, ra: f32, drag3: f32, diff: f32,
  ax: f32, ay: f32, cor: f32, cur: f32,
  vd: f32, q1: f32, q2: f32, q3: f32 };
@group(0) @binding(0) var<uniform> p: Prm;
@group(0) @binding(1) var<storage, read> A: array<vec4<f32>>;
@group(0) @binding(2) var<storage, read_write> B: array<vec4<f32>>;
@group(0) @binding(3) var<storage, read> src: array<vec4<f32>>;   // per column: heat added at the floor, ambient, swirl x, swirl y
@group(0) @binding(4) var<storage, read> P0: array<f32>;
@group(0) @binding(5) var<storage, read_write> P1: array<f32>;
@group(0) @binding(6) var<storage, read_write> D: array<f32>;
@group(0) @binding(7) var<storage, read_write> O: array<f32>;
@group(0) @binding(8) var<storage, read_write> C: array<vec4<f32>>;   // the same buffer as A, written by diffuse and read after it
@group(0) @binding(9) var<storage, read_write> Part: array<vec4<f32>>; // carried cells: x, y (squares), z (levels), and 1 + how fast it sinks (0: free slot)
fn sampB(q: vec3<f32>) -> vec3<f32> {
  let qz = clamp(q.z, 0.0, f32(p.nz - 1)); let f = floor(vec3<f32>(q.x, q.y, qz)); let t = vec3<f32>(q.x, q.y, qz) - f;
  let x0 = i32(f.x); let y0 = i32(f.y); let z0 = i32(f.z); let z1 = min(z0 + 1, p.nz - 1);
  let a = mix(mix(B[id3(x0, y0, z0)].xyz, B[id3(x0 + 1, y0, z0)].xyz, t.x), mix(B[id3(x0, y0 + 1, z0)].xyz, B[id3(x0 + 1, y0 + 1, z0)].xyz, t.x), t.y);
  let b = mix(mix(B[id3(x0, y0, z1)].xyz, B[id3(x0 + 1, y0, z1)].xyz, t.x), mix(B[id3(x0, y0 + 1, z1)].xyz, B[id3(x0 + 1, y0 + 1, z1)].xyz, t.x), t.y);
  return mix(a, b, t.z);
}
// 5b. carried cells move with the water, and sink a little
@compute @workgroup_size(${G3WG}) fn particles(@builtin(global_invocation_id) g: vec3<u32>) {
  let i = g.x; if (i >= arrayLength(&Part)) { return; }
  var q = Part[i]; if (q.w <= 0.0) { return; }
  let v = sampB(q.xyz);
  q.x = q.x + v.x; q.y = q.y + v.y; q.z = clamp(q.z + v.z - (q.w - 1.0), 0.0, f32(p.nz - 1));
  q.x = q.x - floor(q.x / f32(p.nx)) * f32(p.nx); q.y = q.y - floor(q.y / f32(p.ny)) * f32(p.ny);
  Part[i] = q;
}
fn wrap(a: i32, n: i32) -> i32 { return ((a % n) + n) % n; }
fn id3(x: i32, y: i32, z: i32) -> u32 { return u32((clamp(z, 0, p.nz - 1) * p.ny + wrap(y, p.ny)) * p.nx + wrap(x, p.nx)); }
fn coords(i: u32) -> vec3<i32> { let ii = i32(i); let x = ii % p.nx; let y = (ii / p.nx) % p.ny; let z = ii / (p.nx * p.ny); return vec3<i32>(x, y, z); }
fn samp(q: vec3<f32>) -> vec4<f32> {
  let qz = clamp(q.z, 0.0, f32(p.nz - 1));
  let f = floor(vec3<f32>(q.x, q.y, qz)); let t = vec3<f32>(q.x, q.y, qz) - f;
  let x0 = i32(f.x); let y0 = i32(f.y); let z0 = i32(f.z); let z1 = min(z0 + 1, p.nz - 1);
  let a = mix(mix(A[id3(x0, y0, z0)], A[id3(x0 + 1, y0, z0)], t.x), mix(A[id3(x0, y0 + 1, z0)], A[id3(x0 + 1, y0 + 1, z0)], t.x), t.y);
  let b = mix(mix(A[id3(x0, y0, z1)], A[id3(x0 + 1, y0, z1)], t.x), mix(A[id3(x0, y0 + 1, z1)], A[id3(x0 + 1, y0 + 1, z1)], t.x), t.y);
  return mix(a, b, t.z);
}
// 1. carry velocity and heat along the flow, then add the forces
@compute @workgroup_size(${G3WG}) fn advect(@builtin(global_invocation_id) g: vec3<u32>) {
  let V = u32(p.nx * p.ny * p.nz); let i = g.x; if (i >= V) { return; }
  let c = coords(i); let s = A[i];
  var q = samp(vec3<f32>(f32(c.x) - s.x, f32(c.y) - s.y, f32(c.z) - s.z));
  q.z = q.z + p.buoy * p.cur * (q.w - p.tref);                         // buoyancy: warm water rises, cool water sinks
  q = vec4<f32>(q.xyz * (1.0 - p.drag3), q.w);
  let ci = u32(c.y * p.nx + c.x); let sc = src[ci];
  if (c.z == 0) {                                                       // the floor: drag, the vents' swirl and heat, the tide
    q = vec4<f32>(q.x * (1.0 - p.fdrag) + sc.z + p.ax, q.y * (1.0 - p.fdrag) + sc.w + p.ay, q.z, q.w + p.rf * (sc.y - q.w) + sc.x);
  } else if (c.z == p.nz - 1) {                                         // the surface: little drag, and it gives its heat to the air
    q = vec4<f32>(q.x * (1.0 - p.sdrag) + p.ax, q.y * (1.0 - p.sdrag) + p.ay, q.z, q.w + p.ra * (sc.y - q.w));
  }
  if (p.cor != 0.0) { let u = q.x; let v = q.y; q.x = u + p.cor * v; q.y = v - p.cor * u; }
  B[i] = q;
}
// 2. heat spreads a little (B -> C, which is the buffer A; velocity copied)
@compute @workgroup_size(${G3WG}) fn diffuse(@builtin(global_invocation_id) g: vec3<u32>) {
  let V = u32(p.nx * p.ny * p.nz); let i = g.x; if (i >= V) { return; }
  let c = coords(i); let s = B[i];
  let nh = B[id3(c.x + 1, c.y, c.z)].w + B[id3(c.x - 1, c.y, c.z)].w + B[id3(c.x, c.y + 1, c.z)].w + B[id3(c.x, c.y - 1, c.z)].w;
  let nv = B[id3(c.x, c.y, c.z + 1)].w + B[id3(c.x, c.y, c.z - 1)].w;      // heat spreads up and down more slowly than sideways
  let T = clamp(s.w + p.diff * ((nh + p.vd * nv) / (4.0 + 2.0 * p.vd) - s.w), 0.0, 1.3);
  C[i] = vec4<f32>(s.xyz, T);
}
// 3. the divergence of the flow in C (walls at the floor and the surface: no flow through them)
@compute @workgroup_size(${G3WG}) fn divergence(@builtin(global_invocation_id) g: vec3<u32>) {
  let V = u32(p.nx * p.ny * p.nz); let i = g.x; if (i >= V) { return; }
  let c = coords(i);
  var wu = 0.0; var wd = 0.0;
  if (c.z < p.nz - 1) { wu = C[id3(c.x, c.y, c.z + 1)].z; }
  if (c.z > 0) { wd = C[id3(c.x, c.y, c.z - 1)].z; }
  D[i] = .5 * (C[id3(c.x + 1, c.y, c.z)].x - C[id3(c.x - 1, c.y, c.z)].x + C[id3(c.x, c.y + 1, c.z)].y - C[id3(c.x, c.y - 1, c.z)].y + wu - wd);
}
// 4. one Jacobi pass of the pressure solve (P0 -> P1)
@compute @workgroup_size(${G3WG}) fn jacobi(@builtin(global_invocation_id) g: vec3<u32>) {
  let V = u32(p.nx * p.ny * p.nz); let i = g.x; if (i >= V) { return; }
  let c = coords(i); let own = P0[i];
  var up = own; var dn = own;
  if (c.z < p.nz - 1) { up = P0[id3(c.x, c.y, c.z + 1)]; }
  if (c.z > 0) { dn = P0[id3(c.x, c.y, c.z - 1)]; }
  P1[i] = (P0[id3(c.x + 1, c.y, c.z)] + P0[id3(c.x - 1, c.y, c.z)] + P0[id3(c.x, c.y + 1, c.z)] + P0[id3(c.x, c.y - 1, c.z)] + up + dn - D[i]) / 6.0;
}
// 5. take the pressure gradient off the flow (C -> B); no flow through floor or surface; a speed limit
@compute @workgroup_size(${G3WG}) fn project(@builtin(global_invocation_id) g: vec3<u32>) {
  let V = u32(p.nx * p.ny * p.nz); let i = g.x; if (i >= V) { return; }
  let c = coords(i); let s = C[i]; let own = P0[i];
  var up = own; var dn = own;
  if (c.z < p.nz - 1) { up = P0[id3(c.x, c.y, c.z + 1)]; }
  if (c.z > 0) { dn = P0[id3(c.x, c.y, c.z - 1)]; }
  var v = vec3<f32>(s.x - .5 * (P0[id3(c.x + 1, c.y, c.z)] - P0[id3(c.x - 1, c.y, c.z)]), s.y - .5 * (P0[id3(c.x, c.y + 1, c.z)] - P0[id3(c.x, c.y - 1, c.z)]), s.z - .5 * (up - dn));
  if (c.z == 0 || c.z == p.nz - 1) { v.z = 0.0; }
  let m = length(v); if (m > .9) { v = v * (.9 / m); }
  if (!(m >= 0.0)) { v = vec3<f32>(0.0); }
  B[i] = vec4<f32>(v, s.w);
}
// 6. gather what the CPU reads: per column the floor (u, v, T), the surface (u, v, T) and the upwelling above the floor; and a side slice
@compute @workgroup_size(${G3WG}) fn gather(@builtin(global_invocation_id) g: vec3<u32>) {
  let ncol = u32(p.nx * p.ny); let nsl = u32(p.nx * p.nz); let i = g.x;
  if (i < ncol) {
    let x = i32(i) % p.nx; let y = i32(i) / p.nx;
    let f = B[id3(x, y, 0)]; let s = B[id3(x, y, p.nz - 1)]; let w = B[id3(x, y, 1)].z;
    let o = i * 7u; O[o] = f.x; O[o + 1u] = f.y; O[o + 2u] = f.w; O[o + 3u] = s.x; O[o + 4u] = s.y; O[o + 5u] = s.w; O[o + 6u] = w;
  } else if (i < ncol + nsl) {
    let k = i32(i - ncol); let x = k % p.nx; let z = k / p.nx; let q = B[id3(x, p.row, z)];
    let o = ncol * 7u + u32(k) * 3u; O[o] = q.x; O[o + 1u] = q.z; O[o + 2u] = q.w;
  }
}`;
function g3Avail() { return !!(navigator.gpu); }
// one GPU device for the page, shared by the 3D water and the 3D view
let g3DevP = null;
function g3Device() {
  if (G3.dev) return Promise.resolve(G3.dev);
  if (!g3Avail()) return Promise.resolve(null);
  if (!g3DevP) g3DevP = (async () => {
    // ask for the faster GPU; on Windows the system's per-app graphics setting can still give the browser the integrated one
    const ad = await navigator.gpu.requestAdapter({powerPreference: 'high-performance'}); if (!ad) return null;
    const inf = ad.info || {}; G3.adapter = [inf.vendor, inf.architecture, inf.description].filter(Boolean).join(' ') || 'a GPU';
    G3.dev = await ad.requestDevice(); G3.dev.lost.then(() => { G3.state = 'lost'; G3.dev = null; G3.pipes = null; g3DevP = null; });
    return G3.dev;
  })().catch(e => { G3.err = String(e); g3DevP = null; return null; });
  return g3DevP;
}
function g3Setup() {                                       // one start at a time: a second call waits for the first
  if (!P.water3d) return Promise.resolve();
  if (!g3Avail()) { G3.state = 'none'; return Promise.resolve(); }
  if (!G3.setupP) G3.setupP = g3SetupOnce().finally(() => { G3.setupP = null; });
  return G3.setupP;
}
async function g3SetupOnce() {
  G3.state = 'starting';
  try {
    if (!G3.dev) { await g3Device(); if (!G3.dev) { G3.state = 'none'; return; } }
    if (!G3.pipes) {
      G3.mod = G3.dev.createShaderModule({code: G3_WGSL});
      const info = await G3.mod.getCompilationInfo(); const errs = info.messages.filter(m => m.type === 'error');
      if (errs.length) { G3.state = 'error'; G3.err = errs.map(m => m.lineNum + ': ' + m.message).join('; '); return; }
      G3.pipes = {}; for (const e of ['advect', 'diffuse', 'divergence', 'jacobi', 'project', 'particles', 'gather']) G3.pipes[e] = G3.dev.createComputePipeline({layout: 'auto', compute: {module: G3.mod, entryPoint: e}});
    }
    g3Alloc();
  } catch (e) { G3.state = 'error'; G3.err = String(e); }
}
function g3Alloc() {
  const d = G3.dev; if (!d) return;
  const nx = cw, ny = chh, nz = Math.max(4, Math.min(32, P.nz3 | 0)), V = nx * ny * nz;
  G3.nx = nx; G3.ny = ny; G3.nz = nz; G3.V = V;
  const S = GPUBufferUsage.STORAGE, CD = GPUBufferUsage.COPY_DST, CS = GPUBufferUsage.COPY_SRC;
  // a readback may still be pending on the old staging buffer: leave that one to be collected rather than destroy it mid-map
  for (const k of ['bA', 'bB', 'bSrc', 'bP0', 'bP1', 'bD', 'bO', 'bU', 'bPart', 'bPartCol']) if (G3[k]) G3[k].destroy();
  if (G3.bR && !G3.pend) G3.bR.destroy(); G3.pend = false;
  G3.MP = 4096;                                            // carried cells: slots on the GPU, with their genomes kept here
  G3.bPart = d.createBuffer({size: G3.MP * 16, usage: S | CD | CS}); G3.bPartCol = d.createBuffer({size: G3.MP * 4, usage: S | CD});
  G3.slots = new Array(G3.MP).fill(null); G3.free = []; for (let k = G3.MP - 1; k >= 0; k--) G3.free.push(k); G3.ppos = new Float32Array(G3.MP * 4);
  G3.bA = d.createBuffer({size: V * 16, usage: S | CD | CS}); G3.bB = d.createBuffer({size: V * 16, usage: S | CD | CS});
  G3.bSrc = d.createBuffer({size: nx * ny * 16, usage: S | CD});
  G3.bP0 = d.createBuffer({size: V * 4, usage: S | CD}); G3.bP1 = d.createBuffer({size: V * 4, usage: S | CD}); G3.bD = d.createBuffer({size: V * 4, usage: S});
  G3.osz = (nx * ny * 7 + nx * nz * 3) * 4;
  G3.bO = d.createBuffer({size: G3.osz, usage: S | CS}); G3.bR = d.createBuffer({size: G3.osz + G3.MP * 16, usage: GPUBufferUsage.MAP_READ | CD});
  G3.bU = d.createBuffer({size: 80, usage: GPUBufferUsage.UNIFORM | CD});
  // 'auto' layouts keep only the bindings an entry point uses, so each pipeline gets its own bind groups
  G3.bg = {};
  const all = {0: G3.bU, 1: G3.bA, 2: G3.bB, 3: G3.bSrc, 4: G3.bP0, 5: G3.bP1, 6: G3.bD, 7: G3.bO, 8: G3.bA, 9: G3.bPart};
  for (const e of ['advect', 'diffuse', 'divergence', 'project', 'particles', 'gather']) G3.bg[e] = g3BG(G3.pipes[e].getBindGroupLayout(0), e, all);
  G3.bg.jac0 = g3BG(G3.pipes.jacobi.getBindGroupLayout(0), 'jacobi', {0: G3.bU, 4: G3.bP0, 5: G3.bP1, 6: G3.bD});
  G3.bg.jac1 = g3BG(G3.pipes.jacobi.getBindGroupLayout(0), 'jacobi', {0: G3.bU, 4: G3.bP1, 5: G3.bP0, 6: G3.bD});
  G3.slice = new Float32Array(nx * nz * 3); G3.needInit = true; G3.pend = false; G3.state = 'ready';
}
const G3USE = {advect: [0, 1, 2, 3], diffuse: [0, 2, 8], divergence: [0, 6, 8], jacobi: [0, 4, 5, 6], project: [0, 2, 4, 8], particles: [0, 2, 9], gather: [0, 2, 7]};
function g3BG(layout, entry, bufs) {
  return G3.dev.createBindGroup({layout, entries: G3USE[entry].map(b => ({binding: b, resource: {buffer: bufs[b]}}))});
}
function g3Ready() { return P.water3d && G3.state === 'ready' && G3.nx === cw && G3.ny === chh; }
function g3InitState() {                                   // start the water from the CPU's floor and surface temperatures, at rest
  const {nx, ny, nz, V} = G3, a = new Float32Array(V * 4);
  for (let z = 0; z < nz; z++) { const f = z / (nz - 1); for (let c = 0; c < nx * ny; c++) { const o = (z * nx * ny + c) * 4; a[o + 3] = (1 - f) * temp[c] + f * tsurf[c]; } }
  G3.dev.queue.writeBuffer(G3.bA, 0, a); G3.dev.queue.writeBuffer(G3.bB, 0, a);
  G3.dev.queue.writeBuffer(G3.bP0, 0, new Float32Array(V)); G3.dev.queue.writeBuffer(G3.bP1, 0, new Float32Array(V));
  G3.dev.queue.writeBuffer(G3.bPart, 0, new Float32Array(G3.MP * 4)); G3.slots.fill(null); G3.free = []; for (let k = G3.MP - 1; k >= 0; k--) G3.free.push(k); air = [];
  G3.needInit = false;
}
function g3Step(cur, th, R, hv, hl) {
  const d = G3.dev, {nx, ny, nz, V} = G3, n = nx * ny;
  if (G3.needInit) g3InitState();
  const t0 = performance.now();
  // per column: heat the floor gets (vents, cells), the ambient temperature, and the vents' swirl
  const sb = new Float32Array(n * 4);
  for (let c = 0; c < n; c++) { const o = c * 4; sb[o] = R * (hv * (P.plumeW < 1 ? .3 * vglow[c] + .7 * vhot[c] : vglow[c])) + hl * dens[c] / 16; sb[o + 1] = tamb[c]; sb[o + 2] = fvx[c]; sb[o + 3] = fvy[c]; }
  d.queue.writeBuffer(G3.bSrc, 0, sb);
  const row = vents.length ? ((Math.round(vents[0].y) % ny) + ny) % ny : ny >> 1; G3.sliceRow = row;
  const tx = P.tide > 0 ? .02 * Math.cos(th) * cur * P.tide : 0, ty = P.tide > 0 ? .02 * Math.sin(th) * cur * P.tide : 0;
  const ub = new ArrayBuffer(80), ui = new Int32Array(ub), uf = new Float32Array(ub); uf[16] = P.vdiff3;
  ui[0] = nx; ui[1] = ny; ui[2] = nz; ui[3] = row;
  uf[4] = P.buoy3; uf[5] = G3.tref; uf[6] = P.fdrag; uf[7] = P.sdrag; uf[8] = R * P.floorRelax; uf[9] = R * P.airLoss; uf[10] = P.drag3; uf[11] = Math.min(.9, P.heatDiff * 2);
  uf[12] = tx; uf[13] = ty; uf[14] = P.coriolis; uf[15] = cur > 0 ? 1 : 0;
  d.queue.writeBuffer(G3.bU, 0, ub);
  const enc = d.createCommandEncoder(), wg = Math.ceil(V / G3WG);
  const pass = enc.beginComputePass();
  const run = (e, bg, count) => { pass.setPipeline(G3.pipes[e]); pass.setBindGroup(0, bg); pass.dispatchWorkgroups(count); };
  run('advect', G3.bg.advect, wg); run('diffuse', G3.bg.diffuse, wg); run('divergence', G3.bg.divergence, wg);
  for (let it = 0; it < P.jac3; it++) run('jacobi', it & 1 ? G3.bg.jac1 : G3.bg.jac0, wg);
  const pw = Math.ceil(G3.MP / G3WG), gw = Math.ceil((n + nx * nz) / G3WG);
  if (P.jac3 & 1) { pass.end(); enc.copyBufferToBuffer(G3.bP1, 0, G3.bP0, 0, V * 4); const p2 = enc.beginComputePass(); p2.setPipeline(G3.pipes.project); p2.setBindGroup(0, G3.bg.project); p2.dispatchWorkgroups(wg); p2.setPipeline(G3.pipes.particles); p2.setBindGroup(0, G3.bg.particles); p2.dispatchWorkgroups(pw); p2.setPipeline(G3.pipes.gather); p2.setBindGroup(0, G3.bg.gather); p2.dispatchWorkgroups(gw); p2.end(); }
  else { run('project', G3.bg.project, wg); run('particles', G3.bg.particles, pw); run('gather', G3.bg.gather, gw); pass.end(); }
  enc.copyBufferToBuffer(G3.bB, 0, G3.bA, 0, V * 16);            // the new state is the next step's start
  const read = !G3.pend; if (read) { enc.copyBufferToBuffer(G3.bO, 0, G3.bR, 0, G3.osz); enc.copyBufferToBuffer(G3.bPart, 0, G3.bR, G3.osz, G3.MP * 16); }
  d.queue.submit([enc.finish()]); G3.steps++;
  if (read) {
    G3.pend = true; const readStep = G3.steps, rb = G3.bR, osz = G3.osz, mp = G3.MP;
    G3.lastRead = rb.mapAsync(GPUMapMode.READ).then(() => {
      const raw = rb.getMappedRange().slice(0); rb.unmap();
      if (rb !== G3.bR) return;                              // the grid was rebuilt meanwhile: this reading belongs to the old one
      G3.pend = false; G3.reads++;
      const o = new Float32Array(raw, 0, osz / 4);
      if (G3.nx !== cw || G3.ny !== chh) return;
      g3Carried(new Float32Array(raw, osz, mp * 4), readStep);
      let mf = 0, ms = 0;
      for (let c = 0; c < n; c++) { const q = c * 7; fx[c] = o[q]; fy[c] = o[q + 1]; temp[c] = o[q + 2]; ux[c] = o[q + 3]; uy[c] = o[q + 4]; tsurf[c] = o[q + 5]; wup[c] = o[q + 6]; mf += o[q + 2]; ms += o[q + 5]; }
      G3.tref = .5 * (mf + ms) / n;
      G3.slice.set(o.subarray(n * 7, n * 7 + nx * nz * 3));
    }).catch(e => { G3.pend = false; G3.err = String(e); });
  }
  G3.ms = .9 * G3.ms + .1 * (performance.now() - t0);
}
function g3Sync() { return G3.lastRead || Promise.resolve(); }   // for tests: wait until the last readback has landed
// ---- carried cells in 3D: loose cells and spores over rising water are lifted into the water column, carried by the 3D flow on the
// GPU, sink slowly, and settle back onto the floor where they come down. A cell aloft does not feed or breed; it may die there.
function g3Free(s) { G3.slots[s] = null; G3.free.push(s); G3.dev.queue.writeBuffer(G3.bPart, s * 16, new Float32Array(4)); }
function g3Lift() {
  if (!G3.slots || !(P.current > 0) || P.env === 'even') return;
  const lift = P.sporeLift; if (!(lift > 0)) return;
  const n = cw * chh;
  for (let c = 0; c < n; c++) {
    const w = wup[c]; if (w <= .004 || !G3.free.length) continue;
    const qx = c % cw, qy = (c / cw) | 0;
    for (let dy = 0; dy < 4; dy++) for (let dx = 0; dx < 4; dx++) {
      const x = qx * 4 + dx, y = qy * 4 + dy; if (x >= W || y >= H) continue;
      const i = y * W + x; if (!alive[i] || body[i]) continue;
      let pr = lift * w * 10;
      if (!dor[i]) {                                         // an active cell is lifted only if loose (few neighbours), and less often
        const xm = (x - 1 + W) % W, xp = (x + 1) % W, ym = ((y - 1 + H) % H) * W, y0 = y * W, yp = ((y + 1) % H) * W;
        const nb = alive[ym + xm] + alive[ym + x] + alive[ym + xp] + alive[y0 + xm] + alive[y0 + xp] + alive[yp + xm] + alive[yp + x] + alive[yp + xp];
        if (nb > 2) continue; pr *= P.cellLift;
      }
      if (rng() >= pr || !G3.free.length) continue;
      const s = G3.free.pop(), t = colorSlot(gen[i]);
      G3.slots[s] = {g: gen[i], xg: xg[i], rsv: rsv[i], dor: dor[i], ox: x, oy: y, t0: tick, st: G3.steps, ...seqTake(i)};
      const sink = dor[i] ? P.sinkSpore : P.sinkCell;
      G3.dev.queue.writeBuffer(G3.bPart, s * 16, new Float32Array([(x + .5) / 4 - .5, (y + .5) / 4 - .5, 1, 1 + sink]));
      G3.dev.queue.writeBuffer(G3.bPartCol, s * 4, new Uint32Array([(CV[t] | (CV[t + 1] << 8) | (CV[t + 2] << 16) | (255 << 24)) >>> 0]));
      alive[i] = 0; gen[i] = 0; xg[i] = 0; rsv[i] = 0; dor[i] = 0; changed[i] = 1; airStat.lifted++;
    }
  }
}
function g3Carried(pa, readStep) {
  const list = [];
  for (let s = 0; s < G3.MP; s++) {
    const pl = G3.slots[s]; if (!pl || pl.st >= readStep) { if (pl) list.push({x: pl.ox / 4, y: pl.oy / 4}); continue; }
    const x = pa[s * 4], y = pa[s * 4 + 1], z = pa[s * 4 + 2];
    if (rng() < (pl.dor ? P.sporeDeath * 2 : P.aloftDeath)) { airStat.died++; g3Free(s); continue; }
    if (z < 1 && rng() < P.settle3) {                       // near the floor: it settles into an empty cell of its square, or is lost
      const qx = ((Math.round(x) % cw) + cw) % cw, qy = ((Math.round(y) % chh) + chh) % chh; let landed = -1;
      for (let k = 0; k < 6 && landed < 0; k++) { const cx = Math.min(W - 1, qx * 4 + Math.floor(rng() * 4)), cy = Math.min(H - 1, qy * 4 + Math.floor(rng() * 4)), i = cy * W + cx; if (!alive[i]) landed = i; }
      if (landed < 0) { airStat.lost++; g3Free(s); continue; }
      const i = landed; alive[i] = 1; gen[i] = pl.g; xg[i] = pl.xg; rsv[i] = pl.rsv; dor[i] = pl.dor; body[i] = 0; changed[i] = 1; seqPut(i, pl);
      const cx = i % W, cy = (i / W) | 0, ddx = Math.min(Math.abs(cx - pl.ox), W - Math.abs(cx - pl.ox)), ddy = Math.min(Math.abs(cy - pl.oy), H - Math.abs(cy - pl.oy)), dd = Math.hypot(ddx, ddy);
      airStat.settled++; airStat.dist += dd; airStat.time += tick - pl.t0; if (dd > airStat.maxDist) airStat.maxDist = dd;
      airStat.recent.push(dd); if (airStat.recent.length > 300) airStat.recent.shift();
      g3Free(s); continue;
    }
    G3.ppos[s * 4] = x; G3.ppos[s * 4 + 1] = y; G3.ppos[s * 4 + 2] = z;
    list.push({x: x + .5, y: y + .5, z});
  }
  air = list;                                                // the CPU's picture of what is aloft, for the 2D views and the cutaway
}
// the cutaway in 3D: a side slice through the first vent's row, floor at the bottom, surface at the top
function drawCut3() {
  if (!cutCv) drawCut();
  cutCv.style.display = 'block';
  const {nx, nz} = G3, s = G3.slice; if (!s) return;
  const Wd = Math.max(320, nx * 4), Hd = 170; if (cutCv.width !== Wd) { cutCv.width = Wd; cutCv.height = Hd; }
  const g = cutCv.getContext('2d'), sx = Wd / nx, top = 18, bot = 148, sz = (bot - top) / nz;
  g.clearRect(0, 0, Wd, Hd);
  for (let z = 0; z < nz; z++) for (let x = 0; x < nx; x++) { const o = (z * nx + x) * 3, q = irIdx(s[o + 2]); g.fillStyle = `rgb(${IRL[q]},${IRL[q + 1]},${IRL[q + 2]})`; g.fillRect(x * sx, bot - (z + 1) * sz, sx + .5, sz + .5); }
  g.strokeStyle = 'rgba(240,239,236,.85)'; g.lineWidth = 1;
  const stx = Math.max(1, Math.round(nx / 40)), stz = Math.max(1, Math.round(nz / 8));
  for (let z = 0; z < nz; z += stz) for (let x = 0; x < nx; x += stx) {
    const o = (z * nx + x) * 3, X = (x + .5) * sx, Y = bot - (z + .5) * sz, u = s[o] * 60, w = -s[o + 1] * 400;
    const L = Math.hypot(u, w); if (L < 1) continue; const k = Math.min(1, sx * stx / L);
    g.beginPath(); g.moveTo(X, Y); g.lineTo(X + u * k, Y + w * k); g.stroke();
  }
  g.fillStyle = 'rgba(255,238,190,.95)';
  for (const a of air) if (Math.abs(a.y - G3.sliceRow) < 2) g.fillRect(a.x * sx - 1, top + 3, 2.5, 2.5);
  g.font = '11px system-ui'; g.fillStyle = 'rgba(240,239,236,.85)';
  g.fillText(`3D water on the GPU: a side slice through the first vent's row (y = ${G3.sliceRow}), ${nz} levels; the surface is at the top`, 6, 13);
  g.fillText('colour: temperature · lines: the flow in the slice (sideways and up or down) · pale dots: spores aloft · the floor is at the bottom', 6, Hd - 6);
}
