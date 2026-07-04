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

  // In Guitar Improv Lab, LOOPER e' un `const` globale di uno script classico:
  // un const NON diventa window.LOOPER, ma resta accessibile per nome nudo
  // (stesso ambiente lessicale globale condiviso fra script classici).
  function getLooper() {
    try { if (typeof LOOPER !== 'undefined' && LOOPER) return LOOPER; } catch (e) {}
    return window.LOOPER || null;
  }

  /* ── pitch detection: autocorrelazione con "primo picco" anti-ottava ──────
     L'autocorrelazione classica prende il picco MASSIMO, che spesso cade a un
     multiplo del vero periodo → nota un'ottava (o più) troppo bassa. Qui, dopo
     aver trovato il massimo globale, si prende il PRIMO picco (periodo più
     corto) che sia almeno l'85% del massimo: è la fondamentale reale. Con
     interpolazione parabolica per la precisione sub-campione. */
  function localAutocorrelate(buf, sampleRate) {
    const n = buf.length;
    let rms = 0;
    for (let i = 0; i < n; i++) rms += buf[i] * buf[i];
    if (Math.sqrt(rms / n) < 0.02) return -1;
    const minLag = Math.max(2, Math.floor(sampleRate / 1300));   // fino a ~1300 Hz
    const maxLag = Math.min(n - 2, Math.ceil(sampleRate / 70));   // giù a ~70 Hz
    const corr = new Float32Array(maxLag + 2);
    let gmax = 0;
    for (let lag = minLag; lag <= maxLag; lag++) {
      let c = 0;
      const lim = n - lag;
      for (let j = 0; j < lim; j++) c += buf[j] * buf[j + lag];
      corr[lag] = c;
      if (c > gmax) gmax = c;
    }
    if (gmax <= 0) return -1;
    const thr = 0.85 * gmax;                       // soglia "quasi-massimo"
    let bestLag = -1;
    for (let lag = minLag + 1; lag < maxLag; lag++) {
      if (corr[lag] >= thr && corr[lag] > corr[lag - 1] && corr[lag] >= corr[lag + 1]) {
        bestLag = lag; break;                      // primo picco forte = fondamentale
      }
    }
    if (bestLag < 0) return -1;
    // interpolazione parabolica attorno al picco
    const a = corr[bestLag - 1], b = corr[bestLag], c = corr[bestLag + 1];
    const denom = a - 2 * b + c;
    const shift = denom !== 0 ? 0.5 * (a - c) / denom : 0;
    return sampleRate / (bestLag + shift);
  }

  /* ── trascrizione: AudioBuffer → eventi nota ─────────────────────────────── */
  function transcribe(buffer) {
    const sr = buffer.sampleRate;
    const raw = buffer.getChannelData(0);

    // NORMALIZZAZIONE: le registrazioni da microfono hanno livelli molto
    // variabili. Scalo l'intero segnale al ~95% del fondo scala rispetto al
    // suo picco, cosi' il rilevamento del pitch e' indipendente dal volume di
    // registrazione (il silenzio resta proporzionalmente basso).
    let peak = 0;
    for (let i = 0; i < raw.length; i++) { const a = Math.abs(raw[i]); if (a > peak) peak = a; }
    const gain = peak > 1e-4 ? 0.95 / peak : 1;
    const data = new Float32Array(raw.length);
    for (let i = 0; i < raw.length; i++) data[i] = raw[i] * gain;

    // uso una copia locale di autocorrelate: la sua soglia RMS interna e' nota
    // e lavoro su segnale normalizzato (evito dipendenze dai gate del tuner)
    const ac = localAutocorrelate;
    const WIN = 2048, HOP = 512;
    const hopSec = HOP / sr;

    // 1. analisi per finestra: pitch + energia (su segnale normalizzato)
    const frames = [];
    const seg = new Float32Array(WIN);
    let voiced = 0;
    for (let i = 0; i + WIN <= data.length; i += HOP) {
      seg.set(data.subarray(i, i + WIN));
      let e = 0;
      for (let j = 0; j < WIN; j++) e += seg[j] * seg[j];
      const rms = Math.sqrt(e / WIN);
      const f = rms > 0.03 ? ac(seg, sr) : -1;         // gate su segnale normalizzato
      const midi = f > 0 ? Math.round(69 + 12 * Math.log2(f / 440)) : -1;
      const ok = (midi >= 36 && midi <= 88);
      if (ok) voiced++;
      frames.push({ t: i / sr, midi: ok ? midi : -1, rms });
    }

    // 1b. correzione errori d'ottava: se un frame salta di ~12 semitoni
    // rispetto ai vicini, riportalo all'ottava dominante (glitch tipico
    // dell'autocorrelazione sulla chitarra)
    for (let i = 1; i < frames.length - 1; i++) {
      const a = frames[i - 1].midi, b = frames[i].midi, c = frames[i + 1].midi;
      if (a > 0 && c > 0 && b > 0 && Math.abs(a - c) <= 1 && Math.abs(b - a) >= 11)
        frames[i].midi = a;
    }

    // 2. raggruppa le finestre in note. La nota corre finche' il pitch resta
    //    entro ±1.5 semitoni dalla MEDIANA corrente dei suoi frame (robusto a
    //    bend/vibrato). Ogni nota raccoglie tutti i suoi midi: la tonalita'
    //    finale sara' la MODA (non l'attacco, che e' rumoroso).
    const events = [];
    let cur = null;
    const flush = () => {
      if (!cur) return;
      // moda dei midi della nota
      const counts = {};
      let mode = cur.midis[0], best = 0;
      for (const m of cur.midis) {
        counts[m] = (counts[m] || 0) + 1;
        if (counts[m] > best) { best = counts[m]; mode = m; }
      }
      cur.midi = mode;
      // ampiezza dell'escursione di pitch → indizio di vibrato/bend
      let lo = 999, hi = 0;
      for (const m of cur.midis) { if (m < lo) lo = m; if (m > hi) hi = m; }
      cur.span = hi - lo;
      events.push(cur);
      cur = null;
    };
    const median = arr => {
      const s = arr.slice().sort((x, y) => x - y);
      return s[s.length >> 1];
    };
    for (const fr of frames) {
      const on = fr.midi > 0;
      if (cur && on && Math.abs(fr.midi - median(cur.midis)) <= 1.5) {
        cur.end = fr.t + hopSec;
        cur.peak = Math.max(cur.peak, fr.rms);
        cur.midis.push(fr.midi);
        cur.sil = 0;
      } else if (on) {
        flush();
        cur = { t0: fr.t, end: fr.t + hopSec, peak: fr.rms, midis: [fr.midi], sil: 0 };
      } else if (cur && ++cur.sil > 4) {              // tollera fino a ~4 buchi
        flush();
      }
    }
    flush();

    // 3. eventi finali: filtra i glitch corti, velocity dall'energia di picco
    const out = events
      .filter(e => e.end - e.t0 >= 0.06)
      .map(e => ({
        midi: e.midi,
        start: +e.t0.toFixed(3),                       // secondi (bpm=60 → beat)
        duration: +Math.max(0.12, e.end - e.t0).toFixed(3),
        velocity: +Math.min(1.4, 0.45 + e.peak * 3).toFixed(2),
        technique: e.span >= 2 ? 'vibrato' : undefined
      }));

    // diagnostica: se la trascrizione fallisce, questi numeri dicono perche'
    console.log('[guitarzorn] trascrizione: picco=' + peak.toFixed(4) +
      ' gain=' + gain.toFixed(1) + ' frame=' + frames.length +
      ' con-pitch=' + voiced + ' note=' + out.length);
    return out;
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
    const L = getLooper();
    if (!L || !L.buffer) {
      alert('Registra prima un giro con il Looper (REC), poi premi DIPINGI.');
      return;
    }
    const events = transcribe(L.buffer);
    if (!events.length) {
      alert('Nessuna nota riconosciuta nel loop.\n\nSuggerimenti:\n' +
            '• suona note singole e distinte (non accordi fitti)\n' +
            '• assicurati che il volume del loop sia udibile\n' +
            '• apri la Console (F12) per i dettagli della trascrizione');
      return;
    }
    sendToZorn(events);
    console.log('[guitarzorn bridge] loop trascritto:', events);
  }

  function exportJSON() {
    const L = getLooper();
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
