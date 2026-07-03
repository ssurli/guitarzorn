# Integrazione guitarzorn ↔ Guitar Improv Lab (looper)

Il looper di Guitar Improv Lab (repo `guitar`, sezione Basi → 🔁 Looper) registra
**audio dal microfono** (`MediaRecorder` → `AudioBuffer` in `LOOPER.buffer`).
guitarzorn dipinge **eventi nota**. Il ponte fra i due mondi è
`live/improv_lab_bridge.js`: trascrive il loop audio in note via autocorrelazione
(lo stesso algoritmo dell'accordatore del progetto guitar) e le invia alla tela.

## Flusso

```
Guitar Improv Lab                          guitarzorn_live.html
─────────────────                          ────────────────────
🎸 REC → loop audio (AudioBuffer)
   │
   ▼
🎨 DIPINGI (bridge)
   ├─ trascrizione: finestre 2048/512,
   │  autocorrelate() → pitch → MIDI,
   │  RMS → velocity, raggruppamento
   │  in note (±1 semitono = vibrato)
   ▼
   { type:'loop', bpm:60, events:[...] }
   ── BroadcastChannel('guitarzorn') ──►  scheduleEvents(): suona e
   ── window.postMessage ─────────────►  dipinge ogni nota (olio KM,
                                          pennellate stile Pollock/Kandinsky)
```

## Installazione del bridge (lato Guitar Improv Lab)

Una riga in fondo a `index.html` del repo `guitar`:

```html
<script>window.GUITARZORN_URL = 'https://ssurli.github.io/guitarzorn/live/guitarzorn_live.html';</script>
<script src="https://ssurli.github.io/guitarzorn/live/improv_lab_bridge.js"></script>
```

(oppure copia `improv_lab_bridge.js` nel repo guitar e usa un path relativo).
Il bridge aggiunge da solo due pulsanti al deck del looper:

- **🎨 DIPINGI** — trascrive il loop e apre/riusa la finestra guitarzorn che lo
  suona e lo dipinge
- **⇩ NOTE JSON** — scarica la trascrizione come file JSON, caricabile in
  guitarzorn con il pulsante **Carica loop**

Per provare senza toccare il repo: incolla il contenuto di
`improv_lab_bridge.js` nella console della pagina con un loop già registrato.

## Protocollo messaggi (accettato da guitarzorn_live.html)

Canali equivalenti: `BroadcastChannel('guitarzorn')` (stessa origin, es. due tab
di ssurli.github.io), `window.postMessage` (iframe / window.open), API diretta
`window.guitarzorn`.

```js
{ type: 'noteOn',  midi: 57, velocity: 100, technique: 'vibrato' } // live
{ type: 'noteOff', midi: 57 }
{ type: 'loop', bpm: 60, events: [                                  // loop intero
    { midi: 45, start: 0.0, duration: 0.5, velocity: 1.1, technique: 'staccato' },
    ...
  ] }
{ type: 'clear', newSeed: true }                                    // nuova tela
```

- `velocity`: MIDI 0–127 oppure normalizzata 0–1.4 oppure 'p'/'mp'/'mf'/'f'/'ff'
- `start`/`duration` in beat rispetto a `bpm` (il bridge usa bpm=60 → secondi)
- `technique` opzionale: staccato, legato, slide, hammer_on, bend, vibrato,
  powerchord, tapping, dive, harmonic_natural, harmonic_artificial

## Limiti noti della trascrizione

- **Monofonica**: l'autocorrelazione rileva una nota alla volta — accordi e
  powerchord vengono ridotti alla fondamentale (il basso percettivo). Per il
  loop tipico (riff/lick single-note) funziona bene.
- Range chitarra 75–1300 Hz (MIDI 36–88); note fuori range vengono scartate.
- Il vibrato viene riconosciuto (oscillazione ±1 semitono → technique 'vibrato');
  bend lenti possono produrre due note adiacenti.
- L'overdub è già mixato in `LOOPER.buffer`: si trascrive la somma degli strati.

## Verifica automatica

`live/bridge_screenshot.png` — prodotto da test Playwright: (1) `paintLoop` con
6 eventi dipinge il contorno melodico senza errori console; (2) la trascrizione
di 3 note sintetiche (A2, C3, D3 a dente di sega, envelope pluck) restituisce
esattamente MIDI 45/48/50 con timing corretto.
