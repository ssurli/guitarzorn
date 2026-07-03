/* ============================================================================
   guitarzorn ↔ Guitar Improv Lab — BRIDGE
   ----------------------------------------------------------------------------
   Script drop-in per Guitar Improv Lab (repo `guitar`, index.html):
   aggiunge al Looper il pulsante 🎨 DIPINGI che:
     1. prende il loop registrato (LOOPER.buffer, AudioBuffer dal microfono)
     2. lo trascrive in note con autocorrelazione (riusa autocorrelate() del
        tuner se presente, altrimenti usa la copia inclusa qui)
     3. apre guitarzorn_live.html e gli invia gli eventi: la tela dipinge
        (e suona) il tuo giro, pennellata per pennellata.

   INSTALLAZIONE (una riga, in fondo a index.html del repo guitar):
     <script src="URL/di/improv_lab_bridge.js"></script>
   Config opzionale PRIMA dello script:
     <script>window.GUITARZORN_URL = 'https://.../guitarzorn_live.html';</script>

   In alternativa, senza toccare il repo: incolla questo file nella console
   della pagina di Guitar Improv Lab con un loop già registrato.

   Protocollo (accettato da guitarzorn_live.html):
     { type:'loop', bpm, events:[{ midi, start, duration, velocity }] }
     via BroadcastChannel('guitarzorn') e window.postMessage.
   ========================================================================= */
(function () {
  'use strict';

  const ZORN_URL = window.GUITARZORN_URL || '../guitarzorn/live/guitarzorn_live.html';

  /* ── pitch detection (fallback identico all'algoritmo del tuner) ─────────── */
  function localAutocorrelate(buf, sampleRate) {
    const n = buf.length;
    let rms = 0;
    for (let i = 0; i < n; i++) rms += buf[i] * buf[i];
    if (Math.sqrt(rms / n) < 0.015) return -1;
    const minLag = Math.floor(sampleRate / 1300);
    const maxLag = Math.min(n - 2, Math.ceil(sampleRate / 75));
    let maxCorr = -1, bestLag = -1;
    for (let lag = minLag; lag <= maxLag; lag++) {
      let c = 0;
      const lim = n - lag;
      for (let j = 0; j < lim; j++) c += buf[j] * buf[j + lag];
      if (c > maxCorr) { maxCorr = c; bestLag = lag; }
    }
    if (bestLag < 1) return -1;
    return sampleRate / bestLag;
  }

  /* ── trascrizione: AudioBuffer → eventi nota ─────────────────────────────── */
  function transcribe(buffer) {
    const ac = (typeof window.autocorrelate === 'function')
      ? window.autocorrelate : localAutocorrelate;
    const sr = buffer.sampleRate;
    const data = buffer.getChannelData(0);
    const WIN = 2048, HOP = 512;
    const hopSec = HOP / sr;

    // 1. analisi per finestra: pitch + energia
    const frames = [];
    const seg = new Float32Array(WIN);
    for (let i = 0; i + WIN <= data.length; i += HOP) {
      seg.set(data.subarray(i, i + WIN));
      let e = 0;
      for (let j = 0; j < WIN; j++) e += seg[j] * seg[j];
      const rms = Math.sqrt(e / WIN);
      const f = rms > 0.012 ? ac(seg, sr) : -1;
      const midi = f > 0 ? Math.round(69 + 12 * Math.log2(f / 440)) : -1;
      frames.push({ t: i / sr, midi: (midi >= 36 && midi <= 88) ? midi : -1, rms });
    }

    // 2. raggruppa le finestre in note (tollera ±1 semitono per vibrato/bend)
    const events = [];
    let cur = null;
    const flush = () => { if (cur) { events.push(cur); cur = null; } };
    for (const fr of frames) {
      const on = fr.midi > 0;
      if (cur && on && Math.abs(fr.midi - cur.midi) <= 1) {
        cur.end = fr.t + hopSec;
        cur.peak = Math.max(cur.peak, fr.rms);
        cur.bendy += (fr.midi !== cur.midi) ? 1 : 0;
        cur.sil = 0;
      } else if (on) {
        flush();
        cur = { midi: fr.midi, t0: fr.t, end: fr.t + hopSec,
                peak: fr.rms, bendy: 0, sil: 0 };
      } else if (cur && ++cur.sil > 3) {
        flush();
      }
    }
    flush();

    // 3. eventi finali: filtra i glitch corti, velocity dall'energia di picco
    return events
      .filter(e => e.end - e.t0 >= 0.07)
      .map(e => ({
        midi: e.midi,
        start: +e.t0.toFixed(3),                     // secondi (bpm=60 → beat)
        duration: +Math.max(0.12, e.end - e.t0).toFixed(3),
        velocity: +Math.min(1.4, 0.45 + e.peak * 6).toFixed(2),
        technique: e.bendy > 4 ? 'vibrato' : undefined
      }));
  }

  /* ── invio a guitarzorn ──────────────────────────────────────────────────── */
  let zornWin = null;
  function sendToZorn(events) {
    const msg = { type: 'loop', bpm: 60, events };
    let sent = false;
    try { new BroadcastChannel('guitarzorn').postMessage(msg); sent = true; } catch (e) {}
    if (!zornWin || zornWin.closed) {
      zornWin = window.open(ZORN_URL, 'guitarzorn');
      // la tela deve prepararsi prima di ricevere il loop
      setTimeout(() => { try { zornWin.postMessage(msg, '*'); } catch (e) {} }, 2600);
    } else {
      try { zornWin.postMessage(msg, '*'); zornWin.focus(); } catch (e) {}
    }
    return sent;
  }

  function paintLoop() {
    const L = window.LOOPER;
    if (!L || !L.buffer) {
      alert('Registra prima un giro con il Looper (REC), poi premi DIPINGI.');
      return;
    }
    const events = transcribe(L.buffer);
    if (!events.length) {
      alert('Nessuna nota riconosciuta nel loop — riprova con un giro più pulito.');
      return;
    }
    sendToZorn(events);
    console.log('[guitarzorn bridge] loop trascritto:', events);
  }

  function exportJSON() {
    const L = window.LOOPER;
    if (!L || !L.buffer) { alert('Registra prima un loop.'); return; }
    const events = transcribe(L.buffer);
    const blob = new Blob([JSON.stringify({ bpm: 60, events }, null, 2)],
                          { type: 'application/json' });
    const a = document.createElement('a');
    a.download = 'loop_guitarzorn.json';
    a.href = URL.createObjectURL(blob);
    a.click();
    URL.revokeObjectURL(a.href);
  }

  /* ── UI: pulsante nel deck del looper ────────────────────────────────────── */
  function inject() {
    const controls = document.querySelector('.looper-controls');
    if (!controls || document.getElementById('loop-paint-btn')) return;
    const mk = (id, icon, lbl, fn, title) => {
      const b = document.createElement('button');
      b.className = 'looper-btn'; b.id = id; b.title = title;
      b.innerHTML = '<span class="looper-btn-icon">' + icon + '</span>' +
                    '<span class="looper-btn-lbl">' + lbl + '</span>';
      b.addEventListener('click', fn);
      controls.appendChild(b);
    };
    mk('loop-paint-btn', '🎨', 'DIPINGI', paintLoop,
       'Trascrive il loop in note e lo dipinge su guitarzorn (olio virtuale, palette Zorn)');
    mk('loop-export-btn', '⇩', 'NOTE JSON', exportJSON,
       'Esporta la trascrizione del loop come JSON (caricabile in guitarzorn con "Carica loop")');
  }
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', inject);
  else inject();

  window.guitarzornBridge = { transcribe, paintLoop, exportJSON, sendToZorn };
})();
