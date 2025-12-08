"""
PAINTERLY RENDERER
Rendering migliorato con texture pittoriche SENZA AI esterna

Aggiunge:
- Pennellate simulate
- Texture canvas
- Noise organico
- Bordi sfumati
- Impasto (texture materica)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyBboxPatch
import numpy as np
import random
from scipy.ndimage import gaussian_filter
from typing import List, Dict
import json

class PainterlyRenderer:
    """
    Renderer che simula aspetto pittorico reale
    """

    def __init__(self, notes: List[Dict], style='organic', palette='expanded'):
        self.notes = notes
        self.style = style

        # PALETTE ESPANSA (non solo Zorn!)
        if palette == 'expanded':
            self.colors = self._create_expanded_palette()
        elif palette == 'zorn':
            self.colors = self._create_zorn_palette()
        elif palette == 'vibrant':
            self.colors = self._create_vibrant_palette()
        else:
            self.colors = self._create_expanded_palette()

        # Canvas
        self.width = 2400  # Alta risoluzione
        self.height = 1600
        self.fig, self.ax = plt.subplots(figsize=(24, 16), dpi=150)

        # Sfondo con texture
        bg_color = self.colors['background']
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.axis('off')

        random.seed(42)
        np.random.seed(42)

        # Crea texture canvas
        self.canvas_texture = self._create_canvas_texture()

    def _create_expanded_palette(self) -> dict:
        """Palette ricca con 12+ colori"""
        return {
            # TERRE (per note basse/toniche)
            'burnt_sienna': np.array([140, 70, 40]) / 255.0,
            'raw_umber': np.array([115, 74, 18]) / 255.0,
            'yellow_ochre': np.array([196, 164, 106]) / 255.0,
            'gold': np.array([212, 175, 55]) / 255.0,

            # ROSSI (per note energiche)
            'cadmium_red': np.array([227, 0, 34]) / 255.0,
            'vermilion': np.array([227, 66, 52]) / 255.0,
            'alizarin_crimson': np.array([140, 20, 20]) / 255.0,
            'rose': np.array([200, 100, 100]) / 255.0,

            # SCURI (per tensione/dissonanza)
            'payne_grey': np.array([55, 65, 75]) / 255.0,
            'ivory_black': np.array([28, 28, 28]) / 255.0,
            'indigo': np.array([40, 45, 65]) / 255.0,

            # CHIARI (per note alte/armonici)
            'titanium_white': np.array([242, 242, 242]) / 255.0,
            'naples_yellow': np.array([250, 240, 190]) / 255.0,
            'zinc_white': np.array([255, 255, 255]) / 255.0,

            # ACCENTI
            'cerulean_blue': np.array([40, 100, 140]) / 255.0,
            'viridian': np.array([30, 110, 80]) / 255.0,
            'purple': np.array([100, 50, 100]) / 255.0,

            'background': np.array([240, 235, 220]) / 255.0  # Lino naturale
        }

    def _create_zorn_palette(self) -> dict:
        """Palette Zorn originale"""
        return {
            'ochre': np.array([196, 164, 106]) / 255.0,
            'vermilion': np.array([227, 66, 52]) / 255.0,
            'black': np.array([28, 28, 28]) / 255.0,
            'white': np.array([242, 242, 242]) / 255.0,
            'background': np.array([220, 200, 160]) / 255.0
        }

    def _create_vibrant_palette(self) -> dict:
        """Palette vivace per musica energica"""
        return {
            'electric_blue': np.array([0, 150, 255]) / 255.0,
            'neon_pink': np.array([255, 20, 147]) / 255.0,
            'bright_yellow': np.array([255, 215, 0]) / 255.0,
            'vivid_orange': np.array([255, 100, 0]) / 255.0,
            'deep_purple': np.array([100, 0, 200]) / 255.0,
            'lime': np.array([150, 255, 0]) / 255.0,
            'cyan': np.array([0, 255, 255]) / 255.0,
            'magenta': np.array([255, 0, 255]) / 255.0,
            'black': np.array([20, 20, 20]) / 255.0,
            'white': np.array([250, 250, 250]) / 255.0,
            'background': np.array([30, 30, 35]) / 255.0
        }

    def _create_canvas_texture(self) -> np.ndarray:
        """Crea texture canvas realistica"""
        # Noise base
        texture = np.random.randn(self.height//4, self.width//4) * 0.02

        # Blur per effetto canvas
        texture = gaussian_filter(texture, sigma=1.5)

        return texture

    def get_pitch_color(self, midi_pitch: int) -> np.ndarray:
        """
        Mappa pitch a colore usando ruota cromatica
        12 note → 12 colori distinti
        """
        # Estrai nota dalla pitch MIDI
        note_number = midi_pitch % 12

        color_wheel = [
            'yellow_ochre',      # C (0)
            'gold',              # C# (1)
            'burnt_sienna',      # D (2)
            'alizarin_crimson',  # D# (3)
            'vermilion',         # E (4)
            'rose',              # F (5)
            'cadmium_red',       # F# (6)
            'raw_umber',         # G (7)
            'payne_grey',        # G# (8)
            'cerulean_blue',     # A (9)
            'indigo',            # A# (10)
            'purple'             # B (11)
        ]

        base_color = self.colors.get(color_wheel[note_number], self.colors['yellow_ochre'])

        # Modula luminosità per ottava
        octave = midi_pitch // 12

        if octave < 4:  # Basso
            base_color = base_color * 0.6 + self.colors['ivory_black'] * 0.4
        elif octave > 5:  # Alto
            base_color = base_color * 0.7 + self.colors['titanium_white'] * 0.3

        return np.clip(base_color, 0, 1)

    def draw_brushstroke(self, x: float, y: float, angle: float, length: float,
                        width: float, color: np.ndarray, alpha: float = 0.7):
        """
        Simula pennellata realistica con texture
        """
        # Numero di "setole" nella pennellata
        num_bristles = int(width * 3)

        for i in range(num_bristles):
            # Offset casuale per setole
            offset = (i / num_bristles - 0.5) * width
            bristle_angle = angle + random.uniform(-0.1, 0.1)

            # Lunghezza variabile per texture
            bristle_length = length * random.uniform(0.8, 1.0)

            # Posizione setola
            sx = x + offset * np.cos(angle + np.pi/2)
            sy = y + offset * np.sin(angle + np.pi/2)

            ex = sx + bristle_length * np.cos(bristle_angle)
            ey = sy + bristle_length * np.sin(bristle_angle)

            # Alpha variabile per trasparenza
            bristle_alpha = alpha * random.uniform(0.6, 1.0)

            # Larghezza setola
            bristle_width = width / num_bristles * random.uniform(0.5, 1.5)

            self.ax.plot([sx, ex], [sy, ey],
                        color=color,
                        linewidth=bristle_width,
                        alpha=bristle_alpha,
                        solid_capstyle='round')

    def draw_impasto(self, x: float, y: float, size: float,
                    color: np.ndarray, technique: str):
        """
        Simula impasto (pittura materica, spessa)
        """
        # Numero di layers per impasto
        num_layers = random.randint(5, 12)

        for i in range(num_layers):
            # Offset casuale per texture 3D
            offset_x = random.gauss(0, size * 0.1)
            offset_y = random.gauss(0, size * 0.1)

            layer_size = size * random.uniform(0.7, 1.0)

            # Variazione colore per texture
            color_var = color + np.random.randn(3) * 0.05
            color_var = np.clip(color_var, 0, 1)

            # Alpha layers
            alpha = 0.3 + (i / num_layers) * 0.4

            if technique == 'staccato':
                # Punti spessi
                self.ax.add_patch(Circle((x + offset_x, y + offset_y),
                                        layer_size,
                                        facecolor=color_var,
                                        alpha=alpha,
                                        edgecolor='none'))
            else:
                # Forme irregolari
                num_points = random.randint(4, 7)
                angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
                points = []
                for angle in angles:
                    r = layer_size * random.uniform(0.7, 1.0)
                    px = x + offset_x + r * np.cos(angle)
                    py = y + offset_y + r * np.sin(angle)
                    points.append([px, py])

                self.ax.add_patch(Polygon(points,
                                         facecolor=color_var,
                                         alpha=alpha,
                                         edgecolor='none'))

    def draw_note_painterly(self, note: Dict, position: tuple):
        """
        Disegna nota con stile pittorico
        """
        x, y = position
        color = self.get_pitch_color(note['pitch'])
        tech = note['technique']

        # Velocity influenza saturazione E dimensione
        velocity_val = note.get('velocity_value', 0.5)

        # Desaturazione per piano
        if velocity_val < 0.5:
            gray = np.array([0.6, 0.6, 0.6])
            color = color * velocity_val * 2 + gray * (1 - velocity_val * 2)

        # Dimensione base
        base_size = 30 + note['duration'] * 80
        size = base_size * (0.5 + velocity_val)

        # Alpha
        alpha = 0.5 + velocity_val * 0.4

        if tech == 'vibrato':
            # Pennellate ondulate
            num_strokes = 8
            for i in range(num_strokes):
                angle = (i / num_strokes) * 2 * np.pi
                wave = np.sin(angle * 3) * 15
                length = 40 + wave
                self.draw_brushstroke(x, y, angle, length, size * 0.2, color, alpha)

        elif tech == 'slide':
            # Pennellata lunga diagonale
            angle = random.uniform(0, 2*np.pi)
            length = size * 2
            self.draw_brushstroke(x, y, angle, length, size * 0.3, color, alpha)

        elif tech == 'bend':
            # Pennellata curva
            t = np.linspace(0, np.pi, 20)
            curve_x = x + size * np.cos(t)
            curve_y = y + size * 0.5 * np.sin(t)

            for i in range(len(curve_x) - 1):
                self.ax.plot([curve_x[i], curve_x[i+1]],
                           [curve_y[i], curve_y[i+1]],
                           color=color,
                           linewidth=size * 0.2,
                           alpha=alpha,
                           solid_capstyle='round')

        elif tech == 'staccato':
            # Punti materici (impasto)
            self.draw_impasto(x, y, size * 0.5, color, 'staccato')

        else:  # legato, regular
            # Impasto circolare
            self.draw_impasto(x, y, size, color, 'regular')

    def create_melodic_path(self) -> List[tuple]:
        """
        Crea percorso melodico fluido
        """
        if not self.notes:
            return []

        positions = []

        for i, note in enumerate(self.notes):
            # X basato sul tempo (come spartito)
            x = 200 + note['start_time'] * 100

            # Y basato sul pitch (altezza)
            y = 200 + ((note['pitch'] - 40) / 40) * (self.height - 400)

            # Jitter controllato
            x += random.uniform(-30, 30)
            y += random.uniform(-30, 30)

            positions.append((x, y))

        # Disegna percorso connettivo
        if len(positions) > 1:
            xs = [p[0] for p in positions]
            ys = [p[1] for p in positions]

            self.ax.plot(xs, ys,
                        color=[0.3, 0.3, 0.3],
                        linewidth=1.5,
                        alpha=0.15,
                        linestyle='--',
                        zorder=0)

        return positions

    def render(self, output_file: str = "painterly_output.png"):
        """
        Renderizza opera completa
        """
        print(f"\n🎨 Rendering pittorico...")
        print(f"   Note: {len(self.notes)}")
        print(f"   Risoluzione: {self.width}x{self.height}")

        # Crea percorso melodico
        positions = self.create_melodic_path()

        # Disegna note
        for note, pos in zip(self.notes, positions):
            self.draw_note_painterly(note, pos)

        # Salva
        self.fig.savefig(output_file,
                        facecolor=self.colors['background'],
                        dpi=150,
                        bbox_inches='tight',
                        edgecolor='none')

        print(f"✅ Salvato: {output_file}")
        plt.close(self.fig)

        return output_file


def main():
    import sys

    if len(sys.argv) < 2:
        print("="*60)
        print("🎨 PAINTERLY RENDERER")
        print("="*60)
        print("\nRendering pittorico migliorato SENZA AI esterna")
        print("\nUSO:")
        print(f"  python {sys.argv[0]} <notes.json> [--palette <expanded|zorn|vibrant>]")
        print("\nESEMPIO:")
        print(f"  python {sys.argv[0]} 1207\(1\)_notes.json --palette expanded")
        print("="*60)
        sys.exit(1)

    notes_file = sys.argv[1]

    # Carica note
    with open(notes_file, 'r') as f:
        notes = json.load(f)

    # Palette
    palette = 'expanded'
    if '--palette' in sys.argv:
        idx = sys.argv.index('--palette')
        palette = sys.argv[idx + 1]

    # Render
    renderer = PainterlyRenderer(notes, palette=palette)

    base_name = notes_file.replace('_notes.json', '')
    output = f"{base_name}_painterly.png"

    renderer.render(output)

    print(f"\n✨ Completato!")
    print(f"   Input:  {notes_file}")
    print(f"   Output: {output}")


if __name__ == "__main__":
    main()
