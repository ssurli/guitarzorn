// SPDX-License-Identifier: EUPL-1.2
// Copyright (c) 2026 Stefano Surlinelli — https://github.com/ssurli/guitarzorn
/* Guitarzorn — ASCOLTO: dalla chitarra alle note, in tempo reale
   Due parti:
   1. NUCLEO PURO (provabile in Node): createListener() riceve un fotogramma alla
      volta { t (s), f0 (Hz, <= 0 se nessuna altezza), rms } e restituisce eventi:
        { type:'on',      id, t, midi, vel, tech }   nota iniziata (tech: normale | hammer_on | pull_off)
        { type:'gesture', id, t, tech, ... }        la nota tenuta cambia gesto (slide | bend | release | vibrato)
        { type:'off',     id, t }                   nota finita
   2. GUSCIO BROWSER: createMic() apre il microfono, stima l'altezza con
      l'autocorrelazione (stesso metodo "primo picco" del ponte con Improv Lab)
      e passa i fotogrammi al nucleo.
   Una nota alla volta: bicordi e accordi dal microfono non sono riconosciuti. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.GuitarzornAscolto = factory();
}(typeof self !== 'undefined' ? self : this, function () {
'use strict';

const DEFAULTS = {
  gateMin: 0.008,       // rms minimo per considerare suonata una nota
  gateK: 2.5,           // soglia = rumore di fondo × gateK
  onFrames: 2,          // fotogrammi concordi per far partire una nota
  onTol: 0.5,           // …entro mezzo semitono
  offFrames: 3,         // fotogrammi muti per chiuderla
  stableTol: 0.5,       // entro questa distanza dalla nota la nota "non si muove"
  landFrames: 3,        // l'altezza è "arrivata" quando resta ferma per tanti fotogrammi…
  landSpread: 0.15,     // …entro tanti semitoni
  legatoFrames: 2,      // salto compiuto in così pochi fotogrammi = hammer-on / pull-off
  legatoMaxSt: 5,       // oltre questo salto non è un legato
  slidePlateau: 0.25,
  bendMaxSt: 2.6,
  bendMinSt: 0.8,       // sotto, è un vibrato largo o un'intonazione incerta
  fretTol: 0.28,        // "su un tasto": entro tanti semitoni da un semitono intero
  stepWaitS: 0.13,      // un salto di un semitono aspetta così tanto prima di dirsi legato (potrebbe essere uno slide)       // un bend sale al massimo di un tono e mezzo circa: oltre è uno slide    // quota di fotogrammi fermi durante il passaggio: oltre, sono i tasti di uno slide
  attackK: 1.6,         // l'energia degli ultimi ms sale di tanto: nuova pennata
  attackMinS: 0.08,     // …ma non nei primi istanti della nota
  vibWinS: 0.4,         // finestra per riconoscere il vibrato
  vibMinHz: 3.5, vibMaxHz: 9,
  vibMinPP: 0.18, vibMaxPP: 1.6,   // escursione picco-picco in semitoni
  midiLo: 38, midiHi: 92,
};

const toMidi = f => 69 + 12 * Math.log2(f / 440);

function createListener(opts) {
  const o = Object.assign({}, DEFAULTS, opts || {});
  let noise = 0.004, refPeak = 0.05, nextId = 1, cand = [], cur = null, rmsHist = [];
  const median = a => { const s = a.slice().sort((x, y) => x - y); return s[s.length >> 1]; };
  const velOf = rms => Math.max(0.5, Math.min(1.55, 0.5 + 1.05 * Math.min(1, rms / refPeak)));

  function start(out, t, midi, rms, tech, from) {
    const tune = Math.max(-0.45, Math.min(0.45, midi - Math.round(midi)));   // quanto è calante o crescente la chitarra su questa nota
    cur = { id: nextId++, t0: t, base: midi, tune, int: Math.round(midi - tune), hist: [], trans: null, silent: 0, vib: false, bent: 0, pend: null, sliding: 0 };
    out.push({ type: 'on', id: cur.id, t, midi: cur.int, vel: velOf(rms), tech: tech || 'normale', from: from == null ? null : from });
  }
  function stop(out, t) {
    if (cur && cur.pend) { const pd = cur.pend; cur.pend = null; out.push({ type: 'off', id: cur.id, t: pd.t }); cur = null; start(out, pd.t, pd.to, 0, pd.dir > 0 ? 'hammer_on' : 'pull_off', pd.from); }
    if (cur) out.push({ type: 'off', id: cur.id, t }); cur = null;
  }

  function checkVibrato(out, t) {
    if (cur.vib) return;
    const w = cur.hist.filter(h => h.t >= t - o.vibWinS);
    if (w.length < 8 || w[w.length - 1].t - w[0].t < o.vibWinS * 0.8) return;
    const mean = w.reduce((a, h) => a + h.p, 0) / w.length;
    let lo = Infinity, hi = -Infinity, cross = 0, sign = 0;
    for (const h of w) {
      const d = h.p - mean; if (h.p < lo) lo = h.p; if (h.p > hi) hi = h.p;
      if (Math.abs(d) > 0.06) { const s = d > 0 ? 1 : -1; if (sign && s !== sign) cross++; sign = s; }
    }
    const pp = hi - lo, hz = cross / 2 / (w[w.length - 1].t - w[0].t);
    if (pp >= o.vibMinPP && pp <= o.vibMaxPP && hz >= o.vibMinHz && hz <= o.vibMaxHz) {
      cur.vib = true; out.push({ type: 'gesture', id: cur.id, t, tech: 'vibrato', hz: +hz.toFixed(2), pp: +pp.toFixed(2) });
    }
  }

  /** un fotogramma → eventi (anche nessuno) */
  function feed(fr) {
    const out = [], t = fr.t, rms = fr.rms || 0, tail = fr.tail == null ? rms : fr.tail;
    let p = fr.f0 > 0 ? toMidi(fr.f0) : null;
    if (p != null && (p < o.midiLo || p > o.midiHi)) p = null;
    const gate = Math.max(o.gateMin, noise * o.gateK);
    const voiced = p != null && rms > gate;
    if (!voiced) noise = noise * 0.97 + Math.min(rms, 0.2) * 0.03;
    refPeak = Math.max(refPeak * 0.9995, rms, 0.02);
    // pennata: l'energia degli ultimi millisecondi sale di colpo rispetto a poco prima
    const prevTail = rmsHist.length >= 2 ? Math.min(...rmsHist.slice(-3)) : tail;
    const attack = rmsHist.length >= 2 && tail > o.attackK * prevTail && tail > gate * 1.5;
    rmsHist.push(tail); if (rmsHist.length > 8) rmsHist.shift();

    if (!cur) {
      if (!voiced) { cand = []; return out; }
      cand.push({ p, rms });
      if (cand.length >= o.onFrames && Math.abs(cand[cand.length - 1].p - cand[cand.length - 2].p) < o.onTol) {
        start(out, t, median(cand.slice(-o.onFrames).map(c => c.p)), Math.max(...cand.map(c => c.rms)), 'normale');
        cand = [];
      } else if (cand.length > 6) cand.shift();
      return out;
    }
    if (!voiced) { if (++cur.silent >= o.offFrames) stop(out, t); return out; }
    cur.silent = 0;

    // nuova pennata: si chiude la nota e se ne apre un'altra appena l'altezza è stabile
    if (attack && t - cur.t0 > o.attackMinS) { stop(out, t); cand = [{ p, rms }]; return out; }

    cur.hist.push({ t, p });
    if (cur.hist.length > 120) cur.hist.shift();
    checkVibrato(out, t);
    // un passo di un semitono in attesa: se ne segue un altro nella stessa direzione è uno slide, se no un legato
    if (cur.pend && t - cur.pend.t > o.stepWaitS) { const pd = cur.pend; cur.pend = null; legato(out, pd.t, pd.to, pd.from, pd.dir, rms); return out; }
    if (cur.vib) return out;                       // in vibrato l'altezza oscilla: niente bend o slide
    const d = p - cur.base;
    if (!cur.trans) {
      if (Math.abs(d) < o.stableTol) return out;
      cur.trans = { t, frames: [] };
    }
    const tr = cur.trans; tr.frames.push(p);
    // arrivata? le ultime landFrames altezze sono ferme
    const L = o.landFrames, last = tr.frames.slice(-L);
    if (last.length < L) return out;
    const spread = Math.max(...last) - Math.min(...last), here = median(last);
    if (spread > o.landSpread) return out;
    if (Math.abs(here - cur.base) < o.stableTol) { cur.trans = null; return out; }   // tornata: un'oscillazione, non un passaggio
    const moving = tr.frames.slice(0, tr.frames.length - L), delta = here - cur.base;
    const onFret = Math.abs(here - cur.tune - Math.round(here - cur.tune)) < o.fretTol;   // arrivata su un tasto (accordatura della nota)
    const r = Math.round(here - cur.tune);
    // salto rapido sui tasti, senza nuova pennata
    if (moving.length <= o.legatoFrames && onFret && Math.abs(delta) >= 0.7 && Math.abs(delta) <= o.legatoMaxSt) {
      const dir = delta > 0 ? 1 : -1, step = Math.abs(r - cur.int);
      if (cur.pend && cur.pend.dir === dir) {        // secondo scalino nella stessa direzione: è uno slide
        out.push({ type: 'gesture', id: cur.id, t, tech: 'slide', from: cur.pend.from, to: r, dir });
        cur.pend = null; cur.sliding = dir; cur.base = here; cur.int = r; cur.trans = null; return out;
      }
      if (cur.sliding === dir && step === 1) { cur.base = here; cur.int = r; cur.trans = null; return out; }   // lo slide continua
      if (step === 1) { cur.pend = { t, from: cur.int, to: r, dir }; cur.base = here; cur.trans = null; return out; }
      legato(out, t, r, cur.int, dir, rms);
      return out;
    }
    // passaggio lento: slide (sui tasti, a scalini) o bend (continuo, verso l'alto)
    const seq = [cur.base].concat(moving, [here]);
    let flat = 0; for (let i = 1; i < seq.length; i++) if (Math.abs(seq[i] - seq[i - 1]) < 0.07) flat++;
    const plateau = flat / Math.max(1, seq.length - 1);
    let tech = null;
    if (cur.bent && delta < 0 && Math.abs(here - (cur.base - cur.bent)) < 0.6) tech = 'release';
    else if (delta >= o.bendMinSt && delta <= o.bendMaxSt && plateau < o.slidePlateau) tech = 'bend';
    else if (onFret && Math.abs(delta) >= 0.7) tech = 'slide';
    if (!tech) { cur.trans = null; return out; }   // né tasto né bend: un'oscillazione larga, si ignora
    out.push({ type: 'gesture', id: cur.id, t, tech, from: +cur.base.toFixed(2), to: +here.toFixed(2), dir: delta > 0 ? 1 : -1, plateau: +plateau.toFixed(2) });
    cur.bent = tech === 'bend' ? cur.bent + delta : tech === 'release' ? 0 : cur.bent;
    if (tech === 'slide') cur.sliding = delta > 0 ? 1 : -1;
    cur.base = here; cur.int = Math.round(here - cur.tune); cur.trans = null;
    return out;
  }
  function legato(out, t, to, from, dir, rms) { stop(out, t); start(out, t, to, rms, dir > 0 ? 'hammer_on' : 'pull_off', from); }
  function flush(t) { const out = []; stop(out, t); return out; }
  return { feed, flush, get noise() { return noise; }, get active() { return cur ? cur.id : null; } };
}

/* ── altezza: autocorrelazione con "primo picco" anti-ottava ───────────── */
function autocorrelate(buf, sr) {
  const n = buf.length;
  const minLag = Math.max(2, Math.floor(sr / 1300)), maxLag = Math.min(n - 2, Math.ceil(sr / 70));
  const corr = new Float32Array(maxLag + 2);
  for (let lag = minLag - 1; lag <= maxLag + 1; lag++) {
    let c = 0; const lim = n - lag;
    for (let j = 0; j < lim; j++) c += buf[j] * buf[j + lag];
    corr[lag] = c / lim;                          // normalizzata: i ritardi lunghi non sono penalizzati
  }
  // salta la discesa iniziale (dove la correlazione cala solo perché il ritardo cresce):
  // il massimo va cercato dopo il primo minimo, altrimenti le note basse si perdono
  let s0 = minLag; while (s0 < maxLag && corr[s0 + 1] <= corr[s0]) s0++;
  let gmax = 0;
  for (let lag = s0; lag <= maxLag; lag++) if (corr[lag] > gmax) gmax = corr[lag];
  if (gmax <= 0) return -1;
  const thr = 0.85 * gmax;
  let best = -1;
  for (let lag = Math.max(s0, minLag + 1); lag <= maxLag; lag++) if (corr[lag] >= thr && corr[lag] > corr[lag - 1] && corr[lag] >= corr[lag + 1]) { best = lag; break; }
  if (best < 0) return -1;
  const a = corr[best - 1], b = corr[best], c = corr[best + 1], den = a - 2 * b + c;
  return sr / (best + (den !== 0 ? 0.5 * (a - c) / den : 0));
}

/** dal blocco audio al fotogramma: rms e altezza, su segnale dimezzato (metà calcolo) */
function analyseBlock(block, sr) {
  const n = block.length >> 1, half = new Float32Array(n);
  let e = 0;
  for (let i = 0; i < n; i++) { const v = (block[2 * i] + block[2 * i + 1]) * 0.5; half[i] = v; e += v * v; }
  const rms = Math.sqrt(e / n);
  let et = 0; const k0 = n - (n >> 2); for (let i = k0; i < n; i++) et += half[i] * half[i];
  const tail = Math.sqrt(et / (n - k0));            // ultimo quarto del blocco (~10 ms): serve per le pennate
  let mean = 0; for (let i = 0; i < n; i++) mean += half[i]; mean /= n;
  for (let i = 0; i < n; i++) half[i] -= mean;
  return { rms, tail, f0: rms > 0.002 ? autocorrelate(half, sr / 2) : -1 };
}

/* ── guscio browser: microfono → fotogrammi → eventi ───────────────────── */
async function createMic(onEvents, opts) {
  const o = opts || {};
  const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false } });
  const AC = o.context || new (window.AudioContext || window.webkitAudioContext)();
  if (AC.state === 'suspended') { try { await AC.resume(); } catch (e) {} }
  const src = AC.createMediaStreamSource(stream), an = AC.createAnalyser();
  an.fftSize = 2048; an.smoothingTimeConstant = 0;
  src.connect(an);
  const buf = new Float32Array(an.fftSize), L = createListener(o.listener);
  let raf = 0, last = 0, level = 0, alive = true;
  function frame() {
    if (!alive) return;
    raf = requestAnimationFrame(frame);
    const now = AC.currentTime; if (now === last) return;
    const dt = last ? now - last : 0.016; last = now;
    an.getFloatTimeDomainData(buf);
    const a = analyseBlock(buf, AC.sampleRate);
    level = a.rms;
    const ev = L.feed({ t: now, f0: a.f0, rms: a.rms, tail: a.tail, dt });
    if (ev.length) onEvents(ev);
  }
  raf = requestAnimationFrame(frame);
  return {
    get level() { return level; },
    get noise() { return L.noise; },
    stop() { alive = false; cancelAnimationFrame(raf); const ev = L.flush(AC.currentTime); if (ev.length) onEvents(ev); stream.getTracks().forEach(tr => tr.stop()); try { src.disconnect(); } catch (e) {} },
  };
}

return { createListener, autocorrelate, analyseBlock, createMic, DEFAULTS, toMidi };
}));
