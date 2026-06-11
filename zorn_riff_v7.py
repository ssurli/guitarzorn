"""
guitarzorn v7 — Olio Reale (Height-Field + Relief Lighting)
============================================================
Abbandona il motore bristle-IK (port p5.js/Processing) per un renderer
fisicamente ispirato, alla "Fast Paint Texture" (Hertzmann 2002):

  1. Ogni pennellata deposita COLORE + ALTEZZA (impasto reale).
  2. La tela ha una trama tessuta procedurale (ordito/trama) nel rilievo.
  3. Striature per-setola lungo la pennellata (carico di pigmento variabile).
  4. Dry-brush: la pennellata si esaurisce e aggrappa solo i punti alti
     della trama → coda graffiata e spezzata.
  5. Smearing bagnato-su-bagnato: il colore trascina quello sottostante.
  6. Pass finale di illuminazione: normali dal gradiente del height-field
     → diffusa + speculare (il lucido dell'olio) + occlusione nelle valli.

Composizione: campo ocra denso (ground) + 12 segni tecnica-specifici
del riff di Johnny B. Goode, palette Zorn rigorosa.
"""

import math
import random
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

# ─── Palette Zorn ──────────────────────────────────────────────────────────────
ZORN = {
    'ochre':     (196, 164, 106),
    'vermilion': (227,  66,  52),
    'black':     ( 28,  28,  28),
    'white':     (242, 242, 242),
    'gold':      (220, 140,  73),
}
_NOTE_COL = {'A': 'vermilion', 'C': 'ochre', 'D': 'black',
             'E': 'white', 'G': 'gold'}


def zorn_blend(c1, c2, t: float) -> Tuple[int, int, int]:
    return tuple(max(0, min(255, int(c1[i] * (1 - t) + c2[i] * t)))
                 for i in range(3))


def get_note_color(note: str, velocity: str) -> Tuple[int, int, int]:
    base = ZORN[_NOTE_COL.get(note, 'ochre')]
    lum = {'p': -0.28, 'mp': -0.14, 'mf': 0.0,
           'f': 0.18, 'ff': 0.36}.get(velocity, 0.0)
    if lum < 0:
        c = zorn_blend(base, ZORN['black'], abs(lum) * 0.6)
    elif lum > 0:
        c = zorn_blend(base, ZORN['white'], lum * 0.5)
    else:
        c = base
    # C=ocra su fondo ocra → raw sienna (ocra+vermilion caldo) per contrasto caldo
    if note == 'C':
        c = zorn_blend(c, ZORN['vermilion'], 0.38)
    elif note == 'G':
        # oro → ambrato più caldo
        c = zorn_blend(c, ZORN['vermilion'], 0.22)
    return c


# ─── utilità numpy ─────────────────────────────────────────────────────────────

def _box(a: np.ndarray, r: int, axis: int) -> np.ndarray:
    """Box blur 1D via somma cumulativa (vettoriale)."""
    if r <= 0:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r, r)
    ap = np.pad(a, pad, mode='edge')
    c = np.cumsum(ap, axis=axis, dtype=np.float64)
    zshape = list(c.shape)
    zshape[axis] = 1
    c = np.concatenate([np.zeros(zshape), c], axis=axis)
    w = 2 * r + 1
    hi = [slice(None)] * a.ndim
    lo = [slice(None)] * a.ndim
    hi[axis] = slice(w, w + a.shape[axis])
    lo[axis] = slice(0, a.shape[axis])
    return ((c[tuple(hi)] - c[tuple(lo)]) / w).astype(np.float32)


def blur(a: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussiana approssimata: 3 box blur ripetuti (separabili)."""
    if sigma <= 0:
        return a.astype(np.float32)
    r = max(1, int(round(sigma)))
    out = a.astype(np.float32)
    for _ in range(3):
        out = _box(out, r, 0)
        out = _box(out, r, 1)
    return out


def snoise1(rng: np.random.Generator, n: int, scale: float) -> np.ndarray:
    """Rumore liscio 1D in ~[-1,1]."""
    k = max(2, int(n / max(scale, 1.0)) + 2)
    p = rng.standard_normal(k).astype(np.float32)
    x = np.linspace(0, k - 1, n)
    v = np.interp(x, np.arange(k), p)
    s = np.std(v)
    return (v / s if s > 1e-6 else v).astype(np.float32)


def snoise2(rng: np.random.Generator, nt: int, ns: int,
            ts: float, ss: float) -> np.ndarray:
    """Rumore liscio 2D in ~[-1,1], shape (nt, ns)."""
    kt = max(2, int(nt / max(ts, 1.0)) + 2)
    ks = max(2, int(ns / max(ss, 1.0)) + 2)
    g = rng.standard_normal((kt, ks)).astype(np.float32)
    ti = np.clip(np.round(np.linspace(0, kt - 1, nt)).astype(int), 0, kt - 1)
    si = np.clip(np.round(np.linspace(0, ks - 1, ns)).astype(int), 0, ks - 1)
    up = g[ti][:, si]
    up = blur(up, 1.5)
    s = np.std(up)
    return up / s if s > 1e-6 else up


# ─── Tela a olio (color buffer + height field) ────────────────────────────────

class OilCanvas:
    """
    Tela con doppio buffer: colore (float 0..1) e altezza (impasto).
    La trama tessuta della tela vive nel height-field di base, così la
    pittura sottile la lascia trasparire e il dry-brush vi si aggrappa.
    """

    def __init__(self, W: int, H: int, base_color, seed: int = 42):
        self.W, self.H = W, H
        self.rng = np.random.default_rng(seed)

        base = np.asarray(base_color, np.float32) / 255.0
        self.color = np.empty((H, W, 3), np.float32)
        self.color[:] = base

        # ── trama tessuta — molto sottile (fondo liscio come tavola preparata)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        sp = 6.0
        warp = np.sin(xx * (2 * np.pi / sp) + np.sin(yy * 0.55) * 0.6)
        weft = np.sin(yy * (2 * np.pi / (sp * 1.12)) + np.sin(xx * 0.42) * 0.6)
        weave = (warp * 0.5 + 0.5) * 0.55 + (weft * 0.5 + 0.5) * 0.45
        weave += self.rng.standard_normal((H, W)).astype(np.float32) * 0.06
        weave = blur(weave, 2)
        weave -= weave.min()
        weave /= max(weave.max(), 1e-6)
        self.weave = weave
        self.height = np.zeros((H, W), np.float32)  # tela piatta: solo l'impasto conta

        # mottling anisotropico: larghe variazioni orizzontali, piccole verticali
        # → le pennellate del ground affiorano come nel riferimento
        mx = blur(self.rng.standard_normal((H, W)).astype(np.float32), 90)
        my = _box(mx, 4, 0)                          # schiaccia la variazione verticale
        my /= max(np.abs(my).max(), 1e-6)
        self.color += my[..., None] * 0.040          # leggerissima ondulazione calda
        self.color = np.clip(self.color, 0, 1)

    # ── pennellata ────────────────────────────────────────────────────────────
    def stroke(self, x: float, y: float, angle: float,
               length: float, width: float, color,
               opacity: float = 0.92, thickness: float = 1.0,
               curvature: float = 0.0, waviness: float = 0.0,
               wave_freq: float = 4.0, dryness: float = 0.35,
               smear: float = 0.40, taper_end: float = 0.55):
        """
        Deposita una pennellata su colore + altezza.

        curvature  — radianti totali di sterzata lungo il tratto (arco).
        waviness   — ampiezza px dell'oscillazione perpendicolare (vibrato).
        dryness    — 0=carica, 1=quasi secca: la coda aggrappa solo i punti
                     alti della trama (dry-brush).
        smear      — quanto colore sottostante viene trascinato nel tratto.
        thickness  — scala dell'impasto depositato nel height-field.
        """
        rng = self.rng
        col = np.asarray(color, np.float32) / 255.0

        # ── traiettoria (1 px per step) ──────────────────────────────────────
        n = max(8, int(length))
        ts = np.linspace(0.0, 1.0, n).astype(np.float32)
        ang = (angle + curvature * ts
               + snoise1(rng, n, 30) * 0.045)        # tremolio della mano
        dx, dy = np.cos(ang), np.sin(ang)
        px = x + np.cumsum(dx) - dx[0]
        py = y + np.cumsum(dy) - dy[0]
        if waviness > 0:
            osc = np.sin(ts * 2 * np.pi * wave_freq) * waviness
            px += -dy * osc
            py += dx * osc
        nx, ny = -dy, dx                              # normali al tratto

        # ── profilo larghezza lungo t (attacco + rilascio) ───────────────────
        attack = np.minimum(1.0, ts / 0.06) ** 0.6
        release = 1.0 - taper_end * np.clip((ts - 0.72) / 0.28, 0, 1) ** 1.6
        wt = width * attack * release                 # (n,)

        # ── profilo setole attraverso s ──────────────────────────────────────
        nS = max(7, int(width * 1.7))
        s = np.linspace(-1.0, 1.0, nS).astype(np.float32)
        load = rng.random(nS).astype(np.float32)
        k = np.array([0.25, 0.5, 0.25], np.float32)
        load = np.convolve(np.pad(load, 1, mode='edge'), k, 'valid')
        bristle = 0.45 + 0.55 * load                  # carico per-setola
        edge = np.clip((1.0 - np.abs(s)) * 3.0, 0, 1) ** 0.65

        # ── esaurimento pigmento + striature ────────────────────────────────
        dep = (1.0 - 0.62 * ts ** 1.25) * (0.85 + 0.30 * snoise1(rng, n, 18))
        dep = np.clip(dep, 0.05, 1.4)
        streak = 1.0 + 0.30 * snoise2(rng, n, nS, 16, 1.6)
        D = dep[:, None] * bristle[None, :] * np.clip(streak, 0.2, 2.0)
        A = np.clip(D, 0, 1.25) * edge[None, :]       # (n, nS) alpha grezza

        # ── smearing: pickup del colore sottostante (EMA lungo il tratto) ───
        cx = np.clip(px.astype(int), 0, self.W - 1)
        cy = np.clip(py.astype(int), 0, self.H - 1)
        under = self.color[cy, cx]                    # (n,3)
        carried = np.empty_like(under)
        carried[0] = under[0]
        kp = 0.03                                     # pickup lento: non contamina il colore
        for i in range(1, n):
            carried[i] = carried[i - 1] * (1 - kp) + under[i] * kp
        m = (smear * (0.25 + 0.6 * ts))[:, None]      # più sporco verso la coda
        pc = col[None, :] * (1 - m) + carried * m     # (n,3) colore depositato

        # ── campionamento del nastro ─────────────────────────────────────────
        S = s[None, :] * (wt[:, None] * 0.5)          # offset reali (n,nS)
        X = px[:, None] + nx[:, None] * S
        Y = py[:, None] + ny[:, None] * S
        xi = np.round(X).astype(int).ravel()
        yi = np.round(Y).astype(int).ravel()
        a = A.ravel()
        pcol = np.repeat(pc, nS, axis=0)
        d = D.ravel()

        ok = (xi >= 0) & (xi < self.W) & (yi >= 0) & (yi < self.H) & (a > 0.01)
        if not np.any(ok):
            return
        xi, yi, a, d = xi[ok], yi[ok], a[ok], d[ok]
        pcol = pcol[ok]

        # ── dry-brush: dove il pigmento scarseggia, aggrappa solo la trama ──
        # need=0 → corpo carico, copertura piena; need→1 → solo i punti
        # alti della trama ricevono pigmento (coda graffiata).
        need = np.clip((dryness * 1.15 - d) / max(dryness, 1e-3), 0, 1)
        gate = np.clip((self.weave[yi, xi] + (1.0 - need) - 0.82) / 0.22, 0, 1)
        a = a * (0.12 + 0.88 * gate) * opacity

        # ── accumulo locale (bbox) e compositing ────────────────────────────
        x0, x1 = xi.min(), xi.max() + 1
        y0, y1 = yi.min(), yi.max() + 1
        lw, lh = x1 - x0, y1 - y0
        lx, ly = xi - x0, yi - y0

        wsum = np.zeros((lh, lw), np.float32)
        csum = np.zeros((lh, lw, 3), np.float32)
        hsum = np.zeros((lh, lw), np.float32)
        np.add.at(wsum, (ly, lx), a)
        np.add.at(csum, (ly, lx), pcol * a[:, None])
        np.add.at(hsum, (ly, lx), a * d)

        nz = wsum > 1e-4
        Aeff = np.clip(wsum, 0, 0.94)
        mean_col = np.zeros_like(csum)
        mean_col[nz] = csum[nz] / wsum[nz, None]

        roi = self.color[y0:y1, x0:x1]
        roi[nz] = roi[nz] * (1 - Aeff[nz, None]) + mean_col[nz] * Aeff[nz, None]

        # impasto: l'altezza si accumula, con tetto per pennellata.
        # Lieve blur → le creste seguono il gesto invece del rumore per-pixel.
        hadd = blur(np.clip(hsum, 0, 1.8), 1) * (0.70 * thickness)
        self.height[y0:y1, x0:x1] += hadd

    # ── rendering finale con illuminazione ───────────────────────────────────
    def render(self, light=(-0.40, -0.55, 0.82),
               relief: float = 0.9, ambient: float = 0.68,
               spec_strength: float = 0.08, shininess: float = 18.0
               ) -> Image.Image:
        """
        Pass di relief lighting: normali dal gradiente del height-field,
        diffusa + speculare Blinn-Phong, occlusione leggera nelle valli.
        Qui nasce l'effetto olio: la luce rivela impasto e trama.
        """
        h = blur(self.height, 1.5)
        gy, gx = np.gradient(h)
        nx = -gx * relief
        ny = -gy * relief
        nz = np.ones_like(h)
        inv = 1.0 / np.sqrt(nx * nx + ny * ny + 1.0)

        L = np.asarray(light, np.float32)
        L = L / np.linalg.norm(L)
        Hv = L + np.array([0, 0, 1], np.float32)
        Hv = Hv / np.linalg.norm(Hv)

        diff = np.clip((nx * L[0] + ny * L[1] + nz * L[2]) * inv, 0, 1)
        spec = np.clip((nx * Hv[0] + ny * Hv[1] + nz * Hv[2]) * inv, 0, 1)
        spec = spec ** shininess

        # il lucido cresce dove c'è pasta spessa (l'olio è più glossy)
        gloss = 0.45 + 0.55 * np.clip(h / max(h.max(), 1e-6), 0, 1)

        # occlusione: le valli fra i rilievi si scuriscono
        ao = np.clip((blur(h, 6) - h) * 0.55, 0, 0.6)

        out = (self.color * (ambient + (1 - ambient) * diff)[..., None]
               - (ao * 0.55)[..., None] * self.color
               + (spec * spec_strength * gloss)[..., None])
        out = np.clip(out, 0, 1)
        return Image.fromarray((out * 255).astype(np.uint8))


# ─── Composizione: riff → quadro ──────────────────────────────────────────────

class ZornOilPainting:
    """Campo ocra denso + 12 segni del riff, resi con il motore a impasto."""

    W, H = 1600, 1000
    PX_PER_BEAT = 240
    MARGIN = 110

    def __init__(self, seed: int = 42):
        random.seed(seed)
        # fondo: ocra gialla satura (Naples yellow caldo, come nel riferimento)
        bg = zorn_blend(ZORN['ochre'], ZORN['white'], 0.18)
        bg = zorn_blend(bg, (230, 180, 40), 0.30)   # shift verso giallo cadmio
        self.cv = OilCanvas(self.W, self.H, bg, seed)

    # coordinate musicali (come v6)
    def _tx(self, t: float) -> float:
        return self.MARGIN + t * self.PX_PER_BEAT

    def _ty(self, midi: int) -> float:
        nn = (midi - 40) / (80 - 40)
        return self.MARGIN + nn * (self.H - 2 * self.MARGIN)

    @staticmethod
    def _vel(v: str) -> float:
        return {'p': 0.62, 'mp': 0.80, 'mf': 1.0, 'f': 1.22, 'ff': 1.45}.get(v, 1.0)

    # ── ground: campo ocra a pennellate orizzontali ──────────────────────────
    def ground(self):
        base_cols = [
            zorn_blend(ZORN['ochre'], ZORN['white'], 0.16),
            ZORN['ochre'],
            ZORN['ochre'],
            zorn_blend(ZORN['ochre'], ZORN['black'], 0.11),
            zorn_blend(ZORN['ochre'], ZORN['vermilion'], 0.07),
        ]

        # Passata unica: larghissime e quasi opache (stesura piatta,
        # come un'imprimitura a olio su tavola liscia).
        y = -20.0
        while y < self.H + 20:
            x = random.uniform(-300, -80)
            while x < self.W + 50:
                L = random.uniform(350, 700)
                self.cv.stroke(
                    x=x, y=y + random.gauss(0, 6),
                    angle=random.gauss(0.0, 0.04),
                    length=L,
                    width=random.uniform(40, 70),
                    color=random.choice(base_cols),
                    opacity=random.uniform(0.55, 0.78),
                    thickness=random.uniform(0.12, 0.28),
                    curvature=random.gauss(0, 0.04),
                    dryness=random.uniform(0.55, 0.78),
                    smear=random.uniform(0.20, 0.38),
                    taper_end=random.uniform(0.50, 0.80),
                )
                x += L * random.uniform(0.65, 0.90)
            y += random.uniform(30, 46)

        # Accenti lievi di calore/luce (pochissimi, quasi invisibili)
        for col, count in [
            (zorn_blend(ZORN['ochre'], ZORN['white'],     0.30), 8),
            (zorn_blend(ZORN['ochre'], ZORN['vermilion'], 0.08), 6),
        ]:
            for _ in range(count):
                self.cv.stroke(
                    x=random.uniform(0, self.W),
                    y=random.uniform(0, self.H),
                    angle=random.gauss(0.0, 0.08),
                    length=random.uniform(120, 280),
                    width=random.uniform(18, 38),
                    color=col,
                    opacity=random.uniform(0.22, 0.44),
                    thickness=random.uniform(0.08, 0.18),
                    curvature=random.gauss(0, 0.10),
                    dryness=random.uniform(0.60, 0.85),
                    smear=random.uniform(0.25, 0.45),
                    taper_end=random.uniform(0.6, 0.92),
                )

    # ── segni del riff ────────────────────────────────────────────────────────
    # Ogni nota viene ripetuta N_REP volte con jitter di posizione/angolo.
    # Come un pittore che ritorna più volte sulla stessa zona costruendo impasto.
    _N_REP = 2        # pennellate per nota (piccole, non costruite a strati)
    _N_REP_PC = 4     # powerchord leggermente più presente
    _J_POS   = 3.5    # sigma jitter posizione (px)
    _J_ANG   = 0.04   # sigma jitter angolo (rad)

    def riff_marks(self, notes: List[Dict]):
        for i, nd in enumerate(notes):
            x0, y0 = nd['x_pos'], nd['y_pos']
            col = get_note_color(nd['note'], nd['velocity'])
            v = self._vel(nd['velocity'])
            dur = nd['duration']
            tech = nd['technique']

            # angolo verso la prossima nota (per il legato)
            if i + 1 < len(notes):
                ang_next = math.atan2(notes[i + 1]['y_pos'] - y0,
                                      notes[i + 1]['x_pos'] - x0)
            else:
                ang_next = 0.0

            n_rep = self._N_REP_PC if tech == 'powerchord' else self._N_REP
            print(f"  [{i+1:2d}/12] {nd['note']} {tech}  ×{n_rep}")

            for _rep in range(n_rep):
                # jitter posizione e angolo per ogni ripetizione
                x   = x0 + random.gauss(0, self._J_POS)
                y   = y0 + random.gauss(0, self._J_POS)
                aj  = random.gauss(0, self._J_ANG)

                if tech == 'staccato':
                    # dab ovale, carico (come i segni ovali scuri nel riferimento)
                    self.cv.stroke(x, y, math.radians(-30) + aj,
                                   68 * v, 30 * v, col,
                                   opacity=0.93, thickness=0.95,
                                   dryness=0.42, smear=0.08, taper_end=0.52)

                elif tech == 'legato':
                    # tratto morbido verso la nota seguente
                    self.cv.stroke(x, y, ang_next + aj,
                                   (175 + 95 * dur) * v, 26 * v, col,
                                   opacity=0.88, thickness=0.72,
                                   curvature=random.gauss(0, 0.14),
                                   dryness=0.45, smear=0.08, taper_end=0.70)

                elif tech == 'slide':
                    # tre parallele diagonali, centrale dominante
                    for off, opac, wd in [(-14, 0.66, 8),
                                           (  0, 0.90, 17),
                                           ( 14, 0.62, 7)]:
                        self.cv.stroke(x, y + off, math.radians(-15) + aj,
                                       165 * v, wd, col,
                                       opacity=opac, thickness=0.62,
                                       dryness=0.52, smear=0.06, taper_end=0.80)

                elif tech == 'hammer_on':
                    # stella di dab radiali
                    for adeg in (0, 60, 120, 180, 240, 300):
                        a = math.radians(adeg) + aj
                        self.cv.stroke(x + 10 * math.cos(a), y + 10 * math.sin(a),
                                       a, 44 * v, 16 * v, col,
                                       opacity=0.90, thickness=0.82,
                                       dryness=0.38, smear=0.06, taper_end=0.52)

                elif tech == 'bend':
                    # arco curvo, morbido
                    self.cv.stroke(x, y, math.radians(-35) + aj,
                                   142 * v, 28 * v, col,
                                   opacity=0.92, thickness=0.88,
                                   curvature=-1.20, dryness=0.36,
                                   smear=0.07, taper_end=0.60)

                elif tech == 'vibrato':
                    # onda sinusoidale
                    self.cv.stroke(x, y, aj,
                                   (155 + 88 * dur) * v, 23 * v, col,
                                   opacity=0.92, thickness=0.84,
                                   waviness=9.0, wave_freq=5.0,
                                   dryness=0.36, smear=0.07, taper_end=0.56)

                elif tech == 'powerchord':
                    # blocco dominante: tre lastre (il segno più grande)
                    for dyy, ww in [(-36, 32 * v), (0, 40 * v), (36, 32 * v)]:
                        self.cv.stroke(x - 18, y + dyy, aj,
                                       195 * v, ww, col,
                                       opacity=0.96, thickness=1.25,
                                       dryness=0.20, smear=0.06, taper_end=0.46)

                elif tech == 'tapping':
                    # 4 tratti a X, secchi
                    for adeg in (45, 135, 225, 315):
                        a = math.radians(adeg) + aj
                        self.cv.stroke(x + 8 * math.cos(a), y + 8 * math.sin(a),
                                       a, 48 * v, 14, col,
                                       opacity=0.90, thickness=0.88,
                                       dryness=0.40, smear=0.06, taper_end=0.56)

                elif tech == 'dive':
                    # curva discendente, leggera
                    self.cv.stroke(x, y, math.radians(8) + aj,
                                   195 * v, 25 * v, col,
                                   opacity=0.90, thickness=0.84,
                                   curvature=1.10, dryness=0.48,
                                   smear=0.07, taper_end=0.86)

                elif tech == 'harmonic_natural':
                    # tre tratti bianchi etereo
                    hcol = zorn_blend(ZORN['white'], ZORN['ochre'], 0.05)
                    for adeg in (30, 150, 270):
                        a = math.radians(adeg) + aj
                        self.cv.stroke(x + 16 * math.cos(a), y + 16 * math.sin(a),
                                       a, 72, 27, hcol,
                                       opacity=0.90, thickness=0.74,
                                       dryness=0.40, smear=0.06, taper_end=0.70)

                elif tech == 'harmonic_artificial':
                    # 4 scintille brevi
                    for adeg in (0, 90, 180, 270):
                        a = math.radians(adeg) + aj
                        self.cv.stroke(x + 7 * math.cos(a), y + 7 * math.sin(a),
                                       a, 34, 11, col,
                                       opacity=0.86, thickness=0.72,
                                       dryness=0.48, smear=0.06, taper_end=0.78)

    # ── dati riff ─────────────────────────────────────────────────────────────
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

    def create(self, out: str = 'johnny_b_goode_zorn_v7.png'):
        notes = self.parse_riff()
        print("Ground (campo ocra a impasto)...")
        self.ground()
        # Sfuma leggermente il buffer colore dopo il ground per ammorbidire
        # le striature delle pennellate del fondo (come una velatura finale
        # sull'imprimitura prima di iniziare a dipingere i segni).
        # due passaggi: uno trasversale + uno lungo per le striature orizzontali
        self.cv.color = blur(self.cv.color, 14.0)
        self.cv.color = np.clip(self.cv.color, 0, 1)
        print("Segni del riff...")
        self.riff_marks(notes)
        print("Relief lighting (diffusa + speculare + AO)...")
        img = self.cv.render()
        img.save(out, dpi=(150, 150))
        print(f"\nArtwork v7 salvato: {out}")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(
        description='guitarzorn v7 — olio reale con height-field e relief lighting')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--out', default='johnny_b_goode_zorn_v7.png')
    args = p.parse_args()
    ZornOilPainting(seed=args.seed).create(out=args.out)
