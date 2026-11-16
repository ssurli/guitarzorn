// SPDX-License-Identifier: EUPL-1.2
// Copyright (c) 2026 Stefano Surlinelli — https://github.com/ssurli/guitarzorn
/* Guitarzorn — riff → painting, browser oil engine (called "Riff Painting v7" while it was being
   developed; unrelated to zorn_riff_v7.py)
   Pigment-space wet-on-wet oil engine.
   Every pixel of the canvas holds a MIX OF THE FOUR ZORN PIGMENTS (ochre,
   vermilion, ivory black, titanium white) plus a paint thickness. Colour is
   computed from the pigment mix (Kubelka-Munk, subtractive), never blended in
   RGB. A brush is a row of bristles, each with its own paint load: bristles
   deposit paint, pick up what they cross, run dry over the canvas tooth, and
   leave ridges that are lit from the upper left.
   The canvas is persistent and strokes are advanced step by step, so notes can
   be painted while a score scrolls (or a guitar plays). */
(function () {
'use strict';
const W = 1200, H = 800;

// ---- the four pigments (sRGB reflectance out of the tube) -----------------
const PIG_RGB = [[240, 188, 70], [224, 70, 34], [44, 34, 27], [248, 240, 220]]; // ochre, vermilion, black, white
const TINT = [1.0, 1.25, 2.4, 1.5];                                         // tinting strength
const KS = PIG_RGB.map(c => c.map(v => { const r = Math.min(0.98, Math.max(0.02, v / 255)); return (1 - r) * (1 - r) / (2 * r); }));
const pig = (o, v, k, w) => { const s = o + v + k + w || 1; return [o / s, v / s, k / s, w / s]; };

// note → pigment mix (A minor pentatonic ↔ Zorn palette)
const NOTE = {
  A: pig(0.84, 0.09, 0.07, 0),   // ochre, deepened so it reads on the ochre ground
  C: pig(0.12, 0.88, 0, 0),      // vermilion
  D: pig(0.14, 0.06, 0.80, 0),      // ivory black
  E: pig(0.10, 0, 0, 0.90),      // titanium white
  G: pig(0.60, 0.10, 0.30, 0),      // ochre + black
};
const VEL = { p: 0.55, mp: 0.75, mf: 1.0, f: 1.25, ff: 1.55 };
const TUNING = [40, 45, 50, 55, 59, 64];

const RIFF = [
  { note:'A', fret:5, string:6, duration:0.5,  velocity:'mf', technique:'staccato' },
  { note:'C', fret:8, string:6, duration:0.5,  velocity:'f',  technique:'legato' },
  { note:'D', fret:5, string:4, duration:0.25, velocity:'f',  technique:'slide' },
  { note:'A', fret:7, string:5, duration:0.5,  velocity:'mf', technique:'hammer_on' },
  { note:'C', fret:8, string:5, duration:0.25, velocity:'f',  technique:'bend' },
  { note:'D', fret:7, string:3, duration:0.75, velocity:'f',  technique:'vibrato' },
  { note:'E', fret:8, string:1, duration:0.5,  velocity:'f',  technique:'harmonic_natural' },
  { note:'G', fret:3, string:1, duration:0.5,  velocity:'mp', technique:'legato' },
  { note:'A', fret:5, string:1, duration:1.0,  velocity:'ff', technique:'powerchord' },
  { note:'C', fret:8, string:6, duration:0.25, velocity:'mf', technique:'tapping' },
  { note:'D', fret:5, string:4, duration:0.5,  velocity:'f',  technique:'dive' },
  { note:'G', fret:3, string:1, duration:0.25, velocity:'p',  technique:'harmonic_artificial' },
];

function mulberry(a) { return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const sstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };

function create(canvas, seed) {
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(W, H);
  const rnd = mulberry(seed || 42);
  const R = (a, b) => a + (b - a) * rnd();

  const P = new Float32Array(W * H * 4);     // pigment concentrations
  const Ht = new Float32Array(W * H);        // paint thickness
  const tooth = new Float32Array(W * H);     // canvas tooth 0..1
  let dx0 = 0, dy0 = 0, dx1 = W, dy1 = H;    // dirty rect

  function valueNoise(cell) {
    const gw = Math.ceil(W / cell) + 3, gh = Math.ceil(H / cell) + 3, g = new Float32Array(gw * gh);
    for (let i = 0; i < g.length; i++) g[i] = rnd();
    return (x, y) => {
      const fx = clamp(x, 0, W) / cell + 1, fy = clamp(y, 0, H) / cell + 1, ix = fx | 0, iy = fy | 0;
      let tx = fx - ix, ty = fy - iy; tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty);
      const k = iy * gw + ix, a = g[k], b = g[k + 1], c = g[k + gw], d = g[k + gw + 1];
      return a + (b - a) * tx + (c - a) * ty + (a - b - c + d) * tx * ty;
    };
  }
  const nBig = valueNoise(260), nMid = valueNoise(90), nFine = valueNoise(7), nFlow = valueNoise(340), nFlow2 = valueNoise(120);

  // canvas: primed warm, with a soft weave and grain
  for (let y = 0, i = 0; y < H; y++) for (let x = 0; x < W; x++, i++) {
    const weave = 0.5 + 0.12 * Math.sin(x * 2.1) * Math.sin(y * 2.1);
    tooth[i] = clamp(0.4 * weave + 0.6 * nFine(x, y) + 0.3 * (rnd() - 0.5), 0, 1);
    P[i * 4] = 0.80; P[i * 4 + 1] = 0.02; P[i * 4 + 2] = 0; P[i * 4 + 3] = 0.18;
  }

  // ---- path helpers -------------------------------------------------------
  function resample(pts, step) {
    const dense = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || pts[i + 1];
      for (let s = 0; s < 16; s++) {
        const t = s / 16, t2 = t * t, t3 = t2 * t;
        dense.push([0, 1].map(k => 0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)));
      }
    }
    dense.push(pts[pts.length - 1]);
    const out = [dense[0]]; let acc = 0;
    for (let i = 1; i < dense.length; i++) {
      let ax = dense[i - 1][0], ay = dense[i - 1][1]; const bx = dense[i][0], by = dense[i][1];
      let seg = Math.hypot(bx - ax, by - ay);
      while (acc + seg >= step) {
        const t = (step - acc) / seg; ax += (bx - ax) * t; ay += (by - ay) * t;
        out.push([ax, ay]); seg = Math.hypot(bx - ax, by - ay); acc = 0;
      }
      acc += seg;
    }
    return out;
  }

  // ---- a stroke: a row of loaded bristles dragged along a path ------------
  // o: w (brush width px), pig, pig2/mix2 (unevenly mixed second colour), load,
  //    capacity (px of travel one load lasts), pickup, opacity, thick, dry,
  //    taper, p0/p1 (pressure start/end), soft (edge feathering)
  function makeStroke(pts, o) {
    const path = resample(pts, 1.25), n = path.length;
    const w = o.w, nb = Math.max(8, Math.round(w * 1.7));
    const off = new Float32Array(nb), load = new Float32Array(nb), bh = new Float32Array(nb), q = new Float32Array(nb * 4), wander = new Float32Array(nb), delay = new Float32Array(nb), stop = new Float32Array(nb);
    const ramp = o.ramp == null ? 0.1 : o.ramp, ph = R(0, 100), soft = o.soft == null ? 0.5 : o.soft;
    for (let b = 0; b < nb; b++) {
      let u = (b + R(-0.5, 0.5)) / nb * 2 - 1;                       // -1..1 across the brush
      off[b] = u * w * 0.5;
      const clump = 0.5 + 0.5 * Math.sin(u * 2.6 + ph) * Math.sin(u * 5.9 + ph * 1.7);
      const edge = 1 - soft * Math.pow(Math.abs(u), 1.5);           // less paint at the edges
      load[b] = (o.load == null ? 1 : o.load) * (0.7 + 0.5 * clump) * edge * R(0.75, 1.15);
      bh[b] = 0.45 + 1.0 * clump * R(0.85, 1.1);
      const m2 = o.pig2 ? clamp((o.mix2 || 0.3) * (0.3 + 1.4 * (0.5 + 0.5 * Math.sin(u * 3.1 + ph * 2.3))) * R(0.6, 1.3), 0, 1) : 0;
      for (let k = 0; k < 4; k++) q[b * 4 + k] = o.pig[k] * (1 - m2) + (o.pig2 ? o.pig2[k] * m2 : 0);
      wander[b] = R(0, 100); delay[b] = ramp * 1.3 * u * u * R(0.7, 1.2) + R(0, ramp * 0.25); stop[b] = 1 - ramp * 1.3 * u * u * R(0.7, 1.2) - R(0, ramp * 0.25);
    }
    const capacity = o.capacity || 400, pickup = o.pickup == null ? 0.03 : o.pickup, opacity = o.opacity == null ? 0.6 : o.opacity;
    const thick = o.thick == null ? 1 : o.thick, dry = o.dry == null ? 1 : o.dry, taper = o.taper == null ? 0.7 : o.taper;
    const smearK = o.smear == null ? 0.05 : o.smear, flat = o.flat || 0;
    const p0 = o.p0 == null ? 1 : o.p0, p1 = o.p1 == null ? 0.8 : o.p1;
    let s = 0;
    return {
      get done() { return s >= n; },
      advance(steps) {
        const end = Math.min(n, s + steps);
        for (; s < end; s++) {
          const t = n > 1 ? s / (n - 1) : 0, a0 = path[Math.max(0, s - 2)], a1 = path[Math.min(n - 1, s + 2)];
          let tx = a1[0] - a0[0], ty = a1[1] - a0[1]; const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
          const nx = -ty, ny = tx, cx = path[s][0], cy = path[s][1];
          const press = sstep(0, ramp, t) * (1 - taper * sstep(0.5, 1, t)) * (p0 + (p1 - p0) * t);
          const spread = 0.72 + 0.28 * press;
          const mx0 = cx - w, my0 = cy - w, mx1 = cx + w, my1 = cy + w;
          if (mx0 < dx0) dx0 = mx0; if (my0 < dy0) dy0 = my0; if (mx1 > dx1) dx1 = mx1; if (my1 > dy1) dy1 = my1;
          for (let b = 0; b < nb; b++) {
            if (t < delay[b] || t > stop[b]) continue;
            const wob = (1.2 + 2.2 * Math.abs(off[b]) / w) * Math.sin(s * 0.045 + wander[b]);
            const x = cx + nx * (off[b] * spread + wob), y = cy + ny * (off[b] * spread + wob);
            const ix = x | 0, iy = y | 0;
            if (ix < 0 || iy < 0 || ix >= W - 1 || iy >= H - 1) continue;
            const i = iy * W + ix, lb = load[b], q4 = b * 4;
            // dry brush: a starved bristle only touches the high points of the tooth
            const wet = clamp(lb * 1.6, 0, 1);
            const touches = tooth[i] < press * (0.3 + 1.7 * wet) / dry;
            let a = touches ? clamp(opacity * press * (0.2 + 0.8 * wet), 0, 1) : 0;
            const smear = smearK * press;                               // even a dry bristle drags wet paint
            const aa = a > smear ? a : smear;
            // pick up what is on the canvas
            const pu = pickup * press;
            const c4 = i * 4;
            q[q4] += (P[c4] - q[q4]) * pu; q[q4 + 1] += (P[c4 + 1] - q[q4 + 1]) * pu; q[q4 + 2] += (P[c4 + 2] - q[q4 + 2]) * pu; q[q4 + 3] += (P[c4 + 3] - q[q4 + 3]) * pu;
            // deposit on a soft 2x2 footprint
            const fx = x - ix, fy = y - iy;
            for (let j = 0; j < 4; j++) {
              const wgt = (j & 1 ? fx : 1 - fx) * (j & 2 ? fy : 1 - fy) + 0.3;
              const k = (i + (j & 1) + (j & 2 ? W : 0)), k4 = k * 4, al = aa * wgt > 1 ? 1 : aa * wgt;
              P[k4] += (q[q4] - P[k4]) * al; P[k4 + 1] += (q[q4 + 1] - P[k4 + 1]) * al; P[k4 + 2] += (q[q4 + 2] - P[k4 + 2]) * al; P[k4 + 3] += (q[q4 + 3] - P[k4 + 3]) * al;
              // thickness: bristles plough the wet paint into ridges
              const target = thick * bh[b] * (0.25 + 0.75 * wet) * press;
              Ht[k] += (target - Ht[k]) * (a * wgt > 1 ? 1 : a * wgt) * 0.55;
              if (flat) Ht[k] += (flat * 0.5 - Ht[k]) * al * 0.5;
            }
            load[b] = lb - a / capacity * 1.6;
            if (load[b] < 0) load[b] = 0;
          }
        }
        return s >= n;
      },
    };
  }


  // ---- a LIVE stroke: it does not know how long the note will last ---------
  // The brush lands at noteOn, travels while the note is held, and on noteOff
  // lifts over a short release (thinner, drier). Held long enough it simply
  // runs out of paint. o: x, y, ang, curve (rad/px), w, pig, speed (px/s),
  // capacity, thick, dry, pickup, opacity, soft, rampPx, maxLen
  const STEP = 1.25;
  function makeLiveStroke(o) {
    const w = o.w, nb = Math.max(8, Math.round(w * 1.7));
    const off = new Float32Array(nb), load = new Float32Array(nb), bh = new Float32Array(nb), q = new Float32Array(nb * 4), wander = new Float32Array(nb), delayD = new Float32Array(nb), liftAt = new Float32Array(nb);
    const rampPx = o.rampPx == null ? Math.max(8, w * 0.55) : o.rampPx, ph = R(0, 100), soft = o.soft == null ? 0.95 : o.soft;
    for (let b = 0; b < nb; b++) {
      const u = (b + R(-0.5, 0.5)) / nb * 2 - 1;
      off[b] = u * w * 0.5;
      const clump = 0.5 + 0.5 * Math.sin(u * 2.6 + ph) * Math.sin(u * 5.9 + ph * 1.7);
      const edge = 1 - soft * Math.pow(Math.abs(u), 1.5);
      load[b] = (0.7 + 0.5 * clump) * edge * R(0.75, 1.15);
      bh[b] = 0.45 + 1.0 * clump * R(0.85, 1.1);
      for (let k = 0; k < 4; k++) q[b * 4 + k] = o.pig[k];
      wander[b] = R(0, 100);
      delayD[b] = rampPx * 1.3 * u * u * R(0.7, 1.2) + R(0, rampPx * 0.25);   // the brush lands rounded…
      liftAt[b] = 1 - 1.05 * u * u * R(0.7, 1.2) - R(0, 0.12);               // …and lifts rounded
    }
    const capacity = o.capacity || 380, pickup = o.pickup == null ? 0.04 : o.pickup, opacity = o.opacity == null ? 0.75 : o.opacity;
    const thick = o.thick == null ? 1 : o.thick, dry0 = o.dry == null ? 1.5 : o.dry, smearK = 0.05;
    const minLen = o.minLen == null ? w * 0.9 : o.minLen, maxLen = o.maxLen || 560, curve = o.curve || 0;
    const wav = o.wav || 0, wavK = 2 * Math.PI / (o.wavLen || 90);          // vibrato: the wrist trembles
    let x = o.x, y = o.y, ang = o.ang, dist = 0, s = 0, releasing = false, wantRelease = false, rel = 0, relLen = 1, done = false, carry = 0;
    const x0 = x, y0 = y;
    return {
      w, x0, y0, speed: o.speed || 260,
      get x() { return x; }, get y() { return y; }, get length() { return dist; }, get done() { return done; },
      release() { wantRelease = true; },
      /** advance by a distance in px (fractions are carried to the next call) */
      advancePx(px) {
        carry += px / STEP;
        let steps = carry | 0; carry -= steps;
        for (; steps > 0 && !done; steps--) {
          if (!releasing && (dist >= maxLen || (wantRelease && dist >= minLen))) { releasing = true; relLen = clamp(dist * 0.42, 14, 110); }
          if (releasing) { rel += STEP / relLen; if (rel >= 1) { done = true; break; } }
          ang += curve * STEP + 0.006 * Math.sin(dist * 0.021 + ph);
          const dir = wav ? ang + Math.cos(dist * wavK) * Math.min(wav * wavK, 0.75) : ang;
          const tx = Math.cos(dir), ty = Math.sin(dir), nx = -ty, ny = tx;
          x += tx * STEP; y += ty * STEP; dist += STEP; s++;
          if (x < -w || y < -w || x > W + w || y > H + w) { done = true; break; }
          const press = sstep(0, rampPx, dist) * (releasing ? Math.pow(1 - rel, 1.15) : 1) * (1 - 0.18 * sstep(60, 260, dist));
          const dry = dry0 * (1 + 1.3 * rel), spread = 0.72 + 0.28 * press;
          if (x - w < dx0) dx0 = x - w; if (y - w < dy0) dy0 = y - w; if (x + w > dx1) dx1 = x + w; if (y + w > dy1) dy1 = y + w;
          for (let b = 0; b < nb; b++) {
            if (dist < delayD[b] || (releasing && rel > liftAt[b])) continue;
            const wob = (1.2 + 2.2 * Math.abs(off[b]) / w) * Math.sin(s * 0.045 + wander[b]);
            const bx = x + nx * (off[b] * spread + wob), by = y + ny * (off[b] * spread + wob);
            const ix = bx | 0, iy = by | 0;
            if (ix < 0 || iy < 0 || ix >= W - 1 || iy >= H - 1) continue;
            const i = iy * W + ix, lb = load[b], q4 = b * 4;
            const wet = clamp(lb * 1.6, 0, 1);
            const touches = tooth[i] < press * (0.3 + 1.7 * wet) / dry;
            const a = touches ? clamp(opacity * press * (0.2 + 0.8 * wet), 0, 1) : 0;
            const smear = smearK * press, aa = a > smear ? a : smear;
            const pu = pickup * press, c4 = i * 4;
            q[q4] += (P[c4] - q[q4]) * pu; q[q4 + 1] += (P[c4 + 1] - q[q4 + 1]) * pu; q[q4 + 2] += (P[c4 + 2] - q[q4 + 2]) * pu; q[q4 + 3] += (P[c4 + 3] - q[q4 + 3]) * pu;
            const fx = bx - ix, fy = by - iy;
            for (let j = 0; j < 4; j++) {
              const wgt = (j & 1 ? fx : 1 - fx) * (j & 2 ? fy : 1 - fy) + 0.3;
              const k = (i + (j & 1) + (j & 2 ? W : 0)), k4 = k * 4, al = aa * wgt > 1 ? 1 : aa * wgt;
              P[k4] += (q[q4] - P[k4]) * al; P[k4 + 1] += (q[q4 + 1] - P[k4 + 1]) * al; P[k4 + 2] += (q[q4 + 2] - P[k4 + 2]) * al; P[k4 + 3] += (q[q4 + 3] - P[k4 + 3]) * al;
              const target = thick * bh[b] * (0.25 + 0.75 * wet) * press;
              Ht[k] += (target - Ht[k]) * (a * wgt > 1 ? 1 : a * wgt) * 0.55;
            }
            load[b] = lb - a / capacity * 1.6;
            if (load[b] < 0) load[b] = 0;
          }
        }
        return done;
      },
    };
  }
  // a clean dry brush dragged through a finished live mark, start to end
  function smudgeLive(st) {
    const L = Math.hypot(st.x - st.x0, st.y - st.y0), a = Math.atan2(st.y - st.y0, st.x - st.x0) + R(-0.2, 0.2), bw = st.w;
    const len = L * 1.15 + bw * 2, sx = st.x0 - Math.cos(a) * bw * 0.9, sy = st.y0 - Math.sin(a) * bw * 0.9, pts = [];
    for (let j = 0; j <= 3; j++) { const t = j / 3; pts.push([sx + Math.cos(a) * len * t + R(-3, 3), sy + Math.sin(a) * len * t + R(-3, 3)]); }
    return makeStroke(pts, { w: bw * R(1.5, 2.1), pig: pig(0.9, 0.02, 0, 0.08), load: 0, capacity: 100, pickup: 0.22, opacity: 0, smear: R(0.10, 0.2), flat: 1, soft: 0.9, ramp: 0.3, taper: 0.9, dry: 1 });
  }

  // ---- light the relief, turn pigment into colour -------------------------
  const LX = -0.46, LY = -0.60, LZ = 0.655, d = img.data;
  function relight() {
    const x0 = clamp((dx0 | 0) - 3, 0, W - 1), y0 = clamp((dy0 | 0) - 3, 0, H - 1), x1 = clamp((dx1 | 0) + 3, 0, W - 1), y1 = clamp((dy1 | 0) + 3, 0, H - 1);
    if (x1 < x0 || y1 < y0) return;
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
      const i = y * W + x, c4 = i * 4, xm = x > 1 ? i - 2 : i, xp = x < W - 2 ? i + 2 : i, ym = y > 1 ? i - 2 * W : i, yp = y < H - 2 ? i + 2 * W : i;
      const hx = Ht[xp] - Ht[xm] + (tooth[xp] - tooth[xm]) * 0.03, hy = Ht[yp] - Ht[ym] + (tooth[yp] - tooth[ym]) * 0.03;
      const eb = (x < 4 || y < 4 || x > W - 5 || y > H - 5) ? 0 : 0.55;   // no relief on the very edge of the canvas
      const nx = -hx * eb, ny = -hy * eb, il = 1 / Math.sqrt(nx * nx + ny * ny + 1);
      const diff = (nx * LX + ny * LY + LZ) * il;
      const shade = clamp(1 + (diff - LZ) * 0.8, 0.8, 1.16), sp = 0;
      const o = P[c4] * TINT[0], v = P[c4 + 1] * TINT[1], k = P[c4 + 2] * TINT[2], wv = P[c4 + 3] * TINT[3], s = 1 / (o + v + k + wv + 1e-6);
      for (let ch = 0; ch < 3; ch++) {
        const ks = (o * KS[0][ch] + v * KS[1][ch] + k * KS[2][ch] + wv * KS[3][ch]) * s;
        const r = 1 + ks - Math.sqrt(ks * ks + 2 * ks);
        const out = (r * shade + sp) * 255;
        d[c4 + ch] = out > 255 ? 255 : out;
      }
      d[c4 + 3] = 255;
    }
    ctx.putImageData(img, 0, 0, x0, y0, x1 - x0 + 1, y1 - y0 + 1);
    dx0 = W; dy0 = H; dx1 = 0; dy1 = 0;
  }

  function settle(passes) {
    const tmp = new Float32Array(W * H);
    for (let p = 0; p < passes; p++) {
      for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) { const i = y * W + x; tmp[i] = (Ht[i] * 4 + Ht[i - 1] + Ht[i + 1] + Ht[i - W] + Ht[i + W]) / 8; }
      Ht.set(tmp);
    }
    dx0 = 0; dy0 = 0; dx1 = W; dy1 = H;
  }

  // ---- the ground: thick ochre laid in with a wide brush -------------------
  function groundStrokes() {
    const list = [];
    const lay = (count, wMin, wMax, lMin, lMax, opts) => {
      for (let s = 0; s < count; s++) {
        const x = R(-80, W + 80), y = R(-40, H + 40);
        const ang = (nFlow(x, y) - 0.5) * 0.9 + (nFlow2(x, y) - 0.5) * 0.5 + R(-0.1, 0.1) + (rnd() < 0.5 ? Math.PI : 0);
        const len = R(lMin, lMax), bend = R(-0.35, 0.35), pts = [];
        for (let j = 0; j <= 3; j++) { const t = j / 3 - 0.5, a = ang + bend * t; pts.push([x + Math.cos(a) * len * t, y + Math.sin(a) * len * t + Math.sin(t * 3 + s) * 6]); }
        const tone = nBig(x, y) * 0.65 + nMid(x, y) * 0.35, r = rnd();
        let p;
        if (r < 0.50) p = pig(0.93, 0.012, 0.0, 0.06 + 0.12 * tone);
        else if (r < 0.74) p = pig(0.70, 0.006, 0, 0.30 + 0.22 * tone);          // paler, more white
        else if (r < 0.92) p = pig(0.92, 0.05 + 0.04 * tone, 0, 0.03);     // warmer, a touch of vermilion
        else p = pig(0.95, 0.035, 0.002, 0.02);            // deeper, a touch of black
        list.push(makeStroke(pts, Object.assign({ w: R(wMin, wMax), pig: p, pig2: pig(0.7, 0.02, 0, 0.3), mix2: 0.25, capacity: len * R(0.9, 1.8) }, opts)));
      }
    };
    lay(150, 90, 150, 320, 620, { load: 1.2, pickup: 0.02, opacity: 0.8, thick: 0.80, dry: 0.5, taper: 0.5, soft: 0.8, ramp: 0.4 });   // block in
    lay(240, 40, 95, 160, 420, { load: 1.0, pickup: 0.035, opacity: 0.55, thick: 0.90, dry: 0.7, taper: 0.7, soft: 0.85, ramp: 0.4 });  // work it
    lay(70, 26, 60, 120, 320, { load: 0.8, pickup: 0.05, opacity: 0.4, thick: 1.10, dry: 1.0, taper: 0.8, soft: 0.85, ramp: 0.4 });     // loose touches
    list.push({ done: false, advance() { settle(7); this.done = true; return true; } });   // the wet ground levels a little
    return list;
  }

  // ---- notes → gestures of the hand ---------------------------------------
  // No glyphs: a technique changes HOW the brush moves (direction, length,
  // pressure, load, repetition), not which symbol is drawn.
  function layout(riff) {
    const pitches = riff.map(n => TUNING[6 - n.string] + n.fret), lo = Math.min(...pitches), hi = Math.max(...pitches);
    const total = riff.reduce((a, n) => a + n.duration, 0), MX = 110, MY = 130;
    let t = 0;
    return riff.map((n, i) => {
      const x = MX + (t + n.duration * 0.5) / total * (W - 2 * MX), y = H - MY - (pitches[i] - lo) / (hi - lo || 1) * (H - 2 * MY);
      t += n.duration;
      return { n, x: x + R(-14, 14), y: y + R(-22, 22), beatPx: (W - 2 * MX) / total };
    });
  }
  function noteStrokes(ev, next) {
    const { n, x, y, beatPx } = ev, v = VEL[n.velocity] || 1, p = NOTE[n.note], out = [];
    const len = clamp(n.duration * beatPx * 0.9, 40, 300), bw = 30 * v;
    const dirTo = next ? Math.atan2(next.y - y, next.x - x) : R(-0.3, 0.3);
    const seg = (ax, ay, ang, L, curve, o) => {
      const pts = []; for (let j = 0; j <= 4; j++) { const t = j / 4, a = ang + curve * (t - 0.5); pts.push([ax + Math.cos(a) * L * (t - 0.5) + R(-1.5, 1.5), ay + Math.sin(a) * L * (t - 0.5) + R(-1.5, 1.5)]); }
      out.push(makeStroke(pts, Object.assign({ w: bw, pig: p, load: 1, capacity: L * 1.2, pickup: 0.04, opacity: 0.75, thick: 0.90 * v, dry: 1.5, soft: 0.95, ramp: 0.22 }, o)));
    };
    switch (n.technique) {
      case 'staccato':            // one short, loaded touch
        seg(x, y, R(-0.5, 0.5), bw * 1.7, 0.2, { w: bw * 1.1, thick: 1.21 * v, capacity: 200, taper: 0.3, ramp: 0.38 }); break;
      case 'legato':              // a long soft pull toward the next note, picking up the ground
        seg(x, y, dirTo * 0.5, len * 1.3, R(-0.5, 0.5), { pickup: 0.09, opacity: 0.6, p0: 0.75, p1: 0.6, capacity: len * 1.6, thick: 1.10 * v }); break;
      case 'slide':               // a fast drag that runs dry
        seg(x, y, -1.15 + R(-0.15, 0.15), len * 2.6 + 90, 0.12, { w: bw * 1.25, capacity: len * 1.1 + 50, dry: 1.9, taper: 0.9, p0: 1.1, p1: 0.5 });
        seg(x + R(-6, 6), y + R(-4, 4), -1.15 + R(-0.1, 0.1), len * 1.6 + 50, 0.1, { w: bw * 0.55, pig: NOTE.C, capacity: len + 40, dry: 1.6, opacity: 0.6, thick: 1.20 }); break;
      case 'bend':                // pressure rises as the brush curls upward
        seg(x, y, -0.55, len * 1.6 + 40, -0.95, { p0: 0.55, p1: 1.25, taper: 0.25, thick: 1.10 * v, capacity: 260 }); break;
      case 'vibrato': {           // the wrist trembles: short overlapping touches along the note
        const k = Math.max(4, Math.round(len / 16));
        for (let j = 0; j < k; j++) { const t = j / (k - 1) - 0.5; seg(x + t * len * 0.75, y + R(-5, 5), -1.0 + R(-0.18, 0.18), bw * R(1.5, 2.1), 0.25, { w: bw * 0.7, opacity: 0.7, pickup: 0.07, capacity: 110, thick: 1.30 * v, ramp: 0.3, dry: 1.4 }); }
        break; }
      case 'hammer_on':           // a touch, then a harder one laid over it
        seg(x - bw * 0.5, y + 4, R(-0.3, 0.3), bw * 1.6, 0.2, { opacity: 0.6, thick: 1.20, ramp: 0.35 });
        seg(x + bw * 0.4, y - 3, R(-0.3, 0.3), bw * 1.3, 0.2, { w: bw * 0.9, thick: 1.43 * v, capacity: 220, taper: 0.3, ramp: 0.38 }); break;
      case 'powerchord':          // the flat of a wide brush, twice
        seg(x, y, R(-0.12, 0.12), len * 1.1, 0.08, { w: bw * 1.9, capacity: len * 1.0, thick: 0.99, dry: 1.6, ramp: 0.22, taper: 0.85 });
        seg(x + R(-8, 8), y + bw * 0.5, R(-0.12, 0.12), len * 0.8, 0.08, { w: bw * 1.1, pig: NOTE.G, opacity: 0.5, capacity: len * 0.7, thick: 1.40, dry: 1.8, ramp: 0.22 }); break;
      case 'tapping':             // the tip of the brush, pressed and turned
        seg(x, y, R(0, 3), bw * 1.15, 0.3, { w: bw * 1.0, thick: 1.65, capacity: 300, taper: 0.2, soft: 0.8, ramp: 0.45 }); break;
      case 'dive':                // a long fall, the paint giving out
        seg(x, y, 0.75, len * 2.0 + 60, 0.7, { capacity: len * 0.9 + 30, dry: 2.0, taper: 0.95, p0: 1.15, p1: 0.35 }); break;
      case 'harmonic_natural':    // a thick light touch that sits on top
        seg(x, y, R(-0.3, 0.3), bw * 2.6, 0.3, { w: bw * 1.2, pickup: 0.012, thick: 1.65, capacity: 320, taper: 0.5, ramp: 0.3 }); break;
      case 'harmonic_artificial': // barely there
        seg(x, y, R(-0.6, 0.6), bw * 1.3, 0.3, { w: bw * 0.8, pig: pig(0.3, 0, 0.1, 0.6), pickup: 0.02, thick: 1.21, capacity: 200, ramp: 0.4 }); break;
      default:
        seg(x, y, 0, len, 0, {});
    }
    // a clean dry brush dragged through the wet mark: edges dissolve into the ground and leave a tail
    const smudge = (ang, L, wk) => { const pts = []; for (let j = 0; j <= 3; j++) { const t = j / 3; pts.push([x - Math.cos(ang) * L * 0.35 + Math.cos(ang) * L * t + R(-3, 3), y - Math.sin(ang) * L * 0.35 + Math.sin(ang) * L * t + R(-3, 3)]); }
      out.push(makeStroke(pts, { w: bw * wk, pig: pig(0.9, 0.02, 0, 0.08), load: 0, capacity: 100, pickup: 0.22, opacity: 0, smear: R(0.10, 0.2), flat: 1, soft: 0.9, ramp: 0.3, taper: 0.9, dry: 1 })); };
    const sa = n.technique === 'slide' ? -1.15 : n.technique === 'dive' ? 0.75 : n.technique === 'vibrato' ? R(-0.2, 0.2) : R(-0.5, 0.5);
    smudge(sa, clamp(len, 50, 200) + bw * 2, R(1.5, 2.2));
    if (rnd() < 0.6) smudge(sa + R(-0.5, 0.5) + (rnd() < 0.4 ? Math.PI : 0), bw * R(3, 5), R(1.2, 1.8));
    return out;
  }

  // ---- public API ----------------------------------------------------------
  let queue = [];
  const liveNotes = new Map(), liveFading = [];   // strokes of held notes / strokes lifting off
  const api = {
    width: W, height: H, RIFF,
    queueGround() { queue = queue.concat(groundStrokes()); },
    /** lay a riff out on the canvas: returns one event per note (x = time, y = pitch) */
    layoutRiff(riff) { return layout(riff || RIFF); },
    /** queue the brushwork of one laid-out note; `next` lets a legato lean toward what follows */
    queueEvent(ev, next) { queue = queue.concat(noteStrokes(ev, next || null)); },
    queueRiff(riff) { const ev = layout(riff || RIFF); ev.forEach((e, i) => { queue = queue.concat(noteStrokes(e, ev[i + 1])); }); },
    /** paint one note now (score playback / live input): {note, velocity, technique, duration} at canvas x,y */
    paintNote(n, x, y, beatPx) { queue = queue.concat(noteStrokes({ n, x, y, beatPx: beatPx || 120 }, null)); },
    /** LIVE: the brush lands. id identifies the held note. g: { note:'A'|'C'|'D'|'E'|'G' or pig:[4], velocity:'p'..'ff' or number,
        x, y, ang (rad), curve (rad/px), speed (px/s), wMul, thickMul, capacityMul, dry, pickup, opacity, wav, wavLen, maxLen } */
    noteOn(id, g) {
      if (liveNotes.has(id)) api.noteOff(id);
      const v = typeof g.velocity === 'number' ? g.velocity : (VEL[g.velocity] || 1), bw = 30 * v * (g.wMul || 1);
      const st = makeLiveStroke({ x: g.x, y: g.y, ang: g.ang || 0, curve: g.curve || 0, w: bw, pig: g.pig || NOTE[g.note] || NOTE.A,
        speed: g.speed, thick: 1.0 * v * (g.thickMul || 1), capacity: (300 + 160 * v) * (g.capacityMul || 1),
        dry: g.dry, pickup: g.pickup, opacity: g.opacity, wav: g.wav, wavLen: g.wavLen, maxLen: g.maxLen, soft: g.soft, rampPx: g.rampPx });
      liveNotes.set(id, st);
      return st;
    },
    /** LIVE: the brush starts to lift (it still finishes its release over the next frames) */
    noteOff(id) { const st = liveNotes.get(id); if (!st) return; liveNotes.delete(id); st.release(); liveFading.push(st); },
    get liveCount() { return liveNotes.size + liveFading.length; },
    /** advance the queued strokes by a budget of brush steps, and the live strokes by dt seconds; true when nothing is left to paint */
    tick(budget, dt) {
      if (dt) {
        for (const st of liveNotes.values()) if (st.advancePx(st.speed * dt)) st.release();
        for (let i = liveFading.length - 1; i >= 0; i--) {
          const st = liveFading[i];
          if (st.advancePx(st.speed * dt)) { liveFading.splice(i, 1); if (st.length > 6) queue.push(smudgeLive(st)); }
        }
        for (const [id, st] of liveNotes) if (st.done) { liveNotes.delete(id); if (st.length > 6) queue.push(smudgeLive(st)); }
      }
      let left = budget;
      while (left > 0 && queue.length) { const s = queue[0]; s.advance(Math.min(left, 60)); left -= 60; if (s.done) queue.shift(); }
      relight();
      return queue.length === 0 && liveNotes.size === 0 && liveFading.length === 0;
    },
    finish() { while (queue.length) { queue[0].advance(1e9); queue.shift(); } relight(); },
    get pending() { return queue.length; },
  };
  dx0 = 0; dy0 = 0; dx1 = W; dy1 = H; relight();
  return api;
}

window.GuitarzornPaint7 = { create, RIFF, NOTE };
})();
