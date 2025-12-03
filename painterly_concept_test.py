"""
Painterly Concept Test - Simplified rendering with organic blobs only
Quick proof of concept for painterly guitar riff visualization
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Ellipse
import numpy as np
import random
from scipy.ndimage import gaussian_filter


class PainterlyRiffArt:
    """Simplified painterly renderer - only organic blobs, no geometry"""

    def __init__(self, width=1600, height=1000, dpi=150, seed=42):
        # Zorn palette
        self.colors = {
            'ochre': np.array([196, 164, 106]) / 255.0,
            'vermilion': np.array([227, 66, 52]) / 255.0,
            'black': np.array([28, 28, 28]) / 255.0,
            'white': np.array([242, 242, 242]) / 255.0
        }

        # Note to color mapping
        self.note_colors = {
            'A': 'ochre',
            'C': 'vermilion',
            'D': 'black',
            'E': 'white',
            'G': 'ochre'  # Mix ochre+black
        }

        self.width = width
        self.height = height
        self.dpi = dpi
        self.px_per_beat = 140
        self.margin = 80

        # Initialize figure with clean background
        self.fig, self.ax = plt.subplots(
            figsize=(width/dpi, height/dpi),
            dpi=dpi
        )

        bg_color = self.colors['ochre']
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.set_xlim(0, width)
        self.ax.set_ylim(0, height)
        self.ax.axis('off')

        random.seed(seed)
        np.random.seed(seed)

    def parse_johnny_b_goode_riff(self):
        """Parse the riff into note events"""
        riff_notes = [
            {'note': 'A', 'fret': 5, 'string': 6, 'duration': 0.5, 'velocity': 'mf'},
            {'note': 'C', 'fret': 8, 'string': 6, 'duration': 0.5, 'velocity': 'f'},
            {'note': 'D', 'fret': 5, 'string': 4, 'duration': 0.25, 'velocity': 'f'},
            {'note': 'A', 'fret': 7, 'string': 5, 'duration': 0.5, 'velocity': 'mf'},
            {'note': 'C', 'fret': 8, 'string': 5, 'duration': 0.25, 'velocity': 'f'},
            {'note': 'D', 'fret': 7, 'string': 3, 'duration': 0.75, 'velocity': 'f'},
            {'note': 'E', 'fret': 8, 'string': 1, 'duration': 0.5, 'velocity': 'f'},
            {'note': 'G', 'fret': 3, 'string': 1, 'duration': 0.5, 'velocity': 'mp'},
            {'note': 'A', 'fret': 5, 'string': 1, 'duration': 1.0, 'velocity': 'f'},
            {'note': 'C', 'fret': 8, 'string': 6, 'duration': 0.25, 'velocity': 'mf'},
            {'note': 'D', 'fret': 5, 'string': 4, 'duration': 0.5, 'velocity': 'f'},
            {'note': 'G', 'fret': 3, 'string': 1, 'duration': 0.25, 'velocity': 'p'},
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
                'x_pos': self.margin + cumulative_time * self.px_per_beat,
                'y_pos': self.margin + ((midi_pitch - 40) / 40) * (self.height - 2 * self.margin)
            }
            processed_notes.append(processed_note)
            cumulative_time += note_data['duration']

        return processed_notes

    def get_note_color(self, note):
        """Get color for note from Zorn palette"""
        if note == 'G':
            return (self.colors['ochre'] + self.colors['black']) / 2
        color_key = self.note_colors.get(note, 'ochre')
        return self.colors[color_key]

    def get_blob_size(self, duration, velocity):
        """Calculate blob size from duration and velocity"""
        velocity_map = {'p': 0.6, 'mp': 0.8, 'mf': 1.0, 'f': 1.3, 'ff': 1.6}
        velocity_mult = velocity_map.get(velocity, 1.0)

        # Size based on duration
        base_size = 20 + duration * 40  # 20-60px range
        return base_size * velocity_mult

    def draw_paint_blob(self, x, y, size, color, note):
        """
        Draw a single organic paint blob/drop
        Simple ellipse with soft edges and slight irregularity
        """
        # Add organic variation
        size_x = size * random.uniform(0.8, 1.2)
        size_y = size * random.uniform(0.8, 1.2)
        angle = random.uniform(0, 360)

        # Slight position jitter
        x += random.uniform(-3, 3)
        y += random.uniform(-3, 3)

        # Base opacity varies by color
        if note == 'E':  # White is more transparent
            alpha = random.uniform(0.7, 0.85)
        elif note == 'D':  # Black more opaque
            alpha = random.uniform(0.85, 0.95)
        else:
            alpha = random.uniform(0.75, 0.9)

        # Draw main blob
        ellipse = Ellipse(
            (x, y),
            width=size_x,
            height=size_y,
            angle=angle,
            facecolor=color,
            edgecolor='none',
            alpha=alpha
        )
        self.ax.add_patch(ellipse)

        # Add soft shadow/depth (smaller darker blob underneath)
        if random.random() > 0.3:
            shadow_color = self.colors['black']
            shadow_ellipse = Ellipse(
                (x + size_x * 0.1, y - size_y * 0.1),
                width=size_x * 0.9,
                height=size_y * 0.9,
                angle=angle,
                facecolor=shadow_color,
                edgecolor='none',
                alpha=0.15,
                zorder=-1
            )
            self.ax.add_patch(shadow_ellipse)

    def render_notes(self, notes):
        """Render all notes as organic paint blobs"""
        print("   ├─ Rendering notes as paint blobs...")

        for note in notes:
            x = note['x_pos']
            y = note['y_pos']
            size = self.get_blob_size(note['duration'], note['velocity'])
            color = self.get_note_color(note['note'])

            self.draw_paint_blob(x, y, size, color, note['note'])

    def create_artwork(self, filename='painterly_concept.png'):
        """Generate painterly artwork"""
        print("\n🎨 Painterly Concept Test")
        print("=" * 60)
        print("   Simplified rendering: organic blobs only")
        print("-" * 60)

        # NO background elements - clean ochre canvas

        # Parse and render notes
        notes = self.parse_johnny_b_goode_riff()
        self.render_notes(notes)

        # Save
        print(f"   └─ Saving to {filename}...")
        self.fig.savefig(
            filename,
            facecolor=self.colors['ochre'],
            dpi=self.dpi,
            bbox_inches='tight',
            edgecolor='none'
        )

        print("✅ Concept artwork complete!")
        print("=" * 60)
        print(f"\n📁 Output: {filename}")
        print("\nThis is a simplified concept:")
        print("  - Only organic blobs (no geometric shapes)")
        print("  - Clean background")
        print("  - Size = duration + velocity")
        print("  - Color = pitch (pentatonic → Zorn)")
        print("  - Position = time + pitch")

        return filename


if __name__ == "__main__":
    artist = PainterlyRiffArt(seed=42)
    artist.create_artwork()
    plt.show()
