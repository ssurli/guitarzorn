# 🎨 Hybrid Workflow: Code + Stable Diffusion

## Workflow Completo

```
Guitar Riff (code) → Base Artwork → Stable Diffusion → Final Oil Painting
     ↓                    ↓                ↓                    ↓
  Ripetibile         Composizione      Image-to-Image      Effetto AI
  Controllato        Musicale          (Replicate)         Pittorico
```

---

## 🚀 Quick Start

### Step 1: Genera Base Artwork (NO post-processing)

```bash
# Genera solo la composizione base (raw, senza filtri artistici)
python zorn_riff_art_enhanced.py
# Output: johnny_b_goode_abstract_expressionist.png
```

**Importante:** Usa il file **RAW** (senza post-processing) come input per Stable Diffusion. L'AI farà il lavoro artistico.

### Step 2: Stable Diffusion su Replicate

**Modello consigliato:** `stability-ai/sdxl` o `stability-ai/stable-diffusion-img2img`

**URL:** https://replicate.com/stability-ai/sdxl

---

## 📝 Prompt Ottimali per Stable Diffusion

### Prompt Base (Consigliato)

```
oil painting on canvas, soft blended brushstrokes, impressionist style,
Zorn palette with ochre yellow, vermilion red, ivory black and titanium white,
thick impasto texture, painterly, abstract expressionist, materic surface,
natural lighting, high quality canvas texture, artistic, no sharp edges,
dreamlike quality, professional art
```

### Parametri Replicate

```json
{
  "prompt": "[prompt sopra]",
  "image": "[upload johnny_b_goode_abstract_expressionist.png]",
  "strength": 0.65,
  "guidance_scale": 7.5,
  "num_inference_steps": 50,
  "negative_prompt": "digital art, vector, sharp edges, geometric, photograph, 3d render, cartoon, anime"
}
```

### Varianti Prompt

**Per effetto più pittorico:**
```
thick oil paint on linen canvas, alla prima technique, Zorn limited palette,
visible brush marks, impasto texture, impressionist masterpiece, museum quality,
warm ochre tones with vermilion accents, chiaroscuro lighting, painterly abstraction
```

**Per effetto più morbido (come ChatGPT):**
```
soft dreamlike oil painting, blended brushstrokes fading into background,
muted Zorn palette, subtle color transitions, atmospheric, ethereal quality,
delicate impasto, impressionist mood, warm ambient light, artistic blur
```

**Per effetto più materico:**
```
heavy impasto oil painting, thick paint application, palette knife technique,
textured canvas, Zorn limited palette, expressive brushwork, tactile surface,
three-dimensional paint texture, bold color blocking, abstract expressionist
```

---

## 🔧 Strength Parameter Guide

Il parametro `strength` controlla quanto l'AI modifica l'immagine:

| Strength | Effetto | Quando usare |
|----------|---------|--------------|
| **0.4-0.5** | Leggero | Mantiene composizione esatta |
| **0.6-0.7** | Medio | **Consigliato** - bilancia struttura e pittoricità |
| **0.8-0.9** | Forte | Massima libertà artistica AI |

**Per questo progetto:** `strength: 0.65` è ideale.

---

## 🤖 Automatizzazione con API Replicate

### Installazione

```bash
pip install replicate
export REPLICATE_API_TOKEN="<your-token>"
```

### Script Python

Creo uno script che automatizza l'upload:

```python
# hybrid_sd_processor.py
import replicate

def apply_sd_artistic_effect(input_image_path, output_path,
                             strength=0.65, style='balanced'):
    """
    Apply Stable Diffusion artistic effect via Replicate

    Styles:
    - 'balanced': soft oil painting (recommended)
    - 'painterly': thick brushstrokes
    - 'dreamlike': soft blended (ChatGPT style)
    """

    prompts = {
        'balanced': """oil painting on canvas, soft blended brushstrokes,
                      impressionist style, Zorn palette with ochre yellow,
                      vermilion red, ivory black and titanium white,
                      thick impasto texture, painterly, abstract expressionist,
                      materic surface, natural lighting, high quality canvas texture,
                      artistic, no sharp edges, dreamlike quality, professional art""",

        'painterly': """thick oil paint on linen canvas, alla prima technique,
                       Zorn limited palette, visible brush marks, impasto texture,
                       impressionist masterpiece, museum quality, warm ochre tones
                       with vermilion accents, chiaroscuro lighting, painterly abstraction""",

        'dreamlike': """soft dreamlike oil painting, blended brushstrokes fading into background,
                       muted Zorn palette, subtle color transitions, atmospheric, ethereal quality,
                       delicate impasto, impressionist mood, warm ambient light, artistic blur"""
    }

    negative_prompt = """digital art, vector, sharp edges, geometric,
                        photograph, 3d render, cartoon, anime, modern, clean"""

    # Open input image
    with open(input_image_path, "rb") as image_file:

        # Run Stable Diffusion
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "image": image_file,
                "prompt": prompts[style],
                "negative_prompt": negative_prompt,
                "strength": strength,
                "guidance_scale": 7.5,
                "num_inference_steps": 50,
            }
        )

        # Save output
        import urllib.request
        urllib.request.urlretrieve(output[0], output_path)

    print(f"✅ Artistic effect applied: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python hybrid_sd_processor.py input.png [output.png] [style] [strength]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "sd_output.png"
    style = sys.argv[3] if len(sys.argv) > 3 else "balanced"
    strength = float(sys.argv[4]) if len(sys.argv) > 4 else 0.65

    apply_sd_artistic_effect(input_path, output_path, strength, style)
```

---

## 🎯 Complete Pipeline Script

Pipeline completa automatizzata:

```bash
#!/bin/bash
# complete_pipeline.sh

SEED=${1:-42}
STYLE=${2:-dreamlike}
STRENGTH=${3:-0.65}

echo "🎸 Generating guitar riff artwork (seed: $SEED)..."
python zorn_riff_art_enhanced.py --seed $SEED

echo "🎨 Applying Stable Diffusion effect (style: $STYLE)..."
python hybrid_sd_processor.py \
    johnny_b_goode_abstract_expressionist.png \
    final_artwork_sd.png \
    $STYLE \
    $STRENGTH

echo "✅ Complete! Output: final_artwork_sd.png"
```

**Uso:**
```bash
chmod +x complete_pipeline.sh
./complete_pipeline.sh 42 dreamlike 0.65
```

---

## 💡 Tips per Risultati Ottimali

### 1. **Input Image Quality**
- Usa output RAW (senza post-processing)
- Risoluzione: 1600x1000px è ottimale
- Non applicare blur prima di SD (lascia fare all'AI)

### 2. **Strength Sweet Spot**
- Start con `0.65`
- Se troppo modificato: abbassa a `0.55`
- Se troppo simile all'input: alza a `0.75`

### 3. **Batch Processing**
```bash
# Genera 10 variazioni
for i in {1..10}; do
    SEED=$RANDOM
    python zorn_riff_art_enhanced.py --seed $SEED --output variation_$i
    python hybrid_sd_processor.py variation_${i}_raw.png sd_variation_$i.png
done
```

### 4. **A/B Testing Prompts**
Prova 2-3 prompt diversi con stesso input per scegliere il migliore.

---

## 📊 Confronto Risultati

| Metodo | Pros | Cons | Qualità |
|--------|------|------|---------|
| **Solo Codice (dreamlike)** | Ripetibile, veloce, gratis | Texture granulare | ⭐⭐⭐ |
| **Codice + SD (balanced)** | Best of both, controllabile | API cost | ⭐⭐⭐⭐ |
| **Codice + SD (dreamlike)** | Identico a ChatGPT | API cost | ⭐⭐⭐⭐⭐ |

---

## 💰 Costi Replicate

- ~$0.005 per immagine (SDXL)
- 10 immagini = ~$0.05
- 100 immagini = ~$0.50

Molto economico per risultati professionali!

---

## 🔄 Alternative a Replicate

### Hugging Face Inference API
```python
import requests

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

with open(input_path, "rb") as f:
    data = f.read()

response = requests.post(API_URL, headers=headers, data=data)
```

### ComfyUI Locale (Gratis)
- Installa ComfyUI
- Carica workflow img2img
- Batch processing possibile

---

## 📝 Summary Workflow

```bash
# 1. Genera base (ripetibile con seed)
python zorn_riff_art_enhanced.py --seed 42

# 2. (Opzionale) Upload manuale a Replicate.com
#    oppure usa API:

# 3. API automatico
python hybrid_sd_processor.py \
    johnny_b_goode_abstract_expressionist.png \
    final_sd.png \
    dreamlike \
    0.65

# Output: final_sd.png (effetto ChatGPT-like)
```

---

**Risultato:**
- ✅ Composizione musicale ripetibile (seed-based)
- ✅ Effetto pittorico AI professionale
- ✅ Best of both worlds
- ✅ Workflow automabile

🎨🎸 **Ready to go!**
