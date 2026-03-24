# Tinder Photo Portfolio · Nanobanana 🍌

Photo portfolio page with AI enhancement via **Nanobanana** (Google Gemini 2.5 Flash Image).

## Quick start

### 1. Get a Gemini API key
Free tier available at https://aistudio.google.com/

### 2. Install dependencies
```bash
npm install
```

### 3. Add your photos
Copy your 5 photos to the `input/` folder:
```
input/input1.jpg  →  main profile photo (e.g. white shirt, phone call)
input/input2.jpg  →  social / city photo
input/input3.jpg  →  adventure photo 1 (water / snorkeling)
input/input4.jpg  →  adventure photo 2 (cave / water, side angle)
input/input5.jpg  →  beach / full body photo
```

### 4. Run the enhancer
```bash
export GEMINI_API_KEY=your_key_here
npm run enhance
```

Nanobanana processes each photo with a tailored prompt and writes the
enhanced results to `photos/photo1.jpg … photo5.jpg`.

### 5. Open the portfolio
```bash
open index.html   # macOS
xdg-open index.html  # Linux
```

## What Nanobanana does to each photo

| Slot | Scene | Enhancement |
|------|-------|-------------|
| 1 | Portrait / phone | Soft flattering light, skin tone boost |
| 2 | Social / city | Contrast & colour vibrancy |
| 3 | Adventure water 1 | Blue-green water tones, vivid |
| 4 | Adventure water 2 | Cinematic shadows, rock texture |
| 5 | Beach / full body | Turquoise sea, warm summer grade |
