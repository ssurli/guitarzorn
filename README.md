# guitarzorn

> **Between riffs & colors** — musica e pittura intrecciate: il suono(colore) del colore(suono).

Guitarzorn traslittera un riff di chitarra in un dipinto astratto a olio. L'analogia di partenza è tra due semplificazioni: la **scala pentatonica** (5 note) e la **tavolozza di Zorn** (4 pigmenti: ocra gialla, vermiglione, nero avorio, bianco di titanio). L'altezza della nota sceglie il colore, la tecnica (slide, bend, vibrato, power chord, tapping…) sceglie il gesto del pennello, il tempo scorre da sinistra a destra come su uno spartito.

Il riferimento teorico è la *transliteration* di Rosa Juritz: non cercare l'equivalente pittorico di un suono, ma usare il mezzo pittorico allo stesso modo in cui si usa quello musicale.

Il riff di lavoro è l'intro di *Johnny B. Goode* (Chuck Berry, 1958), in La minore pentatonica.

## Cosa c'è nel repository

| Percorso | Contenuto |
|---|---|
| `web-oil/` | Motore a olio nel browser: tela a pigmenti, bagnato su bagnato. Vedi sotto. |
| `live/` | `guitarzorn_live.html`, il painter dal vivo, e `improv_lab_bridge.js`, il ponte verso il looper di Guitar Improv Lab. |
| `score.py` | Partitura canonica dell'intro, condivisa da pittura e audio. |
| `zorn_riff_art*.py`, `zorn_riff_v4.py` … `zorn_riff_v9.py` | Le iterazioni del generatore in Python. |
| `zorn_linear.py`, `zorn_grid.py`, `zorn_spiral.py`, `zorn_palette_reference.py` | Varianti di impaginazione e riferimento della tavolozza. |
| `docs/` | Note di progetto: realismo della pennellata, traslitterazione v2, audit delle versioni, integrazione con Improv Lab. |
| `Parametri grafici.txt`, `come l'ho fatto veramente.txt`, `prompt*.txt` | Specifica bilingue tecnica → pennellata e appunti di studio. |
| `*.png` | Render delle varie versioni e immagine di riferimento. |

## Il motore a olio nel browser (`web-oil/`)

Una pagina statica, senza dipendenze e senza build: `index.html` più `riff-paint-oil.js`.

- **Tela a pigmenti.** Ogni pixel è una miscela dei quattro pigmenti di Zorn più uno spessore di pasta. Il colore si calcola dalla miscela con Kubelka-Munk (sottrattivo), mai mescolando in RGB.
- **Pennello a setole.** Ogni setola ha la sua carica di colore: deposita, raccoglie quello che attraversa, si scarica e a fine corsa lavora a pennello asciutto sulla grana della tela.
- **Rilievo.** Le setole lasciano creste nella pasta, illuminate dall'alto a sinistra.
- **Gesti, non glifi.** Una tecnica cambia *come* si muove il pennello (direzione, lunghezza, pressione, carica, ripetizione), non quale simbolo viene disegnato.
- **Incrementale.** La tela è persistente e le pennellate avanzano a passi, quindi le note si possono dipingere mentre lo spartito scorre.

Uso da codice:

```js
const eng = GuitarzornPaint7.create(canvas, 42);   // seed
eng.queueGround();                                  // stende il fondo
const events = eng.layoutRiff();                    // una voce per nota (x = tempo, y = altezza)
events.forEach((e, i) => eng.queueEvent(e, events[i + 1]));
(function frame() { if (!eng.tick(900)) requestAnimationFrame(frame); })();
```

`eng.paintNote({ note, velocity, technique, duration }, x, y)` dipinge una singola nota, per l'ingresso dal vivo.

**Limiti noti.** La resa non è ancora al livello di un olio vero: il rilievo della pasta è calcolato e risulta troppo regolare. Il riff incorporato è una versione ridotta a 12 note, non la partitura di `score.py`.

## Provarlo

Con GitHub Pages attivo sul branch `main` (cartella radice):

- motore a olio: `https://ssurli.github.io/guitarzorn/web-oil/`
- painter dal vivo: `https://ssurli.github.io/guitarzorn/live/guitarzorn_live.html`

In locale basta aprire `web-oil/index.html` nel browser.

## Licenza

Copyright © 2026 Stefano Surlinelli.

Distribuito con licenza **European Union Public Licence v. 1.2** (EUPL-1.2): vedi [`LICENSE`](LICENSE).

I caratteri tipografici della pagina `web-oil/` sono caricati da Google Fonts e restano soggetti alle rispettive licenze.
