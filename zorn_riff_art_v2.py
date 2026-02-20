"""
Guitarzorn v2 – Traslitterazione riff chitarra → quadro pittorico Zorn
======================================================================
Miglioramenti rispetto alla v1:
  • bristle_line()    – pennellata con crini di pennello simulati
  • tapered_bezier()  – Bézier con spessore variabile (tapered stroke)
  • impasto_blob()    – colpo spesso con highlight/ombra Zorn
  • add_ground_layer()– preparazione della tela con pennellate di fondo
  • pitch → luminosità (ottava bassa = +nero, ottava alta = +bianco)
  • velocity → alpha + spessore + scala impasto (non solo lw)
  • Dive: colore che scurisce progressivamente (vermilion → black)
  • Harmonic natural: alone etereo multistrato
  • Pinch harmonic: scintille a 8 raggi
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle
from matplotlib.path import Path
import numpy as np
import random
from typing import List, Dict, Tuple, Optional


class ZornGuitarRiffArt:
    """
    Pipeline: dati riff chitarra → canvas pittorico con palette Zorn 4 colori.
    """

    def __init__(self, seed: int = 42):
        # ── Palette Zorn (4 soli colori) ──────────────────────────────────
        self.colors = {
            'ochre':     np.array([196, 164, 106]) / 255.0,  # Yellow Ochre
            'vermilion': np.array([227,  66,  52]) / 255.0,  # Vermilion
            'black':     np.array([ 28,  28,  28]) / 255.0,  # Ivory Black
            'white':     np.array([242, 242, 242]) / 255.0,  # Titanium White
        }

        # ── Mapping pentatonica minore La → colori Zorn ───────────────────
        self.note_colors = {
            'A': 'ochre',      # Tonica
            'C': 'vermilion',  # Terza minore
            'D': 'black',      # Quarta
            'E': 'white',      # Quinta
            'G': None,         # blend ochre+black  (settima minore)
        }

        self.px_per_beat = 140
        self.margin      = 80
        self.width       = 1600
        self.height      = 1000

        self.fig, self.ax = plt.subplots(
            figsize=(self.width / 150, self.height / 150), dpi=150
        )
        bg = self.colors['ochre']
        self.fig.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.axis('off')

        random.seed(seed)
        np.random.seed(seed)

    # ═══════════════════════ coordinate helpers ═══════════════════════════

    def time_to_x(self, t: float) -> float:
        return self.margin + t * self.px_per_beat

    def pitch_to_y(self, midi: int) -> float:
        n = (midi - 40) / (80 - 40)
        return self.margin + n * (self.height - 2 * self.margin)

    # ═══════════════════════ colour helpers ═══════════════════════════════

    def get_note_color(self, note: str, midi_pitch: int = 60) -> np.ndarray:
        """
        Colore base dalla mappa Zorn, poi corretto per ottava:
          - registro grave  → blend con ivory black  (fino al 20 %)
          - registro acuto  → blend con titanium white (fino al 25 %)
        Rispetta rigorosamente la palette Zorn: nessun colore extra.
        """
        if note == 'G':
            base = (self.colors['ochre'] + self.colors['black']) / 2.0
        else:
            base = self.colors[self.note_colors.get(note, 'ochre')]

        brightness = (midi_pitch - 40) / (80 - 40)   # [0 .. 1]
        if brightness > 0.5:
            t = (brightness - 0.5) * 0.5              # max 25 % bianco
            color = base * (1 - t) + self.colors['white'] * t
        else:
            t = (0.5 - brightness) * 0.4              # max 20 % nero
            color = base * (1 - t) + self.colors['black'] * t

        return np.clip(color, 0.0, 1.0)

    def velocity_to_params(self, velocity: str) -> Tuple[float, float, float]:
        """
        Ritorna (lw_base, alpha, impasto_scale).
        Dinamica → spessore + opacità + rilievo impasto.
        """
        table = {
            'p':  (1.5, 0.42, 0.45),
            'mp': (2.5, 0.60, 0.65),
            'mf': (4.0, 0.75, 0.85),
            'f':  (6.5, 0.88, 1.00),
            'ff': (9.0, 0.95, 1.25),
        }
        return table.get(velocity, (4.0, 0.75, 0.85))

    # ═══════════════════════ pennellate primitive ═════════════════════════

    def bristle_line(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        color: np.ndarray,
        lw: float,
        alpha: float,
        n_bristles: int = 0,
    ):
        """
        Pennellata con simulazione crini di pennello.
        Traccia N micro-filamenti paralleli leggermente sfasati, ognuno con
        spessore e opacità leggermente variabili → effetto pennellata reale.
        """
        dx, dy = x2 - x1, y2 - y1
        length = max(np.sqrt(dx ** 2 + dy ** 2), 1e-6)
        px, py = -dy / length, dx / length      # vettore perpendicolare

        if n_bristles == 0:
            n_bristles = max(4, int(lw * 1.8))

        for i in range(n_bristles):
            t = (i / (n_bristles - 1) - 0.5) if n_bristles > 1 else 0.0
            offset = t * lw * 0.55

            # Piccolo jitter sui due estremi del filamento
            j1x, j1y = random.gauss(0, 0.4), random.gauss(0, 0.4)
            j2x, j2y = random.gauss(0, 0.4), random.gauss(0, 0.4)

            bx1 = x1 + px * offset + j1x
            by1 = y1 + py * offset + j1y
            bx2 = x2 + px * offset + j2x
            by2 = y2 + py * offset + j2y

            bristle_lw    = lw * random.uniform(0.35, 0.90) / max(n_bristles, 1) * 3.2
            bristle_alpha = alpha * random.uniform(0.60, 1.00)

            self.ax.plot(
                [bx1, bx2], [by1, by2],
                color=color,
                alpha=bristle_alpha,
                lw=bristle_lw,
                solid_capstyle='round',
                solid_joinstyle='round',
            )

    def tapered_bezier(
        self,
        pts: List[Tuple[float, float]],
        color: np.ndarray,
        lw_start: float,
        lw_end: float,
        alpha: float,
        n_segments: int = 32,
    ):
        """
        Bézier quadratica con spessore variabile (tapered stroke):
        simula la pennellata che parte larga e termina fine, o viceversa.
        Ogni micro-segmento ha un lw interpolato e lieve jitter di alpha.
        """
        if len(pts) < 3:
            return
        p0, ctrl, p2 = (np.array(p) for p in pts)

        ts = np.linspace(0, 1, n_segments + 1)

        def bq(t):
            return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * ctrl + t ** 2 * p2

        points = [bq(t) for t in ts]
        for k in range(n_segments):
            t_mid = (ts[k] + ts[k + 1]) / 2
            lw_k  = lw_start + (lw_end - lw_start) * t_mid
            seg_alpha = alpha * random.uniform(0.82, 1.00)
            self.ax.plot(
                [points[k][0], points[k + 1][0]],
                [points[k][1], points[k + 1][1]],
                color=color,
                lw=lw_k,
                alpha=seg_alpha,
                solid_capstyle='round',
                solid_joinstyle='round',
            )

    def impasto_blob(
        self,
        x: float, y: float,
        radius: float,
        color: np.ndarray,
        alpha: float,
    ):
        """
        Macchia di colore spesso (impasto):
          corpo principale + highlight bianco Zorn (luce sul pigmento rialzato)
          + ombra nera Zorn (profondità sotto il rilievo).
        """
        # Corpo
        self.ax.add_patch(Circle(
            (x, y), radius,
            facecolor=color, alpha=alpha, edgecolor='none'
        ))
        # Highlight (Titanium White, in alto a sinistra)
        hl_color = np.clip(color * 0.35 + self.colors['white'] * 0.65, 0, 1)
        hl_r = radius * 0.38
        self.ax.add_patch(Circle(
            (x - radius * 0.22, y + radius * 0.22), hl_r,
            facecolor=hl_color, alpha=alpha * 0.52, edgecolor='none'
        ))
        # Ombra (Ivory Black, in basso a destra)
        sh_color = np.clip(color * 0.45 + self.colors['black'] * 0.55, 0, 1)
        self.ax.add_patch(Circle(
            (x + radius * 0.18, y - radius * 0.18), hl_r * 0.75,
            facecolor=sh_color, alpha=alpha * 0.38, edgecolor='none'
        ))

    # ═══════════════════════ tecniche chitarristiche ══════════════════════

    def draw_staccato(self, note: Dict):
        """
        Staccato – impasto blob: pennellino secco, colpo puntuale.
        Alta dinamica → rilievo impasto più pronunciato.
        """
        x = note['x_pos'] + random.gauss(0, 0.9)
        y = note['y_pos'] + random.gauss(0, 0.9)
        color = self.get_note_color(note['note'], note['pitch'])
        lw, alpha, scale = self.velocity_to_params(note['velocity'])
        self.impasto_blob(x, y, lw * 1.3 * scale, color, alpha)

    def draw_legato(self, note: Dict, next_note: Optional[Dict] = None):
        """
        Legato – Bézier tapered: parte piena e si assottiglia in punta.
        Curva morbida che unisce due note come un colpo fluido di pennello.
        """
        x1, y1 = note['x_pos'], note['y_pos']
        x2 = (next_note['x_pos'] if next_note else x1 + 50)
        y2 = (next_note['y_pos'] if next_note else y1)

        ctrl_x = (x1 + x2) / 2 + random.gauss(0, 10)
        ctrl_y = (y1 + y2) / 2 + random.gauss(0, 10)

        color = self.get_note_color(note['note'], note['pitch'])
        lw, alpha, _ = self.velocity_to_params(note['velocity'])
        self.tapered_bezier(
            [(x1, y1), (ctrl_x, ctrl_y), (x2, y2)],
            color, lw_start=lw, lw_end=lw * 0.28, alpha=alpha
        )

    def draw_slide(self, note: Dict):
        """
        Slide – pennellata diagonale con bristle: il pennello «scivola».
        Angolo ~20° verso l'alto, lunghezza proporzionale alla durata.
        """
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'], note['pitch'])
        lw, alpha, _ = self.velocity_to_params(note['velocity'])
        length = max(note['duration'] * self.px_per_beat, 30)
        self.bristle_line(
            x, y,
            x + length, y + length * 0.34,
            color, lw, alpha
        )

    def draw_bend(self, note: Dict):
        """
        Bend – Bézier tapered con colore virato al vermilion (tensione).
        Il punto di controllo è alzato per simulare la corda «tirata».
        """
        x, y = note['x_pos'], note['y_pos']
        lw, alpha, _ = self.velocity_to_params(note['velocity'])
        base  = self.get_note_color(note['note'], note['pitch'])
        color = np.clip(base * 0.58 + self.colors['vermilion'] * 0.42, 0, 1)
        rise  = lw * 8.5
        self.tapered_bezier(
            [(x, y), (x + 22, y + rise), (x + 44, y + rise * 0.28)],
            color, lw_start=lw, lw_end=lw * 0.45, alpha=alpha
        )

    def draw_vibrato(self, note: Dict):
        """
        Vibrato – sinusoide con bristle a tratti:
        ampiezza proporzionale alla velocità, pennellata tremolante.
        """
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'], note['pitch'])
        lw, alpha, _ = self.velocity_to_params(note['velocity'])
        length = max(note['duration'] * self.px_per_beat, 55)

        n_pts = 140
        xs = np.linspace(x, x + length, n_pts)
        amp  = lw * 1.6
        freq = 9
        ys = y + amp * np.sin(np.linspace(0, freq * 2 * np.pi, n_pts))

        step = 8
        for i in range(0, n_pts - step, step):
            # Spessore oscillante insieme all'ampiezza
            env = 0.7 + 0.3 * abs(np.sin(i / n_pts * np.pi))
            self.bristle_line(
                xs[i], ys[i], xs[i + step], ys[i + step],
                color, lw * env, alpha, n_bristles=3
            )

    def draw_hammer_on(self, note: Dict):
        """
        Hammer-on – due impasto blob connessi da filamento sottile:
        il secondo colpo è più piccolo (dito che cade sulla corda).
        """
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'], note['pitch'])
        lw, alpha, scale = self.velocity_to_params(note['velocity'])
        r = lw * scale * 0.95
        self.impasto_blob(x, y, r, color, alpha)
        x2, y2 = x + lw * 4.2, y + lw * 2.1
        self.impasto_blob(x2, y2, r * 0.68, color, alpha * 0.80)
        self.bristle_line(x, y, x2, y2, color, lw * 0.38, alpha * 0.55, n_bristles=2)

    def draw_powerchord(self, note: Dict):
        """
        Power chord – blocco impasto rettangolare con blend ocra+bianco
        (quinta della nota = bianco Zorn sovrapposto).
        """
        x, y = note['x_pos'], note['y_pos']
        lw, alpha, scale = self.velocity_to_params(note['velocity'])
        w = max(note['duration'] * self.px_per_beat * 0.88, 38)
        h = lw * 2.6 * scale

        color  = self.get_note_color(note['note'], note['pitch'])
        color2 = np.clip(color * 0.62 + self.colors['white'] * 0.38, 0, 1)

        self.ax.add_patch(patches.Rectangle(
            (x, y - h / 2), w, h,
            facecolor=color, alpha=alpha, edgecolor='none'
        ))
        # Strato quinta (bianco Titanio)
        self.ax.add_patch(patches.Rectangle(
            (x, y - h / 2 + h * 0.62), w, h * 0.33,
            facecolor=color2, alpha=alpha * 0.68, edgecolor='none'
        ))

    def draw_tapping(self, note: Dict):
        """
        Tapping – cerchi concentrici luminosi che «emergono» dalla pennellata:
        gocce di luce che bucano il colore, progressivamente più brillanti.
        """
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'], note['pitch'])
        lw, alpha, scale = self.velocity_to_params(note['velocity'])
        base_r = lw * 1.9 * scale

        layers = [
            (1.00, 0.32),   # anello esterno, più trasparente
            (0.65, 0.52),
            (0.35, 0.78),   # nucleo, quasi opaco
        ]
        for k, (r_frac, a_frac) in enumerate(layers):
            t = k / (len(layers) - 1)
            ring_color = np.clip(
                color * (1 - t * 0.35) + self.colors['white'] * t * 0.35,
                0, 1
            )
            self.ax.add_patch(Circle(
                (x, y), base_r * r_frac,
                facecolor=ring_color, alpha=alpha * a_frac, edgecolor='none'
            ))

    def draw_dive(self, note: Dict):
        """
        Dive bomb (whammy bar) – spirale discendente con colore che
        scurisce progressivamente dal colore base all'ivory black.
        """
        x, y = note['x_pos'], note['y_pos']
        lw, alpha, _ = self.velocity_to_params(note['velocity'])
        base = self.get_note_color(note['note'], note['pitch'])

        t = np.linspace(0, 4 * np.pi, 130)
        xs = x + t * 3.6
        ys = y - t * 2.3 + 6.5 * np.sin(t)

        for i in range(len(t) - 1):
            frac  = i / (len(t) - 1)
            c     = np.clip(base * (1 - frac * 0.72) + self.colors['black'] * frac * 0.72, 0, 1)
            lw_i  = lw * (1 - frac * 0.52)
            a_i   = alpha * (1 - frac * 0.42)
            self.ax.plot(
                [xs[i], xs[i + 1]], [ys[i], ys[i + 1]],
                color=c, lw=lw_i, alpha=a_i,
                solid_capstyle='round'
            )

    def draw_harmonic_natural(self, note: Dict):
        """
        Armonico naturale – alone multistrato etereo:
        colore base ibridato con bianco titanio, raggi decrescenti con
        alpha progressiva → effetto «bagliore» aereo.
        """
        x, y = note['x_pos'], note['y_pos']
        lw, alpha, _ = self.velocity_to_params(note['velocity'])
        color = self.get_note_color(note['note'], note['pitch'])
        airy  = np.clip(color * 0.28 + self.colors['white'] * 0.72, 0, 1)

        layers = [
            (lw * 4.5, airy,  0.11),
            (lw * 3.0, airy,  0.22),
            (lw * 1.6, airy,  0.50),
            (lw * 0.5, color, 0.88),   # nucleo pieno
        ]
        for r, c, a in layers:
            self.ax.add_patch(Circle(
                (x, y), r,
                facecolor=np.clip(c, 0, 1),
                alpha=alpha * a,
                edgecolor='none'
            ))

    def draw_harmonic_artificial(self, note: Dict):
        """
        Armonico artificiale (pinch harmonic) – 8 scintille affilate:
        contrasto forte, raggi con bristle tenue.
        """
        x, y = note['x_pos'], note['y_pos']
        lw, alpha, _ = self.velocity_to_params(note['velocity'])
        color      = self.get_note_color(note['note'], note['pitch'])
        spike_len  = lw * 4.2
        spike_col  = np.clip(color * 0.48 + self.colors['white'] * 0.52, 0, 1)

        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = np.radians(angle)
            self.bristle_line(
                x, y,
                x + spike_len * np.cos(rad),
                y + spike_len * np.sin(rad),
                spike_col, lw * 0.38, alpha, n_bristles=2
            )

    # ═══════════════════════ background (ground layer) ════════════════════

    def add_ground_layer(self):
        """
        Strato di fondo pittorico (imprimitura):
        grandi pennellate bristle di varianti tonali dell'ocra Zorn
        (ocra pura, ocra + nero, ocra + bianco) per simulare la
        preparazione della tela con il primer colorato.
        """
        rng_params = [
            # (color_mix_fn, lw_range, alpha_range, n_bristles)
            (lambda: self.colors['ochre'] * random.uniform(0.80, 1.05),
             (10, 28), (0.07, 0.18), 7),
            (lambda: self.colors['ochre'] * 0.70 + self.colors['black'] * 0.09,
             (6, 18), (0.05, 0.14), 5),
            (lambda: self.colors['ochre'] * 0.85 + self.colors['white'] * 0.10,
             (5, 14), (0.04, 0.12), 4),
        ]
        for color_fn, (lw_lo, lw_hi), (a_lo, a_hi), nb in rng_params:
            for _ in range(7):
                x1 = random.uniform(-40, self.width + 40)
                y1 = random.uniform(-40, self.height + 40)
                angle  = random.uniform(-0.25, 0.25)
                length = random.uniform(130, 450)
                x2 = x1 + length * np.cos(angle)
                y2 = y1 + length * np.sin(angle)
                color = np.clip(color_fn(), 0, 1)
                self.bristle_line(
                    x1, y1, x2, y2,
                    color,
                    random.uniform(lw_lo, lw_hi),
                    random.uniform(a_lo, a_hi),
                    n_bristles=nb,
                )

    # ═══════════════════════ data parsing ════════════════════════════════

    def parse_johnny_b_goode_riff(self) -> List[Dict]:
        riff_notes = [
            {'note': 'A', 'fret': 5,  'string': 6, 'duration': 0.50, 'velocity': 'mf', 'technique': 'staccato'},
            {'note': 'C', 'fret': 8,  'string': 6, 'duration': 0.50, 'velocity': 'f',  'technique': 'legato'},
            {'note': 'D', 'fret': 5,  'string': 4, 'duration': 0.25, 'velocity': 'f',  'technique': 'slide'},
            {'note': 'A', 'fret': 7,  'string': 5, 'duration': 0.50, 'velocity': 'mf', 'technique': 'hammer_on'},
            {'note': 'C', 'fret': 8,  'string': 5, 'duration': 0.25, 'velocity': 'f',  'technique': 'bend'},
            {'note': 'D', 'fret': 7,  'string': 3, 'duration': 0.75, 'velocity': 'f',  'technique': 'vibrato'},
            {'note': 'E', 'fret': 8,  'string': 1, 'duration': 0.50, 'velocity': 'f',  'technique': 'harmonic_natural'},
            {'note': 'G', 'fret': 3,  'string': 1, 'duration': 0.50, 'velocity': 'mp', 'technique': 'legato'},
            {'note': 'A', 'fret': 5,  'string': 1, 'duration': 1.00, 'velocity': 'f',  'technique': 'powerchord'},
            {'note': 'C', 'fret': 8,  'string': 6, 'duration': 0.25, 'velocity': 'mf', 'technique': 'tapping'},
            {'note': 'D', 'fret': 5,  'string': 4, 'duration': 0.50, 'velocity': 'f',  'technique': 'dive'},
            {'note': 'G', 'fret': 3,  'string': 1, 'duration': 0.25, 'velocity': 'p',  'technique': 'harmonic_artificial'},
        ]
        string_tuning = [40, 45, 50, 55, 59, 64]
        processed = []
        t = 0.0
        for nd in riff_notes:
            midi = string_tuning[nd['string'] - 1] + nd['fret']
            processed.append({
                'note':       nd['note'],
                'pitch':      midi,
                'start_time': t,
                'duration':   nd['duration'],
                'velocity':   nd['velocity'],
                'technique':  nd['technique'],
                'x_pos':      self.time_to_x(t),
                'y_pos':      self.pitch_to_y(midi),
            })
            t += nd['duration']
        return processed

    # ═══════════════════════ render pipeline ══════════════════════════════

    def render_notes(self, notes: List[Dict]):
        dispatch = {
            'staccato':            self.draw_staccato,
            'slide':               self.draw_slide,
            'bend':                self.draw_bend,
            'vibrato':             self.draw_vibrato,
            'hammer_on':           self.draw_hammer_on,
            'powerchord':          self.draw_powerchord,
            'tapping':             self.draw_tapping,
            'dive':                self.draw_dive,
            'harmonic_natural':    self.draw_harmonic_natural,
            'harmonic_artificial': self.draw_harmonic_artificial,
        }
        for i, note in enumerate(notes):
            tech = note['technique']
            if tech == 'legato':
                nxt = notes[i + 1] if i + 1 < len(notes) else None
                self.draw_legato(note, nxt)
            elif tech in dispatch:
                dispatch[tech](note)
            else:
                # Fallback: pennellata bristle orizzontale
                x, y = note['x_pos'], note['y_pos']
                lw, alpha, _ = self.velocity_to_params(note['velocity'])
                color = self.get_note_color(note['note'], note['pitch'])
                self.bristle_line(x, y, x + 45, y, color, lw, alpha)

    def create_artwork(self, filename: str = 'johnny_b_goode_zorn_riff_v2.png'):
        notes = self.parse_johnny_b_goode_riff()
        self.add_ground_layer()
        self.render_notes(notes)
        self.fig.savefig(
            filename,
            facecolor=self.colors['ochre'],
            dpi=150,
            bbox_inches='tight',
            edgecolor='none',
        )
        print(f"Artwork v2 completato: {filename}")


if __name__ == '__main__':
    artist = ZornGuitarRiffArt()
    artist.create_artwork()
    plt.show()
