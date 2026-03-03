"""
Guitarzorn v3 – Bristle Brush Physics (Processing → Python)
============================================================
Traduzione in Python del sistema di pennellate di Javier García Carpio
(vimeo.com/82104781, CC BY-SA) integrato con il riff Guitarzorn/Zorn.

Algoritmo chiave:
  Bristle  – catena IK di N segmenti: ogni nodo segue il predecessore
             con distanza fissa (atan2-based chain following).
  Brush    – N bristle disposte perpendicolarmente alla direzione di
             movimento, calcolata dallo smoothing su 4 posizioni recenti.
  Trace    – traiettoria con rumore angolare, decadimento alpha,
             mixing "pittura umida" con colore della tela sottostante.

Differenze rispetto all'originale Processing:
  - Nessuna immagine sorgente: i colori vengono dalla palette Zorn
    in base alla nota del riff (pentatonica min. La).
  - Le tracce sono posizionate e orientate in base alla tecnica
    chitarristica (slide, bend, vibrato, ecc.).
  - Backend: PIL/Pillow + numpy (alpha compositing per overlay).
"""

import math
import random
from typing import Dict, List, Tuple, Optional

import numpy as np
from PIL import Image, ImageDraw

# ─── Palette Zorn (4 colori) ──────────────────────────────────────────────────
ZORN = {
    'ochre':     (196, 164, 106),
    'vermilion': (227,  66,  52),
    'black':     ( 28,  28,  28),
    'white':     (242, 242, 242),
}
# Mapping pentatonica minore La → colori Zorn
_NOTE_COL = {'A': 'ochre', 'C': 'vermilion', 'D': 'black', 'E': 'white', 'G': None}


def zorn_blend(c1: Tuple, c2: Tuple, t: float) -> Tuple[int, int, int]:
    """Mix lineare tra due colori Zorn."""
    return tuple(max(0, min(255, int(c1[i] * (1 - t) + c2[i] * t))) for i in range(3))


def get_note_color(note: str, midi: int) -> Tuple[int, int, int]:
    """
    Colore Zorn della nota + correzione per ottava:
      registro grave → blend con ivory black (≤20%)
      registro acuto → blend con titanium white (≤25%)
    """
    base = zorn_blend(ZORN['ochre'], ZORN['black'], 0.5) if note == 'G' \
        else ZORN[_NOTE_COL.get(note, 'ochre')]
    b = (midi - 40) / (80 - 40)   # [0..1]
    if b > 0.5:
        return zorn_blend(base, ZORN['white'],  (b - 0.5) * 0.5)
    else:
        return zorn_blend(base, ZORN['black'],  (0.5 - b) * 0.4)


def _smooth_noise(x: float) -> float:
    """Pseudo-random smooth value in [0, 1] con coerenza temporale."""
    return (math.sin(x * 127.1 + math.cos(x * 0.37) * 311.7) + 1.0) / 2.0


# ─── Bristle ──────────────────────────────────────────────────────────────────
class Bristle:
    """
    Catena IK di N segmenti.
    update(new_pos): il nodo 0 va in new_pos, ogni nodo i segue il
    predecessore (i-1) mantenendo distanza fissa lengths[i] via atan2.
    Traduzione diretta di Bristle.pde di Javier García Carpio.
    """

    def __init__(self, n_parts: int,
                 init_len: float, delta_len: float,
                 init_thick: float, delta_thick: float):
        n = max(2, n_parts + 1)
        self.n = n
        self.pos: List[np.ndarray] = [np.zeros(2) for _ in range(n)]
        self.lengths     = [max(1.0, init_len   - i * delta_len)   for i in range(n)]
        self.thicknesses = [max(0.1, init_thick - i * delta_thick) for i in range(n)]

    def init(self, pos: np.ndarray):
        for i in range(self.n):
            self.pos[i] = pos.copy()

    def update(self, new_pos: np.ndarray):
        self.pos[0] = new_pos.copy()
        for i in range(1, self.n):
            ang = math.atan2(self.pos[i - 1][1] - self.pos[i][1],
                             self.pos[i - 1][0] - self.pos[i][0])
            L = self.lengths[i]
            self.pos[i] = np.array([
                self.pos[i - 1][0] - L * math.cos(ang),
                self.pos[i - 1][1] - L * math.sin(ang),
            ])

    def segments(self) -> List[Tuple[np.ndarray, np.ndarray, float]]:
        return [(self.pos[i - 1].copy(), self.pos[i].copy(), self.thicknesses[i])
                for i in range(1, self.n)]


# ─── Brush ────────────────────────────────────────────────────────────────────
class Brush:
    """
    Pennello: N bristle disposte perpendicolarmente alla direzione di
    movimento. La direzione è la media smoothed delle ultime N_AVG posizioni.
    Il rumore orizzontale (Perlin-style) muove i crini lateralmente.
    Traduzione di Brush.pde di Javier García Carpio.
    """
    N_AVG        = 4
    VERT_NOISE   = 8.0
    HORIZ_NOISE  = 4.0
    NOISE_SPEED  = 0.04

    def __init__(self, init_pos: np.ndarray, size: float,
                 n_bristles: int, bristle_len: float, bristle_thick: float):
        self.pos      = init_pos.copy()
        self.dir      = 0.0
        self.n        = n_bristles
        self.history: List[np.ndarray] = []
        self.avg_pos  = init_pos.copy()
        self.seed     = random.uniform(0, 1000)
        self.counter  = 0
        self._hn      = min(0.3 * size, self.HORIZ_NOISE)

        n_parts  = max(3, round(math.sqrt(2 * bristle_len)))
        delta_t  = bristle_thick / n_parts

        self.bristles: List[Bristle]   = []
        self.b_offsets: List[np.ndarray] = []
        self.b_pos: List[np.ndarray]   = []

        for _ in range(n_bristles):
            self.bristles.append(
                Bristle(n_parts, float(n_parts), 1.0, bristle_thick, delta_t))
            self.b_offsets.append(np.array([
                size * (random.random() - 0.5),
                self.VERT_NOISE * (random.random() - 0.5),
            ]))
            self.b_pos.append(np.zeros(2))

        self._update_bpos()

    def _update_bpos(self):
        ca, sa = math.cos(self.dir), math.sin(self.dir)
        for b in range(self.n):
            nx = (self.b_offsets[b][0]
                  + self._hn * (_smooth_noise(
                      self.seed + self.NOISE_SPEED * self.counter + b * 0.1) - 0.5))
            ny = self.b_offsets[b][1]
            self.b_pos[b] = np.array([
                self.pos[0] + nx * ca - ny * sa,
                self.pos[1] + nx * sa + ny * ca,
            ])

    def update(self, new_pos: np.ndarray):
        if not np.array_equal(new_pos, self.pos):
            self.history.append(new_pos.copy())
            if len(self.history) > self.N_AVG:
                self.history.pop(0)
            new_avg = np.mean(self.history, axis=0)
            self.dir = (math.atan2(new_avg[1] - self.avg_pos[1],
                                   new_avg[0] - self.avg_pos[0])
                        + math.pi / 2)
            self.pos     = new_pos.copy()
            self.avg_pos = new_avg.copy()
            self._update_bpos()
            if len(self.history) < self.N_AVG:
                for b in range(self.n):
                    self.bristles[b].init(self.b_pos[b])
            else:
                for b in range(self.n):
                    self.bristles[b].update(self.b_pos[b])
        self.counter += 1

    def reset(self, init_pos: np.ndarray):
        self.pos = init_pos.copy()
        self.dir = 0.0
        self.history.clear()
        self.avg_pos = init_pos.copy()
        self.counter = 0
        self._update_bpos()

    def is_ready(self) -> bool:
        return len(self.history) >= self.N_AVG

    def paint_step(self, draw: 'ImageDraw.ImageDraw',
                   colors: List[Tuple[int, int, int]], alpha: int):
        if not self.is_ready() or alpha <= 0:
            return
        for b, bristle in enumerate(self.bristles):
            fill = colors[b] + (alpha,)
            for p1, p2, thick in bristle.segments():
                draw.line(
                    [(float(p1[0]), float(p1[1])),
                     (float(p2[0]), float(p2[1]))],
                    fill=fill,
                    width=max(1, int(thick)),
                )


# ─── Trace ────────────────────────────────────────────────────────────────────
class Trace:
    """
    Singola pennellata: traiettoria con rumore angolare, decadimento alpha,
    mixing umido del colore con la tela sottostante.
    Adattato da Trace.pde di Javier García Carpio (no source image: i colori
    vengono dalla palette Zorn via nota del riff).
    """
    SPEED      = 2.0      # pixel per step
    NOISE_F    = 0.007    # frequenza del rumore angolare
    NOISE_AMP  = 0.55     # ampiezza angolare [rad] (Processing usa 2π*(n-0.5) ≈ 0.6π max)
    MIX_START  = 5        # step da cui inizia il mixing con la tela
    MIX_STR    = 0.015    # forza del mixing ("pittura umida")
    BRIGHT_CH  = 12       # variazione di luminosità tra i crini [0..255]
    MIN_ALPHA  = 20       # alpha minimo per disegnare

    _VEL_ALPHA = {'p': 128, 'mp': 170, 'mf': 200, 'f': 228, 'ff': 255}

    def __init__(self, brush: Brush, n_steps: int,
                 init_pos: np.ndarray,
                 note_color: Tuple[int, int, int],
                 velocity: str,
                 preferred_ang: Optional[float] = None):
        self.brush      = brush
        self.n_steps    = max(1, n_steps)
        self.note_color = note_color
        self.colors: Optional[List[List[Tuple[int, int, int]]]] = None

        # ── Traiettoria con rumore angolare (Processing: noise-based walk) ──
        seed    = random.uniform(0, 1000)
        ang     = preferred_ang if preferred_ang is not None \
            else random.uniform(0, 2 * math.pi)
        pos     = init_pos.copy()
        self.positions = [pos.copy()]
        for s in range(1, self.n_steps):
            drift = self.NOISE_AMP * math.pi * (_smooth_noise(seed + self.NOISE_F * s) - 0.5)
            ang_s = ang + drift
            pos   = pos + np.array([self.SPEED * math.cos(ang_s),
                                    self.SPEED * math.sin(ang_s)])
            self.positions.append(pos.copy())

        # ── Alpha decay (Processing: alphaDecrement = min(alpha/nSteps, 25)) ──
        a0    = self._VEL_ALPHA.get(velocity, 200)
        a_dec = min(a0 / self.n_steps, 25.0)
        self.alphas: List[int] = []
        a = float(a0)
        for _ in range(self.n_steps):
            self.alphas.append(int(max(0, a)))
            a = max(0.0, a - a_dec)

    def calculate_colors(self, canvas_arr: np.ndarray):
        """
        Inizializza i colori di ogni bristle per ogni step.
        Step 0..MIX_START: colore nota + variazione di luminosità per bristle.
        Step MIX_START+: mixing progressivo col colore della tela sottostante
        ("pittura umida": il pennello raccoglie il pigmento già depositato).
        """
        n  = self.brush.n
        r0, g0, b0 = self.note_color
        ch = self.BRIGHT_CH

        # Colori iniziali: variazione di luminosità per ogni crine
        step0 = []
        for _ in range(n):
            dv = ch * (random.random() - 0.5)
            step0.append((max(0, min(255, int(r0 + dv))),
                          max(0, min(255, int(g0 + dv))),
                          max(0, min(255, int(b0 + dv)))))

        colors: List[List[Tuple]] = []
        mix_start = min(self.MIX_START, self.n_steps)
        for _ in range(mix_start):
            colors.append(list(step0))

        # Running averages per bristle per il mixing
        rp = [float(c[0]) for c in step0]
        gp = [float(c[1]) for c in step0]
        bp = [float(c[2]) for c in step0]
        H, W = canvas_arr.shape[:2]
        ms   = self.MIX_STR

        for s in range(mix_start, self.n_steps):
            px = int(self.positions[s][0])
            py = int(self.positions[s][1])
            step_cols = []
            for b in range(n):
                if 0 <= py < H and 0 <= px < W:
                    cp = canvas_arr[py, px]   # shape (4,) RGBA
                    rp[b] = (rp[b] + ms * float(cp[0])) / (1 + ms)
                    gp[b] = (gp[b] + ms * float(cp[1])) / (1 + ms)
                    bp[b] = (bp[b] + ms * float(cp[2])) / (1 + ms)
                step_cols.append((int(rp[b]), int(gp[b]), int(bp[b])))
            colors.append(step_cols)

        self.colors = colors

    def paint(self, canvas: Image.Image, canvas_arr: np.ndarray):
        """
        Dipinge la pennellata sulla tela con alpha compositing (overlay).
        Aggiorna canvas e canvas_arr in place.
        """
        overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)

        self.brush.reset(self.positions[0])
        for s in range(self.n_steps):
            self.brush.update(self.positions[s])
            if (self.colors and s < len(self.colors)
                    and self.alphas[s] >= self.MIN_ALPHA):
                self.brush.paint_step(draw, self.colors[s], self.alphas[s])

        # Composita overlay sulla tela
        result = Image.alpha_composite(canvas.convert('RGBA'), overlay)
        canvas.paste(result.convert(canvas.mode))
        canvas_arr[:] = np.array(canvas)
        self.brush.reset(self.positions[0])


# ─── Orchestratore principale ─────────────────────────────────────────────────
class ZornRiffBristlePainting:
    """
    Pipeline completa: riff chitarra → tela pittorica con sistema bristle
    fisicamente simulato e palette Zorn 4 colori.

    Ogni nota del riff genera una o più Trace il cui orientamento e numero
    dipende dalla tecnica chitarristica (slide, bend, vibrato, ecc.).
    """

    def __init__(self, width: int = 1600, height: int = 1000, seed: int = 42):
        self.W, self.H = width, height
        random.seed(seed)
        np.random.seed(seed)

        # Tela iniziale: fondo ocra completamente opaco
        bg = ZORN['ochre'] + (255,)
        self.canvas = Image.new('RGBA', (width, height), bg)
        self.arr    = np.array(self.canvas)   # (H, W, 4) RGBA

        self.px_per_beat = 140
        self.margin      = 80

    # ── coordinate ────────────────────────────────────────────────────────
    def _tx(self, t: float) -> float:
        return self.margin + t * self.px_per_beat

    def _ty(self, midi: int) -> float:
        n = (midi - 40) / (80 - 40)
        return self.margin + n * (self.H - 2 * self.margin)

    # ── costruzione brush ─────────────────────────────────────────────────
    def _make_brush(self, pos: np.ndarray, size: float) -> Brush:
        n_bristles    = int(size * random.uniform(1.6, 1.9))
        bristle_len   = min(2.0 * size, 12.0)
        bristle_thick = min(0.8 * size, 5.0)
        return Brush(pos, size, n_bristles, bristle_len, bristle_thick)

    @staticmethod
    def _vel_to_size(velocity: str) -> float:
        return {'p': 4.0, 'mp': 7.0, 'mf': 12.0, 'f': 18.0, 'ff': 24.0}.get(velocity, 12.0)

    # ── paint singola traccia ─────────────────────────────────────────────
    def _paint_trace(self, pos: np.ndarray, size: float, n_steps: int,
                     color: Tuple, velocity: str,
                     ang: Optional[float] = None,
                     alpha_scale: float = 1.0):
        brush = self._make_brush(pos, size)
        trace = Trace(brush, n_steps, pos, color, velocity, preferred_ang=ang)
        if alpha_scale != 1.0:
            trace.alphas = [int(a * alpha_scale) for a in trace.alphas]
        trace.calculate_colors(self.arr)
        trace.paint(self.canvas, self.arr)

    # ── imprimitura ───────────────────────────────────────────────────────
    def _ground_layer(self):
        """
        Preparazione della tela: pennellate orizzontali grandi di varianti
        tonali dell'ochre (pura, +bianco, +nero) che simulano il ground
        pittorico. Pennelli grandi, alpha bassa, direzione quasi orizzontale.
        """
        configs = [
            # (color_variant_t_to_white, color_variant_t_to_black, size_range, alpha_scale)
            (0.08, 0.00, (18, 40), 0.40),   # ochre chiara
            (0.00, 0.12, (14, 30), 0.32),   # ochre scura
            (0.04, 0.04, (10, 22), 0.25),   # ochre media
        ]
        for t_w, t_b, (sz_lo, sz_hi), a_scale in configs:
            for _ in range(7):
                x    = random.uniform(-80, self.W + 80)
                y    = random.uniform(-80, self.H + 80)
                ang  = random.gauss(0, 0.12)    # quasi orizzontale
                size = random.uniform(sz_lo, sz_hi)
                length = random.uniform(160, 520)
                n_steps = max(10, int(length / Trace.SPEED))

                base = ZORN['ochre']
                if t_w > 0:
                    col = zorn_blend(base, ZORN['white'], t_w)
                elif t_b > 0:
                    col = zorn_blend(base, ZORN['black'], t_b)
                else:
                    col = base

                self._paint_trace(np.array([x, y]), size, n_steps,
                                  col, 'p', ang=ang, alpha_scale=a_scale)

    # ── mapping tecnica → tracce ──────────────────────────────────────────
    def _technique_traces(self, note: Dict, notes: List[Dict], idx: int
                          ) -> List[Tuple[int, Optional[float], float, float]]:
        """
        Ritorna lista di (n_steps, angle, size_mult, alpha_scale)
        per ogni pennellata da disegnare per questa nota.
        """
        tech     = note['technique']
        dur      = note['duration']
        base_sz  = self._vel_to_size(note['velocity'])
        dur_st   = max(8, int((2.3 * base_sz / Trace.SPEED) * dur))

        # Angolo verso la nota successiva (usato da legato)
        nxt = notes[idx + 1] if idx + 1 < len(notes) else None
        if nxt:
            ang_next = math.atan2(nxt['y_pos'] - note['y_pos'],
                                  nxt['x_pos'] - note['x_pos'])
        else:
            ang_next = 0.0

        if tech == 'staccato':
            # Due colpi brevi, random
            return [(12, None, 1.0, 1.0), (10, None, 0.7, 0.75)]

        elif tech == 'legato':
            # Un'unica pennellata lunga verso la nota successiva
            return [(dur_st, ang_next, 1.0, 1.0)]

        elif tech == 'slide':
            # Diagonale ascendente ~20°
            return [(dur_st, math.radians(-20), 0.9, 1.0)]

        elif tech == 'bend':
            # Curva verso l'alto (corda "tirata")
            return [(dur_st, math.radians(-70), 0.9, 1.0),
                    (dur_st // 2, math.radians(-50), 0.5, 0.6)]

        elif tech == 'vibrato':
            # Oscillazione sinistra/destra
            return [(dur_st // 2, math.radians(82),  0.7, 0.85),
                    (dur_st // 2, math.radians(-82), 0.7, 0.85),
                    (dur_st // 3, math.radians(75),  0.5, 0.60)]

        elif tech == 'hammer_on':
            # Due colpi brevi ravvicinati
            return [(12, None, 1.0, 1.0), (10, None, 0.65, 0.80)]

        elif tech == 'powerchord':
            # Tre pennellate orizzontali larghe (accordo potente)
            return [(dur_st, math.radians(0), 1.2, 1.0),
                    (dur_st, math.radians(0), 0.9, 0.75),
                    (dur_st, math.radians(0), 0.7, 0.55)]

        elif tech == 'tapping':
            # 4 tracce radiali corte (dita che percuotono la tastiera)
            return [(10, math.radians(a), 0.6, 0.85) for a in [0, 90, 180, 270]]

        elif tech == 'dive':
            # Spirale discendente (whammy bar)
            return [(dur_st, math.radians(72), 1.0, 1.0),
                    (dur_st // 2, math.radians(85), 0.6, 0.60)]

        elif tech == 'harmonic_natural':
            # Tre tracce radiali leggere (armonico etereo)
            return [(dur_st, math.radians(a), 0.55, 0.50)
                    for a in [30, 150, 270]]

        elif tech == 'harmonic_artificial':
            # 6 scintille radiali brevi (pinch harmonic)
            return [(8, math.radians(a), 0.45, 0.70)
                    for a in [0, 60, 120, 180, 240, 300]]

        else:
            return [(dur_st, None, 1.0, 1.0)]

    # ── riff painting ─────────────────────────────────────────────────────
    def paint_riff(self, notes: List[Dict]):
        for idx, note in enumerate(notes):
            center = np.array([note['x_pos'], note['y_pos']])
            color  = get_note_color(note['note'], note['pitch'])
            base_sz = self._vel_to_size(note['velocity'])

            for n_steps, ang, sz_mult, a_scale in \
                    self._technique_traces(note, notes, idx):
                size = base_sz * sz_mult
                # Piccolo jitter sulla posizione di partenza
                jitter = np.array([random.gauss(0, size * 0.25),
                                   random.gauss(0, size * 0.25)])
                self._paint_trace(center + jitter, size, n_steps,
                                  color, note['velocity'],
                                  ang=ang, alpha_scale=a_scale)

    # ── data ──────────────────────────────────────────────────────────────
    def parse_riff(self) -> List[Dict]:
        riff = [
            {'note': 'A', 'fret': 5, 'string': 6, 'duration': 0.50, 'velocity': 'mf', 'technique': 'staccato'},
            {'note': 'C', 'fret': 8, 'string': 6, 'duration': 0.50, 'velocity': 'f',  'technique': 'legato'},
            {'note': 'D', 'fret': 5, 'string': 4, 'duration': 0.25, 'velocity': 'f',  'technique': 'slide'},
            {'note': 'A', 'fret': 7, 'string': 5, 'duration': 0.50, 'velocity': 'mf', 'technique': 'hammer_on'},
            {'note': 'C', 'fret': 8, 'string': 5, 'duration': 0.25, 'velocity': 'f',  'technique': 'bend'},
            {'note': 'D', 'fret': 7, 'string': 3, 'duration': 0.75, 'velocity': 'f',  'technique': 'vibrato'},
            {'note': 'E', 'fret': 8, 'string': 1, 'duration': 0.50, 'velocity': 'f',  'technique': 'harmonic_natural'},
            {'note': 'G', 'fret': 3, 'string': 1, 'duration': 0.50, 'velocity': 'mp', 'technique': 'legato'},
            {'note': 'A', 'fret': 5, 'string': 1, 'duration': 1.00, 'velocity': 'f',  'technique': 'powerchord'},
            {'note': 'C', 'fret': 8, 'string': 6, 'duration': 0.25, 'velocity': 'mf', 'technique': 'tapping'},
            {'note': 'D', 'fret': 5, 'string': 4, 'duration': 0.50, 'velocity': 'f',  'technique': 'dive'},
            {'note': 'G', 'fret': 3, 'string': 1, 'duration': 0.25, 'velocity': 'p',  'technique': 'harmonic_artificial'},
        ]
        tuning = [40, 45, 50, 55, 59, 64]
        notes, t = [], 0.0
        for nd in riff:
            midi = tuning[nd['string'] - 1] + nd['fret']
            notes.append({**nd,
                          'pitch': midi,
                          'start_time': t,
                          'x_pos': self._tx(t),
                          'y_pos': self._ty(midi)})
            t += nd['duration']
        return notes

    # ── entry point ───────────────────────────────────────────────────────
    def create(self, out: str = 'johnny_b_goode_zorn_riff_v3.png'):
        notes = self.parse_riff()
        print("Ground layer (imprimitura)...")
        self._ground_layer()
        print("Pennellate riff (bristle physics)...")
        self.paint_riff(notes)
        self.canvas.convert('RGB').save(out, dpi=(150, 150))
        print(f"Artwork v3 completato: {out}")


if __name__ == '__main__':
    painting = ZornRiffBristlePainting()
    painting.create()
