import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Ellipse
import numpy as np
import random
from typing import List, Dict

class LayeredTransparencyArt:
    """
    APPROCCIO 2: LAYERED TRANSPARENCY (Color Field)
    Grandi campi di colore semi-trasparenti che si sovrappongono
    La profondità emerge dal blending ottico
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

        self.width = 1600
        self.height = 1000
        self.fig, self.ax = plt.subplots(figsize=(self.width/150, self.height/150), dpi=150)

        bg_color = self.colors['white'] * 0.95  # Sfondo quasi bianco
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
                'index': i
            }
            processed_notes.append(processed_note)
        return processed_notes

    def get_note_color(self, note: str, pitch: int) -> np.ndarray:
        """Colore base modulato dall'altezza"""
        if note == 'G':
            base_color = (self.colors['ochre'] + self.colors['black']) / 2
        else:
            color_key = self.note_colors.get(note, 'ochre')
            base_color = self.colors[color_key]

        # Modula luminosità basata sul pitch
        # Pitch alto → più chiaro, pitch basso → più scuro
        pitch_factor = (pitch - 40) / 40  # Normalizzato 0-1
        if pitch_factor > 0.5:
            # Schiarisci verso white
            base_color = base_color * (1 - pitch_factor*0.3) + self.colors['white'] * (pitch_factor*0.3)
        else:
            # Scurisci verso black
            base_color = base_color * (1 - pitch_factor*0.3) + self.colors['black'] * (pitch_factor*0.3)

        return np.clip(base_color, 0, 1)

    def get_alpha(self, velocity: str, technique: str) -> float:
        """Trasparenza basata su velocity e tecnica"""
        base_alpha = {
            'p': 0.15,
            'mp': 0.25,
            'mf': 0.35,
            'f': 0.45,
            'ff': 0.55
        }.get(velocity, 0.3)

        # Tecniche più "eteree" hanno alpha minore
        if technique in ['harmonic_natural', 'harmonic_artificial']:
            base_alpha *= 0.6
        elif technique in ['staccato']:
            base_alpha *= 1.2

        return min(base_alpha, 0.6)

    def draw_color_field(self, note: Dict, layer_index: int, total_layers: int):
        """
        Disegna un campo di colore basato sulla nota
        La posizione è determinata dalla sequenza e dal pitch
        """
        color = self.get_note_color(note['note'], note['pitch'])
        alpha = self.get_alpha(note['velocity'], note['technique'])

        # Posizionamento: distribuito sul canvas
        # X: basato sull'indice nella sequenza
        # Y: basato sul pitch
        x_base = (layer_index / total_layers) * self.width
        y_base = ((note['pitch'] - 40) / 40) * self.height

        # Jitter per naturalezza
        x_jitter = random.uniform(-100, 100)
        y_jitter = random.uniform(-100, 100)

        x = x_base + x_jitter
        y = y_base + y_jitter

        # Dimensione basata sulla durata
        base_size = 200 + note['duration'] * 300
        width = base_size + random.uniform(-50, 50)
        height = base_size * random.uniform(0.6, 1.4)

        tech = note['technique']

        if tech == 'staccato':
            # Campo circolare netto
            radius = base_size / 2
            circle = plt.Circle((x, y), radius, color=color, alpha=alpha)
            self.ax.add_patch(circle)

        elif tech == 'legato':
            # Campo ellittico orizzontale sfumato
            # Crea effetto sfumato con multiple ellissi concentriche
            num_layers = 5
            for i in range(num_layers):
                scale = 1 - (i / num_layers) * 0.3
                layer_alpha = alpha * (1 - i / num_layers)
                ellipse = Ellipse((x, y), width*scale, height*scale*0.5,
                                 angle=random.uniform(-15, 15),
                                 color=color, alpha=layer_alpha)
                self.ax.add_patch(ellipse)

        elif tech == 'powerchord':
            # Campo rettangolare massiccio
            rect_width = width * 1.2
            rect_height = height * 0.8
            # Multiple layers per effetto materico
            for i in range(3):
                offset = i * 10
                layer_alpha = alpha * (1 - i * 0.2)
                rect = Rectangle((x - rect_width/2 + offset, y - rect_height/2 - offset),
                               rect_width, rect_height,
                               angle=random.uniform(-5, 5),
                               color=color, alpha=layer_alpha)
                self.ax.add_patch(rect)

        elif tech == 'vibrato':
            # Campo con bordi ondulati
            # Simula con ellissi multiple sfalsate
            num_waves = 8
            for i in range(num_waves):
                angle = (i / num_waves) * 360
                offset_x = 15 * np.cos(np.radians(angle * 3))
                offset_y = 15 * np.sin(np.radians(angle * 3))
                ellipse = Ellipse((x + offset_x, y + offset_y),
                                width * 0.9, height * 0.9,
                                angle=angle,
                                color=color, alpha=alpha/2)
                self.ax.add_patch(ellipse)

        elif tech == 'slide':
            # Campo allungato diagonale
            angle = random.uniform(20, 70)
            rect = Rectangle((x - width/2, y - height*0.3/2),
                           width * 1.5, height * 0.3,
                           angle=angle,
                           color=color, alpha=alpha)
            self.ax.add_patch(rect)

        elif tech == 'bend':
            # Campo curvato (simulato con ellissi sfalsate)
            num_segments = 5
            for i in range(num_segments):
                t = i / num_segments
                curve_x = x + t * 80 - 40
                curve_y = y + 50 * np.sin(t * np.pi)
                ellipse = Ellipse((curve_x, curve_y),
                                width/num_segments * 1.5, height,
                                angle=t * 45,
                                color=color, alpha=alpha)
                self.ax.add_patch(ellipse)

        elif tech in ['harmonic_natural', 'harmonic_artificial']:
            # Campo molto sfumato e grande
            num_halos = 6
            for i in range(num_halos):
                scale = 1 + i * 0.3
                layer_alpha = alpha * 0.3 / (i + 1)
                circle = plt.Circle((x, y), base_size/2 * scale,
                                  color=color, alpha=layer_alpha)
                self.ax.add_patch(circle)

        elif tech == 'tapping':
            # Campi concentrici alternati
            for i in range(4):
                radius = (base_size/2) * (0.3 + i * 0.25)
                circle = plt.Circle((x, y), radius,
                                  color=color, alpha=alpha * (1 - i*0.15))
                self.ax.add_patch(circle)

        else:  # default
            # Campo ellittico standard
            ellipse = Ellipse((x, y), width, height,
                            angle=random.uniform(-30, 30),
                            color=color, alpha=alpha)
            self.ax.add_patch(ellipse)

    def create_artwork(self, filename: str = 'layered_transparency_art.png'):
        notes = self.parse_johnny_b_goode_riff()

        # Ordina le note per creare stratificazione interessante
        # Prima le note più scure (sotto), poi le più chiare (sopra)
        sorted_notes = sorted(enumerate(notes),
                            key=lambda x: (x[1]['pitch'], -ord(x[1]['note'][0])))

        # Disegna i layer dal più scuro al più chiaro
        for original_idx, note in sorted_notes:
            self.draw_color_field(note, original_idx, len(notes))

        self.fig.savefig(filename, facecolor=self.colors['white']*0.95,
                        dpi=150, bbox_inches='tight', edgecolor='none')
        print(f"✅ Layered Transparency artwork: {filename}")

if __name__ == "__main__":
    artist = LayeredTransparencyArt()
    artist.create_artwork()
    plt.show()
