import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import random
from typing import List, Dict

class ParticleSystemArt:
    """
    APPROCCIO 3: PARTICLE SYSTEM
    Ogni nota genera un sistema di particelle che si disperde
    Pattern di dispersione basato sulla tecnica
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

        # Sfondo scuro per far risaltare le particelle
        bg_color = self.colors['black'] * 1.1
        bg_color = np.clip(bg_color, 0, 0.15)  # Grigio molto scuro
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

    def get_particle_count(self, velocity: str, duration: float) -> int:
        """Numero di particelle basato su velocity e durata"""
        base_count = {
            'p': 30,
            'mp': 60,
            'mf': 100,
            'f': 150,
            'ff': 200
        }.get(velocity, 80)

        # Durata influenza il numero
        return int(base_count * (0.5 + duration))

    def generate_particles_staccato(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Esplosione radiale uniforme"""
        num_particles = self.get_particle_count(note['velocity'], note['duration'])

        for _ in range(num_particles):
            angle = random.uniform(0, 2*np.pi)
            distance = random.uniform(10, 80)

            px = x + distance * np.cos(angle)
            py = y + distance * np.sin(angle)

            # Dimensione particella
            size = random.uniform(1, 4)
            alpha = random.uniform(0.4, 0.9)

            self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def generate_particles_slide(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Scia direzionale"""
        num_particles = self.get_particle_count(note['velocity'], note['duration'])
        angle = random.uniform(0, 2*np.pi)

        for i in range(num_particles):
            t = i / num_particles
            distance = t * 150

            # Leggera dispersione laterale
            lateral = random.gauss(0, 10)

            px = x + distance * np.cos(angle) + lateral * np.cos(angle + np.pi/2)
            py = y + distance * np.sin(angle) + lateral * np.sin(angle + np.pi/2)

            size = (1 - t) * 3 + 1
            alpha = (1 - t) * 0.6 + 0.3

            self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def generate_particles_vibrato(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Onde di particelle"""
        num_particles = self.get_particle_count(note['velocity'], note['duration'])

        for i in range(num_particles):
            angle = random.uniform(0, 2*np.pi)
            base_distance = random.uniform(20, 100)

            # Modulazione oscillante
            wave = np.sin(angle * 5) * 15

            px = x + (base_distance + wave) * np.cos(angle)
            py = y + (base_distance + wave) * np.sin(angle)

            size = random.uniform(1.5, 4)
            alpha = random.uniform(0.5, 0.8)

            self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def generate_particles_powerchord(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Esplosione massiccia densa"""
        num_particles = self.get_particle_count(note['velocity'], note['duration']) * 2

        for _ in range(num_particles):
            angle = random.uniform(0, 2*np.pi)
            # Distribuzione gaussiana per densità al centro
            distance = abs(random.gauss(0, 50))

            px = x + distance * np.cos(angle)
            py = y + distance * np.sin(angle)

            size = random.uniform(2, 6)
            alpha = random.uniform(0.3, 0.7)

            self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def generate_particles_bend(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Arco di particelle"""
        num_particles = self.get_particle_count(note['velocity'], note['duration'])

        start_angle = random.uniform(0, 2*np.pi)
        arc_span = np.pi * 0.8

        for i in range(num_particles):
            t = i / num_particles
            angle = start_angle + t * arc_span

            distance = 60 + t * 40
            lateral_spread = random.gauss(0, 8)

            px = x + distance * np.cos(angle) + lateral_spread * np.cos(angle + np.pi/2)
            py = y + distance * np.sin(angle) + lateral_spread * np.sin(angle + np.pi/2)

            size = random.uniform(1.5, 4)
            alpha = random.uniform(0.5, 0.9)

            self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def generate_particles_harmonic(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Particelle sparse e luminose"""
        num_particles = self.get_particle_count(note['velocity'], note['duration']) // 2

        for _ in range(num_particles):
            angle = random.uniform(0, 2*np.pi)
            distance = random.uniform(40, 150)

            px = x + distance * np.cos(angle)
            py = y + distance * np.sin(angle)

            # Particelle più grandi e luminose
            size = random.uniform(2, 7)
            alpha = random.uniform(0.2, 0.5)

            # Alone
            self.ax.add_patch(Circle((px, py), size*2, facecolor=color, alpha=alpha*0.3))
            self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def generate_particles_tapping(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Impulsi concentrati"""
        num_rings = 5
        particles_per_ring = 20

        for ring in range(num_rings):
            radius = 20 + ring * 15

            for i in range(particles_per_ring):
                angle = (i / particles_per_ring) * 2 * np.pi
                jitter = random.uniform(-5, 5)

                px = x + (radius + jitter) * np.cos(angle)
                py = y + (radius + jitter) * np.sin(angle)

                size = random.uniform(1.5, 3)
                alpha = 0.7 - ring * 0.1

                self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def generate_particles_dive(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Spirale discendente di particelle"""
        num_particles = self.get_particle_count(note['velocity'], note['duration'])

        for i in range(num_particles):
            t = i / num_particles
            angle = t * 4 * np.pi  # 2 giri
            radius = 40 * (1 - t)

            px = x + radius * np.cos(angle)
            py = y + radius * np.sin(angle) - t * 100

            size = (1 - t) * 3 + 1
            alpha = random.uniform(0.4, 0.8)

            self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def generate_particles_legato(self, x: float, y: float, note: Dict, color: np.ndarray):
        """Flusso fluido di particelle"""
        num_particles = self.get_particle_count(note['velocity'], note['duration'])

        # Direzione principale
        main_angle = random.uniform(0, 2*np.pi)

        for i in range(num_particles):
            t = i / num_particles

            # Flusso sinusoidale
            base_distance = t * 120
            wave = np.sin(t * 2 * np.pi) * 20

            px = x + base_distance * np.cos(main_angle) + wave * np.cos(main_angle + np.pi/2)
            py = y + base_distance * np.sin(main_angle) + wave * np.sin(main_angle + np.pi/2)

            size = random.uniform(1.5, 3.5)
            alpha = random.uniform(0.5, 0.8)

            self.ax.add_patch(Circle((px, py), size, facecolor=color, alpha=alpha))

    def position_note_center(self, note: Dict, index: int, total: int) -> tuple:
        """Posiziona il centro dell'esplosione di particelle"""
        # Griglia con jitter
        cols = 4
        rows = 3

        col = index % cols
        row = index // cols

        x = 200 + col * (self.width - 400) / (cols - 1) + random.uniform(-50, 50)
        y = 200 + row * (self.height - 400) / (rows - 1) + random.uniform(-50, 50)

        return x, y

    def create_artwork(self, filename: str = 'particle_system_art.png'):
        notes = self.parse_johnny_b_goode_riff()

        for i, note in enumerate(notes):
            x, y = self.position_note_center(note, i, len(notes))
            color = self.get_note_color(note['note'])

            tech = note['technique']

            if tech == 'staccato':
                self.generate_particles_staccato(x, y, note, color)
            elif tech == 'slide':
                self.generate_particles_slide(x, y, note, color)
            elif tech == 'vibrato':
                self.generate_particles_vibrato(x, y, note, color)
            elif tech == 'powerchord':
                self.generate_particles_powerchord(x, y, note, color)
            elif tech == 'bend':
                self.generate_particles_bend(x, y, note, color)
            elif tech in ['harmonic_natural', 'harmonic_artificial']:
                self.generate_particles_harmonic(x, y, note, color)
            elif tech == 'tapping':
                self.generate_particles_tapping(x, y, note, color)
            elif tech == 'dive':
                self.generate_particles_dive(x, y, note, color)
            elif tech == 'legato':
                self.generate_particles_legato(x, y, note, color)
            else:
                self.generate_particles_staccato(x, y, note, color)

        bg_color = self.colors['black'] * 1.1
        bg_color = np.clip(bg_color, 0, 0.15)

        self.fig.savefig(filename, facecolor=bg_color,
                        dpi=150, bbox_inches='tight', edgecolor='none')
        print(f"✅ Particle System artwork: {filename}")

if __name__ == "__main__":
    artist = ParticleSystemArt()
    artist.create_artwork()
    plt.show()
