"""
ZORN PENTATONIC LIVE VISUALIZATION
===================================

Genera video animato dell'artwork Zorn che "cresce" in tempo reale
sincronizzato con la musica.

Usa il renderer ZornPentatonicPainterly migliorato con tutte le tecniche pittoriche:
- Pennellate (10-15 setole)
- Impasto (6 layer)
- Glazing
- Dry Brush
- Background ricco

MANTIENE REPLICABILITÀ: stesso JSON + audio = stesso video
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Circle, Polygon
import numpy as np
import random
import json
import sys
import os
import subprocess

class ZornPentatonicLive:
    """
    Genera video animato dell'artwork Zorn che cresce progressivamente
    """

    def __init__(self, notes, audio_file=None):
        """
        Args:
            notes: Lista di note estratte dal JSON
            audio_file: Path all'audio (per sincronizzare e aggiungere al video)
        """
        self.all_notes = notes
        self.audio_file = audio_file

        # PALETTE ZORN RIGOROSA (4 colori base)
        self.zorn_colors = {
            'ochre': np.array([196, 164, 106]) / 255.0,
            'vermilion': np.array([227, 66, 52]) / 255.0,
            'black': np.array([28, 28, 28]) / 255.0,
            'white': np.array([242, 242, 242]) / 255.0,
        }

        # PENTATONICA A MINOR → MIXING ZORN
        self.pentatonic_mapping = {
            'A': self.zorn_colors['ochre'],
            'C': self._mix_colors('vermilion', 'ochre', 0.7),
            'D': self._mix_colors('black', 'ochre', 0.6),
            'E': self._mix_colors('white', 'ochre', 0.7),
            'G': self._mix_colors('ochre', 'black', 0.6),
        }

        # Canvas setup
        self.width = 2000
        self.height = 1200
        self.fig, self.ax = plt.subplots(figsize=(20, 12), dpi=100)

        # Sfondo ocra (tipico Zorn)
        bg_color = self.zorn_colors['ochre'] * 1.1
        bg_color = np.clip(bg_color, 0, 1)
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.axis('off')

        # Calcola durata totale
        if notes:
            self.duration = max(n.get('start_time', 0) + n.get('duration', 0.5) for n in notes)
        else:
            self.duration = 20.0

        # Frame rate
        self.fps = 30
        self.total_frames = int(self.duration * self.fps)

        print(f"🎬 Setup animazione Zorn Pentatonic:")
        print(f"   Durata: {self.duration:.2f}s")
        print(f"   Frames: {self.total_frames} @ {self.fps}fps")
        print(f"   Note: {len(notes)}")

        # Traccia note già disegnate
        self.drawn_notes_set = set()

        # Background già disegnato
        self.background_drawn = False

        random.seed(42)
        np.random.seed(42)

    def _mix_colors(self, color1_name: str, color2_name: str, ratio: float) -> np.ndarray:
        """Mixing lineare di due colori Zorn"""
        c1 = self.zorn_colors[color1_name]
        c2 = self.zorn_colors[color2_name]
        mixed = c1 * (1 - ratio) + c2 * ratio
        return np.clip(mixed, 0, 1)

    def get_note_color(self, note_name: str, velocity: float, octave: int = 4):
        """Restituisce colore per nota pentatonica + alpha"""
        # Colore base dalla pentatonica
        if note_name not in self.pentatonic_mapping:
            note_name = 'A'  # Fallback

        base_color = self.pentatonic_mapping[note_name].copy()

        # OCTAVE → Luminosità
        if octave < 4:
            base_color = base_color * 0.7 + self.zorn_colors['black'] * 0.3
        elif octave > 4:
            base_color = base_color * 0.8 + self.zorn_colors['white'] * 0.2

        # VELOCITY → Saturazione
        if velocity < 0.5:
            gray = np.array([0.4, 0.4, 0.4])
            saturation_factor = velocity / 0.5
            base_color = base_color * saturation_factor + gray * (1 - saturation_factor)

        # VELOCITY → Opacità
        alpha = 0.6 + velocity * 0.35

        return np.clip(base_color, 0, 1), alpha

    def draw_brushstroke(self, x, y, angle, length, width, color, alpha=0.7):
        """Pennellata con setole multiple (versione migliorata)"""
        num_bristles = max(10, int(width * 3))

        for i in range(num_bristles):
            offset_x = random.gauss(0, width * 0.4)
            offset_y = random.gauss(0, width * 0.4)
            bristle_length = length * random.uniform(0.7, 1.2)

            end_x = x + offset_x + np.cos(angle) * bristle_length
            end_y = y + offset_y + np.sin(angle) * bristle_length

            color_var = color + np.random.randn(3) * 0.04
            color_var = np.clip(color_var, 0, 1)

            line_var = width * random.uniform(0.3, 0.6)

            self.ax.plot([x + offset_x, end_x], [y + offset_y, end_y],
                        color=color_var, linewidth=line_var,
                        alpha=alpha*random.uniform(0.6, 1.0),
                        solid_capstyle='round')

    def draw_impasto(self, x, y, radius, color, alpha=0.8):
        """Impasto con 6 layer (versione migliorata)"""
        for layer in range(6):
            offset = layer * 1.5
            layer_alpha = alpha * (1.0 - layer * 0.12)
            layer_radius = radius * (1.0 - layer * 0.08)

            if layer > 0:
                variation = random.uniform(-0.03, 0.08)
                layer_color = color * (1.0 + variation)
                layer_color = np.clip(layer_color, 0, 1)
            else:
                layer_color = color

            num_points = random.randint(8, 15)
            angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)

            points = []
            for angle in angles:
                r = layer_radius * random.uniform(0.6, 1.4)
                px = x + offset + r * np.cos(angle)
                py = y + offset + r * np.sin(angle)
                points.append([px, py])

            polygon = Polygon(points, facecolor=layer_color,
                            edgecolor=None, alpha=layer_alpha)
            self.ax.add_patch(polygon)

    def draw_glazing(self, x, y, radius, color, alpha=0.25):
        """Glazing - layer trasparenti"""
        num_glazes = random.randint(3, 4)

        for i in range(num_glazes):
            offset_x = random.gauss(0, 3)
            offset_y = random.gauss(0, 3)

            glaze_color = color + np.random.randn(3) * 0.02
            glaze_color = np.clip(glaze_color, 0, 1)

            circle = Circle((x + offset_x, y + offset_y),
                          radius * random.uniform(0.8, 1.2),
                          facecolor=glaze_color,
                          edgecolor=None,
                          alpha=alpha * random.uniform(0.7, 1.0))
            self.ax.add_patch(circle)

    def draw_dry_brush(self, x, y, angle, length, color):
        """Dry Brush - pennellate secche interrotte"""
        num_strokes = random.randint(5, 8)

        for i in range(num_strokes):
            t = i / num_strokes
            start_x = x + np.cos(angle) * length * t
            start_y = y + np.sin(angle) * length * t

            stroke_len = length * random.uniform(0.05, 0.15)
            end_x = start_x + np.cos(angle) * stroke_len
            end_y = start_y + np.sin(angle) * stroke_len

            offset = random.gauss(0, 3)
            start_x += np.cos(angle + np.pi/2) * offset
            start_y += np.sin(angle + np.pi/2) * offset
            end_x += np.cos(angle + np.pi/2) * offset
            end_y += np.sin(angle + np.pi/2) * offset

            stroke_color = color + np.random.randn(3) * 0.03
            stroke_color = np.clip(stroke_color, 0, 1)

            self.ax.plot([start_x, end_x], [start_y, end_y],
                        color=stroke_color,
                        linewidth=random.uniform(1, 3),
                        alpha=random.uniform(0.4, 0.7),
                        solid_capstyle='round')

    def draw_background_elements(self):
        """Disegna background ricco (una volta sola all'inizio)"""
        for _ in range(30):
            x = random.uniform(100, self.width - 100)
            y = random.uniform(100, self.height - 100)
            radius = random.uniform(30, 100)

            bg_color_choice = random.choice(['ochre', 'white', 'black', 'vermilion'])
            bg_color = self.zorn_colors[bg_color_choice]

            technique = random.choice(['impasto', 'glazing', 'brushstroke'])

            if technique == 'impasto':
                self.draw_impasto(x, y, radius, bg_color, alpha=0.12)
            elif technique == 'glazing':
                self.draw_glazing(x, y, radius, bg_color, alpha=0.15)
            else:
                angle = random.uniform(0, 2 * np.pi)
                self.draw_brushstroke(x, y, angle, radius * 1.5,
                                    radius * 0.3, bg_color, alpha=0.1)

    def render_note_progressive(self, note, growth_factor):
        """
        Renderizza nota con fattore di crescita progressivo
        growth_factor: 0-1, quanto è cresciuta la nota
        """
        x = note.get('x_pos', 500)
        y = note.get('y_pos', 500)
        note_name = note.get('note', 'A')
        velocity = note.get('velocity_value', 0.7)
        duration = note.get('duration', 0.5)
        technique = note.get('technique', 'normal')
        octave = note.get('pitch', 60) // 12

        # Colore e alpha
        color, alpha = self.get_note_color(note_name, velocity, octave)

        # Dimensione base da velocity e durata, scalata per crescita
        base_size = (30 + velocity * 40 + duration * 20) * growth_factor

        # Renderizza in base alla tecnica
        if technique == 'staccato':
            self.draw_impasto(x, y, base_size * 0.6, color, alpha * 1.1)

        elif technique == 'legato':
            angle = random.uniform(0, 2 * np.pi)
            self.draw_brushstroke(x, y, angle, base_size * 1.5,
                                base_size * 0.3, color, alpha)

        elif technique == 'slide':
            angle = np.pi / 4
            self.draw_brushstroke(x, y, angle, base_size * 2,
                                base_size * 0.4, color, alpha)

        elif technique == 'bend':
            if growth_factor > 0.1:
                t = np.linspace(0, 1, 20)
                curve_x = x + t * base_size
                curve_y = y + np.sin(t * np.pi) * base_size * 0.5

                for i in range(len(t)-1):
                    self.ax.plot([curve_x[i], curve_x[i+1]],
                               [curve_y[i], curve_y[i+1]],
                               color=color, linewidth=base_size*0.2,
                               alpha=alpha, solid_capstyle='round')

        elif technique == 'vibrato':
            num_waves = max(1, int(5 * growth_factor))
            for i in range(num_waves):
                offset_y = np.sin(i / 5 * 2 * np.pi) * base_size * 0.3
                self.draw_impasto(x + i * 10, y + offset_y,
                                base_size * 0.5, color, alpha * 0.7)

        else:
            # Forma standard con tutte le tecniche
            self.draw_impasto(x, y, base_size * 0.7, color, alpha)

            angle = random.uniform(0, 2 * np.pi)
            self.draw_brushstroke(x, y, angle, base_size * 0.8,
                                base_size * 0.2, color, alpha * 0.6)

            # Glazing e dry brush solo se crescita completa
            if growth_factor > 0.7:
                if random.random() < 0.3:
                    self.draw_glazing(x, y, base_size * 0.9, color, alpha * 0.2)

                if random.random() < 0.2:
                    angle_dry = random.uniform(0, 2 * np.pi)
                    self.draw_dry_brush(x, y, angle_dry, base_size * 0.6, color)

    def update_frame(self, frame):
        """Update function per l'animazione"""
        current_time = frame / self.fps

        # Disegna background solo al primo frame
        if not self.background_drawn:
            self.draw_background_elements()
            self.background_drawn = True

        # Trova note che dovrebbero essere visibili ora
        for note in self.all_notes:
            note_start = note.get('start_time', 0)
            note_duration = note.get('duration', 0.5)

            if note_start <= current_time:
                # Calcola crescita
                time_since_start = current_time - note_start
                growth_duration = min(note_duration, 1.0)  # Max 1s di crescita
                growth_factor = min(time_since_start / growth_duration, 1.0)

                # ID univoco per nota + livello di crescita
                note_index = self.all_notes.index(note)
                note_id = (note_index, int(growth_factor * 10))

                # Disegna solo se non già fatto a questo livello
                if note_id not in self.drawn_notes_set:
                    self.drawn_notes_set.add(note_id)
                    self.render_note_progressive(note, growth_factor)

        # Titolo con timestamp
        self.ax.set_title(
            f"Zorn Pentatonic Live • {current_time:.2f}s / {self.duration:.2f}s",
            fontsize=16, color=self.zorn_colors['black'], pad=20, fontweight='bold'
        )

        return self.ax.patches

    def generate_video(self, output_file="zorn_pentatonic_live.mp4"):
        """Genera video dell'animazione"""
        print(f"\n🎬 Generazione video animato Zorn Pentatonic...")
        print(f"   Output: {output_file}")

        # Crea animazione
        anim = FuncAnimation(
            self.fig,
            self.update_frame,
            frames=self.total_frames,
            interval=1000/self.fps,
            blit=False,
            repeat=False
        )

        # Salva come video
        writer = FFMpegWriter(fps=self.fps, bitrate=3000,
                             extra_args=['-vcodec', 'libx264'])

        print("   Rendering frames...")
        anim.save(output_file, writer=writer, dpi=100)

        print(f"✅ Video salvato: {output_file}")

        # Aggiungi audio se disponibile
        if self.audio_file and os.path.exists(self.audio_file):
            output_with_audio = self.add_audio_to_video(output_file, self.audio_file)
            if output_with_audio:
                print(f"🔊 Video con audio: {output_with_audio}")

        plt.close(self.fig)

        return output_file

    def add_audio_to_video(self, video_file, audio_file):
        """Combina video con audio originale"""
        output_with_audio = video_file.replace('.mp4', '_with_audio.mp4')

        print(f"\n🔊 Aggiunta audio...")

        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            '-y',
            output_with_audio
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return output_with_audio
        else:
            print(f"⚠️  Errore aggiunta audio: {result.stderr}")
            return None


def main():
    """Main"""
    if len(sys.argv) < 2:
        print("="*60)
        print("🎬 ZORN PENTATONIC LIVE VISUALIZATION")
        print("="*60)
        print("\nGenera video animato dell'artwork Zorn che cresce con la musica!")
        print("\nUSO:")
        print(f"  python {sys.argv[0]} <notes.json> [audio.wav]")
        print("\nESEMPI:")
        print(f"  python {sys.argv[0]} 1207(1)_notes.json")
        print(f"  python {sys.argv[0]} 1207(1)_notes.json 1207(1).wav")
        print("\nOUTPUT:")
        print("  - Video MP4 con artwork Zorn animato")
        print("  - Sincronizzato con audio (se fornito)")
        print("  - Mantiene replicabilità (seed=42)")
        print("="*60)
        sys.exit(1)

    notes_file = sys.argv[1]
    audio_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(notes_file):
        print(f"❌ File non trovato: {notes_file}")
        sys.exit(1)

    # Carica note
    print(f"📖 Caricando note da: {notes_file}")
    with open(notes_file, 'r') as f:
        notes = json.load(f)

    if isinstance(notes, dict):
        notes = notes.get('notes', [])

    print(f"   {len(notes)} note caricate")

    # Normalizza posizioni se non presenti
    margin = 100
    px_per_beat = 120
    px_per_semitone = 15

    for i, note in enumerate(notes):
        if 'x_pos' not in note:
            note['x_pos'] = margin + note.get('start_time', i * 0.5) * px_per_beat
        if 'y_pos' not in note:
            midi_pitch = note.get('pitch', 60)
            note['y_pos'] = margin + (midi_pitch - 40) * px_per_semitone

        if 'velocity' in note and 'velocity_value' not in note:
            vel_map = {'p': 0.2, 'mp': 0.4, 'mf': 0.6, 'f': 0.9, 'ff': 1.0}
            note['velocity_value'] = vel_map.get(note['velocity'], 0.7)
        elif 'velocity_value' not in note:
            note['velocity_value'] = 0.7

    # Genera video
    base_name = os.path.splitext(os.path.basename(notes_file))[0]
    output_file = f"{base_name}_zorn_live.mp4"

    artist = ZornPentatonicLive(notes, audio_file)
    artist.generate_video(output_file)

    print("\n" + "="*60)
    print("✨ COMPLETATO!")
    print("="*60)


if __name__ == "__main__":
    main()
