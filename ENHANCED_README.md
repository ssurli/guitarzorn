# Guitar Riff to Abstract Art - Enhanced Version

## 🎨 Overview

Sistema di traslitterazione da riff chitarristici a arte astratta espressionista, ispirato alla palette di Zorn e agli stili di Kandinsky/Pollock. **Completamente generato con codice Python ripetibile** - nessuna AI generativa necessaria.

## 🎵 Concetto

**Pentatonica = Palette Zorn**

Entrambi sono sistemi di semplificazione espressiva:
- La **scala pentatonica** riduce le 12 note a 5 note essenziali
- La **palette Zorn** riduce infiniti colori a 4 tonalità fondamentali

### Mappatura Musicale → Visiva

| Elemento Musicale | Elemento Visivo |
|-------------------|-----------------|
| Pitch (nota) | Colore (Zorn palette) |
| Durata | Lunghezza pennellata |
| Dinamica (velocity) | Spessore/intensità |
| Articolazione | Forma (curve, punti, blocchi) |
| Tecniche (slide, bend, vibrato) | Gesti pittorici specifici |
| Tempo | Posizione spaziale (X) |
| Registro (alto/basso) | Luminosità/posizione (Y) |

## 🎨 Palette Zorn

```python
Yellow Ochre:    #C4A46A  (Tonica A)
Vermilion Red:   #E34234  (Terza minore C)
Ivory Black:     #1C1C1C  (Quarta D)
Titanium White:  #F2F2F2  (Quinta E)
Ochre+Black:     Mix      (Settima minore G)
```

## ⚡ Novità Enhanced Version

### 1. Effetti Procedurali
- **Splatter/Dripping** (stile Pollock): gocce e sgocciolature generate algoritmicamente
- **Perlin Noise**: texture organiche per superfici non uniformi
- **Impasto Texture**: simulazione di pittura materica

### 2. Forme Geometriche Astratte (Kandinsky)
- Cerchi, triangoli, quadrati, archi
- Layering con trasparenze controllate
- Composizione geometrica ritmica

### 3. Pennellate Organiche
- Curve di Bézier con variazioni procedurali
- Spessore variabile e texture integrate
- Anti-aliasing e sfumature naturali

### 4. Sistema di Layering
- **Background**: forme astratte e texture di base
- **Middle**: traslitterazione del riff musicale
- **Foreground**: accenti espressivi e splatter

## 🚀 Utilizzo

### Installazione dipendenze

```bash
pip install matplotlib numpy scipy pillow
```

### Esecuzione base

```bash
python zorn_riff_art_enhanced.py
```

Questo genera: `johnny_b_goode_abstract_expressionist.png`

### Personalizzazione

```python
from zorn_riff_art_enhanced import EnhancedZornGuitarRiffArt

# Crea artwork con parametri custom
artist = EnhancedZornGuitarRiffArt(
    width=2000,      # Larghezza canvas (px)
    height=1200,     # Altezza canvas (px)
    dpi=200,         # Risoluzione
    seed=42          # Seed per ripetibilità (cambia per variazioni)
)

# Genera
artist.create_artwork('my_riff_art.png')
```

## 🎯 Tecniche Chitarristiche → Gesti Pittorici

| Tecnica | Rendering Visivo |
|---------|------------------|
| **Staccato** | Punti netti + splatter sottile |
| **Legato** | Curve morbide organiche |
| **Slide** | Pennellata diagonale + drip |
| **Bend** | Arco curvato con tensione |
| **Vibrato** | Linea oscillante con texture |
| **Hammer-on** | Punti connessi con flusso |
| **Power Chord** | Blocco rettangolare + splatter |
| **Tapping** | Cerchi concentrici (glow) |
| **Dive** | Spirale discendente |
| **Armonici naturali** | Alone etereo luminoso |
| **Armonici artificiali** | Linee radianti affilate |

## 🔧 Parametri di Controllo

### Canvas
- `width`, `height`: dimensioni output
- `dpi`: risoluzione (150-300 consigliato)
- `margin`: margini (default 80px)

### Spazialità
- `px_per_beat`: 140px = spaziatura temporale
- Asse X = timeline del riff
- Asse Y = pitch (registro)

### Ripetibilità
- `seed=42`: risultati identici
- Cambia seed → nuove variazioni casuali controllate
- Stessi parametri + stesso seed = stesso output

### Intensità Effetti

Modifica all'interno del codice:

```python
# Splatter intensity
self.draw_splatter_effect(center, color, intensity=30, num_splatters=20)

# Drip length
self.draw_drip_effect(start, color, length=50, width=2)

# Background elements
num_elements = 15  # in add_background_texture()
```

## 🎨 Esempi di Variazione

```python
# Stile minimalista (meno elementi background)
# Modifica in add_background_texture():
num_elements = 5

# Stile esplosivo (più splatter)
# Modifica in add_background_texture():
for _ in range(20):  # invece di 8
    self.draw_splatter_effect(...)

# Canvas panoramico
artist = EnhancedZornGuitarRiffArt(width=2400, height=800)

# Ultra HD
artist = EnhancedZornGuitarRiffArt(width=3840, height=2160, dpi=300)
```

## 📊 Flusso di Generazione

```
1. Parsing riff → lista eventi musicali
   ↓
2. Background layer → forme astratte + splatters
   ↓
3. Traduzione note → gesti pittorici specifici
   ↓
4. Foreground layer → accenti + drips finali
   ↓
5. Compositing → salvataggio PNG
```

## 🔬 Dettagli Tecnici

### Color Blending
Miscelazione lineare RGB (non HSL) per mantenere la palette Zorn pura:

```python
mixed = color1 * ratio + color2 * (1 - ratio)
```

### Jitter Organico
Ogni coordinata ha variazione sub-pixel (±0.5px) per rompere la precisione "plotter"

### Perlin Noise
Generato con multi-octave per texture naturali:
- 4 ottave
- Scale variabile (5-10)
- Gaussian blur per smoothing

### Splatter Algorithm
Distribuzione esponenziale delle distanze dal centro per pattern naturale di schizzi

## 🎼 Input Musicale

Il riff di esempio è l'intro di "Johnny B. Goode" (Chuck Berry):

```
Note sequence (pentatonic A minor):
A - C - D - A - C - D - E - G - A - C - D - G
```

Ogni nota include:
- `pitch`: altezza MIDI
- `duration`: lunghezza in beat
- `velocity`: dinamica (p, mp, mf, f)
- `technique`: slide, bend, vibrato, etc.

## 🆚 Confronto con Versione Originale

| Aspetto | Originale | Enhanced |
|---------|-----------|----------|
| Rendering | Vettoriale pulito | Organico/pittorico |
| Texture | Nessuna | Perlin noise, splatter |
| Background | Semplice | Forme astratte layered |
| Effetti | Base | Dripping, glow, blur |
| Stile | Tecnico | Espressionista |
| Ripetibilità | ✅ | ✅ (migliorata con seed) |

## 🎯 Utilizzo Avanzato

### Creare Serie di Variazioni

```python
for seed in range(10):
    artist = EnhancedZornGuitarRiffArt(seed=seed)
    artist.create_artwork(f'variant_{seed:02d}.png')
```

### Modificare il Riff Sorgente

Edita il metodo `parse_johnny_b_goode_riff()` con il tuo riff:

```python
riff_notes = [
    {'note': 'A', 'fret': 5, 'string': 6, 'duration': 0.5,
     'velocity': 'mf', 'technique': 'staccato'},
    # ... aggiungi le tue note
]
```

### Export Multi-Formato

```python
# Dopo create_artwork()
self.fig.savefig('output.svg', format='svg')  # Vettoriale
self.fig.savefig('output.pdf', format='pdf')  # Stampa
```

## 📐 Architettura del Codice

```
ProceduralEffects              # Generatori di texture
├── perlin_noise_2d()
├── generate_splatter_points()
├── generate_drip_path()
└── generate_impasto_texture()

EnhancedZornGuitarRiffArt     # Engine principale
├── parse_johnny_b_goode_riff()
├── Color mapping (note → Zorn palette)
├── Technique renderers:
│   ├── draw_staccato()
│   ├── draw_legato()
│   ├── draw_slide()
│   └── ... (12 tecniche)
├── Effect layers:
│   ├── add_background_texture()
│   ├── render_notes()
│   └── add_foreground_accents()
└── create_artwork()          # Pipeline completa
```

## 🎨 Filosofia del Progetto

**Constraint Liberation**: limitazioni creative come fonte di espressività

- Pentatonica → 5 note invece di 12
- Zorn → 4 colori invece di milioni
- Codice → algoritmi deterministici invece di AI blackbox

Il risultato è **ripetibile, comprensibile, e modificabile** - ogni aspetto è sotto controllo diretto.

## 🔄 Ripetibilità Garantita

Stesso input → Stesso output (con stesso seed):

```bash
python zorn_riff_art_enhanced.py  # Run 1
python zorn_riff_art_enhanced.py  # Run 2
# → file identici bit-per-bit
```

Cambia seed per esplorare lo spazio delle variazioni:

```python
EnhancedZornGuitarRiffArt(seed=123)  # Nuova variazione
EnhancedZornGuitarRiffArt(seed=456)  # Altra variazione
```

## 📝 Note di Sviluppo

### Eliminazione Dipendenza AI
- ❌ Prima: generazione image-to-image con AI
- ✅ Ora: rendering procedurale puro Python

### Vantaggi
1. **Controllo totale**: ogni parametro è modificabile
2. **Ripetibilità**: seed deterministico
3. **Performance**: no API calls, tutto locale
4. **Comprensibilità**: codice leggibile e commentato
5. **Estendibilità**: facile aggiungere nuove tecniche

## 🚀 Prossimi Sviluppi Possibili

- [ ] Import da file MIDI/MusicXML
- [ ] Animazione (video) del riff che si "dipinge"
- [ ] Interfaccia GUI per parameter tuning
- [ ] Altre palette (Rothko, Matisse, etc.)
- [ ] 3D rendering (pittura su texture)
- [ ] Real-time audio → visual synthesis

## 📄 Licenza

Progetto personale - Codice libero per uso e modifica.

---

**Creato con**: Python 3.11 + Matplotlib + NumPy + SciPy
**Ispirazione**: John Zorn, Wassily Kandinsky, Jackson Pollock, Chuck Berry
