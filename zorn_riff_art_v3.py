"""
Guitarzorn v3 – Bristle Brush Physics (Processing → Python)
============================================================
Traduzione in Python del sistema di pennellate di Javier García Carpio
(vimeo.com/82104781, CC BY-SA) integrato con il riff Guitarzorn/Zorn.

Algoritmo chiave (identico all'originale Processing):
  Bristle  – catena IK: ogni nodo segue il predecessore a distanza fissa
             via atan2. Crea il "draping" naturale dei crini reali.
  Brush    – N bristle disposte PERPENDICOLARMENTE alla direzione di
             movimento (dir = smoothed velocity su 4 frame). Rumore smooth
             laterale simula la flessibilità del ciuffo.
  Trace    – traiettoria con rumore angolare, decadimento alpha lineare,
             mixing "pittura umida" con canvas a partire dallo step 5.

Bugfix rispetto alla prima versione:
  - n_steps era 6-8 (formula sbagliata) → ora 80-150 MINIMO.
  - n_traces era 2-4 → ora 20-35 per nota (densità pittorica reale).
  - alpha_scale e ground layer ricalibrati per massima visibilità.
  - SPEED aumentata a 3.0 px/step → pennellate da 240-450 px.
"""

import math
import random
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw

# ─── Palette Zorn (4 colori rigorosi) ────────────────────────────────────────
ZORN = {
    'ochre':     (196, 164, 106),
    'vermilion': (227,  66,  52),
    'black':     ( 28,  28,  28),
    'white':     (242, 242, 242),
}
_NOTE_COL = {'A': 'ochre', 'C': 'vermilion', 'D': 'black', 'E': 'white'}


def zorn_blend(c1: Tuple, c2: Tuple, t: float) -> Tuple[int, int, int]:
    return tuple(max(0, min(255, int(c1[i] * (1 - t) + c2[i] * t))) for i in range(3))


def get_note_color(note: str, midi: int) -> Tuple[int, int, int]:
    """Colore Zorn della nota + shift luminosità per ottava."""
    base = zorn_blend(ZORN['ochre'], ZORN['black'], 0.5) if note == 'G' \
        else ZORN[_NOTE_COL.get(note, 'ochre')]
    b = (midi - 40) / (80 - 40)
    if b > 0.5:
        return zorn_blend(base, ZORN['white'],  (b - 0.5) * 0.5)
    else:
        return zorn_blend(base, ZORN['black'],  (0.5 - b) * 0.4)


def _snoise(x: float) -> float:
    """Smooth pseudo-random in [0,1] con coerenza temporale."""
    return (math.sin(x * 127.1 + math.cos(x * 0.37) * 311.7) + 1.0) / 2.0


# ─── Bristle ──────────────────────────────────────────────────────────────────
class Bristle:
    """
    Catena IK di N segmenti (Javier García Carpio, CC BY-SA).
    Ogni nodo segue il predecessore a distanza fissa tramite atan2.
    """

    def __init__(self, n_parts: int,
                 init_len: float, delta_len: float,
                 init_thick: float, delta_thick: float):
        n = max(2, n_parts + 1)
        self.n = n
        self.pos: List[np.ndarray] = [np.zeros(2) for _ in range(n)]
        self.lengths     = [max(1.0, init_len   - i * delta_len)   for i in range(n)]
        self.thicknesses = [max(0.3, init_thick - i * delta_thick) for i in range(n)]

    def init(self, pos: np.ndarray):
        for i in range(self.n):
            self.pos[i] = pos.copy()

    def update(self, new_pos: np.ndarray):
        self.pos[0] = new_pos.copy()
        for i in range(1, self.n):
            ang = math.atan2(self.pos[i-1][1] - self.pos[i][1],
                             self.pos[i-1][0] - self.pos[i][0])
            L = self.lengths[i]
            self.pos[i] = np.array([self.pos[i-1][0] - L * math.cos(ang),
                                    self.pos[i-1][1] - L * math.sin(ang)])

    def segments(self):
        for i in range(1, self.n):
            yield self.pos[i-1].copy(), self.pos[i].copy(), self.thicknesses[i]


# ─── Brush ────────────────────────────────────────────────────────────────────
class Brush:
    """
    N bristle perpendicolari alla direzione di movimento.
    Direzione = atan2 della variazione della media su 4 frame recenti.
    """
    N_AVG       = 4
    VERT_NOISE  = 8.0
    HORIZ_NOISE = 4.0
    NOISE_SPEED = 0.04

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

        n_parts = max(3, round(math.sqrt(2 * bristle_len)))
        delta_t = bristle_thick / n_parts

        self.bristles: List[Bristle]     = []
        self.b_offsets: List[np.ndarray] = []
        self.b_pos: List[np.ndarray]     = []

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
                  + self._hn * (_snoise(self.seed + self.NOISE_SPEED * self.counter
                                        + b * 0.1) - 0.5))
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
                                   new_avg[0] - self.avg_pos[0]) + math.pi / 2)
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
    Singola pennellata completa.

    PARAMETRI CORRETTI:
      SPEED    = 3.0 px/step   → tratti da 240-450 px (non 12 px come prima)
      n_steps  = 80-150        → 80+ step garantiti (warmup N_AVG=4 incluso)
      MIX_STR  = 0.015         → wet-paint mixing col canvas sottostante
      NOISE_AMP= 0.30          → variazione angolare moderata (≤54°)
    """
    SPEED     = 3.0
    NOISE_F   = 0.007
    NOISE_AMP = 0.30     # radiani di deviazione max per step
    MIX_START = 5
    MIX_STR   = 0.015
    BRIGHT_CH = 14
    MIN_ALPHA = 15

    _VEL_ALPHA = {'p': 140, 'mp': 175, 'mf': 205, 'f': 230, 'ff': 252}

    def __init__(self, brush: Brush, n_steps: int,
                 init_pos: np.ndarray,
                 note_color: Tuple[int, int, int],
                 velocity: str,
                 preferred_ang: Optional[float] = None):
        self.brush      = brush
        self.n_steps    = max(Brush.N_AVG + 10, n_steps)   # MINIMO sempre sopra warmup
        self.note_color = note_color
        self.colors: Optional[List[List[Tuple]]] = None

        # ── Traiettoria: random walk angolare attorno a preferred_ang ──────
        seed = random.uniform(0, 1000)
        ang  = preferred_ang if preferred_ang is not None \
            else random.gauss(0.0, math.pi / 3)   # bias verso destra
        pos  = init_pos.copy()
        self.positions = [pos.copy()]
        for s in range(1, self.n_steps):
            drift = self.NOISE_AMP * math.pi * (_snoise(seed + self.NOISE_F * s) - 0.5)
            a     = ang + drift
            pos   = pos + np.array([self.SPEED * math.cos(a),
                                    self.SPEED * math.sin(a)])
            self.positions.append(pos.copy())

        # ── Alpha decay ────────────────────────────────────────────────────
        a0    = self._VEL_ALPHA.get(velocity, 200)
        a_dec = min(a0 / self.n_steps, 25.0)
        a     = float(a0)
        self.alphas: List[int] = []
        for _ in range(self.n_steps):
            self.alphas.append(int(max(0, a)))
            a = max(0.0, a - a_dec)

    def calculate_colors(self, canvas_arr: np.ndarray):
        n = self.brush.n
        r0, g0, b0 = self.note_color
        ch = self.BRIGHT_CH

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

        rp = [float(c[0]) for c in step0]
        gp = [float(c[1]) for c in step0]
        bp = [float(c[2]) for c in step0]
        H, W = canvas_arr.shape[:2]
        ms   = self.MIX_STR

        for s in range(mix_start, self.n_steps):
            px, py = int(self.positions[s][0]), int(self.positions[s][1])
            step_cols = []
            for b in range(n):
                if 0 <= py < H and 0 <= px < W:
                    cp   = canvas_arr[py, px]
                    rp[b] = (rp[b] + ms * float(cp[0])) / (1 + ms)
                    gp[b] = (gp[b] + ms * float(cp[1])) / (1 + ms)
                    bp[b] = (bp[b] + ms * float(cp[2])) / (1 + ms)
                step_cols.append((int(rp[b]), int(gp[b]), int(bp[b])))
            colors.append(step_cols)

        self.colors = colors

    def paint(self, canvas: Image.Image, canvas_arr: np.ndarray):
        overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)
        self.brush.reset(self.positions[0])
        for s in range(self.n_steps):
            self.brush.update(self.positions[s])
            if (self.colors and s < len(self.colors)
                    and self.alphas[s] >= self.MIN_ALPHA):
                self.brush.paint_step(draw, self.colors[s], self.alphas[s])
        result = Image.alpha_composite(canvas.convert('RGBA'), overlay)
        canvas.paste(result.convert(canvas.mode))
        canvas_arr[:] = np.array(canvas)
        self.brush.reset(self.positions[0])


# ─── Orchestratore ────────────────────────────────────────────────────────────
class ZornRiffBristlePainting:
    """
    Pipeline: riff chitarra → tela pittorica a pennellate fisicamente simulate.

    Ogni nota genera 20-35 Trace con n_steps 80-150 → pennellate da 240-450 px.
    La densità risultante copre il canvas con textura di olio pittorico reale.
    """

    def __init__(self, width: int = 1600, height: int = 1000, seed: int = 42):
        self.W, self.H = width, height
        random.seed(seed)
        np.random.seed(seed)

        bg = ZORN['ochre'] + (255,)
        self.canvas = Image.new('RGBA', (width, height), bg)
        self.arr    = np.array(self.canvas)

        self.px_per_beat = 200   # più largo → note più distribuite sul canvas
        self.margin      = 100

    def _tx(self, t: float) -> float:
        return self.margin + t * self.px_per_beat

    def _ty(self, midi: int) -> float:
        n = (midi - 40) / (80 - 40)
        return self.margin + n * (self.H - 2 * self.margin)

    # ── costruzione brush ─────────────────────────────────────────────────
    @staticmethod
    def _vel_to_size(v: str) -> float:
        return {'p': 7.0, 'mp': 11.0, 'mf': 17.0, 'f': 23.0, 'ff': 30.0}.get(v, 17.0)

    def _make_brush(self, pos: np.ndarray, size: float) -> Brush:
        n_bristles    = int(size * random.uniform(1.5, 2.0))
        bristle_len   = min(2.2 * size, 14.0)
        bristle_thick = min(0.9 * size, 6.0)
        return Brush(pos, size, n_bristles, bristle_len, bristle_thick)

    # ── paint singola traccia ─────────────────────────────────────────────
    def _paint_one(self, pos: np.ndarray, size: float, n_steps: int,
                   color: Tuple, velocity: str,
                   ang: Optional[float] = None,
                   alpha_scale: float = 1.0):
        brush = self._make_brush(pos, size)
        trace = Trace(brush, n_steps, pos, color, velocity, preferred_ang=ang)
        if alpha_scale != 1.0:
            trace.alphas = [int(a * alpha_scale) for a in trace.alphas]
        trace.calculate_colors(self.arr)
        trace.paint(self.canvas, self.arr)

    # ── ground layer ──────────────────────────────────────────────────────
    def _ground_layer(self):
        """
        Imprimitura: 36 pennellate orizzontali di varianti ochre a media alpha.
        Crea la textura di base della tela preparata.
        """
        configs = [
            # (t_white, t_black, n_strokes, size_lo, size_hi, alpha_scale)
            (0.06, 0.00, 12, 22, 50, 0.58),   # ochre chiara
            (0.00, 0.10, 12, 16, 36, 0.52),   # ochre scura
            (0.03, 0.03, 12, 12, 26, 0.42),   # ochre media
        ]
        for t_w, t_b, n, sz_lo, sz_hi, a_sc in configs:
            base = ZORN['ochre']
            col  = zorn_blend(base, ZORN['white'], t_w) if t_w > 0 \
                else zorn_blend(base, ZORN['black'], t_b)
            for _ in range(n):
                x    = random.uniform(-100, self.W + 100)
                y    = random.uniform(-100, self.H + 100)
                ang  = random.gauss(0, 0.14)
                size = random.uniform(sz_lo, sz_hi)
                # n_steps grande: pennellate lunghe per coprire canvas
                n_st = max(100, int(random.uniform(180, 280)))
                self._paint_one(np.array([x, y], dtype=float),
                                size, n_st, col, 'mf',
                                ang=ang, alpha_scale=a_sc)

    # ── mapping tecnica → elenco pennellate ───────────────────────────────
    def _build_traces(self, note: Dict, notes: List[Dict], idx: int
                      ) -> List[Tuple[int, Optional[float], float, float]]:
        """
        Ritorna lista di (n_steps, angle, size_mult, alpha_scale).
        n_steps è SEMPRE ≥ 80 (era il bug principale nella versione precedente).
        Ogni nota produce 20-35 tracce per densità pittorica reale.
        """
        tech    = note['technique']
        dur     = note['duration']
        base_sz = self._vel_to_size(note['velocity'])

        # Numero di step fisso e lungo: pennellate da 240-450 px
        n_st = max(80, int(80 + dur * 100))   # 80..180 step → 240..540 px

        # Angolo verso nota successiva
        nxt = notes[idx + 1] if idx + 1 < len(notes) else None
        if nxt:
            ang_next = math.atan2(nxt['y_pos'] - note['y_pos'],
                                  nxt['x_pos'] - note['x_pos'])
        else:
            ang_next = 0.0

        # Helper per generare n tracce in ventaglio attorno a center_ang
        def fan(n: int, center: Optional[float], spread: float,
                sm: float = 1.0, asc: float = 1.0, steps_mult: float = 1.0):
            result = []
            for _ in range(n):
                a = (center + random.gauss(0, spread)) if center is not None \
                    else random.uniform(0, 2 * math.pi)
                result.append((max(80, int(n_st * steps_mult)), a, sm, asc))
            return result

        # ── tecniche ──────────────────────────────────────────────────────
        if tech == 'staccato':
            # Colpi brevi radiali: pennellate corte in tutte le direzioni
            return fan(20, None, math.pi, 0.9, 0.90, 0.55)

        elif tech == 'legato':
            # Pennellate lunghe verso la nota successiva
            return (fan(14, ang_next, math.pi / 5, 1.0, 1.0, 1.0)
                    + fan(8,  ang_next, math.pi / 3, 0.7, 0.75, 0.7))

        elif tech == 'slide':
            # Diagonale ascendente ~20°, ventaglio stretto
            ang_slide = math.radians(-20)
            return (fan(15, ang_slide, math.pi / 6, 1.0, 1.0, 1.0)
                    + fan(8,  ang_slide, math.pi / 4, 0.7, 0.70, 0.7))

        elif tech == 'bend':
            # Curvatura verso l'alto, ventaglio moderato
            return (fan(12, math.radians(-70), math.pi / 5, 1.0, 1.0, 1.0)
                    + fan(10, math.radians(-55), math.pi / 3, 0.7, 0.80, 0.8))

        elif tech == 'vibrato':
            # Oscillazione: ventaglio ampio ± orizzontale
            return (fan(10, math.radians(85),  math.pi / 6, 0.8, 0.90, 1.0)
                    + fan(10, math.radians(-85), math.pi / 6, 0.8, 0.90, 1.0)
                    + fan(8,  math.radians(80),  math.pi / 5, 0.6, 0.65, 0.7))

        elif tech == 'hammer_on':
            # Due burst ravvicinati
            return (fan(13, None, math.pi / 2, 1.0, 1.0, 0.6)
                    + fan(10, None, math.pi / 2, 0.7, 0.80, 0.5))

        elif tech == 'powerchord':
            # Tre strati orizzontali molto larghi (accordo potente)
            return (fan(12, math.radians(0), math.pi / 8, 1.3, 1.0, 1.1)
                    + fan(10, math.radians(0), math.pi / 6, 1.0, 0.80, 1.0)
                    + fan(8,  math.radians(0), math.pi / 5, 0.8, 0.60, 0.8))

        elif tech == 'tapping':
            # Raggi radiali a 6 direzioni, brevi
            return [t for ang in [0, 60, 120, 180, 240, 300]
                    for t in fan(4, math.radians(ang), math.pi / 8,
                                 0.65, 0.85, 0.45)]

        elif tech == 'dive':
            # Discendente con ventaglio verso il basso
            return (fan(14, math.radians(75), math.pi / 5, 1.0, 1.0, 1.1)
                    + fan(10, math.radians(80), math.pi / 4, 0.7, 0.70, 0.8))

        elif tech == 'harmonic_natural':
            # Tre raggi leggeri ed eterei
            return [t for ang in [30, 150, 270]
                    for t in fan(8, math.radians(ang), math.pi / 5,
                                 0.55, 0.60, 1.0)]

        elif tech == 'harmonic_artificial':
            # 6 scintille radiali brevi e affilate
            return [t for ang in [0, 60, 120, 180, 240, 300]
                    for t in fan(4, math.radians(ang), math.pi / 10,
                                 0.45, 0.80, 0.40)]

        else:
            return fan(22, None, math.pi / 2, 1.0, 1.0, 1.0)

    # ── riff painting ─────────────────────────────────────────────────────
    def paint_riff(self, notes: List[Dict]):
        for idx, note in enumerate(notes):
            base_sz = self._vel_to_size(note['velocity'])
            center  = np.array([note['x_pos'], note['y_pos']])
            color   = get_note_color(note['note'], note['pitch'])
            traces  = self._build_traces(note, notes, idx)

            print(f"  [{idx+1:2d}/12] {note['note']} {note['technique']:20s}"
                  f"  {len(traces)} tracce × ~{traces[0][0]} step")

            for n_steps, ang, sm, asc in traces:
                size   = base_sz * sm
                # Spread spaziale dal centro della nota (proporzionale alla size)
                jitter = np.array([random.gauss(0, size * 1.2),
                                   random.gauss(0, size * 1.2)])
                self._paint_one(center + jitter, size, n_steps,
                                color, note['velocity'],
                                ang=ang, alpha_scale=asc)

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
            notes.append({**nd, 'pitch': midi, 'start_time': t,
                          'x_pos': self._tx(t), 'y_pos': self._ty(midi)})
            t += nd['duration']
        return notes

    def create(self, out: str = 'johnny_b_goode_zorn_riff_v3.png'):
        notes = self.parse_riff()
        print("Ground layer (imprimitura)...")
        self._ground_layer()
        print("Pennellate riff (bristle physics)...")
        self.paint_riff(notes)
        self.canvas.convert('RGB').save(out, dpi=(150, 150))
        print(f"\nArtwork v3 completato: {out}")


if __name__ == '__main__':
    painting = ZornRiffBristlePainting()
    painting.create()
