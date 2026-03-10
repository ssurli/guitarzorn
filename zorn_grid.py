"""
zorn_grid.py — Quadro astratto stile Zorn con layout a griglia partitura.
JOHNNY B. GOODE — Pentatonica di La — Palette Zorn
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, PathPatch, FancyArrowPatch
from matplotlib.path import Path
import numpy as np
import math
import random

# ---------------------------------------------------------------------------
# Dati fissi
# ---------------------------------------------------------------------------
RIFF = [
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

TUNING = [40, 45, 50, 55, 59, 64]  # MIDI: E2, A2, D3, G3, B3, E4

# ---------------------------------------------------------------------------
# Palette Zorn
# ---------------------------------------------------------------------------
OCHRE     = (196/255, 164/255, 106/255)
VERMILION = (227/255,  66/255,  52/255)
BLACK     = ( 28/255,  28/255,  28/255)
WHITE     = (242/255, 242/255, 242/255)
GOLD      = (220/255, 140/255,  73/255)

# ---------------------------------------------------------------------------
# Helper: calcola MIDI pitch dalla nota, corda e tasto
# ---------------------------------------------------------------------------
def compute_midi(note, fret, string_num):
    """string_num: 1=high e, 6=low E (chitarra standard)"""
    # TUNING index 0=string6(E2), 1=string5(A2), ..., 5=string1(E4)
    open_midi = TUNING[6 - string_num]
    return open_midi + fret

# ---------------------------------------------------------------------------
# Mapping nota → colore base + blend per ottava
# ---------------------------------------------------------------------------
NOTE_COLOR = {
    'A': VERMILION,
    'C': OCHRE,
    'D': BLACK,
    'E': WHITE,
    'G': GOLD,
}

NOTE_EDGE = {
    'A': BLACK,
    'C': BLACK,
    'D': WHITE,       # bordo bianco per visibilità su nero
    'E': (0.5, 0.5, 0.5),  # bordo grigio su bianco
    'G': BLACK,
}

def blend_color(c1, c2, t):
    """Blend lineare tra c1 e c2 con fattore t (0=c1, 1=c2)."""
    return tuple(c1[i] * (1 - t) + c2[i] * t for i in range(3))

def note_color_for_pitch(note, midi_pitch):
    """Colore Zorn modificato per ottava: basse → blend BLACK, alte → blend WHITE."""
    base = NOTE_COLOR.get(note, OCHRE)
    # Range pitch usato: 45–72. Centro ≈ 58.
    # pitch < 52 → blend BLACK, pitch > 64 → blend WHITE
    if midi_pitch < 52:
        t = min((52 - midi_pitch) / 10.0, 0.40)
        return blend_color(base, BLACK, t)
    elif midi_pitch > 64:
        t = min((midi_pitch - 64) / 10.0, 0.40)
        return blend_color(base, WHITE, t)
    return base

# ---------------------------------------------------------------------------
# Velocity → alpha
# ---------------------------------------------------------------------------
VEL_ALPHA = {'p': 0.55, 'mp': 0.70, 'mf': 0.85, 'f': 1.00}

# ---------------------------------------------------------------------------
# Tecniche → riga nella griglia inferiore (0=top … 4=bottom)
# ---------------------------------------------------------------------------
TECH_ROW = {
    'staccato':             0,
    'legato':               1,
    'hammer_on':            1,
    'slide':                2,
    'dive':                 2,
    'bend':                 2,
    'vibrato':              3,
    'harmonic_natural':     3,
    'harmonic_artificial':  3,
    'powerchord':           4,
    'tapping':              4,
}

TECH_LABEL = {
    0: 'STACCATO',
    1: 'LEGATO / HAMMER',
    2: 'BEND · SLIDE · DIVE',
    3: 'HARMONIC / VIBRATO',
    4: 'ALTRI',
}

# ---------------------------------------------------------------------------
# Costanti layout (coordinate matplotlib standard: y=0 in basso)
# ---------------------------------------------------------------------------
FIG_W_PX  = 1600
FIG_H_PX  = 1000
DPI       = 150

# Griglia superiore (pitch-time) — in coordinate figure [0,1600]×[0,1000]
# Matplotlib: y=0 in basso → y_bottom > y_top in pixel tradizionali
# Definiamo regioni in pixel con y=0 in basso:
#   griglia superiore: da y=470 a y=920  (450px, alto in figura = alte y)
#   griglia inferiore: da y=100 a y=380  (280px)

UPPER_Y_BOT = 470   # y basso della griglia pitch-time  (px, y=0 in basso)
UPPER_Y_TOP = 920   # y alto della griglia pitch-time
UPPER_H     = UPPER_Y_TOP - UPPER_Y_BOT  # 450

LOWER_Y_BOT =  80   # y basso della griglia tecnica
LOWER_Y_TOP = 360   # y alto della griglia tecnica
LOWER_H     = LOWER_Y_TOP - LOWER_Y_BOT  # 280

X_START     = 120   # origine x note
BEAT_PX     = 200   # 1 beat = 200 px

PITCH_MIN   = 45
PITCH_MAX   = 72

def pitch_to_y(midi_pitch):
    """Converte MIDI pitch in coordinata y (matplotlib, y=0 in basso)."""
    t = (midi_pitch - PITCH_MIN) / (PITCH_MAX - PITCH_MIN)
    return UPPER_Y_BOT + t * UPPER_H

def beat_to_x(beat):
    return X_START + beat * BEAT_PX

# ---------------------------------------------------------------------------
# Pentatonica A: note MIDI evidenziate
# ---------------------------------------------------------------------------
def penta_a_midi_in_range():
    """Ritorna tutti i MIDI pitch della pentatonica di A (A C D E G) tra 45 e 72."""
    penta_classes = {9, 0, 2, 4, 7}  # A=9, C=0, D=2, E=4, G=7
    result = []
    for p in range(PITCH_MIN, PITCH_MAX + 1):
        if (p % 12) in penta_classes:
            result.append(p)
    return result

# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def render():
    fig = plt.figure(figsize=(FIG_W_PX / DPI, FIG_H_PX / DPI), dpi=DPI,
                     facecolor=OCHRE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FIG_W_PX)
    ax.set_ylim(0, FIG_H_PX)
    ax.set_aspect('equal')
    ax.axis('off')

    # Sfondo generale
    bg = mpatches.Rectangle((0, 0), FIG_W_PX, FIG_H_PX,
                             color=OCHRE, zorder=0)
    ax.add_patch(bg)

    # Sfondo griglia superiore (leggermente più chiaro)
    upper_bg = mpatches.Rectangle((0, UPPER_Y_BOT), FIG_W_PX, UPPER_H,
                                   color=blend_color(OCHRE, WHITE, 0.18), zorder=1)
    ax.add_patch(upper_bg)

    # Sfondo griglia inferiore
    lower_bg = mpatches.Rectangle((0, LOWER_Y_BOT), FIG_W_PX, LOWER_H,
                                   color=blend_color(OCHRE, BLACK, 0.10), zorder=1)
    ax.add_patch(lower_bg)

    # -------------------------------------------------------------------
    # Calcola tempo cumulato e MIDI pitch per ogni nota
    # -------------------------------------------------------------------
    cum_time = 0.0
    note_data = []
    for n in RIFF:
        midi = compute_midi(n['note'], n['fret'], n['string'])
        note_data.append({
            **n,
            'midi': midi,
            'beat_start': cum_time,
        })
        cum_time += n['duration']
    total_beats = cum_time

    # -------------------------------------------------------------------
    # GRIGLIA SUPERIORE: linee orizzontali per semitono
    # -------------------------------------------------------------------
    penta_pitches = set(penta_a_midi_in_range())

    for p in range(PITCH_MIN, PITCH_MAX + 1):
        y = pitch_to_y(p)
        if p in penta_pitches:
            ax.axhline(y=y, xmin=0, xmax=1,
                       color=OCHRE, linewidth=0.8, alpha=0.85, zorder=2)
        else:
            ax.plot([0, FIG_W_PX], [y, y],
                    color=BLACK, linewidth=0.4, alpha=0.3, zorder=2)

    # -------------------------------------------------------------------
    # GRIGLIA SUPERIORE: separatori di battuta
    # -------------------------------------------------------------------
    beat = 0.0
    while beat <= total_beats + 0.01:
        x = beat_to_x(beat)
        if 0 <= x <= FIG_W_PX:
            ax.plot([x, x], [UPPER_Y_BOT, UPPER_Y_TOP],
                    color=BLACK, linewidth=0.8, alpha=0.5, zorder=2)
        beat += 1.0

    # Bordi griglia superiore
    for y_edge in [UPPER_Y_BOT, UPPER_Y_TOP]:
        ax.plot([0, FIG_W_PX], [y_edge, y_edge],
                color=BLACK, linewidth=1.0, alpha=0.6, zorder=3)

    # -------------------------------------------------------------------
    # GRIGLIA SUPERIORE: rettangoli note (FancyBboxPatch)
    # -------------------------------------------------------------------
    NOTE_H = 12  # altezza base in px

    for nd in note_data:
        x0 = beat_to_x(nd['beat_start'])
        w  = nd['duration'] * BEAT_PX
        y0 = pitch_to_y(nd['midi']) - NOTE_H / 2
        color = note_color_for_pitch(nd['note'], nd['midi'])
        edge  = NOTE_EDGE.get(nd['note'], BLACK)
        alpha = VEL_ALPHA.get(nd['velocity'], 0.85)

        # FancyBboxPatch: coordinate (x, y) = angolo basso-sinistro
        patch = FancyBboxPatch(
            (x0 + 1, y0), w - 2, NOTE_H,
            boxstyle="round,pad=1",
            facecolor=color,
            edgecolor=edge,
            linewidth=0.5,
            alpha=alpha,
            zorder=5,
        )
        ax.add_patch(patch)

        # Etichetta nota + numero di tasto
        mid_x = x0 + w / 2
        mid_y = y0 + NOTE_H / 2
        label_color = WHITE if nd['note'] in ('A', 'C', 'G') else BLACK
        ax.text(mid_x, mid_y, f"{nd['note']}{nd['fret']}",
                ha='center', va='center',
                fontsize=5.5, color=label_color,
                fontweight='bold', zorder=6)

    # -------------------------------------------------------------------
    # LINEA DIVISORIA tra le due griglie
    # -------------------------------------------------------------------
    div_y = (UPPER_Y_BOT + LOWER_Y_TOP) / 2
    ax.plot([0, FIG_W_PX], [div_y, div_y],
            color=BLACK, linewidth=1.2, alpha=0.4, zorder=3)

    # -------------------------------------------------------------------
    # GRIGLIA INFERIORE: setup righe tecniche
    # -------------------------------------------------------------------
    N_ROWS   = 5
    N_COLS   = 12
    col_w    = (beat_to_x(total_beats) - X_START) / N_COLS
    row_h    = LOWER_H / N_ROWS
    label_x  = 10  # x per etichette tecniche

    # Bordi e linee orizzontali griglia inferiore
    for r in range(N_ROWS + 1):
        y_line = LOWER_Y_BOT + r * row_h
        ax.plot([0, FIG_W_PX], [y_line, y_line],
                color=BLACK, linewidth=0.5, alpha=0.25, zorder=2)

    for c in range(N_COLS + 1):
        x_line = X_START + c * col_w
        ax.plot([x_line, x_line], [LOWER_Y_BOT, LOWER_Y_TOP],
                color=BLACK, linewidth=0.4, alpha=0.20, zorder=2)

    # Bordi griglia inferiore
    for y_edge in [LOWER_Y_BOT, LOWER_Y_TOP]:
        ax.plot([0, FIG_W_PX], [y_edge, y_edge],
                color=BLACK, linewidth=1.0, alpha=0.6, zorder=3)

    # Etichette righe tecniche
    for row_idx, label in TECH_LABEL.items():
        y_center = LOWER_Y_BOT + (row_idx + 0.5) * row_h
        ax.text(label_x, y_center, label,
                ha='left', va='center',
                fontsize=6, color=BLACK, alpha=0.7,
                fontfamily='monospace', zorder=4)

    # -------------------------------------------------------------------
    # GRIGLIA INFERIORE: icone tecniche per ogni nota
    # -------------------------------------------------------------------
    for i, nd in enumerate(note_data):
        col_idx  = i  # colonna = indice nota (0–11)
        row_idx  = TECH_ROW.get(nd['technique'], 4)
        cx = X_START + (col_idx + 0.5) * col_w       # centro x colonna
        cy = LOWER_Y_BOT + (row_idx + 0.5) * row_h   # centro y riga
        color = note_color_for_pitch(nd['note'], nd['midi'])
        edge  = NOTE_EDGE.get(nd['note'], BLACK)
        alpha = VEL_ALPHA.get(nd['velocity'], 0.85)

        tech = nd['technique']

        if tech == 'staccato':
            # Puntino quadrato
            ax.plot(cx, cy, marker='s', markersize=8,
                    color=color, markeredgecolor=edge,
                    markeredgewidth=0.6, alpha=alpha, zorder=5)

        elif tech in ('legato', 'hammer_on'):
            # Linea curva ∩ (PathPatch)
            r = col_w * 0.28
            verts = [
                (cx - r, cy),
                (cx - r, cy + row_h * 0.35),
                (cx + r, cy + row_h * 0.35),
                (cx + r, cy),
            ]
            codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
            path = Path(verts, codes)
            pp = PathPatch(path, facecolor='none', edgecolor=color,
                           linewidth=1.8, alpha=alpha, zorder=5)
            ax.add_patch(pp)
            if tech == 'hammer_on':
                # Due punti ravvicinati ●●
                for dx in [-r * 0.5, r * 0.5]:
                    ax.plot(cx + dx, cy, marker='o', markersize=4,
                            color=color, alpha=alpha, zorder=6)

        elif tech in ('slide', 'dive'):
            # Linea diagonale /
            dx = col_w * 0.30
            dy = row_h * 0.35
            sign = 1 if tech == 'slide' else -1
            ax.annotate('', xy=(cx + dx, cy + sign * dy),
                        xytext=(cx - dx, cy - sign * dy),
                        arrowprops=dict(arrowstyle='->', color=color,
                                        lw=1.5),
                        alpha=alpha, zorder=5)

        elif tech == 'bend':
            # Freccia curva ↑
            ax.annotate('', xy=(cx, cy + row_h * 0.38),
                        xytext=(cx, cy - row_h * 0.10),
                        arrowprops=dict(
                            arrowstyle='->',
                            color=color,
                            lw=1.5,
                            connectionstyle='arc3,rad=0.4',
                        ),
                        alpha=alpha, zorder=5)

        elif tech == 'vibrato':
            # Sinusoide piccola ~
            xs = np.linspace(cx - col_w * 0.35, cx + col_w * 0.35, 40)
            ys = cy + np.sin(np.linspace(0, 4 * math.pi, 40)) * row_h * 0.12
            ax.plot(xs, ys, color=color, linewidth=1.5, alpha=alpha, zorder=5)

        elif tech == 'harmonic_natural':
            # Cerchio vuoto ○
            circle = plt.Circle((cx, cy), col_w * 0.20,
                                 facecolor='none', edgecolor=color,
                                 linewidth=1.5, alpha=alpha, zorder=5)
            ax.add_patch(circle)

        elif tech == 'harmonic_artificial':
            # Cerchio pieno con raggiera ✳
            circle = plt.Circle((cx, cy), col_w * 0.15,
                                 facecolor=color, edgecolor=edge,
                                 linewidth=0.8, alpha=alpha, zorder=5)
            ax.add_patch(circle)
            n_rays = 8
            r_inner = col_w * 0.17
            r_outer = col_w * 0.30
            for k in range(n_rays):
                angle = k * 2 * math.pi / n_rays
                x1 = cx + r_inner * math.cos(angle)
                y1 = cy + r_inner * math.sin(angle)
                x2 = cx + r_outer * math.cos(angle)
                y2 = cy + r_outer * math.sin(angle)
                ax.plot([x1, x2], [y1, y2],
                        color=color, linewidth=1.0, alpha=alpha * 0.8, zorder=5)

        elif tech == 'powerchord':
            # Rettangolo pieno ■
            rw = col_w * 0.40
            rh = row_h * 0.35
            rect = mpatches.Rectangle((cx - rw / 2, cy - rh / 2), rw, rh,
                                       facecolor=color, edgecolor=edge,
                                       linewidth=0.6, alpha=alpha, zorder=5)
            ax.add_patch(rect)

        elif tech == 'tapping':
            # Cerchi concentrici ◎
            for r_frac in [0.10, 0.20, 0.30]:
                c2 = plt.Circle((cx, cy), col_w * r_frac,
                                 facecolor='none', edgecolor=color,
                                 linewidth=1.0, alpha=alpha * 0.9, zorder=5)
                ax.add_patch(c2)
            ax.plot(cx, cy, marker='o', markersize=3,
                    color=color, alpha=alpha, zorder=6)

        # Etichetta nota sotto l'icona
        ax.text(cx, LOWER_Y_BOT + row_h * 0.15, nd['note'],
                ha='center', va='center',
                fontsize=5.5, color=BLACK, alpha=0.55, zorder=4)

    # -------------------------------------------------------------------
    # ASSI ETICHETTE griglia superiore
    # -------------------------------------------------------------------
    # Etichette pitch asse Y (sinistra)
    note_names_chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F',
                             'F#', 'G', 'G#', 'A', 'A#', 'B']
    for p in range(PITCH_MIN, PITCH_MAX + 1, 2):
        y = pitch_to_y(p)
        name = note_names_chromatic[p % 12]
        octave = p // 12 - 1
        ax.text(X_START - 8, y, f"{name}{octave}",
                ha='right', va='center',
                fontsize=5.5, color=BLACK, alpha=0.6, zorder=4)

    # Etichette tempo asse X (sopra griglia superiore)
    beat = 0.0
    while beat <= total_beats + 0.01:
        x = beat_to_x(beat)
        ax.text(x, UPPER_Y_TOP + 10, f"{beat:.2g}",
                ha='center', va='bottom',
                fontsize=6, color=BLACK, alpha=0.6, zorder=4)
        beat += 1.0

    # Etichetta asse X
    ax.text(beat_to_x(total_beats / 2), UPPER_Y_TOP + 22,
            'Beat', ha='center', va='bottom',
            fontsize=7, color=BLACK, alpha=0.5, zorder=4)

    # -------------------------------------------------------------------
    # TITOLO
    # -------------------------------------------------------------------
    ax.text(FIG_W_PX / 2, FIG_H_PX - 14,
            'JOHNNY B. GOODE — Pentatonica di La — Palette Zorn',
            ha='center', va='top',
            fontsize=10, color=OCHRE,
            fontweight='bold', zorder=10,
            bbox=dict(boxstyle='round,pad=3', facecolor=BLACK,
                      edgecolor=GOLD, linewidth=1.0, alpha=0.80))

    # Etichetta griglia superiore
    ax.text(12, UPPER_Y_TOP - 8, 'PITCH-TIME',
            ha='left', va='top',
            fontsize=7, color=BLACK, alpha=0.55,
            fontfamily='monospace', zorder=4)

    # Etichetta griglia inferiore
    ax.text(12, LOWER_Y_TOP - 4, 'TECNICA',
            ha='left', va='top',
            fontsize=7, color=BLACK, alpha=0.55,
            fontfamily='monospace', zorder=4)

    # -------------------------------------------------------------------
    # LEGENDA colori nota (angolo in basso a destra)
    # -------------------------------------------------------------------
    leg_x = FIG_W_PX - 130
    leg_y_start = LOWER_Y_BOT + LOWER_H / 2 + 40
    ax.text(leg_x, leg_y_start + 14, 'NOTE',
            ha='left', va='bottom',
            fontsize=6, color=BLACK, alpha=0.6,
            fontfamily='monospace', fontweight='bold')
    for k, (note_name, clr) in enumerate(NOTE_COLOR.items()):
        y_leg = leg_y_start - k * 14
        rect = mpatches.Rectangle((leg_x, y_leg - 5), 14, 10,
                                   facecolor=clr,
                                   edgecolor=NOTE_EDGE.get(note_name, BLACK),
                                   linewidth=0.5, zorder=6)
        ax.add_patch(rect)
        ax.text(leg_x + 18, y_leg, note_name,
                ha='left', va='center',
                fontsize=6, color=BLACK, alpha=0.8, zorder=6)

    # -------------------------------------------------------------------
    # Salva
    # -------------------------------------------------------------------
    plt.savefig('riff_grid.png', dpi=DPI, bbox_inches='tight',
                facecolor=OCHRE)
    plt.close(fig)


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    render()
    print("riff_grid.png completato")
