import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyBboxPatch
from matplotlib.path import Path
import matplotlib.patches as mpatches
import numpy as np
import random
from typing import List, Dict

class OrganicGrowthArt:
    """
    APPROCCIO 4: ORGANIC GROWTH
    Ogni nota è un seme che genera crescita organica
    Forme che si sviluppano come organismi naturali
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

        # Sfondo come "terreno"
        bg_color = self.colors['ochre'] * 0.7 + self.colors['white'] * 0.3
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

    def get_note_color(self, note: str) -> np.ndarray:
        if note == 'G':
            base_color = (self.colors['ochre'] + self.colors['black']) / 2
        else:
            color_key = self.note_colors.get(note, 'ochre')
            base_color = self.colors[color_key]
        return np.clip(base_color, 0, 1)

    def get_growth_intensity(self, velocity: str) -> float:
        """Intensità di crescita basata su velocity"""
        velocity_map = {'p': 0.4, 'mp': 0.6, 'mf': 0.8, 'f': 1.0, 'ff': 1.2}
        return velocity_map.get(velocity, 0.7)

    def grow_branches(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Crescita ramificata come un albero"""
        intensity = self.get_growth_intensity(note['velocity'])
        num_branches = int(3 + note['duration'] * 5)
        branch_length = 40 + note['duration'] * 60

        for i in range(num_branches):
            angle = random.uniform(0, 2*np.pi)

            # Ramificazione principale
            segments = int(4 + note['duration'] * 3)
            current_x, current_y = x, y
            current_angle = angle

            for seg in range(segments):
                # Lunghezza del segmento decresce
                seg_length = branch_length / (seg + 1) * intensity
                # Angolo varia leggermente
                current_angle += random.uniform(-0.5, 0.5)

                end_x = current_x + seg_length * np.cos(current_angle)
                end_y = current_y + seg_length * np.sin(current_angle)

                # Spessore decresce
                width = (5 - seg) * intensity
                width = max(width, 1)

                self.ax.plot([current_x, end_x], [current_y, end_y],
                           color=color, linewidth=width,
                           alpha=0.7, solid_capstyle='round')

                # Germogli laterali occasionali
                if random.random() < 0.4:
                    sprout_angle = current_angle + random.choice([-np.pi/3, np.pi/3])
                    sprout_length = seg_length * 0.5
                    sprout_x = end_x + sprout_length * np.cos(sprout_angle)
                    sprout_y = end_y + sprout_length * np.sin(sprout_angle)
                    self.ax.plot([end_x, sprout_x], [end_y, sprout_y],
                               color=color, linewidth=width*0.5,
                               alpha=0.6, solid_capstyle='round')

                current_x, current_y = end_x, end_y

    def grow_cells(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Crescita cellulare organica"""
        intensity = self.get_growth_intensity(note['velocity'])
        num_cells = int(5 + note['duration'] * 10)

        cells = [(x, y, 8 * intensity)]  # (x, y, radius)

        for _ in range(num_cells):
            # Scegli una cellula esistente da cui crescere
            parent = random.choice(cells)
            angle = random.uniform(0, 2*np.pi)
            distance = parent[2] + random.uniform(5, 15)

            new_x = parent[0] + distance * np.cos(angle)
            new_y = parent[1] + distance * np.sin(angle)
            new_radius = random.uniform(4, 10) * intensity

            cells.append((new_x, new_y, new_radius))

        # Disegna le cellule
        for cx, cy, radius in cells:
            self.ax.add_patch(Circle((cx, cy), radius,
                                    facecolor=color, alpha=0.6,
                                    edgecolor=color*0.7, linewidth=1))

    def grow_roots(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Crescita radicale verso il basso"""
        intensity = self.get_growth_intensity(note['velocity'])
        num_roots = int(3 + note['duration'] * 4)

        for i in range(num_roots):
            # Radici tendono verso il basso ma con variazione
            base_angle = np.pi/2 + random.uniform(-np.pi/4, np.pi/4)

            current_x, current_y = x, y
            current_angle = base_angle
            segments = int(5 + note['duration'] * 4)

            for seg in range(segments):
                seg_length = 15 + random.uniform(5, 15)
                # Le radici si piegano
                current_angle += random.uniform(-0.3, 0.3)

                end_x = current_x + seg_length * np.cos(current_angle)
                end_y = current_y + seg_length * np.sin(current_angle)

                width = (6 - seg*0.5) * intensity
                width = max(width, 0.5)

                self.ax.plot([current_x, end_x], [current_y, end_y],
                           color=color, linewidth=width,
                           alpha=0.65, solid_capstyle='round')

                current_x, current_y = end_x, end_y

    def grow_tendrils(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Viticci spiralati"""
        intensity = self.get_growth_intensity(note['velocity'])
        num_tendrils = int(2 + note['duration'] * 3)

        for _ in range(num_tendrils):
            angle = random.uniform(0, 2*np.pi)
            t = np.linspace(0, 3*np.pi, 50)

            # Spirale logaritmica
            r = t * 8 * intensity
            spiral_x = x + r * np.cos(t + angle)
            spiral_y = y + r * np.sin(t + angle)

            self.ax.plot(spiral_x, spiral_y, color=color,
                        linewidth=2*intensity, alpha=0.7,
                        solid_capstyle='round')

            # Puntini lungo il viticcio
            for i in range(0, len(spiral_x), 5):
                self.ax.add_patch(Circle((spiral_x[i], spiral_y[i]),
                                        1.5*intensity,
                                        facecolor=color, alpha=0.8))

    def grow_petals(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Crescita a petali come fiore"""
        intensity = self.get_growth_intensity(note['velocity'])
        num_petals = int(5 + note['duration'] * 3)
        petal_length = 30 + note['duration'] * 40

        for i in range(num_petals):
            angle = (i / num_petals) * 2 * np.pi

            # Crea forma petalo con Bezier
            base_x = x
            base_y = y

            tip_x = x + petal_length * intensity * np.cos(angle)
            tip_y = y + petal_length * intensity * np.sin(angle)

            # Punti di controllo per larghezza petalo
            mid_t = 0.6
            mid_x = x + petal_length * intensity * mid_t * np.cos(angle)
            mid_y = y + petal_length * intensity * mid_t * np.sin(angle)

            width_offset = 15 * intensity
            left_x = mid_x + width_offset * np.cos(angle + np.pi/2)
            left_y = mid_y + width_offset * np.sin(angle + np.pi/2)
            right_x = mid_x + width_offset * np.cos(angle - np.pi/2)
            right_y = mid_y + width_offset * np.sin(angle - np.pi/2)

            # Poligono petalo
            petal_points = [
                [base_x, base_y],
                [left_x, left_y],
                [tip_x, tip_y],
                [right_x, right_y]
            ]

            polygon = Polygon(petal_points, closed=True,
                            facecolor=color, alpha=0.5,
                            edgecolor=color*0.7, linewidth=1.5)
            self.ax.add_patch(polygon)

        # Centro del fiore
        self.ax.add_patch(Circle((x, y), 8*intensity,
                                facecolor=color*0.6, alpha=0.9))

    def grow_explosion(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Esplosione organica"""
        intensity = self.get_growth_intensity(note['velocity'])
        num_rays = int(8 + note['duration'] * 10)

        for i in range(num_rays):
            angle = random.uniform(0, 2*np.pi)
            length = random.uniform(20, 60) * intensity

            # Raggio irregolare
            points = [(x, y)]
            current_x, current_y = x, y

            num_segments = random.randint(3, 6)
            for seg in range(num_segments):
                seg_len = length / num_segments
                angle += random.uniform(-0.4, 0.4)

                end_x = current_x + seg_len * np.cos(angle)
                end_y = current_y + seg_len * np.sin(angle)

                points.append((end_x, end_y))
                current_x, current_y = end_x, end_y

            # Disegna linea spezzata
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            self.ax.plot(xs, ys, color=color,
                        linewidth=2*intensity, alpha=0.7,
                        solid_capstyle='round')

    def position_seed(self, note: Dict, index: int, total: int) -> tuple:
        """Posiziona il seme iniziale"""
        # Distribuzione su griglia con jitter
        cols = 4
        rows = 3

        col = index % cols
        row = index // cols

        x = 200 + col * (self.width - 400) / (cols - 1) + random.uniform(-80, 80)
        y = 200 + row * (self.height - 400) / (rows - 1) + random.uniform(-80, 80)

        return x, y

    def create_artwork(self, filename: str = 'organic_growth_art.png'):
        notes = self.parse_johnny_b_goode_riff()

        for i, note in enumerate(notes):
            x, y = self.position_seed(note, i, len(notes))
            color = self.get_note_color(note['note'])

            tech = note['technique']

            if tech == 'staccato':
                self.grow_cells(x, y, note, color)
            elif tech == 'legato':
                self.grow_tendrils(x, y, note, color)
            elif tech == 'slide':
                self.grow_branches(x, y, note, color)
            elif tech == 'powerchord':
                self.grow_explosion(x, y, note, color)
            elif tech == 'vibrato':
                self.grow_tendrils(x, y, note, color)
            elif tech == 'bend':
                self.grow_branches(x, y, note, color)
            elif tech in ['harmonic_natural', 'harmonic_artificial']:
                self.grow_petals(x, y, note, color)
            elif tech == 'dive':
                self.grow_roots(x, y, note, color)
            else:
                self.grow_branches(x, y, note, color)

        bg_color = self.colors['ochre'] * 0.7 + self.colors['white'] * 0.3

        self.fig.savefig(filename, facecolor=bg_color,
                        dpi=150, bbox_inches='tight', edgecolor='none')
        print(f"✅ Organic Growth artwork: {filename}")

if __name__ == "__main__":
    artist = OrganicGrowthArt()
    artist.create_artwork()
    plt.show()
