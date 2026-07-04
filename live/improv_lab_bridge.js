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

  /* ── pannello inline: guitarzorn incastrato sotto il looper ───────────────── */
  let panel = null, frame = null, frameReady = false, pending = null, pinger = 0;

  function buildPanel() {
    if (panel) return;
    panel = document.createElement('div');
    panel.id = 'guitarzorn-panel';
    panel.style.cssText =
      'margin:18px 0 6px;border:1px solid rgba(255,255,255,.14);border-radius:10px;' +
      'overflow:hidden;background:#141414;display:none;box-shadow:0 8px 30px rgba(0,0,0,.4)';
    const bar = document.createElement('div');
    bar.style.cssText =
      'display:flex;align-items:center;justify-content:space-between;gap:10px;' +
      'padding:8px 12px;font:600 12px/1.2 system-ui,sans-serif;color:#e5c07b;' +
      'letter-spacing:.08em;background:#1c1712;border-bottom:1px solid rgba(255,255,255,.08)';
    bar.innerHTML = '<span>🎨 GUITARZORN — il tuo giro dipinto a olio</span>';
    const acts = document.createElement('div');
    acts.style.cssText = 'display:flex;gap:8px';
    const mkA = (txt, fn) => {
      const b = document.createElement('button');
      b.textContent = txt;
      b.style.cssText =
        'background:#2a2018;color:#e5e5e5;border:1px solid #3a3025;border-radius:6px;' +
        'padding:4px 10px;font:600 11px system-ui;cursor:pointer';
      b.addEventListener('click', fn);
      return b;
    };
    const openBtn = mkA('↗ scheda', () => window.open(ZORN_URL, 'guitarzorn'));
    const closeBtn = mkA('✕ chiudi', () => { panel.style.display = 'none'; });
    acts.appendChild(openBtn); acts.appendChild(closeBtn);
    bar.appendChild(acts);
    frame = document.createElement('iframe');
    frame.src = ZORN_URL;
    frame.title = 'guitarzorn';
    frame.style.cssText = 'display:block;width:100%;height:min(70vh,760px);border:0;background:#111';
    frame.allow = 'autoplay';
    frame.addEventListener('load', () => { frameReady = false; startPing(); });
    panel.appendChild(bar);
    panel.appendChild(frame);
    // il pannello vive subito sotto il deck del looper
    const deck = document.querySelector('.looper-deck') ||
                 document.querySelector('.looper-controls');
    if (deck && deck.parentNode) deck.parentNode.insertBefore(panel, deck.nextSibling);
    else document.body.appendChild(panel);
  }

  // handshake: pinga finché guitarzorn non risponde 'ready', poi invia il loop
  function startPing() {
    clearInterval(pinger);
    let tries = 0;
    pinger = setInterval(() => {
      if (frameReady || ++tries > 40) { clearInterval(pinger); return; }
      try { frame.contentWindow.postMessage({ type: 'guitarzorn:ping' }, '*'); } catch (e) {}
    }, 250);
  }

  window.addEventListener('message', ev => {
    const d = ev.data;
    if (d && d.type === 'guitarzorn:ready') {
      frameReady = true;
      clearInterval(pinger);
      if (pending) { postToFrame(pending); pending = null; }
    }
  });

  function postToFrame(msg) {
    try { frame.contentWindow.postMessage(msg, '*'); } catch (e) {}
    try { new BroadcastChannel('guitarzorn').postMessage(msg); } catch (e) {}
  }

  function sendToZorn(events) {
    const msg = { type: 'loop', bpm: 60, events };
    buildPanel();
    panel.style.display = 'block';
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    if (frameReady) postToFrame(msg);      // tela già pronta → dipingi subito
    else { pending = msg; startPing(); }   // altrimenti attendi l'handshake
    return true;
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
