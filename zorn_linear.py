"""
Zorn Linear — abstract guitar riff visualization in Zorn palette.
Timeline: left → right. Matplotlib-based.
"""

import math
import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, RegularPolygon
from matplotlib.path import Path
import matplotlib.patheffects as pe
import numpy as np

# ---------------------------------------------------------------------------
# Fixed data
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
TUNING = [40, 45, 50, 55, 59, 64]  # E2 A2 D3 G3 B3 E4

# ---------------------------------------------------------------------------
# Palette Zorn
# ---------------------------------------------------------------------------
OCHRE     = (196/255, 164/255, 106/255)
VERMILION = (227/255,  66/255,  52/255)
BLACK     = ( 28/255,  28/255,  28/255)
WHITE     = (242/255, 242/255, 242/255)
GOLD      = (220/255, 140/255,  73/255)

NOTE_COLOR = {
    'A': VERMILION,
    'C': OCHRE,
    'D': BLACK,
    'E': WHITE,
    'G': GOLD,
}

# ---------------------------------------------------------------------------
# Mappings
# ---------------------------------------------------------------------------
VEL_ALPHA = {'p': 0.40, 'mp': 0.60, 'mf': 0.78, 'f': 0.92}
VEL_LW    = {'p': 1.5,  'mp': 2.5,  'mf': 4.0,  'f': 6.5}

# ---------------------------------------------------------------------------
# Canvas / layout constants
# ---------------------------------------------------------------------------
W_PX, H_PX = 1600, 1000
DPI = 150
MARGIN = 80
PX_PER_BEAT = 200
MIDI_MIN, MIDI_MAX = 45, 72

SEED = 42

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def midi_pitch(string_num: int, fret: int) -> int:
    return TUNING[string_num - 1] + fret


def y_from_midi(midi: float, H: float) -> float:
    """Map midi pitch to canvas Y coordinate (low pitch → bottom)."""
    norm = (midi - MIDI_MIN) / (MIDI_MAX - MIDI_MIN)
    return MARGIN + norm * (H - 2 * MARGIN)


def blend(c1, c2, t: float):
    """Linear interpolation between two RGB tuples."""
    return tuple(c1[i] * (1 - t) + c2[i] * t for i in range(3))


def note_color(note: str, midi: int) -> tuple:
    """Base color for a note, shifted toward BLACK (low) or WHITE (high)."""
    base = NOTE_COLOR.get(note, BLACK)
    norm = (midi - MIDI_MIN) / (MIDI_MAX - MIDI_MIN)
    if norm < 0.5:
        t = (0.5 - norm) * 0.55
        return blend(base, BLACK, t)
    else:
        t = (norm - 0.5) * 0.45
        return blend(base, WHITE, t)


def jitter(rng: random.Random, scale: float = 0.3) -> float:
    return rng.uniform(-scale, scale)


# ---------------------------------------------------------------------------
# Technique renderers
# ---------------------------------------------------------------------------

def draw_staccato(ax, x, y, dur_px, color, alpha, lw, rng):
    seg_w = dur_px * 80 / PX_PER_BEAT  # scaled short segment
    seg_w = max(seg_w, 10)
    x0 = x + jitter(rng)
    y0 = y + jitter(rng)
    x1 = x0 + seg_w
    y1 = y0 + jitter(rng)
    ax.plot([x0, x1 - 8], [y0, y1], color=color, alpha=alpha, lw=lw,
            solid_capstyle='butt')
    # Hexagon at end
    hex_patch = RegularPolygon(
        (x1, y1), numVertices=6, radius=5,
        orientation=math.pi / 6,
        facecolor=color, edgecolor=color, alpha=alpha * 0.9,
        transform=ax.transData, zorder=4
    )
    ax.add_patch(hex_patch)


def draw_legato(ax, x, y, dur_px, y_next, color, alpha, lw, rng):
    x0 = x + jitter(rng)
    y0 = y + jitter(rng)
    x3 = x + dur_px + jitter(rng)
    y3 = y_next + jitter(rng)
    # Cubic Bézier control points
    cp_offset = dur_px * 0.35
    x1, y1 = x0 + cp_offset, y0
    x2, y2 = x3 - cp_offset, y3
    verts = [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    path = Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor='none', edgecolor=color,
                               lw=lw, alpha=alpha, zorder=3)
    ax.add_patch(patch)


def draw_slide(ax, x, y, dur_px, y_next, color, alpha, lw, rng):
    x0 = x + jitter(rng)
    y0 = y + jitter(rng)
    x1 = x + dur_px + jitter(rng)
    y1 = y_next + jitter(rng)
    n = 20
    xs = np.linspace(x0, x1, n)
    ys = np.linspace(y0, y1, n)
    for i in range(n - 1):
        t = i / (n - 1)
        seg_lw = lw * 0.4 + lw * 0.6 * t  # thin start, thick end
        ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=color, alpha=alpha, lw=seg_lw,
                solid_capstyle='round')


def draw_hammer_on(ax, x, y, dur_px, color, alpha, lw, rng):
    x0 = x + jitter(rng)
    y0 = y + jitter(rng)
    ax.scatter([x0, x0 + 15], [y0, y0], s=[64, 25],
               c=[color], alpha=alpha, zorder=5, edgecolors='none')
    # Small connecting arc
    verts = [(x0, y0), (x0 + 7.5, y0 + 8), (x0 + 15, y0)]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    path = Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor='none', edgecolor=color,
                               lw=lw * 0.6, alpha=alpha * 0.85, zorder=3)
    ax.add_patch(patch)


def draw_bend(ax, x, y, dur_px, color, alpha, lw, rng):
    x0 = x + jitter(rng)
    y0 = y + jitter(rng)
    x2 = x + dur_px + jitter(rng)
    y2 = y0
    ctrl_x = x0 + dur_px * 0.5
    ctrl_y = y0 + 25
    verts = [(x0, y0), (ctrl_x, ctrl_y), (x2, y2)]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    path = Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor='none', edgecolor=color,
                               lw=lw, alpha=alpha, zorder=3)
    ax.add_patch(patch)
    # Upward arrow at control point
    ax.annotate('', xy=(ctrl_x, ctrl_y + 2), xytext=(ctrl_x, y0 + 6),
                arrowprops=dict(arrowstyle='->', color=color,
                                lw=lw * 0.5, alpha=alpha))


def draw_vibrato(ax, x, y, dur_px, color, alpha, lw, rng):
    amp = 4
    cycles = 8
    n = 80
    xs = np.linspace(x, x + dur_px, n)
    ts = np.linspace(0, cycles * 2 * math.pi, n)
    ys = y + amp * np.sin(ts)
    for i in range(n - 1):
        ax.plot([xs[i] + jitter(rng, 0.15), xs[i+1] + jitter(rng, 0.15)],
                [ys[i] + jitter(rng, 0.15), ys[i+1] + jitter(rng, 0.15)],
                color=color, alpha=alpha, lw=lw * 0.7,
                solid_capstyle='round')


def draw_harmonic_natural(ax, x, y, dur_px, color, alpha, lw, rng):
    cx = x + dur_px * 0.5 + jitter(rng)
    cy = y + jitter(rng)
    for r, a_scale in [(20, 0.25), (14, 0.35), (8, 0.35)]:
        circle = plt.Circle((cx, cy), r,
                             facecolor='none', edgecolor=color,
                             lw=lw * 0.6, alpha=alpha * a_scale, zorder=3)
        ax.add_patch(circle)
    ax.scatter([cx], [cy], s=40, c=[color], alpha=alpha * 0.35,
               zorder=4, edgecolors='none')


def draw_harmonic_artificial(ax, x, y, dur_px, color, alpha, lw, rng):
    cx = x + dur_px * 0.5 + jitter(rng)
    cy = y + jitter(rng)
    blended = blend(color, WHITE, 0.3)
    length = 14
    for angle_deg in [45, 135, 225, 315]:
        angle = math.radians(angle_deg)
        dx = math.cos(angle) * length
        dy = math.sin(angle) * length
        ax.plot([cx, cx + dx], [cy, cy + dy],
                color=blended, alpha=alpha * 0.70, lw=lw * 0.7,
                solid_capstyle='round')


def draw_powerchord(ax, x, y, dur_px, color, alpha, lw, rng):
    w = dur_px * 1.1
    h = 28
    x0 = x + jitter(rng)
    y0 = y - h / 2 + jitter(rng)
    box = FancyBboxPatch((x0, y0), w, h,
                         boxstyle="round,pad=2",
                         facecolor=color, edgecolor=blend(color, WHITE, 0.3),
                         lw=lw * 0.4, alpha=alpha * 0.85, zorder=3)
    ax.add_patch(box)


def draw_tapping(ax, x, y, dur_px, color, alpha, lw, rng):
    cx = x + dur_px * 0.5 + jitter(rng)
    cy = y + jitter(rng)
    light_color = blend(color, WHITE, 0.2)
    for r, a_scale in [(18, 0.25), (10, 0.50), (4, 0.85)]:
        circle = plt.Circle((cx, cy), r,
                             facecolor=light_color, edgecolor='none',
                             alpha=alpha * a_scale, zorder=3)
        ax.add_patch(circle)


def draw_dive(ax, x, y, dur_px, color, alpha, lw, rng):
    n = 30
    xs = np.linspace(x, x + dur_px, n)
    # Progressive downward curve (ease-in)
    ys = np.array([y - 30 * (i / (n - 1)) ** 2 for i in range(n)])
    for i in range(n - 1):
        t = i / (n - 1)
        seg_lw = lw * (1 - t * 0.8) + 1 * t  # 5→1 px
        seg_alpha = alpha * (1 - t * 0.5)
        ax.plot([xs[i] + jitter(rng, 0.2), xs[i+1] + jitter(rng, 0.2)],
                [ys[i] + jitter(rng, 0.2), ys[i+1] + jitter(rng, 0.2)],
                color=color, alpha=seg_alpha, lw=seg_lw,
                solid_capstyle='round')


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def render():
    rng = random.Random(SEED)
    np.random.seed(SEED)

    fig_w = W_PX / DPI
    fig_h = H_PX / DPI
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=DPI)
    fig.patch.set_facecolor(OCHRE)
    ax.set_facecolor(OCHRE)
    ax.set_xlim(0, W_PX)
    ax.set_ylim(0, H_PX)
    ax.set_aspect('equal')
    ax.axis('off')

    # Precompute cumulative times and positions
    events = []
    t_cum = 0.0
    for note_data in RIFF:
        midi = midi_pitch(note_data['string'], note_data['fret'])
        x = MARGIN + t_cum * PX_PER_BEAT
        y = y_from_midi(midi, H_PX)
        dur_px = note_data['duration'] * PX_PER_BEAT
        color = note_color(note_data['note'], midi)
        alpha = VEL_ALPHA[note_data['velocity']]
        lw = VEL_LW[note_data['velocity']]
        events.append({
            **note_data,
            'midi': midi,
            'x': x,
            'y': y,
            'dur_px': dur_px,
            'color': color,
            'alpha': alpha,
            'lw': lw,
        })
        t_cum += note_data['duration']

    # Draw each event
    for idx, ev in enumerate(events):
        x = ev['x']
        y = ev['y']
        dur_px = ev['dur_px']
        color = ev['color']
        alpha = ev['alpha']
        lw = ev['lw']
        tech = ev['technique']

        # Determine next y for pitch-aware techniques
        if idx + 1 < len(events):
            y_next = events[idx + 1]['y']
        else:
            y_next = y

        if tech == 'staccato':
            draw_staccato(ax, x, y, dur_px, color, alpha, lw, rng)
        elif tech == 'legato':
            draw_legato(ax, x, y, dur_px, y_next, color, alpha, lw, rng)
        elif tech == 'slide':
            draw_slide(ax, x, y, dur_px, y_next, color, alpha, lw, rng)
        elif tech == 'hammer_on':
            draw_hammer_on(ax, x, y, dur_px, color, alpha, lw, rng)
        elif tech == 'bend':
            draw_bend(ax, x, y, dur_px, color, alpha, lw, rng)
        elif tech == 'vibrato':
            draw_vibrato(ax, x, y, dur_px, color, alpha, lw, rng)
        elif tech == 'harmonic_natural':
            draw_harmonic_natural(ax, x, y, dur_px, color, alpha, lw, rng)
        elif tech == 'harmonic_artificial':
            draw_harmonic_artificial(ax, x, y, dur_px, color, alpha, lw, rng)
        elif tech == 'powerchord':
            draw_powerchord(ax, x, y, dur_px, color, alpha, lw, rng)
        elif tech == 'tapping':
            draw_tapping(ax, x, y, dur_px, color, alpha, lw, rng)
        elif tech == 'dive':
            draw_dive(ax, x, y, dur_px, color, alpha, lw, rng)

    plt.tight_layout(pad=0)
    fig.savefig('riff_linear.png', dpi=DPI, bbox_inches='tight',
                facecolor=OCHRE)
    plt.close(fig)


if __name__ == '__main__':
    render()
    print("riff_linear.png completato")
