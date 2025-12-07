# 🎸→🎨 LIVE PERFORMANCE TO ART

## Sistema Completo di Traslitterazione Musica-Arte

Questo sistema analizza un **video di te che suoni dal vivo** e lo converte automaticamente in un'**opera d'arte astratta**, usando la palette di Zorn.

---

## 🎯 Concetto: Traslitterazione

**Traslitterazione** = Passare da un linguaggio (musica) a un altro (arte visiva) preservando l'essenza.

- ✅ **Non senti la musica?** → Puoi **vederla**
- ✅ **Ogni tecnica** → Diventa una **forma visiva**
- ✅ **Tensione armonica** → Diventa **tensione compositiva**
- ✅ **Automatico** → Dalla tua performance dal vivo

---

## 🚀 Come Funziona

### 1️⃣ INPUT: Il Tuo Video
```
1207(1).mp4  ← Tu che suoni il riff di Johnny B. Goode
```

### 2️⃣ ANALISI AUTOMATICA
Il sistema estrae:
- 🎵 **Pitch** (altezza note) → Colore
- ⏱️ **Onset** (quando iniziano) → Posizione
- 🔊 **Loudness** (intensità) → Dimensione/Spessore
- ⏳ **Duration** (durata) → Forma
- 🎸 **Tecniche** (vibrato, bend, slide...) → Morfologia
- ⚖️ **Tensione armonica** → Forma geometrica

### 3️⃣ OUTPUT: Opera d'Arte
```
1207(1)_organic_growth.png    ← Forme organiche che crescono
1207(1)_tension_field.png     ← Campo di tensioni armoniche
```

---

## 📦 Installazione

### Dipendenze Python
```bash
pip install librosa soundfile matplotlib numpy ffmpeg-python
```

### FFmpeg (per estrarre audio da video)
```bash
# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Scarica da: https://ffmpeg.org/download.html
```

---

## 🎬 Utilizzo

### Modo Più Semplice
```bash
python live_to_art.py 1207(1).mp4
```

Genera automaticamente:
- `1207(1)_organic_growth.png` (default)
- `1207(1)_notes.json` (dati estratti)

### Scegli lo Stile
```bash
# Solo Organic Growth
python live_to_art.py 1207(1).mp4 --organic

# Solo Tension Field
python live_to_art.py 1207(1).mp4 --tension

# Entrambi
python live_to_art.py 1207(1).mp4 --both
```

### Con File Audio (invece di video)
```bash
python live_to_art.py riff.wav --both
```

---

## 🎨 I Due Stili

### 🌱 ORGANIC GROWTH
**Concept**: Ogni nota è un seme che cresce organicamente

**Tecniche → Forme**:
- **Slide** → Rami con germogli
- **Staccato** → Crescita cellulare (bolle)
- **Legato** → Viticci spiralati
- **Powerchord** → Esplosione organica
- **Armonici** → Petali floreali
- **Dive** → Radici verso il basso
- **Vibrato** → Forme ondulate

**Estetica**: Naturale, botanica, intricata

---

### ⚖️ TENSION FIELD
**Concept**: Tensione armonica → Tensione visiva

**Tensione Armonica → Forma**:
- **A (tonica)** → Cerchi morbidi (consonanza)
- **E (quinta)** → Cerchi/pentagoni
- **C, D (terza, quarta)** → Quadrati
- **G (settima)** → Triangoli irregolari (dissonanza)

**Linee di Forza**:
- Note con tensione simile → Si attraggono (linee curve)
- Note con tensione opposta → Si respingono (linee spezzate)

**Estetica**: Concettuale, geometrica, dinamica

---

## 📊 Processo Tecnico

### 1. Estrazione Audio
```python
from audio_analyzer import extract_audio_from_video
audio = extract_audio_from_video("1207(1).mp4")
```

### 2. Analisi Musicale
```python
from audio_analyzer import AudioAnalyzer

analyzer = AudioAnalyzer(audio)
notes = analyzer.extract_notes()          # Pitch, onset, duration
notes = analyzer.detect_techniques(notes)  # Vibrato, bend, slide...
notes = analyzer.calculate_harmonic_tension(notes)
```

### 3. Generazione Visiva
```python
from live_to_art import OrganicGrowthArtLive

artist = OrganicGrowthArtLive(notes)
artist.create_artwork("output.png")
```

---

## 🎵 Tecniche Rilevate Automaticamente

Il sistema cerca di rilevare:

✅ **Vibrato**: Oscillazione del pitch (tremolo)
✅ **Bend**: Pitch che sale rapidamente
✅ **Slide**: Pitch che cambia gradualmente
✅ **Staccato**: Nota molto breve (< 0.15s)
✅ **Legato**: Nota lunga e fluida (> 0.4s)

⚠️ **Limiti**:
- Tecniche complesse (tapping, sweep picking) sono difficili da rilevare automaticamente
- Usa "regular" come fallback

---

## 📁 File Generati

Dopo l'esecuzione avrai:

```
1207(1)_organic_growth.png    ← Opera d'arte (Organic Growth)
1207(1)_tension_field.png     ← Opera d'arte (Tension Field)
1207(1)_notes.json            ← Dati estratti (per analisi)
temp_extracted_audio.wav      ← Audio estratto (puoi eliminarlo)
```

### Esempio `notes.json`:
```json
[
  {
    "note": "A",
    "pitch": 57,
    "start_time": 0.12,
    "duration": 0.45,
    "velocity": "mf",
    "technique": "staccato",
    "tension": 0.0
  },
  ...
]
```

---

## 🔧 Personalizzazione

### Cambia Palette Colori
Modifica `colors` in `approach_4_organic_growth.py` o `approach_5_tension_field.py`:

```python
self.colors = {
    'ochre': np.array([196, 164, 106]) / 255.0,
    'vermilion': np.array([227, 66, 52]) / 255.0,
    'black': np.array([28, 28, 28]) / 255.0,
    'white': np.array([242, 242, 242]) / 255.0
}
```

### Cambia Tonalità di Riferimento
```python
notes = analyzer.calculate_harmonic_tension(notes, key='E')  # E minor invece di A
```

### Modifica Dimensioni Canvas
```python
self.width = 2400   # Più largo
self.height = 1600  # Più alto
```

---

## 🎯 Esempi di Utilizzo

### Riff Rock
```bash
python live_to_art.py johnny_b_goode.mp4 --organic
# → Forme energiche, crescita esplosiva
```

### Ballad
```bash
python live_to_art.py slow_blues.mp4 --tension
# → Forme morbide, tensione bassa
```

### Assolo Complesso
```bash
python live_to_art.py solo.mp4 --both
# → Confronta i due stili
```

---

## 🐛 Troubleshooting

### Errore: "No module named 'librosa'"
```bash
pip install librosa soundfile
```

### Errore: "ffmpeg not found"
```bash
# Installa ffmpeg (vedi sezione Installazione)
# Oppure usa direttamente un file audio .wav
python live_to_art.py audio.wav
```

### Troppe poche note rilevate
- Il segnale potrebbe essere troppo debole
- Prova ad aumentare il volume del video
- O abbassa la soglia di rilevamento in `audio_analyzer.py`:
  ```python
  onset_frames = librosa.onset.onset_detect(
      ...,
      threshold=0.5  # Riduci da default
  )
  ```

### Note sbagliate
- Il pitch detection non è perfetto, specialmente con:
  - Distorsione pesante
  - Note molto veloci
  - Registrazioni con rumore di fondo

---

## 💡 Idee Future

- [ ] **Animazione**: Renderizzare il riff come video animato
- [ ] **3D**: Estendere a sculture 3D printabili
- [ ] **Interattivo**: Webapp per sperimentare live
- [ ] **Machine Learning**: Migliore rilevamento tecniche
- [ ] **Multi-traccia**: Analizzare più strumenti insieme

---

## 🎨 La Magia della Traslitterazione

Questo sistema non è solo una "visualizzazione" della musica.
È una **traduzione** in un altro linguaggio artistico.

Come tradurre una poesia da una lingua all'altra:
- Non puoi tradurre parola per parola
- Devi catturare l'**essenza**, il **ritmo**, le **emozioni**

Così questa traslitterazione cattura:
- L'**energia** (velocity → dimensione)
- Il **movimento** (tecniche → morfologia)
- La **tensione** (armonia → geometria)
- Il **flusso** (durata → crescita)

🎵 **La musica diventa tangibile, visibile, "leggibile"** 🎨

---

## 📞 Supporto

Per domande o problemi, consulta:
- `APPROCCI_ALTERNATIVI.md` - Dettagli su tutti gli approcci visivi
- `audio_analyzer.py` - Codice sorgente dell'analisi audio
- `approach_4_organic_growth.py` - Codice Organic Growth
- `approach_5_tension_field.py` - Codice Tension Field

---

**Buona traslitterazione!** 🎸→🎨
