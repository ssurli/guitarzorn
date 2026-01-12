# Pipeline Ibrida Zorn - Guida Rapida

## 🎯 Obiettivo

Implementare la strategia "musica decide cosa, materia decide come male viene":

1. **Renderer musicale** → genera la forma semantica pura
2. **Effetti materiali** → aggiungono resistenza fisica del medium
3. **Output finale** → sintesi Juritzsiana di intenzionalità e materia

---

## 📦 Installazione

```bash
# Installa le dipendenze
pip install -r requirements.txt
```

---

## 🚀 Uso Base

### Generare artwork con effetti materiali

```bash
python demo_hybrid_pipeline.py
```

Questo comando genera 3 file in `output/`:
- `johnny_clean.png` — Versione pulita (spartito visivo)
- `johnny_material.png` — Con effetti materiali
- `johnny_comparison.png` — Confronto side-by-side

---

## 🎨 Preset Disponibili

### Subtle (effetti leggeri)
```bash
python demo_hybrid_pipeline.py subtle
```
- Texture tela discreta
- Minima irregolarità
- Per look più "grafico"

### Balanced (default, consigliato)
```bash
python demo_hybrid_pipeline.py balanced
```
- Equilibrio tra pulizia e matericità
- Texture visibile ma non invasiva
- **Raccomandato per la maggior parte dei casi**

### Heavy (degradazione pesante)
```bash
python demo_hybrid_pipeline.py heavy
```
- Texture molto evidente
- Massima irregolarità
- Per look "pittura antica" o "affresco"

---

## 🔧 Uso Avanzato

### Applicare effetti a immagine esistente

```python
from material_effects import MaterialEffects

effects = MaterialEffects(seed=42)
effects.apply_full_material_pipeline(
    "input.png",
    "output_material.png",
    canvas_texture=0.20,      # 0.0-0.5
    paint_irregularity=0.40,  # 0.0-0.8
    brush_drag=0.30,          # 0.0-0.6
    edge_roughness=0.35,      # 0.0-0.8
    color_bleeding=0.15       # 0.0-0.4
)
```

### Applicare singoli effetti

```python
from PIL import Image
from material_effects import MaterialEffects

effects = MaterialEffects(seed=42)
image = Image.open("input.png")

# Solo texture tela
image = effects.apply_canvas_texture(image, intensity=0.2)
image.save("canvas_only.png", dpi=(150, 150))

# Solo brush drag
image = effects.apply_brush_drag(image, direction='horizontal', strength=0.3)
image.save("drag_only.png", dpi=(150, 150))
```

---

## 📊 Parametri degli Effetti

| Parametro | Range | Descrizione |
|-----------|-------|-------------|
| `canvas_texture` | 0.0-0.5 | Texture della tela (Perlin noise + anisotropia) |
| `paint_irregularity` | 0.0-0.8 | Densità pigmento non uniforme |
| `brush_drag` | 0.0-0.6 | Segni direzionali della pennellata |
| `edge_roughness` | 0.0-0.8 | Bordi organici (vs sharp) |
| `color_bleeding` | 0.0-0.4 | Mixing tra colori adiacenti |

### Suggerimenti di tuning

**Per look più "digitale":**
- Abbassa tutti i parametri
- `canvas_texture=0.05, paint_irregularity=0.15`

**Per look "dipinto a mano":**
- Alza canvas_texture e edge_roughness
- `canvas_texture=0.25, edge_roughness=0.45`

**Per look "affresco antico":**
- Alza paint_irregularity e color_bleeding
- `paint_irregularity=0.6, color_bleeding=0.25`

---

## 🎸 Integrare nel Renderer Principale

Per usare il jitter anisotropico direttamente nel renderer:

```python
from material_effects import apply_anisotropic_jitter

# Nel metodo draw_slide() o simili
x, y = note['x_pos'], note['y_pos']
direction = (40, 20)  # direzione dello stroke

x_jittered, y_jittered = apply_anisotropic_jitter(
    x, y,
    direction,
    canvas_roughness=1.0,
    hand_tremor=0.5
)

# Usa x_jittered, y_jittered invece di x, y
```

---

## 📁 Struttura File

```
guitarzorn/
├── zorn_riff_art (1).py           # Renderer musicale originale
├── material_effects.py            # Modulo effetti materiali
├── demo_hybrid_pipeline.py        # Pipeline completa automatizzata
├── requirements.txt               # Dipendenze Python
├── ANALISI_SUGGERIMENTI_CHATGPT.md # Analisi tecnica dettagliata
└── README_HYBRID_PIPELINE.md      # Questa guida
```

---

## 🔬 Come Funzionano gli Effetti

### Canvas Texture
Genera rumore Perlin multi-ottava con anisotropia direzionale (simula trama ordito/trama della tela).

### Paint Irregularity
Mappa di densità a bassa frequenza che modula localmente l'intensità dei colori (simula pigmento più o meno concentrato).

### Brush Drag
Gaussian blur direzionale che crea "code" nella direzione della pennellata.

### Edge Roughness
Blur leggero + rumore ai bordi per eliminare la perfezione dei vector graphics.

### Color Bleeding
Blur selettivo che permette ai colori adiacenti di mescolarsi leggermente (come pittura bagnata).

---

## 🆚 Confronto: Procedurale vs Stable Diffusion

| Aspetto | Procedurale | SD img2img |
|---------|-------------|------------|
| **Velocità** | ~2 secondi | ~30 secondi |
| **GPU** | Non richiesta | Necessaria (4GB+ VRAM) |
| **Riproducibilità** | 100% | ~95% |
| **Preserva colori Zorn** | Perfetto | Problematico |
| **Controllo parametri** | Totale | Limitato |
| **Setup** | `pip install` | Model download + CUDA |

**Raccomandazione:** inizia con procedurale. Sperimenta SD solo se hai GPU e vuoi "sorprese creative".

---

## 🎯 Quick Start (1 minuto)

```bash
# 1. Installa dipendenze
pip install numpy matplotlib pillow scipy

# 2. Genera artwork con effetti
python demo_hybrid_pipeline.py balanced

# 3. Guarda i risultati
open output/johnny_comparison.png  # macOS
xdg-open output/johnny_comparison.png  # Linux
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'scipy'"
```bash
pip install scipy
```

### "FileNotFoundError: 'zorn_riff_art (1).py'"
Verifica che il file del renderer originale sia nella stessa directory.

### Gli effetti sono troppo forti/deboli
Modifica i preset in `demo_hybrid_pipeline.py` (linee 35-59) o passa parametri custom a `apply_full_material_pipeline()`.

---

## 📚 Approfondimenti

Per l'analisi tecnica completa dei suggerimenti ChatGPT e dei principi implementativi, vedi:
- `ANALISI_SUGGERIMENTI_CHATGPT.md`

Per il codice sorgente commentato degli effetti:
- `material_effects.py`

---

## 🎨 Filosofia

> "Musica decide cosa. Materia decide come male viene."

Questa pipeline rispetta la separazione tra:
- **Intenzionalità semantica** (renderer musicale)
- **Resistenza del medium** (effetti materiali)

Il risultato finale è la **negoziazione** tra forma ideale e imperfezione materiale — esattamente ciò che cercava Boris Juritz.

---

*Creato: 2026-01-12*
*Per domande tecniche, vedi il codice sorgente con commenti estesi*
