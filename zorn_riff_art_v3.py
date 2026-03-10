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

    def reset_directed(self, pos: np.ndarray, movement_ang: float):
        """Pre-estende la catena nella direzione OPPOSTA al movimento.
        Elimina il curl iniziale di srotolamento (tentacle bug)."""
        trail_cos = math.cos(movement_ang + math.pi)
        trail_sin = math.sin(movement_ang + math.pi)
        cumlen = 0.0
        for i in range(self.n):
            self.pos[i] = pos + np.array([cumlen * trail_cos,
                                           cumlen * trail_sin])
            if i < self.n - 1:
                cumlen += self.lengths[i + 1]

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

    def reset_directed(self, init_pos: np.ndarray, movement_ang: float):
        """Reset con catena pre-orientata nella direzione movement_ang.
        Pre-popola history → is_ready() True immediatamente → no warmup gap.
        Ogni bristle parte già estesa → no curl iniziale."""
        self.pos     = init_pos.copy()
        self.dir     = movement_ang + math.pi / 2   # perp. al movimento
        self.history = [init_pos.copy() for _ in range(self.N_AVG)]
        self.avg_pos = init_pos.copy()
        self.counter = 0
        self._update_bpos()
        for b in range(self.n):
            self.bristles[b].reset_directed(self.b_pos[b], movement_ang)

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
    SPEED     = 2.5      # px/step → pennellate da 125-250 px (più drammatiche)
    NOISE_F   = 0.007
    NOISE_AMP = 0.07     # ≤12° deviazione → pennellate quasi dritte
    MIX_START = 5
    MIX_STR   = 0.015
    BRIGHT_CH = 14
    MIN_ALPHA = 15

    _VEL_ALPHA = {'p': 140, 'mp': 175, 'mf': 205, 'f': 230, 'ff': 252}

    def __init__(self, brush: Brush, n_steps: int,
                 init_pos: np.ndarray,
                 note_color: Tuple[int, int, int],
                 velocity: str,
                 preferred_ang: Optional[float] = None,
                 ang_vel: float = 0.0):
        self.brush      = brush
        self.n_steps    = max(Brush.N_AVG + 10, n_steps)   # MINIMO sempre sopra warmup
        self.note_color = note_color
        self.colors: Optional[List[List[Tuple]]] = None

        # ── Traiettoria: random walk angolare (ang_vel≠0 → arco/curva) ──────
        seed = random.uniform(0, 1000)
        ang  = preferred_ang if preferred_ang is not None \
            else random.gauss(0.0, math.pi / 3)   # bias verso destra
        pos  = init_pos.copy()
        self.positions = [pos.copy()]
        for s in range(1, self.n_steps):
            ang  += ang_vel   # rotazione progressiva → 0 = dritto, ≠0 = arco
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
        # Calcola direzione iniziale dalla traiettoria
        if len(self.positions) > 1:
            dp       = self.positions[1] - self.positions[0]
            init_ang = math.atan2(dp[1], dp[0])
        else:
            init_ang = 0.0
        # Pre-orienta la catena → elimina curl di srotolamento
        self.brush.reset_directed(self.positions[0], init_ang)
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

    Ogni nota genera 88-124 Trace con n_steps 35-70 → pennellate da 52-105 px.
    La densità risultante (~1200 tracce totali) copre il canvas come olio pittorico.
    """

    def __init__(self, width: int = 1600, height: int = 1000, seed: int = 42):
        self.W, self.H = width, height
        random.seed(seed)
        np.random.seed(seed)

        bg = zorn_blend(ZORN['ochre'], ZORN['white'], 0.28) + (255,)
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
                   alpha_scale: float = 1.0,
                   ang_vel: float = 0.0):
        brush = self._make_brush(pos, size)
        trace = Trace(brush, n_steps, pos, color, velocity,
                      preferred_ang=ang, ang_vel=ang_vel)
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
        # (color_tuple, n_strokes, size_lo, size_hi, alpha_scale, ang_sigma)
        configs = [
            (zorn_blend(ZORN['ochre'], ZORN['white'],     0.08), 18, 24, 55, 0.65, 0.15),
            (zorn_blend(ZORN['ochre'], ZORN['black'],     0.12), 16, 18, 40, 0.60, 0.18),
            (zorn_blend(ZORN['ochre'], ZORN['vermilion'], 0.06), 12, 14, 32, 0.50, 0.20),
            (zorn_blend(ZORN['ochre'], ZORN['black'],     0.06), 10, 10, 22, 0.45, 0.25),
        ]
        for col, n, sz_lo, sz_hi, a_sc, ang_sig in configs:
            for _ in range(n):
                x    = random.uniform(-120, self.W + 120)
                y    = random.uniform(-120, self.H + 120)
                ang  = random.gauss(0, ang_sig)
                size = random.uniform(sz_lo, sz_hi)
                n_st = max(120, int(random.uniform(200, 320)))
                self._paint_one(np.array([x, y], dtype=float),
                                size, n_st, col, 'f',
                                ang=ang, alpha_scale=a_sc)

    # ── mapping tecnica → elenco pennellate ───────────────────────────────
    def _build_traces(self, note: Dict, notes: List[Dict], idx: int
                      ) -> List[Tuple]:
        """
        Ritorna lista di 6-tuple:
          (n_steps, angle, size_mult, alpha_scale, ang_vel, (dx, dy))

        Ogni tecnica ha il suo segno pittorico DISTINTO — pochi segni ma leggibili.
        ang_vel≠0 crea archi (bend=curva verso su, dive=curva verso giù).
        (dx, dy) = offset fisso dal centro nota (per pennellate parallele e cluster).
        """
        tech = note['technique']
        dur  = note['duration']

        # Angolo verso nota successiva (usato da legato)
        nxt = notes[idx + 1] if idx + 1 < len(notes) else None
        ang_next = (math.atan2(nxt['y_pos'] - note['y_pos'],
                               nxt['x_pos'] - note['x_pos'])
                    if nxt else 0.0)

        g = lambda mu=0.0, s=0.12: random.gauss(mu, s)  # shortcut gaussiano

        if tech == 'staccato':
            # 2 pennellate bold lunghe diagonali (~-35°) — 250px, colpo netto e deciso
            return [
                (100, math.radians(-35) + g(), 1.30, 0.96, 0.0, (0,    0)),
                (75,  math.radians(-35) + g(), 1.05, 0.80, 0.0, (g(0,12), g(0,8))),
            ]

        elif tech == 'legato':
            # 2 pennellate lunghe fluide verso nota successiva (più spesse per visibilità)
            return [
                (135, ang_next + g(0, 0.08), 1.00, 0.92, 0.0, (0,    0)),
                (105, ang_next + g(0, 0.10), 0.80, 0.80, 0.0, (g(0,18), g(0,10))),
            ]

        elif tech == 'slide':
            # 3 linee sottili lunghe quasi-orizzontali, semi-trasparenti (effetto fantasma)
            return [
                (200, math.radians(-15) + g(0, 0.04), 0.32, 0.38, 0.0, (0, -20)),
                (185, math.radians(-15) + g(0, 0.04), 0.28, 0.32, 0.0, (0,   0)),
                (165, math.radians(-15) + g(0, 0.04), 0.25, 0.26, 0.0, (0, +20)),
            ]

        elif tech == 'hammer_on':
            # 8 segni corti e densi a raggiera stretta — "botta" sul tasto
            r = 14.0
            return [
                (28, math.radians(a) + g(0, 0.08), 0.62, 0.88, 0.0,
                 (r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
                for a in [0, 45, 90, 135, 180, 225, 270, 315]
            ]

        elif tech == 'bend':
            # 2 archi verso l'alto: partono a -45°, curvano 90° → C rovesciata
            # raggio = SPEED/|ang_vel| = 2.5/0.0262 ≈ 95px → arco netto e leggibile
            n = 60
            av = -math.pi / (2.0 * n)
            return [
                (n,      math.radians(-45) + g(0, 0.06), 1.10, 0.95, av,       (0,  0)),
                (n - 15, math.radians(-37) + g(0, 0.06), 0.82, 0.78, av * 0.9, (8,  8)),
            ]

        elif tech == 'vibrato':
            # 10 tracce corte alternanti su/giù con X-offset progressivo lineare
            # → sinusoide discreta leggibile (non blob caotico)
            return [
                (35, math.radians(-60) + g(0, 0.05), 0.90, 0.90, 0.0, (dx,  0))
                for dx in [0, 12, 24, 36, 48]
            ] + [
                (35, math.radians(+60) + g(0, 0.05), 0.90, 0.90, 0.0, (dx,  0))
                for dx in [6, 18, 30, 42, 54]
            ]

        elif tech == 'powerchord':
            # 3 pennellate bold orizz. ±35px Y — separazione 70px > larghezza brush (31px)
            return [
                (110, math.radians(0) + g(0, 0.05), 1.35, 0.98, 0.0, (0, -35)),
                (110, math.radians(0) + g(0, 0.05), 1.35, 0.98, 0.0, (0,   0)),
                (105, math.radians(0) + g(0, 0.05), 1.20, 0.90, 0.0, (0, +35)),
            ]

        elif tech == 'tapping':
            # 4 raggi a X con offset radiale r=12px — fix: erano tutti a (0,0)
            r = 12.0
            return [
                (22, math.radians(a) + g(0, 0.10), 0.58, 0.82, 0.0,
                 (r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
                for a in [45, 135, 225, 315]
            ]

        elif tech == 'dive':
            # 2 archi verso il basso: partono orizzontali, curvano a +70° (whammy bar)
            n = 145
            av = math.pi / (2.6 * n)   # ~70° totali
            return [
                (n,      math.radians(10) + g(0, 0.06), 0.98, 0.90, av,      (0,  0)),
                (n - 20, math.radians(18) + g(0, 0.06), 0.72, 0.72, av * 0.9, (7,  6)),
            ]

        elif tech == 'harmonic_natural':
            # 3 segni eterei a 120° — n_steps 20→35 per evitare fadeout precoce
            r = 22.0
            return [
                (35, math.radians(a) + g(0, 0.06), 0.38, 0.35, 0.0,
                 (r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
                for a in [30, 150, 270]
            ]

        elif tech == 'harmonic_artificial':
            # 4 scintille a 90° — fix critico: n_steps 15→28, size 0.32→0.55
            r = 16.0
            return [
                (28, math.radians(a) + g(0, 0.08), 0.55, 0.40, 0.0,
                 (r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
                for a in [0, 90, 180, 270]
            ]

        else:
            return [(65, 0.0, 1.0, 1.0, 0.0, (0, 0))]

    # ── riff painting ─────────────────────────────────────────────────────
    def paint_riff(self, notes: List[Dict]):
        for idx, note in enumerate(notes):
            base_sz = self._vel_to_size(note['velocity'])
            center  = np.array([note['x_pos'], note['y_pos']])
            color   = get_note_color(note['note'], note['pitch'])
            traces  = self._build_traces(note, notes, idx)

            print(f"  [{idx+1:2d}/12] {note['note']} {note['technique']:20s}"
                  f"  {len(traces)} tracce × ~{traces[0][0]} step")

            for n_steps, ang, sm, asc, av, (dx, dy) in traces:
                size = base_sz * sm
                # Jitter minimo (σ=15px) → segni rimangono vicini al centro
                # La posizione musicale è preservata: ogni nota ha il suo luogo.
                jitter = np.array([random.gauss(0, 15.0),
                                   random.gauss(0, 15.0)])
                start = np.clip(center + np.array([dx, dy]) + jitter,
                                [0.0, 0.0], [float(self.W), float(self.H)])
                self._paint_one(start, size, n_steps,
                                color, note['velocity'],
                                ang=ang, alpha_scale=asc, ang_vel=av)

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
