"""
guitarzorn v6 — Pittura dei Simboli dell'Algoritmo
===================================================
Ogni evento musicale del riff diventa un segno pittorico distinto
su un campo ocra denso. Non figurativo: l'algoritmo stesso è il soggetto.

Ground: campo orizzontale ocra — denso, materico, tela viva.
Segni: 12 marchi isolati, leggibili, ciascuno con vocabolario visivo
       specifico della tecnica (staccato=punto netto, vibrato=ondulazione,
       bend=arco, slide=diagonale, powerchord=blocco, ecc.)

Differenze chiave da v3/v4:
  — Ground molto più denso (≈70 pennellate orizzontali ocra) → campo pittorico
  — Segni molto più piccoli (0.30× la dimensione v3) → isolati, leggibili
  — Jitter minimo (σ=4px) → ogni segno sta esattamente al suo luogo
  — Repeat ridotto (2-3×) → segni distinti, non blob sovrapposti
  — Alpha piena per i segni (1.05×) → emergono sul fondo
  — Powerchord: unica eccezione, 5× repeat + taglia intera → climax visivo
"""

import importlib.util
import math
import os
import random
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw

# ── carica v3 come modulo (bristle engine) ────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "v3", os.path.join(_here, "zorn_riff_art_v3.py"))
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)

ZORN           = _v3.ZORN
zorn_blend     = _v3.zorn_blend
get_note_color = _v3.get_note_color
ZornBase       = _v3.ZornRiffBristlePainting


class ZornPitturaGrafica(ZornBase):
    """
    v6: i simboli pittorici dell'algoritmo musica→pittura.

    Architettura a due strati:
      Strato 1 (Ground): campo ocra orizzontale denso — la "tela" pittorica.
      Strato 2 (Segni):  12 marchi tecnica-specifici, piccoli e isolati.
    """

    # ── parametri dei segni ───────────────────────────────────────────────────
    _SZ_SCALE     = 0.38   # scala dimensione rispetto a v3 (segni piccoli)
    _SZ_MIN       = 5.0    # floor dimensione (px) — segni G/oro su ocra visibili
    _STEP_SCALE   = 0.45   # scala numero di steps
    _JITTER       = 4.0    # sigma jitter posizione (px)
    _REPEAT       = 3      # ripetizioni per traccia (base)
    _ALPHA_BOOST  = 1.10   # boost alpha segni → emergono sul ground

    def __init__(self, width: int = 1600, height: int = 1000, seed: int = 42):
        super().__init__(width, height, seed)

        # Spaziatura: 240px/battito → note distribuite su più canvas
        self.px_per_beat = 240
        self.margin      = 110

        # Background: ocra caldo puro (base del ground layer)
        bg = zorn_blend(ZORN['ochre'], ZORN['vermilion'], 0.04) + (255,)
        self.canvas = Image.new('RGBA', (width, height), bg)
        self.arr    = np.array(self.canvas)

    # ── dimensioni pennello (base per i segni) ───────────────────────────────
    @staticmethod
    def _vel_to_size(v: str) -> float:
        """Taglie leggermente più grandi di v3 per compensare il _SZ_SCALE."""
        return {'p': 10.0, 'mp': 15.0, 'mf': 21.0, 'f': 27.0, 'ff': 34.0}.get(v, 21.0)

    # ── ground layer ──────────────────────────────────────────────────────────

    def _ground_layer(self):
        """
        Campo ocra orizzontale denso — la base pittorica.

        ~70 pennellate quasi-orizzontali in varianti di ocra:
          ocra+bianco (chiaro), ocra puro, ocra+nero (scuro),
          ocra+vermiglione (caldo). Textura visibile, non piatta.
        Copre l'intera tela come un'imprimitura olio reale.
        """
        # Rumore di tela (texture canvas)
        arr = np.array(self.canvas)
        noise = np.random.normal(0, 9, arr.shape[:2] + (3,)).astype(int)
        arr[:, :, :3] = np.clip(arr[:, :, :3].astype(int) + noise, 0, 255).astype(np.uint8)
        self.canvas.paste(Image.fromarray(arr[:, :, :3].astype(np.uint8)).convert('RGBA'))
        self.arr[:] = np.array(self.canvas)

        # Configurazioni: (colore, n_stroke, sz_lo, sz_hi, a_lo, a_hi, ang_sigma)
        configs = [
            # Luce: ocra+bianco — pennellate più chiare in alto
            (zorn_blend(ZORN['ochre'], ZORN['white'],     0.16), 22, 15, 32, 0.62, 0.80, 0.11),
            # Base: ocra puro — corpo del ground
            (ZORN['ochre'],                                      18, 12, 26, 0.55, 0.72, 0.10),
            # Ombra: ocra+nero — profondità sotto le note gravi
            (zorn_blend(ZORN['ochre'], ZORN['black'],     0.12), 16, 10, 22, 0.46, 0.64, 0.14),
            # Accento: ocra+vermiglione — calore sparso
            (zorn_blend(ZORN['ochre'], ZORN['vermilion'], 0.06),  8,  8, 16, 0.32, 0.50, 0.16),
            # Velatura: bianco puro su punti alti — respiro luminoso
            (zorn_blend(ZORN['white'], ZORN['ochre'],     0.30),  6,  8, 14, 0.20, 0.38, 0.20),
        ]
        for col, n, sz_lo, sz_hi, a_lo, a_hi, ang_sig in configs:
            for _ in range(n):
                x    = random.uniform(-60, self.W + 60)
                y    = random.uniform(-60, self.H + 60)
                ang  = random.gauss(0.0, ang_sig)   # quasi-orizzontale
                size = random.uniform(sz_lo, sz_hi)
                n_st = max(130, int(random.uniform(170, 280)))
                alpha = random.uniform(a_lo, a_hi)
                self._paint_one(
                    np.array([x, y], dtype=float),
                    size, n_st, col, 'f',
                    ang=ang, alpha_scale=alpha)

    # ── pittura segni del riff ────────────────────────────────────────────────

    def paint_riff(self, notes: List[Dict]):
        """
        Dipinge i 12 segni pittorici del riff.

        Ogni nota genera il suo marchio tecnica-specifico tramite il sistema
        _build_traces di v3, scalato a dimensione ridotta per mantenere
        ogni segno leggibile e isolato sul ground.

        Powerchord (nota 9, climax): trattamento speciale — più repetizioni
        e dimensione maggiore per segnare il culmine del riff.
        """
        for idx, note in enumerate(notes):
            traces  = self._build_traces(note, notes, idx)
            base_sz = self._vel_to_size(note['velocity']) * self._SZ_SCALE
            color   = get_note_color(note['note'], note['velocity'])
            center  = np.array([note['x_pos'], note['y_pos']])
            tech    = note['technique']

            # Powerchord = climax visivo: più grande e più ripetuto
            if tech == 'powerchord':
                sz_mult = 0.88   # non scalato a 0.38 — taglia quasi piena
                n_rep   = 8
            else:
                sz_mult = self._SZ_SCALE
                n_rep   = self._REPEAT

            print(f"  [{idx+1:2d}/12] {note['note']} {tech:20s}  "
                  f"sz={base_sz:.1f}px  {len(traces)} tracce")

            for n_steps, ang, sm, asc, av, (dx, dy) in traces:
                for _ in range(n_rep):
                    jitter = np.array([
                        random.gauss(0, self._JITTER),
                        random.gauss(0, self._JITTER)])
                    start  = np.clip(
                        center + np.array([dx, dy]) + jitter,
                        [0.0, 0.0], [float(self.W), float(self.H)])

                    raw_sz = (self._vel_to_size(note['velocity']) * sz_mult
                              if tech == 'powerchord'
                              else base_sz)
                    size = max(self._SZ_MIN, raw_sz * sm)

                    n_st = max(12, int(n_steps * self._STEP_SCALE))

                    self._paint_one(
                        start, size, n_st, color, note['velocity'],
                        ang=ang + random.gauss(0, 0.07),
                        alpha_scale=asc * self._ALPHA_BOOST,
                        ang_vel=av)

    # ── entry point ───────────────────────────────────────────────────────────

    def create(self, out: str = 'johnny_b_goode_zorn_v6.png'):
        notes = self.parse_riff()

        print("Ground layer (campo ocra denso)...")
        self._ground_layer()

        print("Segni pittorici dell'algoritmo (12 note)...")
        self.paint_riff(notes)

        self.canvas.convert('RGB').save(out, dpi=(150, 150))
        print(f"\nArtwork v6 salvato: {out}")


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(
        description='guitarzorn v6 — i simboli pittorici dell\'algoritmo musica→pittura')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--out',  default='johnny_b_goode_zorn_v6.png')
    args = p.parse_args()

    ZornPitturaGrafica(seed=args.seed).create(out=args.out)
