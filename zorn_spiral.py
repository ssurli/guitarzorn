import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import PathPatch, Wedge, Circle
from matplotlib.path import Path
import numpy as np
import math
import random

# ---------------------------------------------------------------------------
# Dati
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
TUNING = [40, 45, 50, 55, 59, 64]

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
# Mapping velocity
# ---------------------------------------------------------------------------
ALPHA_MAP = {'p': 0.40, 'mp': 0.60, 'mf': 0.78, 'f': 0.92}
LW_MAP    = {'p': 2.0,  'mp': 3.5,  'mf': 5.5,  'f': 8.5}

# ---------------------------------------------------------------------------
# Spirale di Archimede — parametri
# ---------------------------------------------------------------------------
CX, CY   = 800.0, 500.0   # centro canvas
R_MIN    =  60.0           # raggio minimo
A_SPIRAL =  40.0           # px per rad
TOTAL_BEATS = 5.5

def archimede_r(theta):
    return R_MIN + A_SPIRAL * theta

def polar_to_cart(r, theta):
    return CX + r * math.cos(theta), CY + r * math.sin(theta)

def blend(color, other, t):
    """Mescola color con other per una frazione t."""
    return tuple(c * (1 - t) + o * t for c, o in zip(color, other))

def note_color(note, string_num):
    """Colore base della nota con blend ottava (corda 6=bassa, 1=alta)."""
    base = NOTE_COLOR.get(note, OCHRE)
    # string 6 → blend BLACK 0.35, string 1 → blend WHITE 0.25
    t_black = (string_num - 1) / 5.0  # 0 (corda 1 alta) → 1 (corda 6 bassa)
    if t_black > 0.5:
        return blend(base, BLACK, (t_black - 0.5) * 0.7)
    else:
        return blend(base, WHITE, (0.5 - t_black) * 0.5)

# ---------------------------------------------------------------------------
# Helper per costruire arco come Path
# ---------------------------------------------------------------------------
def arc_path_points(theta_start, theta_end, r_func, n=60):
    """Restituisce array (N,2) di punti lungo l'arco della spirale."""
    thetas = np.linspace(theta_start, theta_end, n)
    pts = []
    for th in thetas:
        r = r_func(th)
        pts.append(polar_to_cart(r, th))
    return np.array(pts)

def make_path_patch(points, color, lw, alpha, filled=False, facecolor=None):
    codes = [Path.MOVETO] + [Path.LINETO] * (len(points) - 1)
    path  = Path(points, codes)
    fc    = facecolor if filled else 'none'
    patch = PathPatch(path, edgecolor=color, facecolor=fc,
                      linewidth=lw, alpha=alpha, capstyle='round')
    return patch

# ---------------------------------------------------------------------------
# Disegno tecniche
# ---------------------------------------------------------------------------

def draw_staccato(ax, note, theta_s, theta_e, color, alpha, lw):
    r_s = archimede_r(theta_s)
    xc, yc = polar_to_cart(r_s, theta_s)
    # tangente alla spirale
    tang_angle = theta_s + math.pi / 2
    length = note['duration'] * 40.0
    x2 = xc + length * math.cos(tang_angle)
    y2 = yc + length * math.sin(tang_angle)
    ax.plot([xc, x2], [yc, y2], color=color, lw=lw, alpha=alpha,
            solid_capstyle='round')
    ax.scatter([x2], [y2], s=math.pi * 4**2, color=color, alpha=alpha, zorder=5)


def draw_legato(ax, note, theta_s, theta_e, color, alpha, lw):
    pts = arc_path_points(theta_s, theta_e, archimede_r, n=80)
    patch = make_path_patch(pts, color, lw, alpha)
    ax.add_patch(patch)


def draw_slide(ax, note, theta_s, theta_e, color, alpha, lw):
    r_s = archimede_r(theta_s)
    r_e = archimede_r(theta_e)
    x1, y1 = polar_to_cart(r_s, theta_s)
    x2, y2 = polar_to_cart(r_e, theta_e)
    n = 30
    xs = np.linspace(x1, x2, n)
    ys = np.linspace(y1, y2, n)
    for i in range(n - 1):
        t = i / (n - 1)
        seg_lw = lw * (0.5 + t)
        seg_alpha = alpha * (0.4 + 0.6 * t)
        ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=color, lw=seg_lw, alpha=seg_alpha,
                solid_capstyle='round')


def draw_hammer_on(ax, note, theta_s, theta_e, color, alpha, lw):
    theta_mid = theta_s + (theta_e - theta_s) / 2.0
    r_s   = archimede_r(theta_s)
    r_mid = archimede_r(theta_mid)
    xs, ys   = polar_to_cart(r_s,   theta_s)
    xm, ym   = polar_to_cart(r_mid, theta_mid)
    # piccolo arco
    pts = arc_path_points(theta_s, theta_mid, archimede_r, n=40)
    patch = make_path_patch(pts, color, lw * 0.6, alpha * 0.7)
    ax.add_patch(patch)
    # due punti sovrapposti
    ax.scatter([xs, xm], [ys, ym], s=[math.pi * 10**2, math.pi * 6**2],
               color=color, alpha=alpha, zorder=6)


def draw_bend(ax, note, theta_s, theta_e, color, alpha, lw):
    def r_bent(th):
        return archimede_r(th) + 20.0
    pts = arc_path_points(theta_s, theta_e, r_bent, n=80)
    patch = make_path_patch(pts, color, lw, alpha)
    ax.add_patch(patch)


def draw_vibrato(ax, note, theta_s, theta_e, color, alpha, lw):
    n_cycles = 8
    n = 160
    thetas = np.linspace(theta_s, theta_e, n)
    pts = []
    for i, th in enumerate(thetas):
        phase = (i / n) * n_cycles * 2 * math.pi
        r = archimede_r(th) + 4.0 * math.sin(phase)
        pts.append(polar_to_cart(r, th))
    pts = np.array(pts)
    patch = make_path_patch(pts, color, lw, alpha)
    ax.add_patch(patch)


def draw_harmonic_natural(ax, note, theta_s, theta_e, color, alpha, lw):
    r_s = archimede_r(theta_s)
    xc, yc = polar_to_cart(r_s, theta_s)
    for rad in [10, 18, 28]:
        circle = Circle((xc, yc), rad, edgecolor=color, facecolor='none',
                         linewidth=lw * 0.5, alpha=alpha * 0.6)
        ax.add_patch(circle)
    ax.scatter([xc], [yc], s=20, color=color, alpha=alpha, zorder=5)


def draw_harmonic_artificial(ax, note, theta_s, theta_e, color, alpha, lw):
    r_s = archimede_r(theta_s)
    xc, yc = polar_to_cart(r_s, theta_s)
    tang_angle = theta_s + math.pi / 2
    for k in range(4):
        angle = tang_angle + math.pi / 4 + k * math.pi / 2
        x2 = xc + 20.0 * math.cos(angle)
        y2 = yc + 20.0 * math.sin(angle)
        ax.plot([xc, x2], [yc, y2], color=color, lw=lw * 0.7,
                alpha=0.7, solid_capstyle='round')


def draw_powerchord(ax, note, theta_s, theta_e, color, alpha, lw):
    r_s = archimede_r(theta_s)
    theta_s_deg = math.degrees(theta_s)
    delta_deg   = math.degrees(theta_e - theta_s)
    wedge = Wedge(
        center=(CX, CY),
        r=r_s + 14,
        theta1=theta_s_deg,
        theta2=theta_s_deg + delta_deg,
        width=28,
        facecolor=color,
        edgecolor=color,
        alpha=alpha * 0.85,
    )
    ax.add_patch(wedge)


def draw_tapping(ax, note, theta_s, theta_e, color, alpha, lw):
    r_s = archimede_r(theta_s)
    xc, yc = polar_to_cart(r_s, theta_s)
    for rad, a in [(5, 0.85), (12, 0.45), (20, 0.18)]:
        circle = Circle((xc, yc), rad, facecolor=color, edgecolor='none',
                         alpha=a)
        ax.add_patch(circle)


def draw_dive(ax, note, theta_s, theta_e, color, alpha, lw):
    n = 60
    thetas = np.linspace(theta_s, theta_e, n)
    pts = []
    alphas = []
    for i, th in enumerate(thetas):
        t = i / (n - 1)
        r = archimede_r(th) - 30.0 * t
        pts.append(polar_to_cart(r, th))
        alphas.append(alpha * (1.0 - 0.75 * t))
    # disegna segmenti con alpha variabile
    pts = np.array(pts)
    for i in range(len(pts) - 1):
        seg_alpha = (alphas[i] + alphas[i+1]) / 2.0
        ax.plot([pts[i, 0], pts[i+1, 0]], [pts[i, 1], pts[i+1, 1]],
                color=color, lw=lw, alpha=seg_alpha,
                solid_capstyle='round')


TECHNIQUE_DRAW = {
    'staccato':            draw_staccato,
    'legato':              draw_legato,
    'slide':               draw_slide,
    'hammer_on':           draw_hammer_on,
    'bend':                draw_bend,
    'vibrato':             draw_vibrato,
    'harmonic_natural':    draw_harmonic_natural,
    'harmonic_artificial': draw_harmonic_artificial,
    'powerchord':          draw_powerchord,
    'tapping':             draw_tapping,
    'dive':                draw_dive,
}

# ---------------------------------------------------------------------------
# Funzione principale di rendering
# ---------------------------------------------------------------------------

def render():
    fig = plt.figure(figsize=(1600/150, 1000/150), dpi=150)
    ax  = fig.add_axes([0, 0, 1, 1])

    ax.set_xlim(0, 1600)
    ax.set_ylim(0, 1000)
    ax.set_aspect('equal')
    ax.axis('off')

    # Sfondo OCHRE
    fig.patch.set_facecolor(OCHRE)
    ax.set_facecolor(OCHRE)

    # -----------------------------------------------------------------------
    # Disegna prima la spirale guida (sottile, semitrasparente)
    # -----------------------------------------------------------------------
    total_theta = sum(n['duration'] for n in RIFF) * (2 * math.pi / TOTAL_BEATS)
    thetas_guide = np.linspace(0, total_theta, 600)
    guide_pts = np.array([polar_to_cart(archimede_r(th), th) for th in thetas_guide])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(guide_pts) - 1)
    guide_path = Path(guide_pts, codes)
    guide_patch = PathPatch(guide_path, edgecolor=BLACK, facecolor='none',
                            linewidth=1.0, alpha=0.25)
    ax.add_patch(guide_patch)

    # -----------------------------------------------------------------------
    # Itera le note e disegna
    # -----------------------------------------------------------------------
    theta_cursor = 0.0

    for note in RIFF:
        delta_theta = note['duration'] * (2 * math.pi / TOTAL_BEATS)
        theta_s = theta_cursor
        theta_e = theta_cursor + delta_theta

        col   = note_color(note['note'], note['string'])
        alpha = ALPHA_MAP[note['velocity']]
        lw    = LW_MAP[note['velocity']]
        tech  = note['technique']

        draw_fn = TECHNIQUE_DRAW.get(tech)
        if draw_fn is not None:
            draw_fn(ax, note, theta_s, theta_e, col, alpha, lw)

        theta_cursor = theta_e

    # -----------------------------------------------------------------------
    # Piccolo cerchio al centro
    # -----------------------------------------------------------------------
    center_circle = Circle((CX, CY), R_MIN * 0.4,
                            facecolor=BLACK, edgecolor=GOLD,
                            linewidth=2, alpha=0.7, zorder=10)
    ax.add_patch(center_circle)

    plt.savefig('riff_spiral.png', dpi=150, bbox_inches='tight',
                facecolor=OCHRE)
    plt.close(fig)


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    render()
    print("riff_spiral.png completato")
