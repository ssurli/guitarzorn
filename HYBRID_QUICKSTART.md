# 🚀 Hybrid Workflow - Quick Start

## 3 Modi per Usare l'Approccio Ibrido

### 🟢 Modo 1: Manuale (Più Semplice - Nessun Setup)

```bash
# 1. Genera base artwork
python zorn_riff_art_enhanced.py --seed 42

# 2. Vai su Replicate:
#    https://replicate.com/stability-ai/sdxl

# 3. Upload: johnny_b_goode_abstract_expressionist.png

# 4. Usa questo prompt:
```

**Prompt da copiare:**
```
soft dreamlike oil painting, blended brushstrokes fading into background,
muted Zorn palette with ochre yellow vermilion red ivory black titanium white,
subtle color transitions, atmospheric, ethereal quality, delicate impasto,
impressionist mood, warm ambient light, artistic blur, no sharp edges,
organic color blending, smooth texture
```

**Settings:**
- Strength: `0.65`
- Guidance Scale: `7.5`
- Steps: `50`

**Negative Prompt:**
```
digital art, vector, sharp edges, geometric, photograph, 3d render, cartoon
```

---

### 🟡 Modo 2: Script Python (Con API)

```bash
# Setup (una volta sola)
pip install replicate
export REPLICATE_API_TOKEN="your-token-here"

# Usa lo script
python generate_artistic_riff.py --seed 42  # Genera base
python hybrid_sd_processor.py \
    johnny_b_goode_abstract_expressionist.png \
    final_sd.png \
    --style dreamlike \
    --strength 0.65
```

---

### 🟢 Modo 3: Pipeline Completa (Automatica)

```bash
# Setup (una volta sola)
pip install replicate
export REPLICATE_API_TOKEN="your-token-here"

# Run tutto in un comando
./complete_pipeline.sh 42 dreamlike 0.65 my_artwork

# Output: my_artwork_sd.png
```

---

## 📊 Confronto Modi

| Modo | Setup | Costo | Velocità | Controllo |
|------|-------|-------|----------|-----------|
| **1. Manuale** | Zero | Pay-per-use | 2 min | Max |
| **2. Script** | API token | API cost | 30 sec | Alto |
| **3. Pipeline** | API token | API cost | 20 sec | Medio |

---

## 💡 Consigli

### Per risultato identico a ChatGPT:
- ✅ Usa **Modo 1** con preset "dreamlike"
- ✅ Strength: `0.65` - `0.75`
- ✅ Negative prompt importante!

### Per sperimentare:
- 🎨 Prova strength `0.5`, `0.65`, `0.8`
- 🎨 Modifica prompt (più/meno "blur", "soft", etc.)
- 🎨 Cambia seed artwork (`--seed 123`)

---

## 🎯 Risultato Atteso

**Input (code):** Forme geometriche astratte, Zorn palette
**Output (SD):** Olio su tela morbido, pennellate fuse, look AI professionale

**Identico a ChatGPT?** ✅ Sì, con `dreamlike` style!

---

## 📝 Template Prompt Personalizzati

### Più Morbido:
```
extremely soft oil painting, heavily blended, no visible brushstrokes,
atmospheric fog effect, dreamy ethereal quality, muted Zorn colors,
maximum blur, impressionist mood
```

### Più Materico:
```
thick heavy impasto oil painting, visible palette knife texture,
chunky paint application, three dimensional surface, bold Zorn palette,
expressive gestural brushwork, tactile quality
```

### Più Classico:
```
classical oil painting technique, Old Masters style, Zorn palette,
glazing layers, subtle chiaroscuro, refined brushwork, museum quality,
traditional impressionist approach
```

---

## ❓ FAQ

**Q: Devo usare il file raw o artistic?**
A: **RAW** - Senza post-processing. Lascia fare tutto all'AI.

**Q: Quanto costa?**
A: ~$0.005 per immagine su Replicate (~1 centesimo per 2 immagini)

**Q: Posso usare locale invece di API?**
A: Sì! Usa ComfyUI o Automatic1111 con workflow img2img

**Q: Il seed è ripetibile con SD?**
A: Sì se usi stessa seed anche in SD (parametro `seed`)

---

**Ready? Start con Modo 1 (manuale) per testare! 🎨**
