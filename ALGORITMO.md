# Algoritmo di Traslitterazione: Riff Chitarra → Arte Astratta

## 📐 Schema Concettuale

```
INPUT (Musical Domain)          →  PROCESS (Mapping)         →  OUTPUT (Visual Domain)
─────────────────────────────────────────────────────────────────────────────────────
Guitar Riff TAB                →  Parse & Normalize         →  Canvas (1600x1000px)
  ├─ Corda + Tasto             →  MIDI pitch calculation   →  Y coordinate
  ├─ Timing                    →  Cumulative time          →  X coordinate
  ├─ Durata                    →  Duration in beats        →  Stroke length
  ├─ Dinamica (velocity)       →  p/mp/mf/f mapping        →  Stroke width
  ├─ Tecnica                   →  Technique classifier     →  Rendering method
  └─ Articolazione             →  Staccato/Legato          →  Shape/curve type

Pentatonica A minore (5 note)  →  Zorn Palette (4 colori)  →  RGB values
  ├─ A (tonica)                →  Yellow Ochre             →  #C4A46A
  ├─ C (terza minore)          →  Vermilion Red            →  #E34234
  ├─ D (quarta)                →  Ivory Black              →  #1C1C1C
  ├─ E (quinta)                →  Titanium White           →  #F2F2F2
  └─ G (settima minore)        →  Ochre + Black (mix)      →  Blended RGB
```

## 🔢 Pipeline Algoritmica

### FASE 1: Input Processing

```python
def parse_johnny_b_goode_riff():
    """
    Input: Guitar TAB notation (simbolica)
    Output: Lista di eventi normalizzati
    """

    # Esempio nota:
    # {'note': 'A', 'fret': 5, 'string': 6, 'duration': 0.5,
    #  'velocity': 'mf', 'technique': 'staccato'}

    # Step 1.1: MIDI pitch calculation
    string_tuning = [40, 45, 50, 55, 59, 64]  # EADGBE in MIDI
    midi_pitch = string_tuning[string - 1] + fret

    # Step 1.2: Tempo accumulation
    cumulative_time = sum(previous_durations)

    # Step 1.3: Spatial mapping
    x_pos = margin + cumulative_time * px_per_beat
    y_pos = margin + normalize(midi_pitch, range=[40,80]) * canvas_height

    return processed_notes[]
```

**Formule chiave:**

```
MIDI_pitch = string_base_pitch + fret_number

X_coordinate = margin + (time_in_beats × pixels_per_beat)
             = 80 + (t × 140)

Y_coordinate = margin + ((pitch - min_pitch) / (max_pitch - min_pitch)) × (height - 2×margin)
             = 80 + ((p - 40) / 40) × 840

Stroke_width = velocity_map[velocity]
             = {p:2, mp:3, mf:4, f:6, ff:8}

Stroke_length = duration × pixels_per_beat × extension_factor
```

### FASE 2: Color Mapping

```python
def get_note_color(note, octave_offset=0):
    """
    Input: Nota pentatonica (A, C, D, E, G)
    Output: RGB array [0-1] dalla palette Zorn
    """

    # Step 2.1: Base color from pentatonic mapping
    note_to_color = {
        'A': ochre,      # [0.769, 0.643, 0.416]
        'C': vermilion,  # [0.890, 0.259, 0.204]
        'D': black,      # [0.110, 0.110, 0.110]
        'E': white,      # [0.949, 0.949, 0.949]
        'G': mix(ochre, black, 0.5)  # Linear blend
    }

    base_color = note_to_color[note]

    # Step 2.2: Octave adjustment (luminosity shift)
    if octave_offset > 0:  # Higher octave → lighter
        color = clip(base_color + octave_offset * 0.1, 0, 1)
    elif octave_offset < 0:  # Lower octave → darker
        color = clip(base_color + octave_offset * 0.1, 0, 1)

    return color
```

**Color blending formula (lineare RGB):**

```
mixed_color = color1 × ratio + color2 × (1 - ratio)

Esempio G (ochre + black):
G_color = ochre × 0.5 + black × 0.5
        = [0.769, 0.643, 0.416] × 0.5 + [0.110, 0.110, 0.110] × 0.5
        = [0.440, 0.377, 0.263]
```

### FASE 3: Procedural Effects Generation

```python
class ProceduralEffects:
    """Generatori di texture organiche"""

    def perlin_noise_2d(shape, scale, octaves):
        """
        Perlin-like noise per texture naturali
        Formula multi-octave:
        """
        noise = 0
        for octave in range(octaves):
            frequency = 2^octave
            amplitude = 1 / frequency

            # Generate noise layer
            layer = gaussian_filter(random_noise, sigma=scale/frequency)
            noise += layer × amplitude

        # Normalize to [0, 1]
        return (noise - min) / (max - min)


    def generate_splatter_points(center, intensity, num_points):
        """
        Pollock-style splatter distribution
        Usa distribuzione esponenziale per naturale decay
        """
        angles = uniform(0, 2π, num_points)
        distances = exponential(λ=intensity, num_points)

        for angle, distance in zip(angles, distances):
            x = center_x + distance × cos(angle)
            y = center_y + distance × sin(angle)
            size = exponential(λ=2) + 0.5

            yield (x, y, size)


    def generate_drip_path(start, length, wobble):
        """
        Dripping paint trajectory
        Gravity-driven con variazione laterale
        """
        x, y = start
        path = [(x, y)]

        for step in range(length):
            x += uniform(-wobble, wobble)  # Random walk horizontal
            y -= uniform(0.5, 2.0)         # Consistent downward

            path.append((x, y))

        return path
```

**Splatter distribution (esponenziale):**

```
P(distance) = λ × e^(-λ × distance)

Dove λ = 1/intensity controlla il decay rate
```

**Perlin noise (multi-octave):**

```
N(x,y) = Σ(i=0 to octaves) [ noise_i(x,y) × amplitude_i ]

Dove:
  frequency_i = 2^i
  amplitude_i = 1 / frequency_i
  noise_i = GaussianBlur(random_field, σ = scale/frequency_i)
```

### FASE 4: Technique-Specific Rendering

Ogni tecnica chitarristica ha un renderer dedicato:

#### 4.1 Staccato (note brevi staccate)

```python
def draw_staccato(note):
    # Main dot
    Circle(center, radius=width×1.5, color, alpha=0.9)

    # Micro-splatter (50% probability)
    if random() > 0.5:
        generate_splatter(center, intensity=10, n=5)
```

**Risultato:** Punti netti + schizzi sottili

#### 4.2 Legato (note legate fluide)

```python
def draw_legato(note1, note2):
    # Quadratic Bezier curve
    t = linspace(0, 1, segments)
    control_offset = random(-20, 20)

    # Bezier formula: B(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
    x(t) = (1-t)² × x1 + 2(1-t)t × ctrl_x + t² × x2
    y(t) = (1-t)² × y1 + 2(1-t)t × ctrl_y + t² × y2

    # Draw with texture variation
    for segment in curve:
        width_variant = width × (1 + uniform(-0.3, 0.3))
        draw_segment(segment, width=width_variant)
```

**Risultato:** Curve morbide organiche con spessore variabile

#### 4.3 Slide (scivolata tra tasti)

```python
def draw_slide(note):
    # Diagonal stroke
    draw_organic_stroke(x, y, x+60, y+30, color, width)

    # Dripping effect (60% probability)
    if random() > 0.6:
        drip_path = generate_drip(start=(x+30, y+15), length=20)
        draw_drip(drip_path, width=width×0.5)
```

**Risultato:** Pennellata diagonale + sgocciolatura

#### 4.4 Bend (piegatura corda)

```python
def draw_bend(note):
    # Sinusoidal arc (tensione della corda)
    t = linspace(0, 1, 30)
    x(t) = x_start + t × 50
    y(t) = y_start + 30 × sin(t × π)

    draw_curve(x(t), y(t), width, color)
```

**Formula bend:**

```
y(t) = y₀ + amplitude × sin(t × π)

Dove t ∈ [0, 1] e amplitude = tensione
```

#### 4.5 Vibrato (oscillazione)

```python
def draw_vibrato(note):
    # High-frequency oscillation
    t = linspace(0, length, 100)
    x(t) = x_start + t
    y(t) = y_start + amplitude × sin(frequency × t)

    # Variable width for organic feel
    for segment in curve:
        w(t) = width × (1 + 0.3 × sin(t/5))
        draw_segment(x(t), y(t), width=w(t))
```

**Formula vibrato:**

```
y(t) = y₀ + A × sin(ω × t)

Dove:
  A = 8px (ampiezza oscillazione)
  ω = 12 (frequenza angolare)
  t ∈ [0, length]
```

#### 4.6 Power Chord (accordo di potenza)

```python
def draw_powerchord(note):
    # Bold rectangular block
    FancyBboxPatch(
        (x, y-10), width=50, height=20,
        boxstyle="round,pad=2",
        facecolor=color, alpha=0.85,
        edgecolor=darken(color, 0.6), linewidth=3
    )

    # Surrounding splatter
    generate_splatter(center, intensity=15, n=8)
```

**Risultato:** Blocco rettangolare + aura di schizzi

#### 4.7 Tapping (tecnica percussiva)

```python
def draw_tapping(note):
    # Concentric circles (effetto glow)
    radii = [15, 10, 5, 2]
    alphas = [0.3, 0.5, 0.7, 0.9]

    for r, α in zip(radii, alphas):
        Circle(center, radius=r, color, alpha=α)
```

**Risultato:** Cerchi concentrici con fade-out radiale

#### 4.8 Dive (leva tremolo in picchiata)

```python
def draw_dive(note):
    # Spiral descent
    t = linspace(0, 4π, 100)
    x(t) = x_start + t × 3
    y(t) = y_start - t × 2 + 8 × sin(t)

    # Fade alpha mentre scende
    for i, segment in enumerate(path):
        α(i) = 0.8 × (1 - i/length)
        w(i) = 3 × (1 - i/length) + 1
        draw_segment(segment, width=w(i), alpha=α(i))
```

**Formula spirale:**

```
x(t) = x₀ + k₁ × t
y(t) = y₀ - k₂ × t + A × sin(t)

Dove:
  k₁ = 3 (velocità orizzontale)
  k₂ = 2 (velocità discesa)
  A = 8 (ampiezza oscillazione)
  t ∈ [0, 4π]
```

### FASE 5: Layering & Composition

```python
def create_artwork():
    """Pipeline di composizione a 3 layer"""

    # LAYER 1: Background (Kandinsky-inspired)
    add_background_texture()
        ├─ 15 forme geometriche astratte (circle, triangle, square, arc)
        ├─ 8 cluster di splatter (50 punti ciascuno)
        └─ Random positioning con palette Zorn

    # LAYER 2: Main content (riff translation)
    notes = parse_riff()
    for note in notes:
        dispatch_technique_renderer(note)
        ├─ Legge tecnica dal note data
        ├─ Chiama renderer specifico (draw_staccato, draw_legato, etc.)
        └─ Applica jitter organico (±0.5px)

    # LAYER 3: Foreground accents (Pollock-inspired)
    add_foreground_accents()
        └─ 5 drip casuali da alto verso basso

    # COMPOSITING
    savefig(facecolor=ochre, dpi=150, bbox_inches='tight')
```

### FASE 6: Jitter & Organic Variation

```python
def add_jitter(x, y, intensity=0.5):
    """
    Sub-pixel variation per rompere precisione "plotter"
    """
    x_jittered = x + uniform(-intensity, intensity)
    y_jittered = y + uniform(-intensity, intensity)

    return x_jittered, y_jittered
```

**Jitter applicato a:**
- Coordinate iniziali/finali di pennellate
- Centri di cerchi e forme
- Control points delle curve di Bézier

**Intensità:**
- Default: ±0.5px (impercettibile ma efficace)
- Per effetti più "gestual": ±2-3px

## 📊 Parametri Numerici di Riferimento

```python
# Canvas
WIDTH = 1600 px
HEIGHT = 1000 px
DPI = 150
MARGIN = 80 px

# Spacing
PX_PER_BEAT = 140 px         # Timeline horizontal spacing
PX_PER_SEMITONE = 12 px      # Pitch vertical spacing

# Velocity → Width mapping
VELOCITY_MAP = {
    'p':  2 px,   # Piano
    'mp': 3 px,   # Mezzo-piano
    'mf': 4 px,   # Mezzo-forte
    'f':  6 px,   # Forte
    'ff': 8 px    # Fortissimo
}

# Opacity levels
MAIN_STROKES = 0.85
ACCENTS = 0.6
BACKGROUND = 0.3-0.7 (variable)

# Effects intensity
SPLATTER_DEFAULT = {intensity: 30, num_points: 20}
DRIP_LENGTH = 50 px (average)
PERLIN_SCALE = 10 (texture frequency)
PERLIN_OCTAVES = 4 (detail layers)

# Jitter
JITTER_INTENSITY = 0.5 px (default)

# Random seed
SEED = 42 (for repeatability)
```

## 🔄 Garanzie di Ripetibilità

```python
# Tutti i generatori casuali usano seed fisso
random.seed(SEED)
np.random.seed(SEED)
rng = np.random.RandomState(SEED)

# Risultato:
# Stesso seed → stesso output (bit-per-bit identical)
# Diverso seed → variazione controllata nello spazio creativo
```

## 🎯 Complessità Computazionale

```
Input size: n = numero di note (tipicamente 10-20)

Parsing:          O(n)
Color mapping:    O(n)
Rendering:        O(n × k) dove k = complessità per tecnica
  - Staccato:     O(1)
  - Legato:       O(segments) = O(20)
  - Vibrato:      O(100)
  - Splatter:     O(num_points) = O(20-50)

Background:       O(num_elements) = O(15 + 8×50) ≈ O(400)
Foreground:       O(5 × drip_length) = O(5 × 50) = O(250)

Total: O(n × 100 + 650) ≈ O(n)

Performance: ~1-2 secondi per 1600×1000px @ 150 DPI
```

## 📐 Formule Ricapitolative

### Coordinate Transform

```
time → X:    X = margin + t × px_per_beat
pitch → Y:   Y = margin + normalize(pitch) × (height - 2×margin)
```

### Color Mixing

```
blend(c₁, c₂, α) = c₁ × α + c₂ × (1 - α)
```

### Bezier Quadratic

```
B(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂,  t ∈ [0,1]
```

### Exponential Distribution (splatter)

```
f(x; λ) = λe^(-λx),  x ≥ 0
```

### Sinusoidal Modulation (vibrato, bend)

```
y(t) = y₀ + A sin(ωt + φ)
```

### Perlin Multi-Octave

```
P(x,y) = Σᵢ₌₀ⁿ⁻¹ [Nᵢ(x,y) / 2ⁱ]
```

## 🎨 Output Characteristics

```
File format:     PNG (RGB + Alpha)
Color space:     sRGB
Bit depth:       8-bit per channel
File size:       50-150 KB (typical, depends on complexity)
Rendering time:  1-2 seconds
Repeatability:   Deterministic with fixed seed
```

---

**Nota finale:** Questo algoritmo è completamente deterministico e ripetibile. Ogni parametro può essere modificato per esplorare lo spazio creativo mantenendo il controllo totale sul processo generativo.
