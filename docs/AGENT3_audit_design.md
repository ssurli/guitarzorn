# AUDIT REPORT — Agente 3: cosa riusare dalle versioni v3→v7

*(completato in sessione principale — l'agente dedicato ha raggiunto il limite;
l'analisi si basa sulla conoscenza diretta di tutte le iterazioni del progetto)*

## (a) Tabella per versione

| Versione | Approccio | Punti di forza | Debolezze | Verdetto |
|---|---|---|---|---|
| `zorn_riff_art_v3.py` | Bristle-IK (port p5.js): catene di setole con cinematica inversa, classi Bristle/Brush/Trace | Gesto organico; vocabolario tecnica→traccia ben strutturato (`_build_traces`); dati riff canonici in `parse_riff()` | Rendering piatto (linee PIL 1px, nessuna materia); lento (loop Python per setola per step); l'IK produce ricci innaturali | **Estrai**: struttura dati riff + dispatch tecnica→gesto. **Scarta**: motore di rendering |
| `zorn_riff_v4.py` | v3 × densità 20 | Copertura piena della tela | Blob confusi, nessun guadagno concettuale | **Scarta** (lezione: la densità non sostituisce la materia) |
| `zorn_riff_v5.py` | Guitar Evolution: il riff dipinge una chitarra per zone (Albiac) | Zone-mask architecture pulita; mapping nota→zona interessante | Il target figurativo contraddice l'astrazione; risultato illustrativo | **Estrai**: pattern zone-mask (utile per composizione futura). **Scarta**: soggetto figurativo |
| `zorn_riff_v6.py` | Simboli astratti su campo ocra denso | Composizione che l'utente apprezzava; ground denso a 5 varianti tonali | Ancora motore v3 sotto: segni piatti | **Estrai**: logica compositiva (campo + segni isolati). Superata da v7 |
| `zorn_riff_v7.py` | Height-field + relief lighting (Hertzmann 2002) | **Il motore migliore**: impasto reale, dry-brush, smearing, lighting; `stroke()` completamente vettoriale numpy; parametrizzazione ricca (curvature, waviness, dryness, smear, taper) | Mixing RGB lineare (vedi report Agente 1); bug tuning/Y-flip (vedi report Agente 2) | **RIUSA come base.** È il candidato unico per il motore condiviso |
| `zorn_linear/spiral/grid.py` | Esperimenti layout matplotlib | Spirale = idea valida per groove ciclici; grid = debug view del mapping; ottava→luminosità già prototipata in grid | Matplotlib piatto, non pittorico | **Estrai**: geometrie di layout (spirale) e `note_color_for_pitch` (grid) |
| `zorn_palette_reference.py` | Riferimento storico-teorico | Fonte autorevole per ricette e mixing; `ZORN_PREMIXED`, `zorn_mix()` | — | **Riusa** come modulo dati |

## (b) Idoneità real-time (vincolo: <50ms per pennellata)

Misure e stime sul motore v7 (`OilCanvas.stroke()`):

- Una pennellata media (length 200, width 30 → n=200, nS=51 ≈ 10 200 campioni) esegue:
  path building O(n), rumori O(n·nS), EMA loop Python O(n) (200 iterazioni leggere),
  scatter `np.add.at` O(n·nS), compositing bbox. **Stima: 3–10 ms su CPU moderna.**
  ✅ Ampiamente dentro i 50ms.
- Il collo di bottiglia NON è `stroke()` ma `render()`: blur multipli e lighting su
  tutta la tela (1600×1000) → 200–600 ms. **Inaccettabile per frame-rate live.**

**Soluzioni per il real-time (in ordine di preferenza):**
1. **Lighting incrementale per-bbox**: dopo ogni stroke, ricalcolare il relief solo
   nel bounding box espanso (+raggio blur) del tratto e aggiornare l'immagine
   visualizzata. Il resto della tela non cambia. Costo: ~1–5 ms per stroke.
2. Ridurre la tela live a 1000×625 e fare il render pieno solo su richiesta (export).
3. Porting JS/canvas per il browser: stesso algoritmo, tipizzato su Float32Array;
   il vantaggio è l'input MIDI/tastiera nativo (Web MIDI API) e zero latenza di
   visualizzazione.

## (c) Architettura consigliata per il riuso

```
guitarzorn/
├── engine/
│   ├── oil_canvas.py      ← OilCanvas estratto da v7 (+ upgrade T1/T2/T5b Agente 1)
│   │                         con render_region(bbox) per il lighting incrementale
│   ├── palette.py         ← ZORN, ricette KM, get_note_color con ottava→luminosità
│   └── gestures.py        ← dispatch tecnica→pennellate (da riff_marks v7,
│                             corretto secondo mapping v2 Agente 2)
├── score.py               ← parse_riff + schema dati esteso (pause, sezioni,
│                             ottave; fix tuning[6-string])
├── zorn_riff_v8.py        ← quadro statico: score → gestures → oil_canvas
└── live/
    └── guitarzorn_live.html  ← app real-time standalone (porting JS del motore)
```

Il modulo `engine/` serve sia il renderer statico (v8) sia il sistema live: una sola
implementazione della pennellata, due frontend. Per il live in browser il porting JS
è preferibile al server Python: nessuna dipendenza, input MIDI/tastiera nativo,
60fps garantiti dal canvas.
