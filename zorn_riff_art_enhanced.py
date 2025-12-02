"""
Enhanced Guitar Riff to Abstract Art Translator
Translates guitar riffs to abstract expressionist paintings (Kandinsky/Pollock style)
Using Zorn palette with procedural texture generation - fully repeatable with code only
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Wedge
from matplotlib.path import Path
import numpy as np
import random
from typing import List, Dict, Tuple
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFilter


class ProceduralEffects:
    """Procedural texture and effect generators for painterly results"""

    def __init__(self, seed=42):
        self.rng = np.random.RandomState(seed)
        random.seed(seed)

    def perlin_noise_2d(self, shape, scale=10, octaves=4):
        """Generate Perlin-like noise for organic texture"""
        noise = np.zeros(shape)
        for octave in range(octaves):
            freq = 2 ** octave
            amplitude = 1.0 / freq

            # Generate random gradients
            grid_shape = (shape[0] // (scale // freq) + 2, shape[1] // (scale // freq) + 2)
            gradients = self.rng.randn(grid_shape[0], grid_shape[1], 2)

            # Simple noise approximation
            octave_noise = self.rng.randn(shape[0], shape[1])
            octave_noise = gaussian_filter(octave_noise, sigma=scale/freq)
            noise += octave_noise * amplitude

        return (noise - noise.min()) / (noise.max() - noise.min())

    def generate_splatter_points(self, center, intensity, num_points):
        """Generate splatter effect coordinates (Pollock-style)"""
        x, y = center
        angles = self.rng.uniform(0, 2*np.pi, num_points)
        distances = self.rng.exponential(intensity, num_points)

        points = []
        for angle, dist in zip(angles, distances):
            px = x + dist * np.cos(angle)
            py = y + dist * np.sin(angle)
            size = self.rng.exponential(2) + 0.5
            points.append((px, py, size))

        return points

    def generate_drip_path(self, start_point, length, wobble=5):
        """Generate dripping paint path"""
        x, y = start_point
        points = [(x, y)]

        for i in range(int(length)):
            x += self.rng.uniform(-wobble, wobble)
            y -= self.rng.uniform(0.5, 2.0)  # Drip downward
            points.append((x, y))

        return points

    def generate_impasto_texture(self, shape, scale=5):
        """Generate impasto (thick paint) texture"""
        texture = self.perlin_noise_2d(shape, scale=scale, octaves=3)
        # Add high-frequency detail
        detail = self.rng.randn(*shape) * 0.1
        texture += detail
        texture = gaussian_filter(texture, sigma=1.5)
        return texture


class EnhancedZornGuitarRiffArt:
    """Enhanced version with procedural painterly effects"""

    def __init__(self, width=1600, height=1000, dpi=150, seed=42):
        # Zorn palette
        self.colors = {
            'ochre': np.array([196, 164, 106]) / 255.0,
            'vermilion': np.array([227, 66, 52]) / 255.0,
            'black': np.array([28, 28, 28]) / 255.0,
            'white': np.array([242, 242, 242]) / 255.0
        }

        # Note to color mapping (pentatonic A minor)
        self.note_colors = {
            'A': 'ochre',
            'C': 'vermilion',
            'D': 'black',
            'E': 'white',
            'G': 'ochre'  # Mix ochre+black
        }

        # Canvas parameters
        self.width = width
        self.height = height
        self.dpi = dpi
        self.px_per_beat = 140
        self.margin = 80

        # Initialize figure
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

        # Initialize procedural effects
        self.effects = ProceduralEffects(seed=seed)
        random.seed(seed)
        np.random.seed(seed)

        # Layer system for complex compositions
        self.layers = []

    def parse_johnny_b_goode_riff(self) -> List[Dict]:
        """Parse the iconic Johnny B. Goode intro riff"""
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

        # Convert to MIDI pitches
        string_tuning = [40, 45, 50, 55, 59, 64]  # EADGBE
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
        """Convert time (beats) to X coordinate"""
        return self.margin + time * self.px_per_beat

    def pitch_to_y(self, midi_pitch: int) -> float:
        """Convert MIDI pitch to Y coordinate"""
        min_pitch, max_pitch = 40, 80
        normalized = (midi_pitch - min_pitch) / (max_pitch - min_pitch)
        return self.margin + normalized * (self.height - 2 * self.margin)

    def get_note_color(self, note: str, octave_offset: int = 0) -> np.ndarray:
        """Get color for a note from Zorn palette"""
        if note == 'G':
            # Mix ochre + black for G
            base_color = (self.colors['ochre'] + self.colors['black']) / 2
        else:
            color_key = self.note_colors.get(note, 'ochre')
            base_color = self.colors[color_key]

        # Adjust for octave (lighter for higher, darker for lower)
        if octave_offset > 0:
            base_color = np.clip(base_color + octave_offset * 0.1, 0, 1)
        elif octave_offset < 0:
            base_color = np.clip(base_color + octave_offset * 0.1, 0, 1)

        return base_color

    def get_stroke_width(self, velocity: str) -> float:
        """Map velocity to stroke width"""
        velocity_map = {'p': 2, 'mp': 3, 'mf': 4, 'f': 6, 'ff': 8}
        return velocity_map.get(velocity, 4)

    def add_jitter(self, x: float, y: float, intensity: float = 0.5) -> Tuple[float, float]:
        """Add organic variation to coordinates"""
        return (
            x + random.uniform(-intensity, intensity),
            y + random.uniform(-intensity, intensity)
        )

    def blend_colors(self, color1, color2, ratio=0.5):
        """Linear RGB color blending"""
        return np.clip(color1 * ratio + color2 * (1 - ratio), 0, 1)

    # ==================== ENHANCED DRAWING METHODS ====================

    def draw_splatter_effect(self, center, color, intensity=30, num_splatters=20):
        """Draw Pollock-style splatter effect"""
        splatter_points = self.effects.generate_splatter_points(
            center, intensity, num_splatters
        )

        for px, py, size in splatter_points:
            if 0 <= px <= self.width and 0 <= py <= self.height:
                alpha = random.uniform(0.3, 0.8)
                self.ax.add_patch(Circle(
                    (px, py), size,
                    facecolor=color,
                    alpha=alpha,
                    edgecolor='none'
                ))

    def draw_drip_effect(self, start_point, color, length=50, width=2):
        """Draw dripping paint effect"""
        drip_path = self.effects.generate_drip_path(start_point, length, wobble=3)

        if len(drip_path) < 2:
            return

        xs, ys = zip(*drip_path)

        # Draw drip with varying opacity
        for i in range(len(xs)-1):
            alpha = 0.7 * (1 - i/len(xs))  # Fade as it drips
            self.ax.plot(
                [xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=color,
                linewidth=width,
                alpha=alpha,
                solid_capstyle='round'
            )

    def draw_organic_brush_stroke(self, x1, y1, x2, y2, color, width, texture_level=0.3):
        """Draw organic brushstroke with texture variation"""
        # Create path with slight curvature
        num_segments = 20
        t = np.linspace(0, 1, num_segments)

        # Add Bezier curve variation
        ctrl_offset = random.uniform(-20, 20)
        ctrl_x = (x1 + x2) / 2 + ctrl_offset
        ctrl_y = (y1 + y2) / 2 + ctrl_offset

        # Quadratic Bezier
        xs = (1-t)**2 * x1 + 2*(1-t)*t * ctrl_x + t**2 * x2
        ys = (1-t)**2 * y1 + 2*(1-t)*t * ctrl_y + t**2 * y2

        # Add texture variation to width
        for i in range(len(xs)-1):
            segment_width = width * (1 + random.uniform(-texture_level, texture_level))
            alpha = random.uniform(0.6, 0.9)

            self.ax.plot(
                [xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=color,
                linewidth=segment_width,
                alpha=alpha,
                solid_capstyle='round',
                solid_joinstyle='round'
            )

    def draw_abstract_shape(self, center, color, shape_type='kandinsky', size=40):
        """Draw abstract geometric shapes (Kandinsky-inspired)"""
        x, y = center

        if shape_type == 'circle':
            self.ax.add_patch(Circle(
                (x, y), size,
                facecolor=color,
                alpha=random.uniform(0.4, 0.7),
                edgecolor=self.blend_colors(color, self.colors['black'], 0.7),
                linewidth=2
            ))

        elif shape_type == 'triangle':
            angles = np.array([0, 120, 240]) * np.pi / 180 + random.uniform(0, 2*np.pi)
            points = [(x + size*np.cos(a), y + size*np.sin(a)) for a in angles]
            self.ax.add_patch(Polygon(
                points,
                facecolor=color,
                alpha=random.uniform(0.4, 0.7),
                edgecolor=self.blend_colors(color, self.colors['black'], 0.7),
                linewidth=2
            ))

        elif shape_type == 'square':
            self.ax.add_patch(patches.Rectangle(
                (x - size/2, y - size/2), size, size,
                facecolor=color,
                alpha=random.uniform(0.4, 0.7),
                edgecolor=self.blend_colors(color, self.colors['black'], 0.7),
                linewidth=2,
                angle=random.uniform(0, 45)
            ))

        elif shape_type == 'arc':
            theta1 = random.uniform(0, 180)
            theta2 = theta1 + random.uniform(90, 270)
            self.ax.add_patch(Wedge(
                (x, y), size, theta1, theta2,
                facecolor=color,
                alpha=random.uniform(0.4, 0.7),
                edgecolor=self.blend_colors(color, self.colors['black'], 0.7),
                linewidth=2
            ))

    # ==================== TECHNIQUE RENDERERS (Enhanced) ====================

    def draw_staccato(self, note):
        """Staccato: sharp dots with splatter"""
        x, y = self.add_jitter(note['x_pos'], note['y_pos'])
        color = self.get_note_color(note['note'])
        width = self.get_stroke_width(note['velocity'])

        # Main dot
        self.ax.add_patch(Circle((x, y), width*1.5, facecolor=color, alpha=0.9))

        # Add subtle splatter
        if random.random() > 0.5:
            self.draw_splatter_effect((x, y), color, intensity=10, num_splatters=5)

    def draw_legato(self, note, next_note=None):
        """Legato: smooth organic curves"""
        x1, y1 = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'])
        width = self.get_stroke_width(note['velocity'])

        if next_note:
            x2, y2 = next_note['x_pos'], next_note['y_pos']
            self.draw_organic_brush_stroke(x1, y1, x2, y2, color, width)
        else:
            # Single legato note - smooth elongated shape
            self.draw_organic_brush_stroke(x1, y1, x1+40, y1, color, width)

    def draw_slide(self, note):
        """Slide: diagonal stroke with drip"""
        x, y = self.add_jitter(note['x_pos'], note['y_pos'])
        color = self.get_note_color(note['note'])
        width = self.get_stroke_width(note['velocity'])

        # Main slide stroke
        self.draw_organic_brush_stroke(x, y, x+60, y+30, color, width)

        # Add drip effect
        if random.random() > 0.6:
            self.draw_drip_effect((x+30, y+15), color, length=20, width=width*0.5)

    def draw_bend(self, note):
        """Bend: curved arc with tension"""
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'])
        width = self.get_stroke_width(note['velocity'])

        # Curved bend path
        t = np.linspace(0, 1, 30)
        xs = x + t * 50
        ys = y + 30 * np.sin(t * np.pi)

        for i in range(len(xs)-1):
            self.ax.plot(
                [xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=color,
                linewidth=width,
                alpha=0.8,
                solid_capstyle='round'
            )

    def draw_vibrato(self, note):
        """Vibrato: oscillating line with texture"""
        x = note['x_pos']
        y = note['y_pos']
        color = self.get_note_color(note['note'])
        width = self.get_stroke_width(note['velocity'])

        length = 60
        xs = np.linspace(x, x+length, 100)
        ys = y + 8*np.sin(np.linspace(0, 12, 100))

        # Draw with varying width for organic feel
        for i in range(len(xs)-1):
            w = width * (1 + 0.3*np.sin(i/5))
            self.ax.plot(
                [xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=color,
                linewidth=w,
                alpha=0.8
            )

    def draw_hammer_on(self, note):
        """Hammer-on: connected dots with flow"""
        x, y = self.add_jitter(note['x_pos'], note['y_pos'])
        color = self.get_note_color(note['note'])

        # Two connected notes
        self.ax.add_patch(Circle((x, y), 6, facecolor=color, alpha=0.8))
        self.ax.add_patch(Circle((x+20, y+12), 5, facecolor=color, alpha=0.8))

        # Connection
        self.draw_organic_brush_stroke(x, y, x+20, y+12, color, 2, texture_level=0.2)

    def draw_powerchord(self, note):
        """Powerchord: bold rectangular block with texture"""
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'])

        # Main rectangle
        rect = patches.FancyBboxPatch(
            (x, y-10), 50, 20,
            boxstyle="round,pad=2",
            facecolor=color,
            alpha=0.85,
            edgecolor=self.blend_colors(color, self.colors['black'], 0.6),
            linewidth=3
        )
        self.ax.add_patch(rect)

        # Add splatter around it
        self.draw_splatter_effect((x+25, y), color, intensity=15, num_splatters=8)

    def draw_tapping(self, note):
        """Tapping: concentric circles with glow effect"""
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'])

        # Concentric circles with decreasing alpha
        for r, alpha in [(15, 0.3), (10, 0.5), (5, 0.7), (2, 0.9)]:
            self.ax.add_patch(Circle(
                (x, y), r,
                facecolor=color,
                alpha=alpha,
                edgecolor='none'
            ))

    def draw_dive(self, note):
        """Dive: spiral descent with paint trailing"""
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'])

        # Spiral path
        t = np.linspace(0, 4*np.pi, 100)
        xs = x + t*3
        ys = y - t*2 + 8*np.sin(t)

        for i in range(len(xs)-1):
            alpha = 0.8 * (1 - i/len(xs))
            width = 3 * (1 - i/len(xs)) + 1
            self.ax.plot(
                [xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=color,
                linewidth=width,
                alpha=alpha
            )

    def draw_harmonic_natural(self, note):
        """Natural harmonic: ethereal halo"""
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'])
        light_color = self.blend_colors(color, self.colors['white'], 0.3)

        # Outer glow
        self.ax.add_patch(Circle((x, y), 18, facecolor=light_color, alpha=0.2))
        self.ax.add_patch(Circle((x, y), 12, facecolor=light_color, alpha=0.3))
        # Core
        self.ax.add_patch(Circle((x, y), 4, facecolor=color, alpha=0.8))

    def draw_harmonic_artificial(self, note):
        """Artificial harmonic: sharp radiating lines"""
        x, y = note['x_pos'], note['y_pos']
        color = self.get_note_color(note['note'])

        # Radiating spikes
        for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
            length = random.uniform(12, 20)
            x2 = x + length * np.cos(angle)
            y2 = y + length * np.sin(angle)

            self.ax.plot(
                [x, x2], [y, y2],
                color=color,
                linewidth=2,
                alpha=0.7
            )

    def draw_regular_note(self, note):
        """Regular note: organic brushstroke"""
        x, y = self.add_jitter(note['x_pos'], note['y_pos'])
        color = self.get_note_color(note['note'])
        width = self.get_stroke_width(note['velocity'])

        self.draw_organic_brush_stroke(x, y, x+35, y, color, width)

    # ==================== RENDERING ORCHESTRATION ====================

    def add_background_texture(self):
        """Add organic background texture layer"""
        num_elements = 15

        for _ in range(num_elements):
            x = random.uniform(self.margin, self.width - self.margin)
            y = random.uniform(self.margin, self.height - self.margin)

            # Random shape type
            shape_type = random.choice(['circle', 'triangle', 'square', 'arc'])
            color_name = random.choice(['ochre', 'vermilion', 'black', 'white'])
            color = self.colors[color_name]
            size = random.uniform(20, 60)

            self.draw_abstract_shape((x, y), color, shape_type, size)

        # Add some background splatters
        for _ in range(8):
            x = random.uniform(self.margin, self.width - self.margin)
            y = random.uniform(self.margin, self.height - self.margin)
            color_name = random.choice(['ochre', 'vermilion', 'black'])
            color = self.colors[color_name]

            self.draw_splatter_effect((x, y), color, intensity=50, num_splatters=30)

    def render_notes(self, notes: List[Dict]):
        """Render all notes with their techniques"""
        technique_dispatch = {
            'staccato': self.draw_staccato,
            'legato': lambda n, nn=None: self.draw_legato(n, nn),
            'slide': self.draw_slide,
            'bend': self.draw_bend,
            'vibrato': self.draw_vibrato,
            'hammer_on': self.draw_hammer_on,
            'powerchord': self.draw_powerchord,
            'tapping': self.draw_tapping,
            'dive': self.draw_dive,
            'harmonic_natural': self.draw_harmonic_natural,
            'harmonic_artificial': self.draw_harmonic_artificial,
        }

        for i, note in enumerate(notes):
            tech = note['technique']

            if tech == 'legato':
                next_note = notes[i+1] if i+1 < len(notes) else None
                self.draw_legato(note, next_note)
            elif tech in technique_dispatch:
                technique_dispatch[tech](note)
            else:
                self.draw_regular_note(note)

    def add_foreground_accents(self):
        """Add final expressive accents on top"""
        # Random drips from top
        for _ in range(5):
            x = random.uniform(self.margin, self.width - self.margin)
            y = random.uniform(self.height * 0.7, self.height - self.margin)
            color_name = random.choice(['black', 'vermilion'])
            color = self.colors[color_name]

            length = random.uniform(30, 80)
            self.draw_drip_effect((x, y), color, length=length, width=3)

    def create_artwork(self, filename: str = 'johnny_b_goode_enhanced.png'):
        """Main composition pipeline"""
        print("🎨 Generating abstract expressionist artwork from guitar riff...")

        # 1. Background texture layer (Kandinsky-inspired geometry)
        print("   ├─ Adding background abstract shapes...")
        self.add_background_texture()

        # 2. Parse and render musical notes (main content)
        print("   ├─ Translating musical riff to visual forms...")
        notes = self.parse_johnny_b_goode_riff()
        self.render_notes(notes)

        # 3. Foreground accents (Pollock-inspired spontaneity)
        print("   ├─ Adding expressive accents and drips...")
        self.add_foreground_accents()

        # 4. Save artwork
        print(f"   └─ Saving to {filename}...")
        self.fig.savefig(
            filename,
            facecolor=self.colors['ochre'],
            dpi=self.dpi,
            bbox_inches='tight',
            edgecolor='none'
        )

        print(f"✅ Artwork complete: {filename}")
        print(f"   Canvas: {self.width}x{self.height}px @ {self.dpi} DPI")
        print(f"   Palette: Zorn (Ochre, Vermilion, Ivory Black, Titanium White)")
        print(f"   Style: Abstract Expressionist (Kandinsky/Pollock inspired)")

        return filename


def main():
    """Generate the enhanced artwork"""
    artist = EnhancedZornGuitarRiffArt(
        width=1600,
        height=1000,
        dpi=150,
        seed=42  # Change seed for variations while maintaining repeatability
    )

    output_file = artist.create_artwork('johnny_b_goode_abstract_expressionist.png')

    # Optionally display
    plt.show()

    return output_file


if __name__ == "__main__":
    main()
