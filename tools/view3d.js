// ---------------- the 3D view: the water seen as a box, rendered on the GPU (WebGPU), that can be rotated and zoomed
// The floor is the cell picture (the same image the 2D view draws). Above it the water is drawn as a volume by ray marching:
// warm water glows orange, cool water is faintly blue. Arrows sampled through the water show the overturning: orange rising,
// blue sinking, pale sideways. Spores aloft are pale specks near the surface. With the 3D water running, the view reads the GPU's
// own water buffer directly; otherwise it builds a two-level volume (floor and surface) from the two-layer model on the CPU.
const V3 = {cv: null, ctx: null, fmt: null, pipes: null, bgl: null, ub: null, smp: null, tex: null, texW: 0, texH: 0, depth: null, dW: 0, dH: 0,
  fb: null, fbN: 0, lines: null, nLines: 0, linesKey: '', sp: null, spN: 0, bg: null, bgKey: '', yaw: -.65, pitch: .42, dist: 0, tgt: null, boxKey: '',
  drag: null, msg: '', legend: null, running: false, frames: 0, ms: 0};
const V3_WGSL = /* wgsl */`
struct U { vp: mat4x4<f32>, inv: mat4x4<f32>, cam: vec4<f32>, box: vec4<f32>, misc: vec4<f32>, right: vec4<f32>, up: vec4<f32>, lat: vec4<f32>, scr: vec4<f32> };
@group(0) @binding(0) var<uniform> u: U;
@group(0) @binding(1) var<storage, read> S: array<vec4<f32>>;
@group(0) @binding(2) var tex: texture_2d<f32>;
@group(0) @binding(3) var smp: sampler;
@group(0) @binding(4) var<storage, read> Part: array<vec4<f32>>;      // carried cells (from the 3D water), or a dummy
@group(0) @binding(5) var<storage, read> PartCol: array<u32>;
// a cube, 36 corners from the vertex index: 6 faces of 2 triangles, with the face's normal for shading
fn cubeCorner(vi: u32) -> array<vec3<f32>, 2> {
  var N = array<vec3<f32>, 6>(vec3<f32>(1.0, 0.0, 0.0), vec3<f32>(-1.0, 0.0, 0.0), vec3<f32>(0.0, 1.0, 0.0), vec3<f32>(0.0, -1.0, 0.0), vec3<f32>(0.0, 0.0, 1.0), vec3<f32>(0.0, 0.0, -1.0));
  var A = array<vec3<f32>, 6>(vec3<f32>(0.0, 1.0, 0.0), vec3<f32>(0.0, 0.0, 1.0), vec3<f32>(0.0, 0.0, 1.0), vec3<f32>(1.0, 0.0, 0.0), vec3<f32>(1.0, 0.0, 0.0), vec3<f32>(0.0, 1.0, 0.0));
  var Bt = array<vec3<f32>, 6>(vec3<f32>(0.0, 0.0, 1.0), vec3<f32>(0.0, 1.0, 0.0), vec3<f32>(1.0, 0.0, 0.0), vec3<f32>(0.0, 0.0, 1.0), vec3<f32>(0.0, 1.0, 0.0), vec3<f32>(1.0, 0.0, 0.0));
  var Q = array<vec2<f32>, 6>(vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, -1.0), vec2<f32>(1.0, 1.0), vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, 1.0), vec2<f32>(-1.0, 1.0));
  let f = vi / 6u; let q = Q[vi % 6u];
  return array<vec3<f32>, 2>((N[f] + A[f] * q.x + Bt[f] * q.y) * .5, N[f]);
}
fn shade(n: vec3<f32>) -> f32 { return .42 + .58 * max(dot(n, normalize(vec3<f32>(.45, 1.0, .3))), 0.0); }
// cells on the floor: one cube per living cell, coloured as in the 2D view
@vertex fn vsCell(@builtin(vertex_index) vi: u32, @location(0) p: vec3<f32>, @location(1) c: vec4<f32>) -> LO {
  let k = cubeCorner(vi); let s = .25;
  var o: LO; o.pos = u.vp * vec4<f32>(p + k[0] * s + vec3<f32>(0.0, s * .5, 0.0), 1.0); o.c = vec4<f32>(c.rgb * shade(k[1]), 1.0); return o;
}
// carried cells: their positions come straight from the 3D water's particle buffer on the GPU
@vertex fn vsPart(@builtin(vertex_index) vi: u32, @builtin(instance_index) ii: u32) -> LO {
  let q = Part[ii]; var o: LO;
  if (q.w <= 0.0) { o.pos = vec4<f32>(2.0, 2.0, 2.0, 1.0); o.c = vec4<f32>(0.0); return o; }
  let k = cubeCorner(vi); let s = .32;
  let w = vec3<f32>(q.x + .5, (q.z + .5) / u.box.z * u.box.w, q.y + .5);
  let cc = PartCol[ii]; let col = vec3<f32>(f32(cc & 255u), f32((cc >> 8u) & 255u), f32((cc >> 16u) & 255u)) / 255.0;
  o.pos = u.vp * vec4<f32>(w + k[0] * s, 1.0); o.c = vec4<f32>(mix(col, vec3<f32>(1.0, .95, .8), .25) * shade(k[1]), 1.0); return o;
}
fn wrapi(a: i32, n: i32) -> i32 { return ((a % n) + n) % n; }
fn sid(x: i32, y: i32, z: i32) -> u32 { let nx = i32(u.box.x); let ny = i32(u.box.y); let nz = i32(u.box.z); return u32((clamp(z, 0, nz - 1) * ny + wrapi(y, ny)) * nx + wrapi(x, nx)); }
fn sampT(g: vec3<f32>) -> f32 {                         // trilinear temperature at grid coordinates (x, y across; z up)
  let nz = u.box.z; let q = vec3<f32>(g.x, g.y, clamp(g.z, 0.0, nz - 1.0)); let f = floor(q); let t = q - f;
  let x0 = i32(f.x); let y0 = i32(f.y); let z0 = i32(f.z); let z1 = min(z0 + 1, i32(nz) - 1);
  let a = mix(mix(S[sid(x0, y0, z0)].w, S[sid(x0 + 1, y0, z0)].w, t.x), mix(S[sid(x0, y0 + 1, z0)].w, S[sid(x0 + 1, y0 + 1, z0)].w, t.x), t.y);
  let b = mix(mix(S[sid(x0, y0, z1)].w, S[sid(x0 + 1, y0, z1)].w, t.x), mix(S[sid(x0, y0 + 1, z1)].w, S[sid(x0 + 1, y0 + 1, z1)].w, t.x), t.y);
  return mix(a, b, t.z);
}
// the floor: the cell picture
struct FO { @builtin(position) pos: vec4<f32>, @location(0) uv: vec2<f32> };
@vertex fn vsFloor(@builtin(vertex_index) i: u32) -> FO {
  var q = array<vec2<f32>, 6>(vec2<f32>(0.0, 0.0), vec2<f32>(1.0, 0.0), vec2<f32>(1.0, 1.0), vec2<f32>(0.0, 0.0), vec2<f32>(1.0, 1.0), vec2<f32>(0.0, 1.0));
  let t = q[i]; var o: FO; o.pos = u.vp * vec4<f32>(t.x * u.box.x, 0.0, t.y * u.box.y, 1.0); o.uv = vec2<f32>(t.x * u.misc.y, t.y * u.misc.z); return o;
}
@fragment fn fsFloor(i: FO) -> @location(0) vec4<f32> { let c = textureSample(tex, smp, min(i.uv, vec2<f32>(.9999))).rgb; return vec4<f32>(c * .38 + vec3<f32>(.02, .03, .05), 1.0); }   // dimmed: the cells stand on it as blocks
// the water: a volume, marched front to back
struct VO { @builtin(position) pos: vec4<f32> };
@vertex fn vsFull(@builtin(vertex_index) i: u32) -> VO { var q = array<vec2<f32>, 3>(vec2<f32>(-1.0, -1.0), vec2<f32>(3.0, -1.0), vec2<f32>(-1.0, 3.0)); var o: VO; o.pos = vec4<f32>(q[i], 0.0, 1.0); return o; }
@fragment fn fsVol(i: VO) -> @location(0) vec4<f32> {
  let ndc = vec2<f32>(i.pos.x / u.scr.x * 2.0 - 1.0, 1.0 - i.pos.y / u.scr.y * 2.0);
  let a4 = u.inv * vec4<f32>(ndc, 0.0, 1.0); let b4 = u.inv * vec4<f32>(ndc, 1.0, 1.0);
  let ro = a4.xyz / a4.w; let rd = normalize(b4.xyz / b4.w - ro);
  let bmax = vec3<f32>(u.box.x, u.box.w, u.box.y);
  let inv = 1.0 / rd; let t0 = (vec3<f32>(0.0) - ro) * inv; let t1 = (bmax - ro) * inv;
  let tn = max(max(min(t0.x, t1.x), min(t0.y, t1.y)), min(t0.z, t1.z)); let tf = min(min(max(t0.x, t1.x), max(t0.y, t1.y)), max(t0.z, t1.z));
  if (tf <= max(tn, 0.0)) { return vec4<f32>(0.0); }
  let ta = max(tn, 0.0); let n = 96; let dt = (tf - ta) / f32(n);
  let k = dt / (u.box.w * .02);                          // opacity per step, independent of the box's size
  var col = vec3<f32>(0.0); var acc = 0.0;
  for (var s = 0; s < n; s = s + 1) {
    let p = ro + rd * (ta + (f32(s) + .5) * dt);
    let T = sampT(vec3<f32>(p.x - .5, p.z - .5, p.y / u.box.w * u.box.z - .5));
    let an = T - u.misc.x;
    var c = vec3<f32>(.10, .22, .40); var al = .006 * k;                      // the water itself: a faint blue
    if (an > .04) { let h = clamp((an - .04) * 4.0, 0.0, 1.0); c = mix(vec3<f32>(.85, .30, .18), vec3<f32>(1.0, .78, .35), h); al = al + clamp((an - .04) * u.misc.w, 0.0, .5) * k; }
    else if (an < 0.0) { c = mix(c, vec3<f32>(.35, .55, .95), clamp(-an * 6.0, 0.0, 1.0)); al = al + clamp(-an * u.misc.w * .15, 0.0, .05) * k; }
    al = clamp(al, 0.0, 1.0);
    col = col + (1.0 - acc) * c * al; acc = acc + (1.0 - acc) * al;
    if (acc > .97) { break; }
  }
  return vec4<f32>(col, acc);
}
// lines: the box's edges and the boundary between the layers
struct LO { @builtin(position) pos: vec4<f32>, @location(0) c: vec4<f32> };
@vertex fn vsLine(@location(0) p: vec3<f32>, @location(1) c: vec4<f32>) -> LO { var o: LO; o.pos = u.vp * vec4<f32>(p, 1.0); o.c = c; return o; }
@fragment fn fsLine(i: LO) -> @location(0) vec4<f32> { return vec4<f32>(i.c.rgb * i.c.a, i.c.a); }
// arrows: the flow sampled on a lattice through the water
@vertex fn vsArrow(@builtin(vertex_index) vi: u32) -> LO {
  let ax = u32(u.lat.x); let ay = u32(u.lat.y); let az = u32(u.lat.z);
  let a = vi / 6u; let part = vi % 6u;
  let ix = a % ax; let iy = (a / ax) % ay; let iz = a / (ax * ay);
  let nx = u.box.x; let ny = u.box.y; let nz = u.box.z; let H = u.box.w;
  let gx = (f32(ix) + .5) * nx / f32(ax); let gy = (f32(iy) + .5) * ny / f32(ay); let gz = (f32(iz) + .5) * nz / f32(az);
  let v = S[sid(i32(gx), i32(gy), i32(gz))].xyz;
  let base = vec3<f32>(gx, (floor(gz) + .5) / nz * H, gy);
  let d = vec3<f32>(v.x, v.z * H / nz * u.lat.w * 6.0, v.y);   // vertical motion is shown stretched, so the slow sinking is visible
  let m = length(d);
  var o: LO;
  if (m < 1e-4) { o.pos = vec4<f32>(2.0, 2.0, 2.0, 1.0); o.c = vec4<f32>(0.0); return o; }
  let L = min(m * u.lat.w * 40.0, nx / f32(ax) * 1.4); let dir = d / m; let tip = base + dir * L;
  let side = normalize(cross(dir, normalize(tip - u.cam.xyz)) + vec3<f32>(1e-5, 0.0, 0.0)) * L * .18;
  var p = base;
  if (part == 1u) { p = tip; } else if (part == 2u) { p = tip; } else if (part == 3u) { p = tip - dir * L * .3 + side; }
  else if (part == 4u) { p = tip; } else if (part == 5u) { p = tip - dir * L * .3 - side; }
  let up = v.z * H / nz;
  var c = vec4<f32>(.95, .92, .85, .85);
  if (up > .0004) { c = vec4<f32>(1.0, .70, .40, .95); } else if (up < -.0002) { c = vec4<f32>(.60, .78, 1.0, .95); }
  o.pos = u.vp * vec4<f32>(p, 1.0); o.c = c; return o;
}
// spores aloft: small pale squares that face the camera
@vertex fn vsSpore(@builtin(vertex_index) vi: u32, @location(0) p: vec3<f32>) -> LO {
  var q = array<vec2<f32>, 6>(vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, -1.0), vec2<f32>(1.0, 1.0), vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, 1.0), vec2<f32>(-1.0, 1.0));
  let t = q[vi] * u.cam.w;
  var o: LO; o.pos = u.vp * vec4<f32>(p + u.right.xyz * t.x + u.up.xyz * t.y, 1.0); o.c = vec4<f32>(1.0, .93, .74, .95); return o;
}`;
// ---- small matrix helpers (column-major, as WGSL reads them)
const m4 = {
  mul(a, b) { const r = new Float32Array(16); for (let c = 0; c < 4; c++) for (let rr = 0; rr < 4; rr++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + rr] * b[c * 4 + k]; r[c * 4 + rr] = s; } return r; },
  persp(fy, asp, n, f) { const t = 1 / Math.tan(fy / 2), r = new Float32Array(16); r[0] = t / asp; r[5] = t; r[10] = f / (n - f); r[11] = -1; r[14] = n * f / (n - f); return r; },
  look(e, t, up) {
    const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], cr = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    const nr = a => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }, dt = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    const z = nr(sub(e, t)), x = nr(cr(up, z)), y = cr(z, x);
    return {m: new Float32Array([x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dt(x, e), -dt(y, e), -dt(z, e), 1]), x, y};
  },
  inv(m) {
    const a = m, r = new Float32Array(16);
    const b00 = a[0] * a[5] - a[1] * a[4], b01 = a[0] * a[6] - a[2] * a[4], b02 = a[0] * a[7] - a[3] * a[4], b03 = a[1] * a[6] - a[2] * a[5], b04 = a[1] * a[7] - a[3] * a[5], b05 = a[2] * a[7] - a[3] * a[6];
    const b06 = a[8] * a[13] - a[9] * a[12], b07 = a[8] * a[14] - a[10] * a[12], b08 = a[8] * a[15] - a[11] * a[12], b09 = a[9] * a[14] - a[10] * a[13], b10 = a[9] * a[15] - a[11] * a[13], b11 = a[10] * a[15] - a[11] * a[14];
    let d = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06; if (!d) return r; d = 1 / d;
    r[0] = (a[5] * b11 - a[6] * b10 + a[7] * b09) * d; r[1] = (a[2] * b10 - a[1] * b11 - a[3] * b09) * d; r[2] = (a[13] * b05 - a[14] * b04 + a[15] * b03) * d; r[3] = (a[10] * b04 - a[9] * b05 - a[11] * b03) * d;
    r[4] = (a[6] * b08 - a[4] * b11 - a[7] * b07) * d; r[5] = (a[0] * b11 - a[2] * b08 + a[3] * b07) * d; r[6] = (a[14] * b02 - a[12] * b05 - a[15] * b01) * d; r[7] = (a[8] * b05 - a[10] * b02 + a[11] * b01) * d;
    r[8] = (a[4] * b10 - a[5] * b08 + a[7] * b06) * d; r[9] = (a[1] * b08 - a[0] * b10 - a[3] * b06) * d; r[10] = (a[12] * b04 - a[13] * b02 + a[15] * b00) * d; r[11] = (a[9] * b02 - a[8] * b04 - a[11] * b00) * d;
    r[12] = (a[5] * b07 - a[4] * b09 - a[6] * b06) * d; r[13] = (a[0] * b09 - a[1] * b07 + a[2] * b06) * d; r[14] = (a[13] * b01 - a[12] * b03 - a[14] * b00) * d; r[15] = (a[8] * b03 - a[9] * b01 + a[10] * b00) * d;
    return r;
  }
};
const V3LAT = [12, 8, 3];                                 // arrows: across, across, levels
async function v3Init() {
  const st = document.getElementById('stage');
  if (!V3.cv) {
    V3.cv = document.createElement('canvas'); V3.cv.id = 'view3d';
    Object.assign(V3.cv.style, {position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', zIndex: 2, display: 'none', cursor: 'grab', touchAction: 'none', background: '#06080c'});
    st.appendChild(V3.cv);
    V3.legend = document.createElement('div');
    Object.assign(V3.legend.style, {position: 'absolute', left: '10px', bottom: '10px', zIndex: 3, display: 'none', color: '#d8d6cf', font: '12px system-ui', background: 'rgba(10,12,16,.72)', padding: '6px 9px', borderRadius: '6px', pointerEvents: 'none', maxWidth: 'calc(100% - 140px)'});
    st.appendChild(V3.legend);
    for (const el of st.querySelectorAll('.topbtns, .hud')) el.style.zIndex = 5;   // the menu and the status line stay above the 3D view
    v3Controls();
  }
  if (V3.pipes) return true;
  const dev = await g3Device(); if (!dev) { V3.msg = 'The 3D view needs WebGPU, which this browser does not offer.'; return false; }
  V3.ctx = V3.cv.getContext('webgpu'); V3.fmt = navigator.gpu.getPreferredCanvasFormat();
  V3.ctx.configure({device: dev, format: V3.fmt, alphaMode: 'opaque'});
  const mod = dev.createShaderModule({code: V3_WGSL});
  const info = await mod.getCompilationInfo(); const errs = info.messages.filter(m => m.type === 'error');
  if (errs.length) { V3.msg = '3D view shader error: ' + errs.map(m => m.lineNum + ': ' + m.message).join('; '); return false; }
  const VF = GPUShaderStage.VERTEX | GPUShaderStage.FRAGMENT;
  V3.bgl = dev.createBindGroupLayout({entries: [{binding: 0, visibility: VF, buffer: {type: 'uniform'}}, {binding: 1, visibility: VF, buffer: {type: 'read-only-storage'}},
    {binding: 2, visibility: GPUShaderStage.FRAGMENT, texture: {}}, {binding: 3, visibility: GPUShaderStage.FRAGMENT, sampler: {}},
    {binding: 4, visibility: GPUShaderStage.VERTEX, buffer: {type: 'read-only-storage'}}, {binding: 5, visibility: GPUShaderStage.VERTEX, buffer: {type: 'read-only-storage'}}]});
  V3.dummy = dev.createBuffer({size: 16, usage: GPUBufferUsage.STORAGE});
  const layout = dev.createPipelineLayout({bindGroupLayouts: [V3.bgl]});
  const blend = {color: {srcFactor: 'one', dstFactor: 'one-minus-src-alpha'}, alpha: {srcFactor: 'one', dstFactor: 'one-minus-src-alpha'}};
  const ds = (write, cmp) => ({format: 'depth24plus', depthWriteEnabled: write, depthCompare: cmp});
  V3.pipes = {
    floor: dev.createRenderPipeline({layout, vertex: {module: mod, entryPoint: 'vsFloor'}, fragment: {module: mod, entryPoint: 'fsFloor', targets: [{format: V3.fmt}]}, primitive: {topology: 'triangle-list'}, depthStencil: ds(true, 'less')}),
    vol: dev.createRenderPipeline({layout, vertex: {module: mod, entryPoint: 'vsFull'}, fragment: {module: mod, entryPoint: 'fsVol', targets: [{format: V3.fmt, blend}]}, primitive: {topology: 'triangle-list'}, depthStencil: ds(false, 'always')}),
    line: dev.createRenderPipeline({layout, vertex: {module: mod, entryPoint: 'vsLine', buffers: [{arrayStride: 28, attributes: [{shaderLocation: 0, offset: 0, format: 'float32x3'}, {shaderLocation: 1, offset: 12, format: 'float32x4'}]}]},
      fragment: {module: mod, entryPoint: 'fsLine', targets: [{format: V3.fmt, blend}]}, primitive: {topology: 'line-list'}, depthStencil: ds(false, 'less')}),
    arrow: dev.createRenderPipeline({layout, vertex: {module: mod, entryPoint: 'vsArrow'}, fragment: {module: mod, entryPoint: 'fsLine', targets: [{format: V3.fmt, blend}]}, primitive: {topology: 'line-list'}, depthStencil: ds(false, 'less')}),
    cell: dev.createRenderPipeline({layout, vertex: {module: mod, entryPoint: 'vsCell', buffers: [{arrayStride: 16, stepMode: 'instance', attributes: [{shaderLocation: 0, offset: 0, format: 'float32x3'}, {shaderLocation: 1, offset: 12, format: 'unorm8x4'}]}]},
      fragment: {module: mod, entryPoint: 'fsLine', targets: [{format: V3.fmt}]}, primitive: {topology: 'triangle-list'}, depthStencil: ds(true, 'less')}),
    part: dev.createRenderPipeline({layout, vertex: {module: mod, entryPoint: 'vsPart'}, fragment: {module: mod, entryPoint: 'fsLine', targets: [{format: V3.fmt}]}, primitive: {topology: 'triangle-list'}, depthStencil: ds(true, 'less')}),
    spore: dev.createRenderPipeline({layout, vertex: {module: mod, entryPoint: 'vsSpore', buffers: [{arrayStride: 12, stepMode: 'instance', attributes: [{shaderLocation: 0, offset: 0, format: 'float32x3'}]}]},
      fragment: {module: mod, entryPoint: 'fsLine', targets: [{format: V3.fmt, blend}]}, primitive: {topology: 'triangle-list'}, depthStencil: ds(false, 'less')})
  };
  V3.ub = dev.createBuffer({size: 256, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST});
  V3.smp = dev.createSampler({magFilter: 'nearest', minFilter: 'linear'});
  return true;
}
function v3Controls() {
  const cv = V3.cv;
  cv.addEventListener('contextmenu', e => e.preventDefault());
  cv.addEventListener('pointerdown', e => { cv.setPointerCapture(e.pointerId); V3.drag = {x: e.clientX, y: e.clientY, pan: e.button === 2 || e.shiftKey, yaw: V3.yaw, pitch: V3.pitch, tgt: V3.tgt.slice()}; cv.style.cursor = 'grabbing'; });
  cv.addEventListener('pointermove', e => {
    const d = V3.drag; if (!d) return; const dx = e.clientX - d.x, dy = e.clientY - d.y;
    if (d.pan) {                                            // pan across the floor, in the camera's own directions
      const s = V3.dist / 700, rx = Math.cos(V3.yaw), rz = -Math.sin(V3.yaw), fx_ = -Math.sin(V3.yaw), fz = -Math.cos(V3.yaw);
      V3.tgt = [d.tgt[0] - dx * s * rx + dy * s * fx_, d.tgt[1], d.tgt[2] - dx * s * rz + dy * s * fz];
    } else { V3.yaw = d.yaw - dx * .006; V3.pitch = Math.max(.05, Math.min(1.5, d.pitch + dy * .005)); }
  });
  const up = () => { V3.drag = null; cv.style.cursor = 'grab'; };
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('wheel', e => { e.preventDefault(); V3.dist = Math.max(1.5, Math.min(5000, V3.dist * Math.exp(e.deltaY * .0012))); }, {passive: false});
  cv.addEventListener('dblclick', () => { V3.boxKey = ''; });           // double-click: back to the starting view
}
function v3Source() {                                       // where the water comes from: the GPU's 3D buffer, or the two layers
  const dev = G3.dev;
  if (typeof g3Ready === 'function' && g3Ready() && G3.bA) return {buf: G3.bA, nz: G3.nz, tref: G3.tref, kind: '3D water on the GPU, ' + G3.nz + ' levels'};
  const n = cw * chh, nz = 2;
  if (!V3.fb || V3.fbN !== n) { if (V3.fb) V3.fb.destroy(); V3.fb = dev.createBuffer({size: n * nz * 16, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST}); V3.fbN = n; V3.fbData = new Float32Array(n * nz * 4); }
  const a = V3.fbData; let mt = 0;
  for (let c = 0; c < n; c++) { const o = c * 4, o2 = (n + c) * 4; a[o] = fx[c]; a[o + 1] = fy[c]; a[o + 2] = wup[c]; a[o + 3] = temp[c]; a[o2] = ux[c]; a[o2 + 1] = uy[c]; a[o2 + 2] = 0; a[o2 + 3] = tsurf[c]; mt += temp[c] + tsurf[c]; }
  dev.queue.writeBuffer(V3.fb, 0, a);
  return {buf: V3.fb, nz, tref: mt / (2 * n), kind: P.twoLayer ? 'the two layers (floor and surface)' : 'the floor layer'};
}
function v3Lines(nx, ny, Hb) {
  const key = nx + ',' + ny + ',' + Hb; if (V3.linesKey === key) return; V3.linesKey = key;
  const L = [], e = (a, b, c) => L.push(a[0], a[1], a[2], c[0], c[1], c[2], c[3], b[0], b[1], b[2], c[0], c[1], c[2], c[3]);
  const C = [.72, .85, .98, .75], C2 = [.72, .85, .98, .35];
  const P8 = [[0, 0, 0], [nx, 0, 0], [nx, 0, ny], [0, 0, ny], [0, Hb, 0], [nx, Hb, 0], [nx, Hb, ny], [0, Hb, ny]];
  for (const [a, b] of [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]]) e(P8[a], P8[b], C);
  const h = Hb * .5, seg = Math.max(nx, ny) / 40;          // the boundary between the layers, dashed
  for (const [x0, z0, x1, z1] of [[0, 0, nx, 0], [nx, 0, nx, ny], [nx, ny, 0, ny], [0, ny, 0, 0]]) {
    const len = Math.hypot(x1 - x0, z1 - z0), k = Math.floor(len / seg);
    for (let s = 0; s < k; s += 2) { const t0 = s / k, t1 = Math.min(1, (s + 1) / k); e([x0 + (x1 - x0) * t0, h, z0 + (z1 - z0) * t0], [x0 + (x1 - x0) * t1, h, z0 + (z1 - z0) * t1], C2); }
  }
  const data = new Float32Array(L);
  if (V3.lines) V3.lines.destroy();
  V3.lines = G3.dev.createBuffer({size: data.byteLength, usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST}); G3.dev.queue.writeBuffer(V3.lines, 0, data); V3.nLines = data.length / 7;
}
function v3Frame() {
  const dev = G3.dev; if (!dev || !V3.pipes) return;
  const t0 = performance.now();
  const r = V3.cv.getBoundingClientRect(), dpr = Math.min(2, devicePixelRatio || 1), Wp = Math.max(1, Math.round(r.width * dpr)), Hp = Math.max(1, Math.round(r.height * dpr));
  if (V3.cv.width !== Wp || V3.cv.height !== Hp) { V3.cv.width = Wp; V3.cv.height = Hp; }
  if (!V3.depth || V3.dW !== Wp || V3.dH !== Hp) { if (V3.depth) V3.depth.destroy(); V3.depth = dev.createTexture({size: [Wp, Hp], format: 'depth24plus', usage: GPUTextureUsage.RENDER_ATTACHMENT}); V3.dW = Wp; V3.dH = Hp; }
  const nx = cw, ny = chh, Hb = .42 * Math.max(nx, ny);
  // the floor's picture: the 2D view's image of the cells
  if (!V3.tex || V3.texW !== W || V3.texH !== H) { if (V3.tex) V3.tex.destroy(); V3.tex = dev.createTexture({size: [W, H], format: 'rgba8unorm', usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST | GPUTextureUsage.RENDER_ATTACHMENT}); V3.texW = W; V3.texH = H; V3.bgKey = ''; }
  dev.queue.copyExternalImageToTexture({source: off}, {texture: V3.tex}, [W, H]);
  const src = v3Source(), gpuParts = src.buf !== V3.fb && G3.bPart;
  const pb = gpuParts ? G3.bPart : V3.dummy, pc = gpuParts ? G3.bPartCol : V3.dummy;
  const bk = nx + ',' + ny + ',' + src.nz + ',' + (src.buf === V3.fb ? 'f' : 'g') + V3.texW + 'x' + V3.texH;
  if (V3.bgKey !== bk || V3.bgBuf !== src.buf || V3.bgTex !== V3.tex || V3.bgPart !== pb) {
    V3.bg = dev.createBindGroup({layout: V3.bgl, entries: [{binding: 0, resource: {buffer: V3.ub}}, {binding: 1, resource: {buffer: src.buf}}, {binding: 2, resource: V3.tex.createView()}, {binding: 3, resource: V3.smp},
      {binding: 4, resource: {buffer: pb}}, {binding: 5, resource: {buffer: pc}}]});
    V3.bgKey = bk; V3.bgBuf = src.buf; V3.bgTex = V3.tex; V3.bgPart = pb;
  }
  // the cells on the floor, as blocks: rebuilt when the world has moved on
  if (V3.cellTick !== tick || !V3.cells) {
    V3.cellTick = tick; const d = img.data;
    let n = 0; for (let i = 0; i < N; i++) n += alive[i];
    if (!V3.cells || V3.cellCap < n) { if (V3.cells) V3.cells.destroy(); V3.cellCap = Math.max(4096, Math.ceil(n * 1.5)); V3.cells = dev.createBuffer({size: V3.cellCap * 16, usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST}); V3.cellAB = new ArrayBuffer(V3.cellCap * 16); }
    const f = new Float32Array(V3.cellAB), u8 = new Uint8Array(V3.cellAB); let k = 0;
    for (let i = 0; i < N && k < n; i++) {
      if (!alive[i]) continue;
      const x = i % W, y = (i / W) | 0, o = k * 4, p = i * 4;
      f[o] = (x + .5) / 4; f[o + 1] = 0; f[o + 2] = (y + .5) / 4;
      u8[o * 4 + 12] = d[p]; u8[o * 4 + 13] = d[p + 1]; u8[o * 4 + 14] = d[p + 2]; u8[o * 4 + 15] = 255; k++;
    }
    V3.nCells = k; if (k) dev.queue.writeBuffer(V3.cells, 0, V3.cellAB, 0, k * 16);
  }
  v3Lines(nx, ny, Hb);
  // the camera: it orbits a point over the floor
  const key = nx + 'x' + ny; if (V3.boxKey !== key) { V3.boxKey = key; V3.tgt = [nx / 2, Hb * .3, ny / 2]; V3.dist = 1.95 * Math.max(nx, ny); V3.yaw = -.65; V3.pitch = .42; }
  const cp = Math.cos(V3.pitch), eye = [V3.tgt[0] + V3.dist * cp * Math.sin(V3.yaw), V3.tgt[1] + V3.dist * Math.sin(V3.pitch), V3.tgt[2] + V3.dist * cp * Math.cos(V3.yaw)];
  // the clipping planes: far enough to hold the whole box from wherever the camera is, near enough for close-ups
  let far = 1; for (const cx of [0, nx]) for (const cy of [0, Hb]) for (const cz of [0, ny]) far = Math.max(far, Math.hypot(eye[0] - cx, eye[1] - cy, eye[2] - cz));
  far = far * 1.1 + 10; const near = Math.max(.05, far * 2e-4);
  const lk = m4.look(eye, V3.tgt, [0, 1, 0]), pr = m4.persp(.8, Wp / Hp, near, far), vp = m4.mul(pr, lk.m), iv = m4.inv(vp);
  const U = new Float32Array(64);
  U.set(vp, 0); U.set(iv, 16);
  U.set([eye[0], eye[1], eye[2], Math.max(nx, ny) * .004], 32);                // the camera, and the spores' size
  U.set([nx, ny, src.nz, Hb], 36);
  U.set([src.tref, nx * 4 / W, ny * 4 / H, .7], 40);                          // the reference temperature, the floor's texture scale, the glow
  U.set([lk.x[0], lk.x[1], lk.x[2], 0], 44); U.set([lk.y[0], lk.y[1], lk.y[2], 0], 48);
  U.set([V3LAT[0], V3LAT[1], Math.min(V3LAT[2], src.nz), 1], 52);
  U.set([Wp, Hp, 0, 0], 56);
  dev.queue.writeBuffer(V3.ub, 0, U);
  // carried cells with the two layers (no 3D water): pale specks near the surface
  const ns = gpuParts ? 0 : Math.min(air.length, 4000);
  if (ns) {
    if (!V3.sp || V3.spN < ns) { if (V3.sp) V3.sp.destroy(); V3.spN = Math.max(256, ns * 2); V3.sp = dev.createBuffer({size: V3.spN * 12, usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST}); }
    const sd = new Float32Array(ns * 3); for (let k = 0; k < ns; k++) { const s = air[k]; sd[k * 3] = s.x; sd[k * 3 + 1] = Hb * (.86 + .1 * ((k * .618) % 1)); sd[k * 3 + 2] = s.y; }
    dev.queue.writeBuffer(V3.sp, 0, sd);
  }
  const enc = dev.createCommandEncoder();
  const pass = enc.beginRenderPass({colorAttachments: [{view: V3.ctx.getCurrentTexture().createView(), clearValue: {r: .024, g: .03, b: .045, a: 1}, loadOp: 'clear', storeOp: 'store'}],
    depthStencilAttachment: {view: V3.depth.createView(), depthClearValue: 1, depthLoadOp: 'clear', depthStoreOp: 'store'}});
  pass.setBindGroup(0, V3.bg);
  pass.setPipeline(V3.pipes.floor); pass.draw(6);
  if (V3.nCells) { pass.setPipeline(V3.pipes.cell); pass.setVertexBuffer(0, V3.cells); pass.draw(36, V3.nCells); }
  if (gpuParts) { pass.setPipeline(V3.pipes.part); pass.draw(36, G3.MP); }
  if (V3.showHeat) { pass.setPipeline(V3.pipes.vol); pass.draw(3); }
  pass.setPipeline(V3.pipes.line); pass.setVertexBuffer(0, V3.lines); pass.draw(V3.nLines);
  if (V3.showFlow) { pass.setPipeline(V3.pipes.arrow); pass.draw(V3LAT[0] * V3LAT[1] * Math.min(V3LAT[2], src.nz) * 6); }
  if (ns) { pass.setPipeline(V3.pipes.spore); pass.setVertexBuffer(0, V3.sp); pass.draw(6, ns); }
  pass.end(); dev.queue.submit([enc.finish()]);
  V3.frames++; V3.ms = .9 * V3.ms + .1 * (performance.now() - t0);
  const info = `water from ${src.kind}${G3.adapter ? ' · on ' + G3.adapter : ''} · ${V3.nCells.toLocaleString()} cells on the floor, ${air.length} carried`;
  if (V3.legInfo) V3.legInfo.textContent = info;
}
// the legend, with the switches for heat and the flow (both off at first)
function v3Legend() {
  const L = V3.legend; L.style.pointerEvents = 'auto';
  L.innerHTML = `<b>3D view</b> · <span id="v3info"></span><br>
   <label style="margin-right:10px"><input type="checkbox" id="v3heat"> Show heat</label><label><input type="checkbox" id="v3flow"> Show the flow (arrows)</label><br>
   Cells are blocks on the floor; carried cells ride the water${''} · warm water glows orange · arrows: <span style="color:#ffb366">rising</span>, <span style="color:#9cc6ff">sinking</span>, pale sideways<br>
   <span style="color:#9a988f">W A S D: move · Q, E: down, up · Shift: faster · drag: rotate · wheel: zoom · right-drag: pan · double-click: reset</span>`;
  V3.legInfo = L.querySelector('#v3info');
  const h = L.querySelector('#v3heat'), f = L.querySelector('#v3flow');
  h.checked = !!V3.showHeat; f.checked = !!V3.showFlow;
  h.onchange = () => { V3.showHeat = h.checked; }; f.onchange = () => { V3.showFlow = f.checked; };
}
// W A S D move across the floor, Q and E down and up, in the camera's own directions; Shift goes faster
V3.keys = new Set(); V3.lastT = 0;
addEventListener('keydown', e => {
  if (!P.view3d || e.ctrlKey || e.metaKey || e.altKey || /INPUT|SELECT|TEXTAREA/.test((e.target && e.target.tagName) || '')) return;
  const k = e.key.toLowerCase(); if ('wasdqe'.includes(k) && k.length === 1) { V3.keys.add(k); e.preventDefault(); e.stopImmediatePropagation(); }
  if (e.key === 'Shift') V3.keys.add('shift');
}, true);
addEventListener('keyup', e => { V3.keys.delete(e.key.toLowerCase()); if (e.key === 'Shift') V3.keys.delete('shift'); }, true);
addEventListener('blur', () => V3.keys.clear());
function v3Move() {
  const now = performance.now(), dt = V3.lastT ? Math.min(.1, (now - V3.lastT) / 1000) : 0; V3.lastT = now;
  if (!V3.keys.size || !V3.tgt) return;
  const sp = V3.dist * .6 * dt * (V3.keys.has('shift') ? 3 : 1), sy = Math.sin(V3.yaw), cy = Math.cos(V3.yaw);
  const fw = [-sy, -cy], rt = [cy, -sy];
  let mx = 0, mz = 0, my = 0;
  if (V3.keys.has('w')) { mx += fw[0]; mz += fw[1]; } if (V3.keys.has('s')) { mx -= fw[0]; mz -= fw[1]; }
  if (V3.keys.has('d')) { mx += rt[0]; mz += rt[1]; } if (V3.keys.has('a')) { mx -= rt[0]; mz -= rt[1]; }
  if (V3.keys.has('e')) my += 1; if (V3.keys.has('q')) my -= 1;
  V3.tgt[0] += mx * sp; V3.tgt[2] += mz * sp; V3.tgt[1] = Math.max(-50, V3.tgt[1] + my * sp);
}
async function v3Show(on) {
  P.view3d = on; const b = document.getElementById('btn3d'); if (b) b.textContent = on ? '2D view' : '3D view';
  if (!on) { if (V3.cv) { V3.cv.style.display = 'none'; V3.legend.style.display = 'none'; } return; }
  const ok = await v3Init();
  V3.cv.style.display = 'block'; V3.legend.style.display = 'block';
  if (!ok) { V3.legend.innerHTML = V3.msg; return; }
  if (!V3.legInfo) v3Legend();
  if (!V3.running) { V3.running = true; const loop = () => { if (!P.view3d) { V3.running = false; return; } try { v3Move(); v3Frame(); } catch (e) { V3.msg = String(e); V3.legend.innerHTML = '3D view error: ' + V3.msg; } requestAnimationFrame(loop); }; requestAnimationFrame(loop); }
}
{ const b = document.getElementById('btn3d'); if (b) b.onclick = () => v3Show(!P.view3d); if (P.view3d) v3Show(true); }
