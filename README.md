# guitarzorn

> **Between riffs & colors** — musica e pittura intrecciate: il suono(colore) del colore(suono).

Guitarzorn traduce in pittura, in tempo reale, quello che suona una chitarra. L'idea di partenza è un'analogia tra due semplificazioni: la **scala pentatonica** (5 note) semplifica la musica come la **tavolozza di Zorn** (4 pigmenti: ocra gialla, vermiglione, nero avorio, bianco di titanio) semplifica la pittura.

Una codifica fissa collega i due mondi:

- la **nota** sceglie il pigmento;
- l'**ottava** la luminosità;
- la **tecnica** (hammer-on, pull-off, slide, bend, vibrato…) il tipo di pennellata;
- la **dinamica** quanto colore e quanta pasta.

Le note possono arrivare da una tablatura, dalla tastiera del computer o, in prospettiva, direttamente dallo strumento.

Il riferimento teorico è la *transliteration* di Rosa Juritz: non cercare l'equivalente pittorico di un suono, ma usare il mezzo pittorico allo stesso modo in cui si usa quello musicale.

## Provarlo

Con GitHub Pages attivo sul branch `main` (cartella radice), la pagina principale è:

**`https://ssurli.github.io/guitarzorn/web-oil/`**

1. Scegli un esempio (*Johnny B. Goode* o uno dei sei studi) oppure incolla una tablatura.
2. Imposta il tempo in battiti al minuto e scegli il suono (chitarra classica, acustica, elettrica o sintetico).
3. Premi **Suona e dipingi**. Con **Tela vuota** puoi invece suonare a mano: `Z X C V B` · `A S D F G` · `W E R T Y` (La minore pentatonica su tre ottave, Maiusc = forte), oppure i cinque tasti a schermo.

In locale basta aprire `web-oil/index.html` nel browser, ma i suoni campionati si caricano solo da un server: servi la cartella (per esempio `python -m http.server` dentro `web-oil/`), altrimenti la pagina usa il sintetizzatore.

## La codifica

È in un solo file, [`web-oil/codifica.js`](web-oil/codifica.js), ricavato da `Parametri grafici.txt`. La pagina la mostra anche come legenda.

| Nota | Pigmento | Ruolo |
|---|---|---|
| A | Giallo ocra | tonica |
| C | Rosso vermiglione | terza minore |
| D | Nero avorio | quarta |
| E | Bianco di titanio | quinta |
| G | Ocra + nero | settima minore |
| Bb, F | Rosso scuro, grigio | note esterne |
| altre | sfumatura tra le due note di scala vicine | note esterne |

Stessa nota in un'ottava diversa: stessa tinta, più chiara salendo e più scura scendendo.

| Tecnica | In tablatura | Pennellata |
|---|---|---|
| Nota singola | `5` | corta se la nota è breve, lunga e sfumata se è tenuta |
| Hammer-on / pull-off | `5h7` / `7p5` | due macchie ravvicinate con sfumatura di unione |
| Slide | `5/7` | diagonale continua che scivola |
| Bend | `7b9` | curva che si piega verso l'alto |
| Vibrato | `7~` | pennellata tremolante |
| Bicordo | due note nella stessa colonna | due pennellate sovrapposte |
| Power chord | tre note, o una quinta sui bassi | blocco squadrato, colori fusi |
| Tapping | `t12` | piccole gocce di luce |
| Armonico | `<12>` | alone leggero, molto chiaro |

Staccato, legato, armonico artificiale e leva del tremolo sono nella codifica ma non hanno un simbolo di tablatura: si usano scrivendo gli eventi.

**Tablatura.** Sei righe di testo, cantino in alto, accordatura standard. La tablatura non scrive il ritmo: la posizione orizzontale è il tempo, con le colonne per battito e i battiti al minuto impostati prima di suonare. Ogni nota dura fino alla successiva.

## Il motore pittorico

Una pagina statica, senza dipendenze e senza build.

- **Tela a pigmenti.** Ogni pixel è una miscela dei quattro pigmenti di Zorn più uno spessore di pasta. Il colore si calcola dalla miscela con Kubelka-Munk (sottrattivo), mai mescolando in RGB.
- **Pennello a setole.** Ogni setola ha la sua carica di colore: deposita, raccoglie quello che attraversa, si scarica e a fine corsa lavora a pennello asciutto sulla grana della tela. Dopo ogni nota un pennello pulito sfuma il segno nel fondo.
- **Pennellata dal vivo.** Il pennello atterra quando la nota inizia, avanza finché è tenuta e si alza quando finisce: non serve sapere in anticipo quanto durerà.
- **Gesti, non glifi.** Una tecnica cambia *come* si muove il pennello (direzione, curvatura, velocità, pressione, carica), non quale simbolo viene disegnato.
- **Rilievo.** Le setole lasciano creste nella pasta, illuminate dall'alto a sinistra.

| File | Ruolo |
|---|---|
| `web-oil/index.html` | La pagina: brano, tempo, tablatura, suono, tastiera, legenda |
| `web-oil/riff-paint-oil.js` | Il motore pittorico |
| `web-oil/codifica.js` | La codifica |
| `web-oil/tab.js` | Lettore di tablature e sei studi originali in La minore pentatonica |
| `web-oil/suoni/` | Chitarra classica, acustica ed elettrica, una registrazione per nota (MIDI 40–88) |

Uso da codice:

```js
const eng = GuitarzornPaint7.create(canvas, 42);   // seed della tela
eng.queueGround();                                  // stende il fondo a impasto
eng.noteOn('n1', { note: 'C', velocity: 'f', x: 300, y: 400, ang: -0.3 });   // il pennello atterra
// … finché la nota è tenuta, a ogni fotogramma:
eng.tick(900, dt);                                  // dt in secondi
eng.noteOff('n1');                                  // il pennello si alza e si asciuga
```

## Stato e prossimi passi

**Suonare con la chitarra.** Il collegamento con la chitarra passa da [Guitar Improv Lab](https://ssurli.github.io/guitar/), che ascolta lo strumento dal microfono: oggi registra un giro nel looper e, con 🎨 DIPINGI, lo fa dipingere dopo, non mentre suoni.

**Limiti noti.**
- La resa non è ancora al livello di un olio vero: il rilievo della pasta è calcolato e risulta troppo regolare.
- Tapping e armonici sono quasi invisibili sul fondo chiaro.
- I power chord fondono i colori in un bruno simile per ogni accordo.

**Prossimi passi.**
1. **Ricevere i giri dal looper di [Guitar Improv Lab](https://ssurli.github.io/guitar/).** Oggi il pulsante 🎨 DIPINGI del looper manda il giro a `live/`, non a questa pagina.
2. **Ingresso dalla chitarra in tempo reale.** Nota, bend, slide e vibrato letti dall'altezza del suono; il riconoscimento dell'altezza esiste già in Guitar Improv Lab.
3. **Pennellate fotografate.** Pennellate vere, dipinte e fotografate, al posto del rilievo calcolato.

## Cosa c'è nel repository

| Percorso | Contenuto |
|---|---|
| `web-oil/` | **La pagina principale**, descritta sopra. |
| `live/` | Il painter precedente (`guitarzorn_live.html`), con ingresso MIDI e loop, e `improv_lab_bridge.js`, il ponte usato oggi dal looper di [Guitar Improv Lab](https://ssurli.github.io/guitar/). |
| `score.py` | Partitura canonica dell'intro di *Johnny B. Goode*, condivisa da pittura e audio. |
| `zorn_riff_art*.py`, `zorn_riff_v4.py` … `zorn_riff_v9.py` | Le iterazioni del generatore in Python. |
| `zorn_linear.py`, `zorn_grid.py`, `zorn_spiral.py`, `zorn_palette_reference.py` | Varianti di impaginazione e riferimento della tavolozza. |
| `docs/` | Note di progetto: realismo della pennellata, traslitterazione v2, audit delle versioni, integrazione con Improv Lab. |
| `Parametri grafici.txt`, `come l'ho fatto veramente.txt`, `prompt*.txt` | La specifica musica → pittura e appunti di studio. |
| `*.png` | Render delle varie versioni e immagine di riferimento. |

## Licenza

Copyright © 2026 Stefano Surlinelli.

Distribuito con licenza **European Union Public Licence v. 1.2** (EUPL-1.2): vedi [`LICENSE`](LICENSE).

I caratteri tipografici della pagina `web-oil/` sono caricati da Google Fonts e restano soggetti alle rispettive licenze.

I suoni di chitarra in `web-oil/suoni/` vengono dal soundfont *FluidR3_GM* (Frank Wen), nella resa per nota del progetto midi-js-soundfonts, e restano sotto licenza Creative Commons Attribuzione 3.0: vedi [`web-oil/suoni/LEGGIMI.md`](web-oil/suoni/LEGGIMI.md).
