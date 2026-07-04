"""
guitarzorn v8 — Olio Reale + Kubelka-Munk + Mapping v2
=======================================================
Evoluzione del motore v7 (Hertzmann height-field + relief lighting) con
le tre tecniche a maggior impatto del report Agente 1 e il mapping
raffinato v2 del report Agente 2.

PARTE A — motore:
  T1  Mixing Kubelka-Munk in spazio-concentrazione dei 4 pigmenti Zorn:
      il buffer colore è (H,W,4) concentrazioni [ocra, vermilion, nero,
      bianco]; il mixing (compositing, pickup, ricette) è lerp delle
      concentrazioni; l'RGB nasce solo in render() via KM single-constant.
      Il nero avorio ha una lieve dominante spettrale fredda (com'è il
      bone black reale): è ciò che fa nascere il "verde Zorn" da ocra+nero.
  T2  Aratura della pasta: il pennello raschia l'impasto esistente nel
      corpo del tratto e lo ridistribuisce in creste ai bordi (70%) e in
      coda (30%); rilascio finale a monticello scalato con (1-dryness).
  T5b Tela nel lighting: la trama tessuta affiora nel rilievo dove la
      pittura è sottile e sparisce sotto l'impasto:
          h = blur(height + weave*0.15*exp(-height/0.35), 1.5)

PARTE B — traslitterazione v2 (partitura canonica in score.py):
  pitch class → tinta | ottava → luminosità | MIDI → Y (acuto=ALTO)
  beat → X | durata → lunghezza (TUTTE le tecniche) | velocity → SOLO
  materia (width/thickness/opacity) | direzione melodica → angolo ±35°
  slide/bend/hammer proporzionali all'intervallo reale | double-stop
  bicolore wet-on-wet | shuffle forte/debole | barline a velatura |
  pausa = tela nuda.

Standalone: importa solo score.py, numpy, PIL.  Output 1920x1080, seed 42.
"""

import math
import random
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

from score import JOHNNY_B_GOODE_INTRO, BEATS_TOTAL, pitch_class, octave

# ═══════════════════════════════════════════════════════════════════════════
# T1 — Kubelka-Munk a 4 pigmenti Zorn
# ═══════════════════════════════════════════════════════════════════════════
# Masstone RGB dei 4 pigmenti (palette Zorn canonica del progetto).
PIG_RGB = np.array([
    [196, 164, 106],   # 0  ocra gialla
    [227,  66,  52],   # 1  vermilion
    [ 28,  28,  28],   # 2  nero avorio
    [242, 242, 242],   # 3  bianco titanio
], np.float32) / 255.0

# Riflettanza efficace per il calcolo K/S (clampata per stabilità).
_R_EFF = np.clip(PIG_RGB, 0.02, 0.98).copy()
# Correzione spettrale del nero avorio: un K/S a 3 canali derivato da un
# masstone perfettamente neutro non può produrre il verde Zorn (ocra+nero).
# Il bone black reale è leggermente freddo: riflette un filo più nel verde
# che nel rosso. Bias minimo, il masstone resta un nero (≈ 26,31,28).
_R_EFF[2] = [0.100, 0.120, 0.110]

_EPS = 1e-4
KS_PIG = ((1.0 - _R_EFF) ** 2 / (2.0 * _R_EFF + _EPS)).astype(np.float32)  # (4,3)


def km_rgb(conc: np.ndarray) -> np.ndarray:
    """Concentrazioni (...,4) → riflettanza RGB (...,3) via KM single-constant."""
    ks = conc @ KS_PIG
    return np.clip(1.0 + ks - np.sqrt(ks * ks + 2.0 * ks), 0.0, 1.0)


# vettori-concentrazione dei pigmenti puri
OCHRE = np.array([1, 0, 0, 0], np.float32)
VERM  = np.array([0, 1, 0, 0], np.float32)
BLACK = np.array([0, 0, 1, 0], np.float32)
WHITE = np.array([0, 0, 0, 1], np.float32)


def mixc(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    """Mixing di due ricette = lerp delle concentrazioni (il KM fa il resto)."""
    return (a * (1.0 - t) + b * t).astype(np.float32)


# Ricette colore per pitch class (mapping v2).
# Nota: nel KM il vermiglio domina i mix con l'ocra (K/S alto in G,B), quindi
# i pesi sono riequilibrati per centrare i target percettivi del report
# (C = raw sienna terroso, G = oro ambrato distinto da C).
NOTE_CONC: Dict[str, np.ndarray] = {
    'A':  VERM.copy(),                       # vermiglio pieno (tonica)
    'C':  mixc(OCHRE, VERM, 0.38),           # raw sienna (ocra+verm 62/38)
    'D':  BLACK.copy(),                      # nero avorio
    'E':  WHITE.copy(),                      # bianco titanio
    'G':  mixc(OCHRE, VERM, 0.22),           # oro ambrato ("ocra+verm ~55/45" percettivo)
    'Bb': mixc(VERM, BLACK, 0.40),           # esterna: bruno rosso profondo
    'B':  mixc(VERM, WHITE, 0.45),           # esterna: rosa salmone
    'F':  mixc(WHITE, BLACK, 0.45),          # esterna: grigio
}


def note_conc(midi: int) -> np.ndarray:
    """Ricetta della nota: tinta da pitch class + luminosità da ottava.

    C# (nota di passaggio dell'hammer) = ricetta di C con un tocco di
    bianco in più (passaggio brillante b3→3).
    Ottava: ±0.12 di concentrazione bianco/nero per ottava dalla 4.
    """
    if midi % 12 == 1:                                   # C#
        base = mixc(NOTE_CONC['C'], WHITE, 0.18)
    else:
        base = NOTE_CONC[pitch_class(midi)]
    t = 0.12 * (octave(midi) - 4)
    t = max(-0.36, min(0.36, t))
    if t > 0:
        return mixc(base, WHITE, t)
    if t < 0:
        return mixc(base, BLACK, -t)
    return base.copy()


# velocity → SOLO materia (mapping v2 #6): niente shift di luminosità.
VEL_WIDTH = {'p': 14, 'mp': 20, 'mf': 26, 'f': 34, 'ff': 42}
VEL_THICK = {'p': 0.40, 'mp': 0.62, 'mf': 0.85, 'f': 1.07, 'ff': 1.30}
VEL_OPAC  = {'p': 0.72, 'mp': 0.78, 'mf': 0.84, 'f': 0.90, 'ff': 0.96}

# durata → lunghezza: fattore per tecnica (mapping v2 #5)
K_TECH = {'legato': 0.85, 'vibrato': 0.85,
          'staccato': 0.55, 'double_stop': 0.55,
          'slide': 1.0, 'bend': 1.0, 'hammer_on': 0.70,
          'double_stop_final': 1.0}

MAX_ANG = math.radians(35.0)     # clamp dell'angolo melodico


# ═══════════════════════════════════════════════════════════════════════════
# utilità numpy (invariata da v7)
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# Tela a olio: concentrazioni KM (H,W,4) + height field
# ═══════════════════════════════════════════════════════════════════════════

class OilCanvas:
    """
    Tela con doppio buffer: concentrazioni pigmento (float, somma≈1) e
    altezza (impasto). Il colore RGB nasce solo in render() via KM.
    """

    def __init__(self, W: int, H: int, base_conc: np.ndarray, seed: int = 42):
        self.W, self.H = W, H
        self.rng = np.random.default_rng(seed)

        self.conc = np.empty((H, W, 4), np.float32)
        self.conc[:] = base_conc

        # ── trama tessuta — sottile ma pronta ad affiorare nel lighting (T5b)
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
        self.height = np.zeros((H, W), np.float32)

        # mottling anisotropico in spazio-concentrazione: larghe variazioni
        # orizzontali di luminosità (verso bianco / verso ocra scura)
        mx = blur(self.rng.standard_normal((H, W)).astype(np.float32), 90)
        my = _box(mx, 4, 0)
        my /= max(np.abs(my).max(), 1e-6)
        t = my * 0.035
        pos = np.clip(t, 0, None)[..., None]
        neg = np.clip(-t, 0, None)[..., None]
        dark = mixc(OCHRE, BLACK, 0.05)
        self.conc = (self.conc * (1.0 - pos - neg)
                     + WHITE[None, None, :] * pos
                     + dark[None, None, :] * neg)
        self.conc = np.clip(self.conc, 0, 1)

    # ── pennellata ────────────────────────────────────────────────────────
    def stroke(self, x: float, y: float, angle: float,
               length: float, width: float, conc,
               opacity: float = 0.92, thickness: float = 1.0,
               curvature: float = 0.0, waviness: float = 0.0,
               wave_freq: float = 4.0, dryness: float = 0.35,
               smear: float = 0.40, taper_end: float = 0.55):
        """
        Deposita una pennellata su concentrazioni + altezza, arando la
        pasta esistente (T2).

        conc — vettore (4,) di concentrazioni pigmenti [ocra,verm,nero,bianco].
        Gli altri parametri come v7.
        """
        rng = self.rng
        col = np.asarray(conc, np.float32)

        # ── traiettoria (1 px per step) ─────────────────────────────────
        n = max(8, int(length))
        ts = np.linspace(0.0, 1.0, n).astype(np.float32)
        ang = (angle + curvature * ts
               + snoise1(rng, n, 30) * 0.045)          # tremolio della mano
        dx, dy = np.cos(ang), np.sin(ang)
        px = x + np.cumsum(dx) - dx[0]
        py = y + np.cumsum(dy) - dy[0]
        if waviness > 0:
            osc = np.sin(ts * 2 * np.pi * wave_freq) * waviness
            px += -dy * osc
            py += dx * osc
        nx, ny = -dy, dx                                # normali al tratto

        # ── profilo larghezza lungo t (attacco + rilascio) ──────────────
        attack = np.minimum(1.0, ts / 0.06) ** 0.6
        release = 1.0 - taper_end * np.clip((ts - 0.72) / 0.28, 0, 1) ** 1.6
        wt = width * attack * release                   # (n,)

        # ── profilo setole attraverso s ─────────────────────────────────
        nS = max(7, int(width * 1.7))
        s = np.linspace(-1.0, 1.0, nS).astype(np.float32)
        load = rng.random(nS).astype(np.float32)
        k = np.array([0.25, 0.5, 0.25], np.float32)
        load = np.convolve(np.pad(load, 1, mode='edge'), k, 'valid')
        bristle = 0.45 + 0.55 * load                    # carico per-setola
        edge = np.clip((1.0 - np.abs(s)) * 3.0, 0, 1) ** 0.65

        # ── esaurimento pigmento + striature ────────────────────────────
        dep = (1.0 - 0.62 * ts ** 1.25) * (0.85 + 0.30 * snoise1(rng, n, 18))
        dep = np.clip(dep, 0.05, 1.4)
        streak = 1.0 + 0.30 * snoise2(rng, n, nS, 16, 1.6)
        D = dep[:, None] * bristle[None, :] * np.clip(streak, 0.2, 2.0)
        A = np.clip(D, 0, 1.25) * edge[None, :]         # (n, nS) alpha grezza

        # ── smearing: pickup delle CONCENTRAZIONI sottostanti (EMA) ─────
        cx = np.clip(px.astype(int), 0, self.W - 1)
        cy = np.clip(py.astype(int), 0, self.H - 1)
        under = self.conc[cy, cx]                       # (n,4)
        carried = np.empty_like(under)
        carried[0] = under[0]
        kp = 0.03
        for i in range(1, n):
            carried[i] = carried[i - 1] * (1 - kp) + under[i] * kp
        m = (smear * (0.25 + 0.6 * ts))[:, None]
        pc = col[None, :] * (1 - m) + carried * m       # (n,4) conc depositata

        # ── campionamento del nastro ────────────────────────────────────
        S = s[None, :] * (wt[:, None] * 0.5)
        X = px[:, None] + nx[:, None] * S
        Y = py[:, None] + ny[:, None] * S
        xi = np.round(X).astype(int).ravel()
        yi = np.round(Y).astype(int).ravel()
        a = A.ravel()
        pcol = np.repeat(pc, nS, axis=0)
        d = D.ravel()
        tsf = np.repeat(ts, nS)                         # ts per campione

        ok = (xi >= 0) & (xi < self.W) & (yi >= 0) & (yi < self.H) & (a > 0.01)
        if not np.any(ok):
            return
        xi, yi, a, d, tsf = xi[ok], yi[ok], a[ok], d[ok], tsf[ok]
        pcol = pcol[ok]

        # ── dry-brush: la coda scarica aggrappa solo la trama ───────────
        need = np.clip((dryness * 1.15 - d) / max(dryness, 1e-3), 0, 1)
        gate = np.clip((self.weave[yi, xi] + (1.0 - need) - 0.82) / 0.22, 0, 1)
        a = a * (0.12 + 0.88 * gate) * opacity

        # ── bbox locale (con bordo per le creste dell'aratura) ──────────
        pad = 6
        x0 = max(0, xi.min() - pad); x1 = min(self.W, xi.max() + 1 + pad)
        y0 = max(0, yi.min() - pad); y1 = min(self.H, yi.max() + 1 + pad)
        lw, lh = x1 - x0, y1 - y0
        lx, ly = xi - x0, yi - y0

        wsum = np.zeros((lh, lw), np.float32)
        csum = np.zeros((lh, lw, 4), np.float32)
        hsum = np.zeros((lh, lw), np.float32)
        np.add.at(wsum, (ly, lx), a)
        np.add.at(csum, (ly, lx), pcol * a[:, None])
        # rilascio finale: monticello dove ts→1, scalato con (1-dryness)
        rel = np.clip((tsf - 0.80) / 0.20, 0, 1) ** 1.6
        np.add.at(hsum, (ly, lx), a * (d + rel * 0.55 * (1.0 - dryness)))

        # ── T2: aratura — il pennello raschia la pasta esistente ────────
        Hroi = self.height[y0:y1, x0:x1]
        body = wsum > 0.15
        if np.any(body):
            plow = np.where(body, Hroi, 0.0).astype(np.float32) \
                * (0.35 * thickness)
            Hroi -= plow
            removed = float(plow.sum())
            if removed > 1e-5:
                bodyf = body.astype(np.float32)
                dil = blur(bodyf, 2)                    # dilatazione morbida
                ridge = dil * (1.0 - bodyf)             # solo fuori dal corpo
                rs = float(ridge.sum())
                if rs > 1e-6:                            # ~70% in creste laterali
                    Hroi += ridge * (removed * 0.70 / rs)
                tail = np.zeros_like(wsum)               # ~30% in coda
                np.add.at(tail, (ly, lx),
                          a * np.clip((tsf - 0.65) / 0.35, 0, 1) ** 2)
                tsum = float(tail.sum())
                if tsum > 1e-6:
                    Hroi += tail * (removed * 0.30 / tsum)
            np.clip(Hroi, 0, None, out=Hroi)

        # ── compositing concentrazioni ──────────────────────────────────
        nz = wsum > 1e-4
        Aeff = np.clip(wsum, 0, 0.94)
        mean_col = np.zeros_like(csum)
        mean_col[nz] = csum[nz] / wsum[nz, None]

        roi = self.conc[y0:y1, x0:x1]
        roi[nz] = roi[nz] * (1 - Aeff[nz, None]) + mean_col[nz] * Aeff[nz, None]

        # impasto: deposito d'altezza (dopo l'aratura)
        hadd = blur(np.clip(hsum, 0, 1.9), 1) * (0.70 * thickness)
        Hroi += hadd

    # ── rendering finale con illuminazione ──────────────────────────────
    def render(self, light=(-0.40, -0.55, 0.82),
               relief: float = 0.9, ambient: float = 0.68,
               spec_strength: float = 0.08, shininess: float = 18.0
               ) -> Image.Image:
        """
        Relief lighting su un height-field che include la trama della tela
        dove la pittura è sottile (T5b) — il colore nasce qui dal KM (T1).
        """
        color = km_rgb(np.clip(self.conc, 0, None))

        # T5b: la trama affiora nelle velature, sparisce sotto l'impasto
        h = blur(self.height
                 + self.weave * 0.15 * np.exp(-self.height / 0.35), 1.5)
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

        gloss = 0.45 + 0.55 * np.clip(h / max(h.max(), 1e-6), 0, 1)
        ao = np.clip((blur(h, 6) - h) * 0.55, 0, 0.6)

        out = (color * (ambient + (1 - ambient) * diff)[..., None]
               - (ao * 0.55)[..., None] * color
               + (spec * spec_strength * gloss)[..., None])
        out = np.clip(out, 0, 1)
        return Image.fromarray((out * 255).astype(np.uint8))


# ═══════════════════════════════════════════════════════════════════════════
# Composizione: partitura → quadro (mapping v2)
# ═══════════════════════════════════════════════════════════════════════════

class ZornOilPaintingV8:
    W, H = 1920, 1080
    MARGIN = 120

    _N_REP = 2          # pennellate per nota (mano che ritorna)
    _J_POS = 3.5        # sigma jitter posizione (px)
    _J_ANG = 0.04       # sigma jitter angolo (rad)

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.ppb = (self.W - 2 * self.MARGIN) / BEATS_TOTAL   # px per beat

        # range dinamico Y: [min_midi-3, max_midi+3] sulla partitura
        midis = []
        for e in JOHNNY_B_GOODE_INTRO:
            midis += e.get('dyad') or [e['midi']]
            if 'slide_to' in e:
                midis.append(e['slide_to'])
            if 'hammer_to' in e:
                midis.append(e['hammer_to'])
            if 'bend' in e:
                midis.append(e['midi'] + e['bend'])
        self.midi_lo = min(midis) - 3
        self.midi_hi = max(midis) + 3
        self.semipx = (self.H - 2 * self.MARGIN) / (self.midi_hi - self.midi_lo)

        # fondo: Naples yellow caldo in concentrazioni (ocra + bianco
        # + un soffio di vermiglio per il calore dorato del v7)
        bg = mixc(mixc(OCHRE, WHITE, 0.35), VERM, 0.012)
        self.cv = OilCanvas(self.W, self.H, bg, seed)

    # ── coordinate musicali ─────────────────────────────────────────────
    def _tx(self, t: float) -> float:
        return self.MARGIN + t * self.ppb

    def _ty(self, midi: float) -> float:
        nn = (midi - self.midi_lo) / (self.midi_hi - self.midi_lo)
        return self.H - self.MARGIN - nn * (self.H - 2 * self.MARGIN)  # acuto=ALTO

    @staticmethod
    def _clamp_ang(a: float) -> float:
        return max(-MAX_ANG, min(MAX_ANG, a))

    @staticmethod
    def _dry(t: float) -> float:
        """Downbeat = pennello carico, levare = più secco."""
        return 0.28 if (t % 1.0) < 0.05 else 0.52

    @staticmethod
    def _shuffle_w(t: float) -> float:
        """Alternanza deterministica ottavo forte/debole."""
        return 1.15 if (t % 1.0) < 0.5 else 0.85

    # ── ground: campo ocra liscio (stile v7, in concentrazioni) ────────
    # NB: nel KM nero e vermiglio hanno un potere tingente enorme —
    # le percentuali v7 (11% nero) qui vanno divise per ~4, altrimenti
    # l'imprimitura si copre di blotch oliva.
    def ground(self):
        base_cols = [
            mixc(OCHRE, WHITE, 0.16),
            OCHRE, OCHRE,
            mixc(OCHRE, BLACK, 0.022),
            mixc(OCHRE, VERM, 0.030),
        ]
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
                    conc=random.choice(base_cols),
                    opacity=random.uniform(0.55, 0.78),
                    thickness=random.uniform(0.12, 0.28),
                    curvature=random.gauss(0, 0.04),
                    dryness=random.uniform(0.55, 0.78),
                    smear=random.uniform(0.20, 0.38),
                    taper_end=random.uniform(0.50, 0.80),
                )
                x += L * random.uniform(0.65, 0.90)
            y += random.uniform(30, 46)

        # accenti lievi di calore/luce
        for col, count in [(mixc(OCHRE, WHITE, 0.30), 8),
                           (mixc(OCHRE, VERM, 0.035), 6)]:
            for _ in range(count):
                self.cv.stroke(
                    x=random.uniform(0, self.W),
                    y=random.uniform(0, self.H),
                    angle=random.gauss(0.0, 0.08),
                    length=random.uniform(120, 280),
                    width=random.uniform(18, 38),
                    conc=col,
                    opacity=random.uniform(0.22, 0.44),
                    thickness=random.uniform(0.08, 0.18),
                    curvature=random.gauss(0, 0.10),
                    dryness=random.uniform(0.60, 0.85),
                    smear=random.uniform(0.25, 0.45),
                    taper_end=random.uniform(0.6, 0.92),
                )

    # ── barline: velatura verticale quasi invisibile a t=4,8,12 ────────
    def barlines(self):
        col = mixc(OCHRE, BLACK, 0.10)
        for t in (4.0, 8.0, 12.0):
            x = self._tx(t)
            self.cv.stroke(
                x=x + random.gauss(0, 2), y=self.MARGIN * 0.8,
                angle=math.pi / 2 + random.gauss(0, 0.01),
                length=self.H - 1.6 * self.MARGIN,
                width=9,
                conc=col,
                opacity=0.07, thickness=0.04,
                dryness=0.75, smear=0.25, taper_end=0.35,
            )

    # ── segni del riff (mapping v2) ─────────────────────────────────────
    def riff_marks(self):
        evs = JOHNNY_B_GOODE_INTRO
        centers = []
        for e in evs:
            notes = e.get('dyad') or [e['midi']]
            mm = sum(notes) / len(notes)
            centers.append((self._tx(e['t']), self._ty(mm)))

        for i, e in enumerate(evs):
            tech = e['tech']
            t, d, vel = e['t'], e['d'], e['vel']
            x0, y0 = centers[i]
            sw = self._shuffle_w(t)                       # shuffle forte/debole
            width = VEL_WIDTH[vel] * sw
            thick = VEL_THICK[vel]
            opac = VEL_OPAC[vel]
            dry = self._dry(t)
            k = K_TECH.get(tech, 0.85)
            length = max(d * self.ppb * k, width * 1.05)

            # angolo = direzione melodica verso la nota successiva
            if i + 1 < len(evs):
                nx_, ny_ = centers[i + 1]
                dir_ang = self._clamp_ang(math.atan2(ny_ - y0, nx_ - x0))
            else:
                dir_ang = 0.0

            names = '+'.join(pitch_class(m) for m in (e.get('dyad') or [e['midi']]))
            print(f"  [{i+1:2d}/{len(evs)}] t={t:6.3f}  {names:5s} {tech}")

            for _rep in range(self._N_REP):
                x = x0 + random.gauss(0, self._J_POS)
                y = y0 + random.gauss(0, self._J_POS)
                aj = random.gauss(0, self._J_ANG)

                if tech == 'staccato':
                    conc = note_conc(e['midi'])
                    self.cv.stroke(x, y, math.radians(-30) + aj,
                                   length, width, conc,
                                   opacity=opac, thickness=thick,
                                   dryness=dry, smear=0.08, taper_end=0.52)

                elif tech == 'legato':
                    conc = note_conc(e['midi'])
                    self.cv.stroke(x, y, dir_ang + aj,
                                   length, width, conc,
                                   opacity=opac, thickness=thick,
                                   curvature=random.gauss(0, 0.10),
                                   dryness=dry, smear=0.10, taper_end=0.70)

                elif tech == 'slide':
                    # ESATTAMENTE dal (x,y) della nota al y del slide_to
                    conc = note_conc(e['midi'])
                    ty1 = self._ty(e['slide_to'])
                    run = d * self.ppb
                    s_ang = math.atan2(ty1 - y0, run)
                    s_len = math.hypot(run, ty1 - y0)
                    nxp, nyp = -math.sin(s_ang), math.cos(s_ang)
                    for off, om, wf in [(-0.55, 0.72, 0.34),
                                        (0.0, 1.0, 0.70),
                                        (0.55, 0.68, 0.30)]:
                        self.cv.stroke(x + nxp * off * width,
                                       y + nyp * off * width,
                                       s_ang + aj,
                                       s_len, width * wf, conc,
                                       opacity=opac * om, thickness=thick * 0.8,
                                       dryness=dry + 0.10, smear=0.06,
                                       taper_end=0.72)

                elif tech == 'bend':
                    # curvatura ∝ semitoni; il tratto si alza di bend*semipx
                    conc = note_conc(e['midi'])
                    semi = e['bend']
                    rise = semi * self.semipx
                    blen = max(length, rise * 1.55, 60.0)
                    curv = -0.65 * semi                    # 2 semitoni → -1.3
                    mean = math.asin(max(-0.95, min(0.95, -rise / blen)))
                    a0 = mean - curv / 2
                    self.cv.stroke(x, y, a0 + aj,
                                   blen, width * 0.82, conc,
                                   opacity=opac, thickness=thick,
                                   curvature=curv, dryness=dry,
                                   smear=0.07, taper_end=0.60)

                elif tech == 'hammer_on':
                    # dab sulla nota + tratto verso hammer_to
                    conc = note_conc(e['midi'])
                    self.cv.stroke(x, y, math.radians(-30) + aj,
                                   width * 1.3, width * 0.9, conc,
                                   opacity=opac, thickness=thick,
                                   dryness=dry, smear=0.06, taper_end=0.50)
                    ty1 = self._ty(e['hammer_to'])
                    run = d * self.ppb
                    h_ang = math.atan2(ty1 - y0, run)
                    h_len = math.hypot(run, ty1 - y0)
                    conc2 = note_conc(e['hammer_to'])
                    self.cv.stroke(x, y, h_ang + aj,
                                   h_len, width * 0.7, conc2,
                                   opacity=opac * 0.92, thickness=thick * 0.8,
                                   dryness=dry + 0.08, smear=0.10,
                                   taper_end=0.70)

                elif tech == 'vibrato':
                    conc = note_conc(e['midi'])
                    self.cv.stroke(x, y, dir_ang + aj,
                                   length, width, conc,
                                   opacity=opac, thickness=thick,
                                   waviness=9.0, wave_freq=5.0,
                                   dryness=dry, smear=0.07, taper_end=0.56)

                elif tech in ('double_stop', 'double_stop_final'):
                    # DUE pennellate, una per nota del dyad, ciascuna al suo
                    # Y col suo colore; la superiore wet-on-wet (smear 0.5)
                    lo_m, hi_m = e['dyad']
                    final = (tech == 'double_stop_final')
                    wav = 8.0 if final else 0.0
                    thk = 1.30 if final else thick
                    for j, (m_, sm) in enumerate([(lo_m, 0.10), (hi_m, 0.50)]):
                        conc = note_conc(m_)
                        ym = self._ty(m_) + (y - y0)
                        self.cv.stroke(x, ym, math.radians(-30) + aj,
                                       length, width, conc,
                                       opacity=opac, thickness=thk,
                                       waviness=wav, wave_freq=4.0,
                                       dryness=dry, smear=sm,
                                       taper_end=0.52 if not final else 0.60)

    # ── creazione ───────────────────────────────────────────────────────
    def create(self, out: str = 'johnny_b_goode_zorn_v8.png'):
        # sanity check T1: il "verde Zorn" (ocra+nero 50/50)
        zg = km_rgb(mixc(OCHRE, BLACK, 0.5)[None, :])[0] * 255
        print(f"Sanity KM — verde Zorn (ocra+nero 50/50): "
              f"RGB=({zg[0]:.0f}, {zg[1]:.0f}, {zg[2]:.0f})  "
              f"[atteso: verde oliva scuro, G>R>B]")
        for nm in ('A', 'C', 'D', 'E', 'G'):
            c = km_rgb(NOTE_CONC[nm][None, :])[0] * 255
            print(f"  masstone {nm}: RGB=({c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f})")

        print("Ground (campo ocra a impasto, concentrazioni KM)...")
        self.ground()
        # velatura di ammorbidimento sull'imprimitura (come v7)
        self.cv.conc = np.clip(blur(self.cv.conc, 14.0), 0, 1)
        print("Barline (velature verticali)...")
        self.barlines()
        print("Segni del riff (mapping v2)...")
        self.riff_marks()
        print("Relief lighting (KM → RGB, tela nel rilievo)...")
        img = self.cv.render()
        img.save(out, dpi=(150, 150))
        print(f"\nArtwork v8 salvato: {out}")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(
        description='guitarzorn v8 — KM 4 pigmenti + aratura + mapping v2')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--out', default='johnny_b_goode_zorn_v8.png')
    args = p.parse_args()
    ZornOilPaintingV8(seed=args.seed).create(out=args.out)
