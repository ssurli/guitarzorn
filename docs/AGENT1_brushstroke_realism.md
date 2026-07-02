# REPORT — Agente 1: Brushstroke Realism Research (guitarzorn v7 → v8)

## Stato attuale del motore (`zorn_riff_v7.py`)

La classe `OilCanvas` è un solido Hertzmann-2002: color buffer + height field, trama
tessuta procedurale (`self.weave`), striature per-setola via rumore 2D, dry-brush gate
sulla trama, pickup EMA del colore sottostante, compositing alpha-mediato in bbox,
relief lighting Blinn-Phong + AO in `render()`. I punti deboli rispetto all'olio vero:

1. **Tutto il mixing è lerp RGB lineare** (`zorn_blend`, il compositing, il pickup).
   L'olio vero mescola in modo sottrattivo: i mix RGB producono medie spente e
   grigiastre, mai le transizioni sature di pigmento reale.
2. **Il pickup è monodimensionale e mono-colore**: `under = self.color[cy, cx]`
   campiona solo il pixel centrale della traiettoria; tutte le setole trascinano lo
   *stesso* colore. Nell'olio vero ogni setola si sporca in modo indipendente →
   strie di colore contaminato ai bordi del tratto.
3. **La pennellata solo deposita, non sposta**: un pennello vero *ara* la pasta:
   la abbassa nel corpo del tratto e la accumula in creste ai bordi e a fine corsa
   (conservazione della pasta). È il singolo indizio visivo più forte dell'impasto.
4. **Rasterizzazione a pixel interi** (`np.round`): aliasing sulle diagonali, le
   striature per-setola si spezzano invece di scorrere continue.
5. **Le striature non persistono lungo il tratto**: `streak` decorrela ogni ~16 px,
   mentre le setole reali lasciano solchi continui per tutta la corsa.
6. **La trama della tela non appare nel lighting**: `weave` è usata solo come gate
   dry-brush; dove la pittura è sottile la tessitura dovrebbe emergere nel rilievo.

## Stato dell'arte consultato

- **Mixbox** (Sochorová & Jamriška, "Practical Pigment Mixing for Digital Painting",
  SIGGRAPH Asia 2021): latent space dove ogni RGB è decomposto in concentrazioni di
  4 pigmenti reali + residuo additivo; mixing = lerp delle concentrazioni, poi ritorno
  a RGB via Kubelka-Munk. Licenza CC BY-NC (non riusabile liberamente), ma l'*idea* —
  mixare in spazio-concentrazione — è implementabile da zero.
- **Kubelka-Munk single-constant** (base di Mixbox, spectral.js, plugin Krita):
  `K/S = (1−R)²/(2R)`, mixing lineare dei K/S, inversione
  `R′ = 1 + (K/S) − √((K/S)² + 2·K/S)`.
- **IMPaSTo** (Baxter, Wendt & Lin, NPAR 2004): trasferimento **bidirezionale**
  pennello↔tela guidato dalla differenza di altezza, paint come fluido
  non-newtoniano approssimato, rendering KM a 8 campioni spettrali.
- **RealBrush** (Lu et al., SIGGRAPH 2013): data-driven da scansioni di tratti reali;
  i tre comportamenti chiave: *shape, smear, smudge* trattati separatamente.
- **WetBrush** (Chen, Kim et al., SIGGRAPH Asia 2015, Adobe+NVIDIA): simulazione a
  livello di setola con fluido ibrido su GPU — fuori portata in numpy, ma conferma i
  fenomeni da approssimare: spinta della pasta, mixing viscoso, output 3D con creste.

## Le 5 tecniche a maggior impatto (tutte numpy puro)

### T1 — Mixing Kubelka-Munk in spazio-concentrazione dei 4 pigmenti Zorn ★ PRIORITÀ 1

**Principio.** La palette è *chiusa* (ocra, vermilion, nero avorio, bianco titanio —
4 pigmenti veri). Non serve il problema inverso generale di Mixbox: si tiene per ogni
pixel un buffer di **concentrazioni** `C ∈ (H,W,4)` invece del solo RGB, si mescola
linearmente lì, e si converte in RGB con KM single-constant solo alla fine.

```python
# Offline: per ciascuno dei 4 pigmenti, dal suo RGB masstone R (0..1):
KS_pig = (1 - R)**2 / (2 * R + eps)          # shape (4, 3)

def km_rgb(conc):                            # conc: (...,4), somma=1
    ks = conc @ KS_pig                       # (...,3) mixing lineare dei K/S
    return 1 + ks - np.sqrt(ks*ks + 2*ks)    # riflettanza -> RGB
```

Aggiustamento pratico (Mixbox/Krita): lerp con pesi non lineari
`t' = t²/(t²+(1-t)²)` o pesare il bianco per il suo potere coprente.

**Costo.** ~60-80 righe. Runtime: +1 buffer, conversione KM O(H·W) una volta in render().

**Impatto visivo: ALTO.** È la differenza tra "digitale" e "olio": vermilion+bianco →
rosa salmone caldo, **ocra+nero → verdastro oliva (il famoso "verde Zorn"!)**,
vermilion+nero → bruno profondo. Filologicamente perfetto per la palette Zorn.

### T2 — Spinta della pasta: il pennello ara e crea creste (paint displacement)

**Principio.** Da WetBrush/IMPaSTo: un colpo di pennello su pasta fresca la *sposta*.
Approssimazione 2.5D: nel corpo del tratto l'altezza esistente viene raschiata; la
pasta rimossa viene ridistribuita ai bordi laterali del nastro e nella coda.

```python
body = wsum > 0.15                      # footprint del tratto nella bbox
plow = self.height[y0:y1, x0:x1] * body * 0.35 * pressione
self.height[y0:y1, x0:x1] -= plow
# ridistribuzione: ~70% ai bordi (dilate(body) & ~body), 30% in coda
# bonus: rilascio finale — monticello dove ts→1, scalato con (1-dryness)
```

**Costo.** ~25-35 righe. **Impatto visivo: ALTO** — le creste ai bordi dei tratti sono
*il* marcatore dell'impasto a olio (ogni Van Gogh le mostra).

### T3 — Pickup bidirezionale per-setola

**Principio.** Il reservoir `carried` da `(n,3)` diventa per-setola `(n,nS,3)`,
campionando la tela sotto *ogni* setola. Il tasso di pickup `kp` dipende dalla
bagnatura locale (T5) e dall'altezza.

**Costo.** ~20 righe di refactor. **Impatto: MEDIO-ALTO** — code dei tratti con strie
multicolori indipendenti, la firma del wet-on-wet vero.

### T4 — Splatting bilineare sub-pixel + striature persistenti

(a) Scatter bilineare sui 4 pixel vicini invece di `np.round` — niente aliasing.
(b) `streak` con correlazione quasi-intero-tratto + "solco" per-setola che incide
il height-field: `hadd += (bristle - bristle.mean()) * 0.25 * profilo(ts)`.

**Costo.** ~20 righe. **Impatto: MEDIO** ma economicissimo — rigatura parallela
continua tipica della setola dura.

### T5 — Wet map + drying; trama della tela nel rilievo dove la pittura è sottile

(a) Buffer `self.wet (H,W)`: ogni stroke deposita bagnatura ∝ `thickness·(1-dryness)`,
decadimento nel tempo; `smear`, `kp`, aratura scalano con `wet` locale.
(b) In `render()`, **una riga** con il miglior rapporto resa/costo dell'intero report:

```python
h = blur(self.height + self.weave * 0.15 * np.exp(-self.height / 0.35), 1.5)
```

La trama traspare nelle velature e sparisce sotto l'impasto, come su tela vera.

## Raccomandazione prioritaria

**Ordine consigliato: T1 → T2 → T5b → T4 → T3 → T5a.**

T1 (Kubelka-Munk a 4 pigmenti) è l'unica tecnica che cambia la *natura* del colore:
il progetto è nel caso ideale (palette chiusa = niente problema inverso, ~70 righe di
numpy), e la palette Zorn è storicamente *definita* dai mix sottrattivi (i verdi da
ocra+nero). T1+T2+T5b insieme: ~120 righe, zero dipendenze nuove, runtime invariato —
coprono i tre canali percettivi dell'olio: colore (sottrattivo), rilievo (creste),
supporto (tela).

**Fonti:** Mixbox <https://scrtwpns.com/mixbox/> · IMPaSTo (Baxter et al., NPAR 2004)
· WetBrush (Chen et al., SIGGRAPH Asia 2015) · RealBrush (Lu et al., SIGGRAPH 2013)
· spectral.js (MIT) · Kubelka-Munk single-constant.
