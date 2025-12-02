# 🎨 Quick Start: Guitar Riff to Oil Painting

## Installazione Veloce

```bash
pip install -r requirements.txt
```

## 🚀 Uso Rapido

### Opzione 1: Pipeline Completa (Consigliata)

Genera artwork + applica effetto pittorico in un comando:

```bash
# Genera con effetto bilanciato (consigliato)
python generate_artistic_riff.py

# Output:
# - artistic_riff_raw.png (versione digitale)
# - artistic_riff_artistic.png (versione pittorica) ✨
```

### Opzione 2: Personalizza il Preset

```bash
# Effetto leggero
python generate_artistic_riff.py --preset subtle

# Effetto bilanciato (default)
python generate_artistic_riff.py --preset balanced

# Effetto forte
python generate_artistic_riff.py --preset strong

# Effetto impasto (pennellate spesse)
python generate_artistic_riff.py --preset impasto
```

### Opzione 3: Cambia Seed per Variazioni

```bash
# Seed diverso = artwork diverso (ma ripetibile)
python generate_artistic_riff.py --seed 123
python generate_artistic_riff.py --seed 456
python generate_artistic_riff.py --seed 789
```

### Opzione 4: Genera Batch di Variazioni

```bash
# Genera 10 variazioni casuali
python generate_artistic_riff.py --batch 10
```

### Opzione 5: Confronta Tutti i Preset

```bash
# Genera lo stesso riff con tutti e 4 i preset
python generate_artistic_riff.py --compare
```

## 📊 Confronto Preset

| Preset | Effetto | Usa quando... |
|--------|---------|---------------|
| **subtle** | Leggero | Vuoi mantenere dettagli nitidi |
| **balanced** | Medio | Look pittorico equilibrato (consigliato) |
| **strong** | Forte | Vuoi massimo effetto "olio su tela" |
| **impasto** | Materico | Vuoi simulare pittura molto spessa |

## 🎯 Esempi Completi

### Alta Risoluzione per Stampa

```bash
python generate_artistic_riff.py \
  --width 3000 \
  --height 2000 \
  --dpi 300 \
  --preset balanced \
  --output print_quality
```

### Formato Panoramico

```bash
python generate_artistic_riff.py \
  --width 2400 \
  --height 800 \
  --preset strong
```

### Serie Artistica (Triptych)

```bash
python generate_artistic_riff.py --seed 100 --output panel_1
python generate_artistic_riff.py --seed 200 --output panel_2
python generate_artistic_riff.py --seed 300 --output panel_3
```

## 🔧 Post-Processing Manuale

Se hai già un'immagine e vuoi solo applicare l'effetto pittorico:

```bash
python artistic_postprocessing.py input.png output.png balanced
```

## 🎨 Parametri Personalizzati Avanzati

Modifica `artistic_postprocessing.py` per controllo fine:

```python
processor = ArtisticPostProcessor()
processor.apply_full_pipeline(
    'input.png',
    'output.png',
    oil_radius=5,           # 3-7: dimensione pennellata
    canvas_strength=0.35,   # 0.1-0.5: texture tela
    brush_strength=0.45,    # 0.2-0.6: texture pennellata
    impasto_strength=0.7,   # 0.4-0.8: spessore pittura
    blur_sigma=1.3,         # 0.5-2.0: morbidezza bordi
    color_variation=0.15,   # 0.05-0.2: variazione colore
    saturation_boost=1.25   # 1.0-1.5: vivacità colori
)
```

## 📁 Output Files

```
johnny_artistic_raw.png       # Versione digitale (72KB)
johnny_artistic_artistic.png  # Versione pittorica (1.2MB) ✨
```

La versione pittorica è più grande perché contiene texture dettagliate.

## ✨ Vantaggi vs AI Generativa

| Aspetto | Questo Sistema | AI Generativa |
|---------|----------------|---------------|
| **Ripetibilità** | ✅ Identico con stesso seed | ❌ Output sempre diverso |
| **Controllo** | ✅ Ogni parametro modificabile | ❌ Black box |
| **Dipendenze** | ✅ Solo Python locale | ❌ API esterne/internet |
| **Costo** | ✅ Gratis | ❌ $$ per API |
| **Privacy** | ✅ Tutto locale | ❌ Dati su server esterni |
| **Comprensibilità** | ✅ Codice leggibile | ❌ Modello opaco |

## 🎵 Modificare il Riff Sorgente

Edita `zorn_riff_art_enhanced.py` nel metodo `parse_johnny_b_goode_riff()`:

```python
riff_notes = [
    {'note': 'A', 'fret': 5, 'string': 6, 'duration': 0.5,
     'velocity': 'mf', 'technique': 'staccato'},
    # Aggiungi le tue note qui
]
```

Tecniche disponibili:
- `staccato`, `legato`, `slide`, `bend`, `vibrato`
- `hammer_on`, `powerchord`, `tapping`, `dive`
- `harmonic_natural`, `harmonic_artificial`

## 🆘 Troubleshooting

### Errore "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Immagine troppo "digitale"
Usa preset più forte: `--preset strong` o `--preset impasto`

### Immagine troppo sfocata
Usa preset più leggero: `--preset subtle`

### Voglio più variazioni
Cambia seed: `--seed 123` o usa batch: `--batch 20`

## 📚 Documentazione Completa

- `ENHANCED_README.md`: Guida completa con dettagli
- `ALGORITMO.md`: Spiegazione algoritmo e formule
- `examples_variations.py`: 8 esempi interattivi

## 🎯 Workflow Consigliato

1. **Prima esplorazione:**
   ```bash
   python generate_artistic_riff.py --compare
   ```
   Confronta i 4 preset e scegli quello che ti piace

2. **Genera variazioni:**
   ```bash
   python generate_artistic_riff.py --batch 10 --preset balanced
   ```
   Ottieni 10 variazioni casuali

3. **Affina il preferito:**
   Trova il seed che ti piace e usalo con parametri custom

---

**Creato con ❤️ - 100% codice Python, 0% AI generativa**
