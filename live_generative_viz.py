"""
LIVE GENERATIVE VISUALIZATION
Genera l'artwork progressivamente mentre la musica suona

L'opera d'arte "cresce" in tempo reale sincronizzata con l'audio
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Polygon, Wedge, Ellipse
from matplotlib.path import Path
import numpy as np
import random
import json
import sys
import os
from audio_analyzer import AudioAnalyzer, extract_audio_from_video
import soundfile as sf

class LiveGenerativeArt:
    """
    Genera artwork in tempo reale mentre la musica procede
    """

    def __init__(self, notes, audio_file=None, style='organic'):
        """
        Args:
            notes: Lista di note estratte
            audio_file: Path all'audio (per sincronizzare)
            style: 'organic' o 'tension'
        """
        self.notes = notes
        self.audio_file = audio_file
        self.style = style

        # Palette Zorn
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
            'G': 'ochre',
            'B': 'vermilion',
            'F': 'black'
        }

        # Setup canvas
        self.width = 1600
        self.height = 1000
        self.fig, self.ax = plt.subplots(figsize=(16, 10), dpi=100)

        # Sfondo
        if style == 'organic':
            bg_color = self.colors['ochre'] * 0.7 + self.colors['white'] * 0.3
        else:
            bg_color = self.colors['ochre'] * 0.5 + self.colors['white'] * 0.5

        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.axis('off')

        # Calcola durata totale
        if notes:
            self.duration = max(n['start_time'] + n['duration'] for n in notes)
        else:
            self.duration = 20.0

        # Frame rate
        self.fps = 30
        self.total_frames = int(self.duration * self.fps)

        print(f"🎬 Setup animazione: {self.duration:.2f}s, {self.total_frames} frames @ {self.fps}fps")

        # Traccia note già disegnate
        self.drawn_notes = []

        random.seed(42)
        np.random.seed(42)

    def get_note_color(self, note: str) -> np.ndarray:
        """Colore per la nota"""
        note_base = note.replace('#', '').replace('b', '')

        if note_base == 'G':
            return (self.colors['ochre'] + self.colors['black']) / 2
        else:
            color_key = self.note_colors.get(note_base, 'ochre')
            return np.clip(self.colors[color_key], 0, 1)

    def draw_organic_form(self, note: dict, growth_factor: float):
        """
        Disegna forma organica che cresce progressivamente
        growth_factor: 0-1, quanto è cresciuta la forma
        """
        # Posizione basata su indice e pitch
        index = note['index']
        total = len(self.notes)

        x = 200 + (index / total) * (self.width - 400)
        y = 200 + ((note['pitch'] - 40) / 40) * (self.height - 400)

        x += random.uniform(-80, 80)
        y += random.uniform(-80, 80)

        color = self.get_note_color(note['note'])
        tech = note['technique']

        # Scala la forma in base a quanto è cresciuta
        base_size = (20 + note['duration'] * 40) * growth_factor

        if tech == 'staccato':
            # Cellule che appaiono
            num_cells = int(5 * growth_factor) + 1
            for i in range(num_cells):
                angle = (i / max(num_cells, 1)) * 2 * np.pi
                distance = base_size * 0.5
                cx = x + distance * np.cos(angle)
                cy = y + distance * np.sin(angle)
                radius = (5 + random.uniform(0, 5)) * growth_factor

                self.ax.add_patch(Circle((cx, cy), radius,
                                        facecolor=color, alpha=0.6,
                                        edgecolor=color*0.7, linewidth=1))

        elif tech == 'vibrato':
            # Viticci che crescono spiralmente
            if growth_factor > 0.1:
                t_max = 3 * np.pi * growth_factor
                t = np.linspace(0, t_max, int(50 * growth_factor) + 2)
                r = t * 8 * growth_factor
                angle_offset = random.uniform(0, 2*np.pi)
                spiral_x = x + r * np.cos(t + angle_offset)
                spiral_y = y + r * np.sin(t + angle_offset)

                self.ax.plot(spiral_x, spiral_y, color=color,
                           linewidth=2, alpha=0.7)

        elif tech == 'slide':
            # Rami che crescono
            num_branches = max(1, int(3 * growth_factor))
            for i in range(num_branches):
                angle = random.uniform(0, 2*np.pi)
                length = base_size * 2 * growth_factor

                # Segmenti del ramo
                segments = max(2, int(4 * growth_factor))
                current_x, current_y = x, y

                for seg in range(segments):
                    seg_length = length / segments
                    end_x = current_x + seg_length * np.cos(angle)
                    end_y = current_y + seg_length * np.sin(angle)

                    width = (3 - seg*0.5) * growth_factor
                    self.ax.plot([current_x, end_x], [current_y, end_y],
                               color=color, linewidth=max(width, 0.5),
                               alpha=0.7)

                    current_x, current_y = end_x, end_y
                    angle += random.uniform(-0.3, 0.3)

        elif tech == 'bend':
            # Arco che si piega
            if growth_factor > 0.1:
                angles = np.linspace(0, np.pi * 1.5 * growth_factor, int(30 * growth_factor) + 2)
                radius_curve = base_size
                curve_x = x + radius_curve * np.cos(angles)
                curve_y = y + radius_curve * np.sin(angles)

                self.ax.plot(curve_x, curve_y, color=color,
                           linewidth=3, alpha=0.8)

        else:  # legato, regular
            # Cerchi concentrici che si espandono
            num_rings = max(1, int(5 * growth_factor))
            for i in range(num_rings):
                radius = base_size * (i / max(num_rings, 1)) * growth_factor
                alpha = 0.5 * (1 - i/max(num_rings, 1))

                self.ax.add_patch(Circle((x, y), radius,
                                        facecolor=color, alpha=alpha,
                                        edgecolor='none'))

    def draw_tension_form(self, note: dict, growth_factor: float):
        """
        Disegna forma basata su tensione che appare progressivamente
        """
        index = note['index']
        total = len(self.notes)

        x = 150 + (index / total) * (self.width - 300)
        y = 200 + (1 - note['tension']) * (self.height - 400)

        x += random.uniform(-60, 60)
        y += random.uniform(-60, 60)

        color = self.get_note_color(note['note'])
        tension = note['tension']

        base_size = (40 + note['duration'] * 60) * growth_factor

        # Forma basata su tensione
        if tension < 0.3:
            # Cerchio morbido
            num_layers = max(1, int(5 * growth_factor))
            for i in range(num_layers):
                radius = base_size * (1 - i/max(num_layers, 1))
                alpha = (0.6 - i * 0.1) * growth_factor

                self.ax.add_patch(Circle((x, y), radius,
                                        facecolor=color, alpha=alpha))

        elif tension < 0.5:
            # Pentagono
            if growth_factor > 0.2:
                num_points = 5
                angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
                points = []
                for angle in angles:
                    r = base_size
                    px = x + r * np.cos(angle)
                    py = y + r * np.sin(angle)
                    points.append([px, py])

                self.ax.add_patch(Polygon(points, facecolor=color,
                                         alpha=0.5 * growth_factor,
                                         edgecolor=color*0.6, linewidth=2))

        else:
            # Triangolo (alta tensione)
            if growth_factor > 0.2:
                num_points = 3
                angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
                points = []
                for angle in angles:
                    r = base_size * (1 + random.uniform(-0.2, 0.2))
                    px = x + r * np.cos(angle)
                    py = y + r * np.sin(angle)
                    points.append([px, py])

                self.ax.add_patch(Polygon(points, facecolor=color,
                                         alpha=0.5 * growth_factor,
                                         edgecolor=color*0.6, linewidth=2))

    def update_frame(self, frame):
        """
        Update function per l'animazione
        frame: numero del frame corrente
        """
        current_time = frame / self.fps

        # Trova note che dovrebbero essere visibili a questo tempo
        for note in self.notes:
            note_start = note['start_time']
            note_end = note_start + note['duration']

            if note_start <= current_time:
                # Calcola quanto è cresciuta questa nota
                time_since_start = current_time - note_start
                growth_duration = min(note['duration'], 1.0)  # Max 1s di crescita
                growth_factor = min(time_since_start / growth_duration, 1.0)

                # Verifica se non l'abbiamo già disegnata a questo livello
                note_id = (note['index'], int(growth_factor * 10))

                if note_id not in self.drawn_notes:
                    self.drawn_notes.append(note_id)

                    if self.style == 'organic':
                        self.draw_organic_form(note, growth_factor)
                    else:
                        self.draw_tension_form(note, growth_factor)

        # Titolo con timestamp
        self.ax.set_title(f"Time: {current_time:.2f}s / {self.duration:.2f}s",
                         fontsize=14, color='gray', pad=20)

        return self.ax.patches

    def generate_video(self, output_file: str = "live_generative.mp4"):
        """
        Genera video dell'animazione
        """
        print(f"\n🎬 Generazione video animato...")
        print(f"   Stile: {self.style}")
        print(f"   Frames totali: {self.total_frames}")
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
        writer = FFMpegWriter(fps=self.fps, bitrate=2000,
                             extra_args=['-vcodec', 'libx264'])

        print("   Rendering in corso...")
        anim.save(output_file, writer=writer, dpi=100)

        print(f"✅ Video salvato: {output_file}")

        # Se abbiamo l'audio originale, combinalo
        if self.audio_file and os.path.exists(self.audio_file):
            self.add_audio_to_video(output_file, self.audio_file)

        plt.close(self.fig)

        return output_file

    def add_audio_to_video(self, video_file: str, audio_file: str):
        """
        Combina video con audio originale
        """
        output_with_audio = video_file.replace('.mp4', '_with_audio.mp4')

        print(f"\n🔊 Aggiunta audio al video...")

        import subprocess

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

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode == 0:
            print(f"✅ Video con audio: {output_with_audio}")
            return output_with_audio
        else:
            print(f"⚠️  Errore aggiunta audio, mantieni: {video_file}")
            return video_file


def main():
    """
    Main per generare visualizzazione live
    """
    if len(sys.argv) < 2:
        print("="*60)
        print("🎬 LIVE GENERATIVE VISUALIZATION")
        print("="*60)
        print("\nGenera video animato dell'artwork che cresce con la musica!")
        print("\nUSO:")
        print(f"  python {sys.argv[0]} <video_o_audio> [--organic|--tension|--both]")
        print("\nESEMPI:")
        print(f"  python {sys.argv[0]} 1207(1).mp4")
        print(f"  python {sys.argv[0]} 1207(1).mp4 --both")
        print(f"  python {sys.argv[0]} riff.wav --organic")
        print("\nOUTPUT:")
        print("  - Video MP4 dell'artwork che si genera")
        print("  - Sincronizzato con l'audio originale")
        print("="*60)
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"❌ File non trovato: {input_file}")
        sys.exit(1)

    # Opzioni
    generate_organic = '--organic' in sys.argv or '--both' in sys.argv or len(sys.argv) == 2
    generate_tension = '--tension' in sys.argv or '--both' in sys.argv

    print("\n" + "="*60)
    print("🎬 LIVE GENERATIVE VISUALIZATION")
    print("="*60)

    # Estrai audio se necessario
    if input_file.endswith(('.mp4', '.mov', '.avi', '.MP4', '.MOV', '.webm')):
        audio_file = extract_audio_from_video(input_file, "temp_for_animation.wav")
    else:
        audio_file = input_file

    # Carica o analizza le note
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    notes_file = f"{base_name}_notes.json"

    if os.path.exists(notes_file):
        print(f"\n📂 Caricamento note esistenti: {notes_file}")
        with open(notes_file, 'r') as f:
            notes = json.load(f)
    else:
        print(f"\n🎵 Analisi audio...")
        analyzer = AudioAnalyzer(audio_file)
        notes = analyzer.extract_notes()
        notes = analyzer.detect_techniques(notes)
        notes = analyzer.calculate_harmonic_tension(notes)

        # Salva
        with open(notes_file, 'w') as f:
            json.dump(notes, f, indent=2)
        print(f"💾 Note salvate: {notes_file}")

    print(f"\n📊 Note totali: {len(notes)}")

    # Genera animazioni
    if generate_organic:
        print("\n" + "="*60)
        print("🌱 GENERAZIONE ORGANIC GROWTH (animato)")
        print("="*60)

        artist = LiveGenerativeArt(notes, audio_file, style='organic')
        output = f"{base_name}_organic_growth_live.mp4"
        artist.generate_video(output)

    if generate_tension:
        print("\n" + "="*60)
        print("⚖️ GENERAZIONE TENSION FIELD (animato)")
        print("="*60)

        artist = LiveGenerativeArt(notes, audio_file, style='tension')
        output = f"{base_name}_tension_field_live.mp4"
        artist.generate_video(output)

    print("\n" + "="*60)
    print("✨ ANIMAZIONI COMPLETE!")
    print("="*60)

    # Cleanup
    if audio_file.startswith("temp_"):
        os.remove(audio_file)
        print(f"\n🗑️  Rimosso file temporaneo: {audio_file}")


if __name__ == "__main__":
    main()
