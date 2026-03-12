"""
guitarzorn v4 — Alta Densità Pittorica
=======================================
Stesso motore IK bristle di v3, ma:
  - 20× più pennellate per nota (20 ripetizioni per trace-set)
  - Ground layer denso: 80 pennellate invece di 18
  - Canvas 1200×800, px_per_beat=100 → note più vicine e compresse
  - Brush sizes 1.8× più grandi
  - Nota E (bianca) dipinta per ultima su base scura → visibile
  - Jitter σ=55px → accumulo pittorico naturale
"""

import importlib.util, sys, os, random, math
import numpy as np
from PIL import Image

# ─── carica v3 come modulo ────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("v3", os.path.join(_here, "zorn_riff_art_v3.py"))
_v3   = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)

# ri-esponi i simboli che usiamo direttamente
ZORN           = _v3.ZORN
zorn_blend     = _v3.zorn_blend
get_note_color = _v3.get_note_color
ZornBase       = _v3.ZornRiffBristlePainting


# ─── V4 ───────────────────────────────────────────────────────────────────────
class ZornRiffV4(ZornBase):
    """Alta densità: 20× tracce per nota, ground ricco, canvas compresso."""

    # note da dipingere PER ULTIME (su fondo scuro → visibili)
    _PAINT_LAST = {'E'}

    def __init__(self, seed: int = 42):
        super().__init__(width=1200, height=800, seed=seed)
        self.px_per_beat = 100   # era 200
        self.margin      = 80

    # ── dimensioni pennello 1.8× ──────────────────────────────────────────
    @staticmethod
    def _vel_to_size(v: str) -> float:
        return {'p': 12.0, 'mp': 20.0, 'mf': 30.0, 'f': 40.0, 'ff': 52.0}.get(v, 30.0)

    # ── ground denso ──────────────────────────────────────────────────────
    def _ground_layer(self):
        """80 pennellate di imprimitura che coprono ~70% della tela."""
        arr   = np.array(self.canvas)
        noise = np.random.normal(0, 10, arr.shape[:2] + (3,)).astype(int)
        arr[:, :, :3] = np.clip(arr[:, :, :3].astype(int) + noise, 0, 255).astype(np.uint8)
        self.canvas.paste(Image.fromarray(arr[:, :, :3].astype(np.uint8)).convert('RGBA'))
        self.arr[:] = np.array(self.canvas)

        configs = [
            # (colore, n_strokes, sz_lo, sz_hi, alpha_scale, ang_sigma)
            (zorn_blend(ZORN['ochre'],     ZORN['white'],     0.10), 22, 22, 48, 0.60, 0.30),
            (zorn_blend(ZORN['ochre'],     ZORN['black'],     0.15), 18, 16, 38, 0.55, 0.35),
            (zorn_blend(ZORN['ochre'],     ZORN['vermilion'], 0.08), 14, 10, 28, 0.45, 0.28),
            (zorn_blend(ZORN['vermilion'], ZORN['black'],     0.20), 14,  8, 22, 0.38, 0.40),
            (zorn_blend(ZORN['black'],     ZORN['white'],     0.25), 12, 12, 24, 0.32, 0.22),
        ]
        for col, n, sz_lo, sz_hi, a_sc, ang_sig in configs:
            for _ in range(n):
                x    = random.uniform(-60, self.W + 60)
                y    = random.uniform(-60, self.H + 60)
                ang  = random.gauss(0, ang_sig)
                size = random.uniform(sz_lo, sz_hi)
                n_st = max(80, int(random.uniform(130, 210)))
                self._paint_one(
                    np.array([x, y], dtype=float),
                    size, n_st, col, 'f',
                    ang=ang, alpha_scale=a_sc)

    # ── pittura riff ad alta densità ──────────────────────────────────────
    def _paint_note(self, note, notes, idx, alpha_boost: float = 1.0):
        N_REPEAT = 20
        base_sz  = self._vel_to_size(note['velocity'])
        center   = np.array([note['x_pos'], note['y_pos']])
        color    = get_note_color(note['note'], note['velocity'])
        traces   = self._build_traces(note, notes, idx)

        for _ in range(N_REPEAT):
            for n_steps, ang, sm, asc, av, (dx, dy) in traces:
                jitter = np.array([random.gauss(0, 55.0),
                                   random.gauss(0, 42.0)])
                ang_j  = random.gauss(0, 0.28)
                size   = base_sz * sm * random.uniform(0.75, 1.35)
                start  = np.clip(
                    center + np.array([dx, dy]) + jitter,
                    [0.0, 0.0], [float(self.W), float(self.H)])
                n_st   = max(30, int(n_steps * random.uniform(0.7, 1.3)))
                self._paint_one(
                    start, size, n_st, color, note['velocity'],
                    ang=ang + ang_j,
                    alpha_scale=asc * alpha_boost,
                    ang_vel=av)

    def paint_riff(self, notes):
        # Dipinge prima le note scure, poi le chiare (E/bianco) in cima
        ordered = sorted(notes, key=lambda n: n['note'] in self._PAINT_LAST)
        for idx_orig, note in enumerate(notes):
            pass  # solo per avere idx_orig se serve
        for note in ordered:
            idx = notes.index(note)
            boost = 1.05 if note['note'] in self._PAINT_LAST else 1.0
            n_traces = len(self._build_traces(note, notes, idx)) * 20
            print(f"  {note['note']} {note['technique']:20s}  {n_traces} tracce")
            self._paint_note(note, notes, idx, alpha_boost=boost)

    # ── entry point ───────────────────────────────────────────────────────
    def create(self, out: str = 'johnny_b_goode_zorn_v4.png'):
        notes = self.parse_riff()
        # aggiorna x_pos con px_per_beat=100 e margin=80
        for nd in notes:
            nd['x_pos'] = self._tx(nd['start_time'])

        print("Ground layer denso (80 pennellate)...")
        self._ground_layer()
        print("Pittura riff ad alta densità (20× per nota)...")
        self.paint_riff(notes)
        self.canvas.convert('RGB').save(out, dpi=(150, 150))
        print(f"\nArtwork v4 salvato: {out}")


if __name__ == '__main__':
    ZornRiffV4().create()
