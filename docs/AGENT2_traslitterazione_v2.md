# GUITARZORN — DESIGN DOCUMENT: Traslitterazione v2

*Agente 2 — Transliteration Design | basato su: `Parametri grafici.txt`,
`zorn_riff_v7.py`, `zorn_palette_reference.py`, `zorn_spiral.py`, `zorn_grid.py`,
`zorn_linear.py`*

## 1. Stato attuale (v7) in sintesi

v7 è un renderer a olio eccellente ma la **traslitterazione** è rimasta a metà: dei 6
parametri musicali disponibili, solo 3 (pitch→Y, tempo→X, tecnica→forma) sono mappati
con costanza; velocity fa doppio lavoro (dimensione E luminosità), la durata influenza
la lunghezza solo per legato/vibrato, e l'ottava non esiste come dimensione.

**Due difetti oggettivi trovati nel codice:**

1. **Inversione delle corde** — `tuning = [40,45,50,55,59,64]` indicizzato con
   `tuning[string - 1]`, ma nei dati `string=6` è il MI basso. Risultato: corda 6 →
   E4, corda 1 → E2. La prima nota (A, tasto 5, corda 6) diventa MIDI 69 (A4) invece
   di 45 (A2). `zorn_grid.py:51` fa la cosa giusta (`TUNING[6 - string_num]`). Le
   classi di nota (e quindi i colori) restano corrette, ma **il contorno melodico sul
   quadro è strapazzato**.
2. **Asse Y invertito** — `_ty()` mappa MIDI alto → y grande, ma in PIL y cresce verso
   il basso: le note acute finiscono in basso. Il documento originale vuole
   "altezza = altezza".

## 2. Gap analysis: documento originale vs v7

### Tradotto fedelmente
| Vocabolo del documento | Implementazione v7 |
|---|---|
| X = tempo cumulato in battiti | `_tx()`, 240 px/beat |
| Palette Zorn rigorosa, mix lineare RGB | `ZORN` + `zorn_blend`, nessun colore fuori gamma |
| Sfondo/ground ocra partecipante | `ground()` a pennellate materiche |
| Tecnica → forma | 11 tecniche distinte in `riff_marks()` |
| Vibrato = pennellata ondulata | `waviness=9, wave_freq=5` — fedele |
| Bend = curva "tirata" | `curvature=-1.20` — fedele |
| Jitter solo come "mano" | `_J_POS/_J_ANG` e tremolio setole — corretto in spirito |

### Semplificato / deviato
| Documento | v7 | Giudizio |
|---|---|---|
| A=ocra, C=vermiglio, G=ocra+nero | A=vermiglio, C=ocra(+38% verm.), G=oro | Deviazione documentata (tonica = colore dominante). Da mantenere come mapping ufficiale v2. |
| Velocity → spessore + saturazione | Velocity → luminosità + scala | La luminosità è il canale riservato alle **ottave** → collisione semantica. |
| Durata → lunghezza del segno | Solo legato/vibrato usano `dur` | La durata è quasi illeggibile nel quadro. |
| Slide = diagonale **tra i due pitch** | Diagonale a −15° fisso | Perde l'informazione di intervallo. Idem bend. |
| Legato = curva verso la nota adiacente | `ang_next` usato solo per legato | Direzione melodica su 2 note su 12. |

### Mancante del tutto
- **Ottave → stessa tinta, luminosità diversa** (già prototipato in `zorn_grid.py:77-88`)
- **Pausa = spazio vuoto** (il vero intro di JBG ha pause; lo schema dati non le codifica)
- **Battute = separatori visivi**
- **Shuffle = pennellate alternate spesse/sottili** (il riff È shuffle)
- **Crescendo = gradiente che si intensifica**
- **Arpeggio = collana di perle**; **pull-off** distinto; **note esterne** (Bb, F);
  **accordi = fusione colori** (il powerchord A5 dovrebbe fondere A+E = vermiglio+bianco)
- **Struttura del brano → composizione della tela** (previsto nello schema dati, non usato)

## 3. MAPPING RAFFINATO v2

Principio ordinatore: **un canale musicale → un canale pittorico, senza collisioni**.
Colore = *cosa* (pitch class), posizione = *quando/quanto alto*, dimensione+materia =
*quanto forte*, forma = *come*.

| # | Parametro musicale | Parametro pittorico | Regola deterministica |
|---|---|---|---|
| 1 | **Pitch class** (A C D E G) | **Tinta** | A=vermiglio, C=raw sienna, D=nero avorio, E=bianco titanio, G=oro. Esterne: Bb=verm.+nero 40%, F=grigio. |
| 2 | **Ottava** | **Luminosità della tinta** | `L = base + 0.12·(ottava − 4)`, max ±0.36. *Richiede fix tuning.* |
| 3 | **Tempo (beat)** | **Posizione X** | `x = margine + t·240px`. Invariato. |
| 4 | **Pitch assoluto (MIDI)** | **Posizione Y** | Acuto = **alto** (flip). Range dinamico sul riff (min−3, max+3 semitoni). |
| 5 | **Durata** | **Lunghezza del segno** | `lunghezza = durata·240px·k_tecnica` per TUTTE le tecniche → il quadro diventa "suonabile a vista". |
| 6 | **Velocity (p→ff)** | **Larghezza + impasto + opacità** (NON luminosità) | width: p=14, mp=20, mf=26, f=34, ff=42 px; thickness 0.4→1.3; opacity 0.72→0.96. Forte = materico, piano = velatura. |
| 7 | **Tecnica** | **Forma** | Come v7 con 3 correzioni: slide = diagonale dal pitch di partenza a quello reale; bend = curvatura ∝ ampiezza (½ tono=0.6 rad, tono=1.2); powerchord = **due colori fusi** (fondamentale+quinta 60/40). Aggiunte: arpeggio = catena di dab; pull-off = hammer-on specchiato; shuffle = alternanza ×1.15/×0.85 su ottavi pari/dispari. |
| 8 | **Direzione melodica** | **Angolo del segno** | `angle = clamp(atan2(Δy,Δx), ±35°)` per tecniche direzionali; staccato/tapping/armonici puntuali. |
| 9 | **Posizione nella battuta** | **Secchezza + separatori** | Downbeat → dryness=0.25 (carico); levare → 0.55 (dry-brush). Barline: velatura verticale ocra-scura (opacità 0.15). |
| 10 | **Pausa** | **Vuoto** | Nessun segno. Il silenzio è tela. |
| 11 | **Crescendo/diminuendo** | **Gradiente lungo il tratto** | Se vel(n+1) > vel(n): opacità e width crescono lungo t. |
| 12 | **Accordo** | **Sovrapposizione wet-on-wet** | Segni sovrapposti dal grave all'acuto, smear alto (0.5) sul superiore. |
| 13 | **Struttura (intro/verse/solo)** | **Zona/densità della tela** | Campo `section` nello schema dati. Predisposto. |

**Casualità ammessa (fisica della mano):** tremolio traiettoria, carico per-setola,
striature, jitter di ripetizione, ground. Tutto sotto seed → **stessa musica + stesso
seed = stesso quadro, pixel-identico**. Nessuna decisione compositiva legge l'RNG.

### Layout: lineare vs spirale vs griglia
- **Lineare (v7)**: massima leggibilità temporale; formato principale.
- **Spirale**: groove ciclici/riff ripetuti — un giro = 2 battute. Variante
  `--layout spiral` sul motore olio (pitch → raggio, tempo → angolo).
- **Griglia**: strumento di verifica del mapping ("debug view"), non output artistico.

## 4. Tre raccomandazioni prioritarie

1. **Ripristinare la verità geometrica: fix tuning + flip Y + durata→lunghezza
   universale.** Massimo guadagno di leggibilità: chi conosce il riff deve poterlo
   "canticchiare" seguendo i segni.
2. **Separare i canali: velocity → materia, ottava → luminosità.** Ogni proprietà
   visiva ha un solo significato musicale — condizione per un quadro decodificabile.
3. **Rendere i segni relazionali: angolo = direzione melodica, slide/bend
   proporzionali all'intervallo, powerchord bicolore, separatori di battuta, shuffle
   come alternanza spessa/sottile.** Il quadro deve raccontare il *fraseggio*: la
   musica sta tra le note.
