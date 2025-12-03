"""
Painterly Technique Demo - Show how guitar techniques map to organic brush strokes
Quick visual example of the mapping
"""

import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib.patches import PathPatch
from matplotlib.path import Path


class PainterlyTechniqueDemo:
    """Visual demo of technique → brush stroke mapping"""

    def __init__(self):
        self.colors = {
            'ochre': np.array([196, 164, 106]) / 255.0,
            'vermilion': np.array([227, 66, 52]) / 255.0,
            'black': np.array([28, 28, 28]) / 255.0,
            'white': np.array([242, 242, 242]) / 255.0
        }

        self.fig, self.ax = plt.subplots(figsize=(16, 10), dpi=150)
        bg_color = self.colors['ochre']
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.set_xlim(0, 1600)
        self.ax.set_ylim(0, 1000)
        self.ax.axis('off')

        random.seed(42)
        np.random.seed(42)

    def draw_organic_stroke(self, start, end, width, color, label=""):
        """Draw organic brush stroke between two points"""
        x1, y1 = start
        x2, y2 = end

        # Generate organic path with slight curve
        num_points = 20
        t = np.linspace(0, 1, num_points)

        # Add slight curve variation
        curve_offset = random.uniform(-15, 15)
        ctrl_x = (x1 + x2) / 2 + curve_offset
        ctrl_y = (y1 + y2) / 2 + curve_offset

        # Quadratic Bézier curve
        xs = (1-t)**2 * x1 + 2*(1-t)*t * ctrl_x + t**2 * x2
        ys = (1-t)**2 * y1 + 2*(1-t)*t * ctrl_y + t**2 * y2

        # Variable width along stroke
        widths = width * (1 + 0.3 * np.sin(t * np.pi))

        # Draw stroke segments with varying width and alpha
        for i in range(len(xs)-1):
            alpha = 0.7 + 0.2 * (1 - abs(t[i] - 0.5) * 2)
            self.ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]],
                        color=color, linewidth=widths[i],
                        alpha=alpha, solid_capstyle='round')

        # Add label
        if label:
            self.ax.text(x1 - 120, y1, label, fontsize=12, ha='right',
                        color=self.colors['black'], weight='bold')

    def draw_slide(self, x, y, color):
        """SLIDE: diagonal organic brush stroke"""
        self.draw_organic_stroke(
            (x, y), (x + 150, y + 80),
            width=8, color=color, label="SLIDE →"
        )

    def draw_legato(self, x, y, color):
        """LEGATO: connected flowing strokes"""
        # Two connected strokes
        self.draw_organic_stroke(
            (x, y), (x + 80, y + 20),
            width=6, color=color, label="LEGATO ~"
        )
        self.draw_organic_stroke(
            (x + 80, y + 20), (x + 160, y - 10),
            width=6, color=color, label=""
        )

    def draw_staccato(self, x, y, color):
        """STACCATO: isolated blob/dot"""
        from matplotlib.patches import Ellipse
        ellipse = Ellipse((x + 40, y), 25, 20,
                         angle=random.uniform(0, 360),
                         facecolor=color, alpha=0.85)
        self.ax.add_patch(ellipse)
        self.ax.text(x - 120, y, "STACCATO •", fontsize=12, ha='right',
                    color=self.colors['black'], weight='bold')

    def draw_bend(self, x, y, color):
        """BEND: curved upward stroke"""
        # Curved path upward
        t = np.linspace(0, 1, 30)
        xs = x + t * 120
        ys = y + 60 * np.sin(t * np.pi * 0.8)

        for i in range(len(xs)-1):
            width = 7 * (1 + 0.2 * np.sin(i / 3))
            self.ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]],
                        color=color, linewidth=width,
                        alpha=0.8, solid_capstyle='round')

        self.ax.text(x - 120, y, "BEND ↗", fontsize=12, ha='right',
                    color=self.colors['black'], weight='bold')

    def draw_vibrato(self, x, y, color):
        """VIBRATO: wavy oscillating stroke"""
        t = np.linspace(0, 1, 80)
        xs = x + t * 140
        ys = y + 15 * np.sin(t * 20)

        for i in range(len(xs)-1):
            width = 5 * (1 + 0.3 * np.sin(i / 5))
            self.ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]],
                        color=color, linewidth=width,
                        alpha=0.8, solid_capstyle='round')

        self.ax.text(x - 120, y, "VIBRATO ≈", fontsize=12, ha='right',
                    color=self.colors['black'], weight='bold')

    def draw_powerchord(self, x, y, color):
        """POWERCHORD: thick heavy stroke"""
        self.draw_organic_stroke(
            (x, y - 15), (x + 100, y + 15),
            width=20, color=color, label="POWER □"
        )

    def draw_hammer_on(self, x, y, color):
        """HAMMER-ON: two blobs merging"""
        from matplotlib.patches import Ellipse
        # First blob
        e1 = Ellipse((x + 20, y), 20, 18, facecolor=color, alpha=0.75)
        self.ax.add_patch(e1)
        # Second blob overlapping
        e2 = Ellipse((x + 50, y + 15), 22, 20, facecolor=color, alpha=0.75)
        self.ax.add_patch(e2)
        # Connection
        self.draw_organic_stroke((x + 20, y), (x + 50, y + 15),
                                width=4, color=color, label="HAMMER h")

    def create_demo(self, filename='painterly_techniques_demo.png'):
        """Create visual demo of all techniques"""
        print("\n🎨 Painterly Techniques Mapping Demo")
        print("=" * 60)

        # Layout techniques vertically
        y_positions = [850, 720, 590, 460, 330, 200, 70]
        x_start = 300

        colors = [
            self.colors['vermilion'],
            self.colors['ochre'],
            self.colors['black'],
            self.colors['vermilion'],
            self.colors['black'],
            self.colors['ochre'],
            self.colors['vermilion']
        ]

        techniques = [
            ("Slide", self.draw_slide),
            ("Legato", self.draw_legato),
            ("Staccato", self.draw_staccato),
            ("Bend", self.draw_bend),
            ("Vibrato", self.draw_vibrato),
            ("Powerchord", self.draw_powerchord),
            ("Hammer-on", self.draw_hammer_on)
        ]

        for i, (name, draw_func) in enumerate(techniques):
            print(f"   ├─ Drawing {name}...")
            draw_func(x_start, y_positions[i], colors[i])

        # Title
        self.ax.text(800, 950, "Guitar Techniques → Organic Brush Strokes",
                    fontsize=18, ha='center', weight='bold',
                    color=self.colors['black'])

        # Save
        print(f"   └─ Saving to {filename}...")
        self.fig.savefig(filename, facecolor=self.colors['ochre'],
                        dpi=150, bbox_inches='tight')

        print("✅ Demo complete!")
        print("=" * 60)
        print(f"\n📁 Output: {filename}")
        print("\nThis shows how each technique maps to organic brush strokes:")
        print("  - SLIDE: diagonal flowing stroke")
        print("  - LEGATO: connected smooth strokes")
        print("  - STACCATO: isolated dot/blob")
        print("  - BEND: curved upward stroke")
        print("  - VIBRATO: wavy oscillating stroke")
        print("  - POWERCHORD: thick heavy stroke")
        print("  - HAMMER-ON: two merging blobs")
        print("\nEach keeps the musical meaning but looks painterly!")


if __name__ == "__main__":
    demo = PainterlyTechniqueDemo()
    demo.create_demo()
    plt.show()
