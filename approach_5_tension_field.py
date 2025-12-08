import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Wedge
from matplotlib.path import Path
import matplotlib.patches as mpatches
import numpy as np
import random
from typing import List, Dict, Tuple

class TensionFieldArt:
    """
    APPROCCIO 5: TENSION FIELD
    Mappa tensione armonica → tensione visiva
    Note consonanti = forme morbide, dissonanti = forme angolari
    I campi interagiscono attraverso linee di forza
    """
    def __init__(self):
        self.colors = {
            'ochre': np.array([196, 164, 106]) / 255.0,
            'vermilion': np.array([227, 66, 52]) / 255.0,
            'black': np.array([28, 28, 28]) / 255.0,
            'white': np.array([242, 242, 242]) / 255.0
        }

        self.note_colors = {
            'A': 'ochre',
            'C': 'vermilion',
            'D': 'black',
            'E': 'white',
            'G': 'ochre'
        }

        # Tensione armonica delle note nella scala di A minor pentatonic
        # A (tonica) = 0, E (quinta) = bassa, C (terza minore) = media, D (quarta) = media, G (settima) = alta
        self.harmonic_tension = {
            'A': 0.0,   # Tonica - massima consonanza
            'E': 0.2,   # Quinta - molto consonante
            'C': 0.5,   # Terza minore - media tensione
            'D': 0.6,   # Quarta - media-alta tensione
            'G': 0.8    # Settima minore - alta tensione
        }

        self.width = 1600
        self.height = 1000
        self.fig, self.ax = plt.subplots(figsize=(self.width/150, self.height/150), dpi=150)

        # Sfondo neutro
        bg_color = self.colors['ochre'] * 0.5 + self.colors['white'] * 0.5
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.axis('off')

        random.seed(42)
        np.random.seed(42)

    def parse_johnny_b_goode_riff(self) -> List[Dict]:
        riff_notes = [
            {'note': 'A', 'fret': 5, 'string': 6, 'duration': 0.5, 'velocity': 'mf', 'technique': 'staccato'},
            {'note': 'C', 'fret': 8, 'string': 6, 'duration': 0.5, 'velocity': 'f', 'technique': 'legato'},
            {'note': 'D', 'fret': 5, 'string': 4, 'duration': 0.25, 'velocity': 'f', 'technique': 'slide'},
            {'note': 'A', 'fret': 7, 'string': 5, 'duration': 0.5, 'velocity': 'mf', 'technique': 'hammer_on'},
            {'note': 'C', 'fret': 8, 'string': 5, 'duration': 0.25, 'velocity': 'f', 'technique': 'bend'},
            {'note': 'D', 'fret': 7, 'string': 3, 'duration': 0.75, 'velocity': 'f', 'technique': 'vibrato'},
            {'note': 'E', 'fret': 8, 'string': 1, 'duration': 0.5, 'velocity': 'f', 'technique': 'harmonic_natural'},
            {'note': 'G', 'fret': 3, 'string': 1, 'duration': 0.5, 'velocity': 'mp', 'technique': 'legato'},
            {'note': 'A', 'fret': 5, 'string': 1, 'duration': 1.0, 'velocity': 'f', 'technique': 'powerchord'},
            {'note': 'C', 'fret': 8, 'string': 6, 'duration': 0.25, 'velocity': 'mf', 'technique': 'tapping'},
            {'note': 'D', 'fret': 5, 'string': 4, 'duration': 0.5, 'velocity': 'f', 'technique': 'dive'},
            {'note': 'G', 'fret': 3, 'string': 1, 'duration': 0.25, 'velocity': 'p', 'technique': 'harmonic_artificial'},
        ]

        string_tuning = [40, 45, 50, 55, 59, 64]
        processed_notes = []

        for i, note_data in enumerate(riff_notes):
            midi_pitch = string_tuning[note_data['string'] - 1] + note_data['fret']
            processed_note = {
                'note': note_data['note'],
                'pitch': midi_pitch,
                'duration': note_data['duration'],
                'velocity': note_data['velocity'],
                'technique': note_data['technique'],
                'tension': self.harmonic_tension.get(note_data['note'], 0.5),
                'index': i
            }
            processed_notes.append(processed_note)
        return processed_notes

    def get_note_color(self, note: str) -> np.ndarray:
        if note == 'G':
            base_color = (self.colors['ochre'] + self.colors['black']) / 2
        else:
            color_key = self.note_colors.get(note, 'ochre')
            base_color = self.colors[color_key]
        return np.clip(base_color, 0, 1)

    def get_shape_spikiness(self, tension: float) -> int:
        """
        Più alta la tensione, più spigolosa la forma
        Ritorna numero di spigoli
        """
        if tension < 0.3:
            return 0  # Circolare
        elif tension < 0.5:
            return 5  # Pentagono
        elif tension < 0.7:
            return 4  # Quadrato
        else:
            return 3  # Triangolo (più spigoloso)

    def draw_tension_shape(self, x: float, y: float, note: Dict, color: np.ndarray):
        """
        Disegna forma basata sulla tensione armonica
        """
        tension = note['tension']
        size = 40 + note['duration'] * 60

        spikiness = self.get_shape_spikiness(tension)

        if spikiness == 0:
            # Forma circolare morbida (consonanza)
            num_circles = 5
            for i in range(num_circles):
                radius = size * (1 - i/num_circles*0.4)
                alpha = 0.6 - i * 0.1
                self.ax.add_patch(Circle((x, y), radius,
                                        facecolor=color, alpha=alpha,
                                        edgecolor='none'))
        else:
            # Poligono spigoloso (tensione)
            num_points = spikiness

            # Genera poligono irregolare
            angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)

            # Irregolarità aumenta con tensione
            irregularity = tension * 0.4

            points = []
            for angle in angles:
                # Raggio varia con irregolarità
                r = size * (1 + random.uniform(-irregularity, irregularity))
                px = x + r * np.cos(angle)
                py = y + r * np.sin(angle)
                points.append([px, py])

            # Disegna poligono con layers per profondità
            num_layers = 3
            for i in range(num_layers):
                scale = 1 - i * 0.15
                scaled_points = []
                for px, py in points:
                    spx = x + (px - x) * scale
                    spy = y + (py - y) * scale
                    scaled_points.append([spx, spy])

                alpha = 0.5 - i * 0.1
                polygon = Polygon(scaled_points, closed=True,
                                facecolor=color, alpha=alpha,
                                edgecolor=color*0.6, linewidth=2)
                self.ax.add_patch(polygon)

    def draw_force_lines(self, notes_positions: List[Tuple[float, float, Dict]]):
        """
        Disegna linee di forza tra note
        Più forte l'attrazione/repulsione, più intensa la linea
        """
        for i, (x1, y1, note1) in enumerate(notes_positions):
            for j, (x2, y2, note2) in enumerate(notes_positions):
                if i >= j:
                    continue

                # Calcola "affinità" armonica
                tension_diff = abs(note1['tension'] - note2['tension'])

                # Note con tensione simile si attraggono
                # Note con tensione opposta si respingono
                if tension_diff < 0.3:
                    # Attrazione - linea continua
                    strength = (0.3 - tension_diff) / 0.3
                    color1 = self.get_note_color(note1['note'])
                    color2 = self.get_note_color(note2['note'])
                    blend_color = (color1 + color2) / 2

                    # Linea curva
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    # Control point offset
                    offset = random.uniform(-50, 50)

                    verts = [(x1, y1),
                            (mid_x + offset, mid_y + offset),
                            (x2, y2)]
                    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
                    path = Path(verts, codes)

                    patch = mpatches.PathPatch(path, facecolor='none',
                                              edgecolor=blend_color,
                                              linewidth=strength * 2,
                                              alpha=strength * 0.4)
                    self.ax.add_patch(patch)

                elif tension_diff > 0.5:
                    # Repulsione - linea spezzata
                    strength = (tension_diff - 0.5) / 0.5
                    color1 = self.get_note_color(note1['note'])

                    # Linea con "schegge"
                    num_segments = 5
                    for k in range(num_segments):
                        t1 = k / num_segments
                        t2 = (k + 1) / num_segments

                        sx1 = x1 + (x2 - x1) * t1 + random.uniform(-20, 20)
                        sy1 = y1 + (y2 - y1) * t1 + random.uniform(-20, 20)
                        sx2 = x1 + (x2 - x1) * t2 + random.uniform(-20, 20)
                        sy2 = y1 + (y2 - y1) * t2 + random.uniform(-20, 20)

                        self.ax.plot([sx1, sx2], [sy1, sy2],
                                   color=color1, linewidth=strength * 1.5,
                                   alpha=strength * 0.3,
                                   linestyle='--')

    def draw_technique_modifier(self, x: float, y: float, note: Dict, color: np.ndarray):
        """
        Aggiunte visive basate sulla tecnica
        """
        tech = note['technique']
        tension = note['tension']

        if tech == 'bend':
            # Arco di tensione
            angle_start = random.uniform(0, 180)
            angle_extent = 120
            radius = 50 + note['duration'] * 30

            wedge = Wedge((x, y), radius, angle_start, angle_start + angle_extent,
                         facecolor='none', edgecolor=color,
                         linewidth=3 * (1 + tension), alpha=0.6)
            self.ax.add_patch(wedge)

        elif tech == 'vibrato':
            # Onde di tensione
            num_waves = int(4 + tension * 6)
            for i in range(num_waves):
                angle = (i / num_waves) * 2 * np.pi
                r = 40 + i * 8
                alpha_val = max(0.05, 0.3 - i*0.05)  # Clamp to avoid negative
                self.ax.add_patch(Circle((x, y), r,
                                        facecolor='none',
                                        edgecolor=color,
                                        linewidth=1.5,
                                        alpha=alpha_val))

        elif tech == 'slide':
            # Freccia direzionale
            angle = random.uniform(0, 2*np.pi)
            length = 60 + tension * 40
            end_x = x + length * np.cos(angle)
            end_y = y + length * np.sin(angle)

            self.ax.annotate('', xy=(end_x, end_y), xytext=(x, y),
                           arrowprops=dict(arrowstyle='->', lw=2 + tension*2,
                                         color=color, alpha=0.7))

        elif tech == 'powerchord':
            # Espansione quadrata
            size = 50 + note['duration'] * 40
            for i in range(3):
                s = size * (1 + i * 0.3)
                rect_points = [
                    [x - s, y - s],
                    [x + s, y - s],
                    [x + s, y + s],
                    [x - s, y + s]
                ]
                polygon = Polygon(rect_points, closed=True,
                                facecolor='none',
                                edgecolor=color,
                                linewidth=2,
                                alpha=0.4 - i*0.1)
                self.ax.add_patch(polygon)

    def position_note(self, note: Dict, index: int, total: int) -> Tuple[float, float]:
        """
        Posiziona le note considerando sia sequenza che tensione
        """
        # X: basato sulla sequenza temporale
        x_base = 150 + (index / total) * (self.width - 300)

        # Y: basato sulla tensione (alta tensione = alto, bassa = basso)
        y_base = 200 + (1 - note['tension']) * (self.height - 400)

        # Jitter
        x = x_base + random.uniform(-60, 60)
        y = y_base + random.uniform(-60, 60)

        return x, y

    def create_artwork(self, filename: str = 'tension_field_art.png'):
        notes = self.parse_johnny_b_goode_riff()

        # Posiziona le note
        notes_positions = []
        for i, note in enumerate(notes):
            x, y = self.position_note(note, i, len(notes))
            notes_positions.append((x, y, note))

        # Prima: disegna linee di forza (sotto)
        self.draw_force_lines(notes_positions)

        # Poi: disegna forme di tensione (sopra)
        for x, y, note in notes_positions:
            color = self.get_note_color(note['note'])
            self.draw_tension_shape(x, y, note, color)
            self.draw_technique_modifier(x, y, note, color)

        bg_color = self.colors['ochre'] * 0.5 + self.colors['white'] * 0.5

        self.fig.savefig(filename, facecolor=bg_color,
                        dpi=150, bbox_inches='tight', edgecolor='none')
        print(f"✅ Tension Field artwork: {filename}")

if __name__ == "__main__":
    artist = TensionFieldArt()
    artist.create_artwork()
    plt.show()
