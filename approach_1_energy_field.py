import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge
import numpy as np
import random
from typing import List, Dict

class EnergyFieldArt:
    """
    APPROCCIO 1: ENERGY FIELD
    Ogni nota = esplosione energetica radiale
    Non più timeline lineare, ma distribuzione organica sul canvas
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

        bg_color = self.colors['ochre']
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

    def get_energy_intensity(self, velocity: str) -> float:
        """Mappa velocity a intensità energetica (0-1)"""
        velocity_map = {'p': 0.3, 'mp': 0.5, 'mf': 0.7, 'f': 0.9, 'ff': 1.0}
        return velocity_map.get(velocity, 0.6)

    def distribute_positions(self, notes: List[Dict]) -> List[tuple]:
        """
        Distribuzione organica delle note sul canvas
        Usa una spirale di Fibonacci modificata per distribuzione naturale
        """
        positions = []
        n = len(notes)
        golden_angle = np.pi * (3 - np.sqrt(5))  # ~137.5 gradi

        for i in range(n):
            # Spirale logaritmica con jitter
            angle = i * golden_angle
            radius = 300 * np.sqrt(i / n)  # Spirale che si espande

            # Centro del canvas con offset
            cx = self.width / 2
            cy = self.height / 2

            # Posizione base
            x = cx + radius * np.cos(angle)
            y = cy + radius * np.sin(angle)

            # Jitter per naturalezza
            x += random.uniform(-50, 50)
            y += random.uniform(-50, 50)

            # Clamp ai bordi
            x = np.clip(x, 150, self.width - 150)
            y = np.clip(y, 150, self.height - 150)

            positions.append((x, y))

        return positions

    def draw_energy_explosion(self, x: float, y: float, note: Dict, color: np.ndarray):
        """
        Disegna un'esplosione energetica basata sulla tecnica
        """
        intensity = self.get_energy_intensity(note['velocity'])
        base_radius = 30 + note['duration'] * 50  # Durata → dimensione base

        tech = note['technique']

        if tech == 'staccato':
            # Esplosione a punti radianti
            num_dots = int(10 * intensity)
            for _ in range(num_dots):
                angle = random.uniform(0, 2*np.pi)
                r = random.uniform(base_radius * 0.3, base_radius)
                dx = x + r * np.cos(angle)
                dy = y + r * np.sin(angle)
                dot_size = random.uniform(2, 6) * intensity
                self.ax.add_patch(Circle((dx, dy), dot_size,
                                        facecolor=color, alpha=0.7))

        elif tech == 'powerchord':
            # Esplosione quadrata massiccia
            size = base_radius * 1.5
            angle = random.uniform(-15, 15)
            # Crea un quadrato ruotato usando Polygon
            cos_a = np.cos(np.radians(angle))
            sin_a = np.sin(np.radians(angle))
            half = size / 2
            corners = [[-half, -half], [half, -half], [half, half], [-half, half]]
            rotated_corners = []
            for cx, cy in corners:
                rx = x + cx * cos_a - cy * sin_a
                ry = y + cx * sin_a + cy * cos_a
                rotated_corners.append([rx, ry])
            from matplotlib.patches import Polygon
            self.ax.add_patch(Polygon(rotated_corners, facecolor=color, alpha=0.85))

            # Onde d'urto circolari
            for r in [size * 0.8, size * 1.2, size * 1.6]:
                self.ax.add_patch(Circle((x, y), r,
                                        facecolor='none',
                                        edgecolor=color,
                                        linewidth=2 * intensity,
                                        alpha=0.3))

        elif tech == 'vibrato':
            # Onde concentriche vibranti
            num_waves = 8
            for i in range(num_waves):
                r = base_radius * (0.3 + i * 0.15)
                alpha = 0.6 - i * 0.06
                self.ax.add_patch(Circle((x, y), r,
                                        facecolor='none',
                                        edgecolor=color,
                                        linewidth=1.5,
                                        alpha=alpha))

        elif tech == 'slide':
            # Raggio direzionale con scia
            angle = random.uniform(0, 2*np.pi)
            length = base_radius * 2
            end_x = x + length * np.cos(angle)
            end_y = y + length * np.sin(angle)

            # Raggio principale
            self.ax.plot([x, end_x], [y, end_y],
                        color=color, linewidth=4*intensity,
                        alpha=0.8, solid_capstyle='round')

            # Particelle lungo il raggio
            num_particles = 10
            for i in range(num_particles):
                t = i / num_particles
                px = x + (end_x - x) * t
                py = y + (end_y - y) * t
                psize = (1 - t) * 4 * intensity
                self.ax.add_patch(Circle((px, py), psize,
                                        facecolor=color, alpha=0.6))

        elif tech == 'bend':
            # Arco energetico curvato
            angles = np.linspace(0, np.pi * 1.5, 50)
            radius_curve = base_radius
            curve_x = x + radius_curve * np.cos(angles)
            curve_y = y + radius_curve * np.sin(angles)

            self.ax.plot(curve_x, curve_y, color=color,
                        linewidth=3*intensity, alpha=0.8,
                        solid_capstyle='round')

        elif tech == 'tapping':
            # Impulsi concentrici luminosi
            num_rings = 5
            for i in range(num_rings):
                r = base_radius * (0.2 + i * 0.25)
                # Alternate filled/empty
                if i % 2 == 0:
                    self.ax.add_patch(Circle((x, y), r,
                                            facecolor=color, alpha=0.6))
                else:
                    self.ax.add_patch(Circle((x, y), r,
                                            facecolor='none',
                                            edgecolor=color,
                                            linewidth=2,
                                            alpha=0.5))

        elif tech == 'harmonic_natural':
            # Alone eterea espansa
            for r_mult in [1.0, 1.5, 2.0]:
                r = base_radius * r_mult
                self.ax.add_patch(Circle((x, y), r,
                                        facecolor=color,
                                        alpha=0.15 / r_mult))

        elif tech == 'harmonic_artificial':
            # Raggi affilati a stella
            num_rays = 8
            for i in range(num_rays):
                angle = i * (2*np.pi / num_rays)
                length = base_radius * 1.2
                end_x = x + length * np.cos(angle)
                end_y = y + length * np.sin(angle)
                self.ax.plot([x, end_x], [y, end_y],
                            color=color, linewidth=2*intensity,
                            alpha=0.7, solid_capstyle='butt')

        elif tech == 'dive':
            # Spirale discendente
            t = np.linspace(0, 4*np.pi, 100)
            spiral_r = base_radius * (1 - t/(4*np.pi)) * 0.5
            spiral_x = x + spiral_r * np.cos(t)
            spiral_y = y + spiral_r * np.sin(t) - t * 5

            self.ax.plot(spiral_x, spiral_y, color=color,
                        linewidth=2*intensity, alpha=0.7)

        else:  # legato, hammer_on, default
            # Esplosione radiale sfumata
            num_layers = 8
            for i in range(num_layers):
                r = base_radius * (1 - i/num_layers)
                alpha = 0.4 * (i/num_layers)
                self.ax.add_patch(Circle((x, y), r,
                                        facecolor=color, alpha=alpha))

    def create_artwork(self, filename: str = 'energy_field_art.png'):
        notes = self.parse_johnny_b_goode_riff()
        positions = self.distribute_positions(notes)

        # Disegna le esplosioni energetiche
        for note, (x, y) in zip(notes, positions):
            color = self.get_note_color(note['note'])
            self.draw_energy_explosion(x, y, note, color)

        # Linee di connessione sottili tra note successive (opzionale)
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i+1]
            color = self.get_note_color(notes[i]['note'])
            self.ax.plot([x1, x2], [y1, y2],
                        color=color, linewidth=0.5,
                        alpha=0.2, linestyle='--')

        self.fig.savefig(filename, facecolor=self.colors['ochre'],
                        dpi=150, bbox_inches='tight', edgecolor='none')
        print(f"✅ Energy Field artwork: {filename}")

if __name__ == "__main__":
    artist = EnergyFieldArt()
    artist.create_artwork()
    plt.show()
