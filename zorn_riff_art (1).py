import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.path import Path
import numpy as np
import random
from typing import List, Dict, Tuple

class ZornGuitarRiffArt:
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

        self.px_per_beat = 140
        self.margin = 80

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
        cumulative_time = 0

        for note_data in riff_notes:
            midi_pitch = string_tuning[note_data['string'] - 1] + note_data['fret']
            processed_note = {
                'note': note_data['note'],
                'pitch': midi_pitch,
                'start_time': cumulative_time,
                'duration': note_data['duration'],
                'velocity': note_data['velocity'],
                'technique': note_data['technique'],
                'x_pos': self.time_to_x(cumulative_time),
                'y_pos': self.pitch_to_y(midi_pitch)
            }
            processed_notes.append(processed_note)
            cumulative_time += note_data['duration']
        return processed_notes

    def time_to_x(self, time: float) -> float:
        return self.margin + time * self.px_per_beat

    def pitch_to_y(self, midi_pitch: int) -> float:
        min_pitch, max_pitch = 40, 80
        normalized = (midi_pitch - min_pitch) / (max_pitch - min_pitch)
        return self.margin + normalized * (self.height - 2 * self.margin)

    def get_note_color(self, note: str, octave_offset: int = 0) -> np.ndarray:
        if note == 'G':
            base_color = (self.colors['ochre'] + self.colors['black']) / 2
        else:
            color_key = self.note_colors.get(note, 'ochre')
            base_color = self.colors[color_key]
        return np.clip(base_color, 0, 1)

    def get_stroke_width(self, velocity: str) -> float:
        velocity_map = {'p': 2, 'mp': 3, 'mf': 4, 'f': 6, 'ff': 8}
        return velocity_map.get(velocity, 4)

    def add_jitter(self, x: float, y: float, intensity: float = 0.5) -> Tuple[float, float]:
        return x + random.uniform(-intensity, intensity), y + random.uniform(-intensity, intensity)

    def draw_staccato(self, note):
        x, y = self.add_jitter(note['x_pos'], note['y_pos'])
        color = self.get_note_color(note['note'])
        width = self.get_stroke_width(note['velocity'])
        self.ax.add_patch(Circle((x, y), width, facecolor=color, alpha=0.9))

    def draw_legato(self, note, next_note=None):
        x1, y1 = note['x_pos'], note['y_pos']
        if next_note:
            x2, y2 = next_note['x_pos'], next_note['y_pos']
            ctrl_x = (x1 + x2) / 2
            ctrl_y = (y1 + y2) / 2
            verts = [(x1, y1), (ctrl_x, ctrl_y), (x2, y2)]
            codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
            path = Path(verts, codes)
            self.ax.add_patch(patches.PathPatch(path, facecolor='none', edgecolor=self.get_note_color(note['note']), lw=2))

    def draw_slide(self, note):
        x, y = self.add_jitter(note['x_pos'], note['y_pos'])
        self.ax.add_line(plt.Line2D([x, x+40], [y, y+20], color=self.get_note_color(note['note']), lw=2))

    def draw_bend(self, note):
        x, y = note['x_pos'], note['y_pos']
        verts = [(x, y), (x+20, y+30), (x+40, y+10)]
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
        path = Path(verts, codes)
        self.ax.add_patch(patches.PathPatch(path, facecolor='none', edgecolor=self.get_note_color(note['note']), lw=2))

    def draw_vibrato(self, note):
        x = note['x_pos']
        y = note['y_pos']
        length = 50
        xs = np.linspace(x, x+length, 100)
        ys = y + 5*np.sin(np.linspace(0, 10, 100))
        self.ax.plot(xs, ys, color=self.get_note_color(note['note']), lw=2)

    def draw_hammer_on(self, note):
        x, y = self.add_jitter(note['x_pos'], note['y_pos'])
        self.ax.add_patch(Circle((x, y), 5, facecolor=self.get_note_color(note['note']), alpha=0.8))
        self.ax.add_patch(Circle((x+15, y+10), 4, facecolor=self.get_note_color(note['note']), alpha=0.8))

    def draw_powerchord(self, note):
        x, y = note['x_pos'], note['y_pos']
        self.ax.add_patch(patches.Rectangle((x, y-5), 40, 10, facecolor=self.get_note_color(note['note']), alpha=0.9))

    def draw_tapping(self, note):
        x, y = note['x_pos'], note['y_pos']
        for r in [10, 6, 3]:
            self.ax.add_patch(Circle((x, y), r, facecolor=self.get_note_color(note['note']), alpha=0.5))

    def draw_dive(self, note):
        x, y = note['x_pos'], note['y_pos']
        t = np.linspace(0, 4*np.pi, 100)
        xs = x + t*2
        ys = y - t + 5*np.sin(t)
        self.ax.plot(xs, ys, color=self.get_note_color(note['note']), lw=2, alpha=0.7)

    def draw_harmonic_natural(self, note):
        x, y = note['x_pos'], note['y_pos']
        self.ax.add_patch(Circle((x, y), 12, facecolor=self.get_note_color(note['note']), alpha=0.3))
        self.ax.add_patch(Circle((x, y), 3, facecolor=self.get_note_color(note['note']), alpha=0.8))

    def draw_harmonic_artificial(self, note):
        x, y = note['x_pos'], note['y_pos']
        for angle in [0, 45, 90, 135]:
            rad = np.radians(angle)
            self.ax.add_line(plt.Line2D([x, x+15*np.cos(rad)], [y, y+15*np.sin(rad)], color=self.get_note_color(note['note']), lw=1))

    def draw_regular_note(self, note):
        x, y = self.add_jitter(note['x_pos'], note['y_pos'])
        color = self.get_note_color(note['note'])
        self.ax.add_patch(FancyBboxPatch((x, y-2), 30, 4, boxstyle="round,pad=0.1", facecolor=color, edgecolor=color, alpha=0.85))

    def render_notes(self, notes: List[Dict]):
        for i, note in enumerate(notes):
            tech = note['technique']
            if tech == 'staccato':
                self.draw_staccato(note)
            elif tech == 'legato':
                next_note = notes[i+1] if i+1 < len(notes) else None
                self.draw_legato(note, next_note)
            elif tech == 'slide':
                self.draw_slide(note)
            elif tech == 'bend':
                self.draw_bend(note)
            elif tech == 'vibrato':
                self.draw_vibrato(note)
            elif tech == 'hammer_on':
                self.draw_hammer_on(note)
            elif tech == 'powerchord':
                self.draw_powerchord(note)
            elif tech == 'tapping':
                self.draw_tapping(note)
            elif tech == 'dive':
                self.draw_dive(note)
            elif tech == 'harmonic_natural':
                self.draw_harmonic_natural(note)
            elif tech == 'harmonic_artificial':
                self.draw_harmonic_artificial(note)
            else:
                self.draw_regular_note(note)

    def add_zorn_background_elements(self):
        for _ in range(12):
            x = random.uniform(self.margin, self.width - self.margin)
            y = random.uniform(self.margin, self.height - self.margin)
            radius = random.uniform(5, 20)
            color_choice = random.choice(['ochre', 'vermilion', 'black', 'white'])
            color = self.colors[color_choice]
            alpha = random.uniform(0.3, 0.7)
            self.ax.add_patch(Circle((x, y), radius, facecolor=color, alpha=alpha))

    def create_artwork(self, filename: str = 'johnny_b_goode_zorn_riff.png'):
        notes = self.parse_johnny_b_goode_riff()
        self.add_zorn_background_elements()
        self.render_notes(notes)
        self.fig.savefig(filename, facecolor=self.colors['ochre'], dpi=150, bbox_inches='tight', edgecolor='none')
        print(f"✅ Artwork completato: {filename}")

if __name__ == "__main__":
    artist = ZornGuitarRiffArt()
    artist.create_artwork()
    plt.show()
