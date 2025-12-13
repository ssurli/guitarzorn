"""
ZORN PENTATONIC PURE LIVE VISUALIZATION
========================================

Video animato PURO - 100% musicalmente derivato
Nessuna decorazione, solo translitterazione Juritz rigorosa.

Usa ZornPentatonicPainterly con:
- Analisi contesto musicale (dinamica, intervalli, ritmo, contorno)
- Tecniche aggiornate (12 layers, 30-50 bristles, wet-on-wet)
- Zero decorazioni
- Rendering progressivo sincronizzato

DETERMINISTICO: seed=42, stesso JSON → stesso video
"""

import sys
import os

# Import the pure renderer class
sys.path.insert(0, os.path.dirname(__file__))
from zorn_pentatonic_painterly import ZornPentatonicPainterly

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import numpy as np
import random
import json
import subprocess


class ZornPentatonicPureLive(ZornPentatonicPainterly):
    """
    Live renderer PURO - estende ZornPentatonicPainterly
    con capacità di animazione progressiva
    """

    def __init__(self, notes, audio_file=None, fps=30):
        """
        Args:
            notes: Lista note da JSON
            audio_file: Path audio per sync e overlay
            fps: Frame per secondo (default 30)
        """
        # Initialize parent class
        super().__init__()

        self.all_notes = notes
        self.audio_file = audio_file
        self.fps = fps

        # Calcola durata totale
        if notes:
            last_note = max(notes, key=lambda n: n.get('start_time', 0) + n.get('duration', 0))
            self.duration = last_note.get('start_time', 0) + last_note.get('duration', 0) + 1.0
        else:
            self.duration = 10.0

        self.total_frames = int(self.duration * self.fps)

        # Tracking per progressive rendering
        self.drawn_notes_set = set()
        self.background_drawn = False

        # ANALISI MUSICALE GLOBALE (eseguita una volta)
        print("🔬 Analisi musicale contestuale...")
        self.dynamics_analysis = self.analyze_dynamics(notes)
        self.contours = self.analyze_melodic_contour(notes)

        print(f"   Dinamica: avg={self.dynamics_analysis['avg']:.2f}, "
              f"range={self.dynamics_analysis['range']:.2f}, "
              f"climax @ nota {self.dynamics_analysis['climax_idx']}")

        print(f"🎬 Setup video: {self.total_frames} frames @ {fps}fps = {self.duration:.1f}s")

    def get_musical_context(self, note_index: int, note: dict) -> dict:
        """
        Costruisce contesto musicale per una nota specifica
        """
        musical_context = {
            'dynamics': self.dynamics_analysis,
            'contour': self.contours[note_index] if note_index < len(self.contours) else 'static',
        }

        # Distanza dal climax
        climax_idx = self.dynamics_analysis['climax_idx']
        distance = abs(note_index - climax_idx) / max(len(self.all_notes), 1)
        musical_context['climax_distance'] = distance

        # Intervallo con nota precedente
        if note_index > 0:
            interval_info = self.analyze_interval(self.all_notes[note_index-1], note)
            musical_context['interval'] = interval_info

        # Analisi ritmica
        prev_note = self.all_notes[note_index-1] if note_index > 0 else None
        rhythm_info = self.analyze_rhythm(note, prev_note)
        musical_context['rhythm'] = rhythm_info

        return musical_context

    def render_note_progressive(self, note: dict, note_index: int, growth_factor: float):
        """
        Renderizza nota con crescita progressiva

        Args:
            note: Dati nota
            note_index: Indice nota nell'array
            growth_factor: 0-1, quanto è cresciuta la nota
        """
        if growth_factor <= 0:
            return

        # Ottieni contesto musicale
        musical_context = self.get_musical_context(note_index, note)

        # Scala dimensioni in base a crescita
        # Modifichiamo temporaneamente la durata per scalare le dimensioni
        original_duration = note.get('duration', 0.5)
        note['duration'] = original_duration * growth_factor

        # Renderizza con contesto musicale
        self.render_note(note, musical_context=musical_context)

        # Ripristina durata originale
        note['duration'] = original_duration

    def update_frame(self, frame):
        """Update function per animazione progressiva"""
        current_time = frame / self.fps

        # Background solo al primo frame
        if not self.background_drawn:
            print(f"   Frame 0: Canvas texture + Melodic path")
            # Canvas texture (substrato)
            self.apply_canvas_texture()
            # Melodic path (musicale)
            self.draw_melodic_path(self.all_notes, alpha=0.12)
            self.background_drawn = True

        # Renderizza note che dovrebbero essere visibili
        for note_index, note in enumerate(self.all_notes):
            note_start = note.get('start_time', 0)
            note_duration = note.get('duration', 0.5)

            if note_start <= current_time:
                # Calcola crescita
                time_since_start = current_time - note_start
                growth_duration = min(note_duration, 1.0)  # Max 1s crescita
                growth_factor = min(time_since_start / growth_duration, 1.0)

                # ID univoco per livello di crescita
                note_id = (note_index, int(growth_factor * 10))

                # Disegna solo se non già fatto a questo livello
                if note_id not in self.drawn_notes_set:
                    self.drawn_notes_set.add(note_id)
                    self.render_note_progressive(note, note_index, growth_factor)

        # Titolo con timestamp e info dinamica
        climax_note = self.dynamics_analysis['climax_idx']
        self.ax.set_title(
            f"Zorn Pentatonic PURE • {current_time:.2f}s / {self.duration:.2f}s • "
            f"Climax @ nota {climax_note}",
            fontsize=14, color=self.zorn_colors['black'], pad=15, fontweight='bold'
        )

        return self.ax.patches

    def generate_video(self, output_file="zorn_pentatonic_pure_live.mp4"):
        """Genera video animato puro"""
        print(f"\n🎬 Generazione video PURO Zorn Pentatonic...")
        print(f"   Output: {output_file}")
        print(f"   Frames: {self.total_frames} @ {self.fps}fps")

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
                return output_with_audio

        plt.close(self.fig)
        return output_file

    def add_audio_to_video(self, video_file, audio_file):
        """Combina video con audio"""
        output_with_audio = video_file.replace('.mp4', '_with_audio.mp4')

        print(f"\n🔊 Aggiunta audio...")

        cmd = [
            'ffmpeg', '-y',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-shortest',
            output_with_audio
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_with_audio
        except subprocess.CalledProcessError as e:
            print(f"❌ Errore ffmpeg: {e.stderr.decode()}")
            return None


def load_notes_from_json(json_path: str):
    """Carica note da JSON"""
    with open(json_path, 'r') as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    return data.get('notes', [])


def main():
    if len(sys.argv) < 2:
        print("Uso: python zorn_pentatonic_pure_live.py <notes.json> [audio.wav] [output.mp4]")
        print("\nEsempio:")
        print("  python zorn_pentatonic_pure_live.py 1207(1)_notes.json 1207(1)_audio.wav")
        sys.exit(1)

    input_json = sys.argv[1]
    audio_file = sys.argv[2] if len(sys.argv) > 2 else None
    output_mp4 = sys.argv[3] if len(sys.argv) > 3 else 'zorn_pentatonic_pure_live.mp4'

    # Carica note
    print(f"📖 Caricando note da: {input_json}")
    notes = load_notes_from_json(input_json)

    if not notes:
        print("❌ Nessuna nota trovata!")
        sys.exit(1)

    # Normalizza posizioni e velocity
    margin = 100
    px_per_beat = 120
    px_per_semitone = 15

    for i, note in enumerate(notes):
        if 'x_pos' not in note:
            note['x_pos'] = margin + note.get('start_time', i * 0.5) * px_per_beat
        if 'y_pos' not in note:
            midi_pitch = note.get('pitch', 60)
            note['y_pos'] = margin + (midi_pitch - 40) * px_per_semitone

        # Normalizza velocity
        if 'velocity' in note:
            vel_map = {'p': 0.2, 'mp': 0.4, 'mf': 0.6, 'f': 0.9, 'ff': 1.0}
            note['velocity_value'] = vel_map.get(note['velocity'], 0.7)
        else:
            note['velocity_value'] = 0.7

    print(f"   {len(notes)} note pronte")

    # Genera video
    renderer = ZornPentatonicPureLive(notes, audio_file, fps=30)
    output = renderer.generate_video(output_mp4)

    print(f"\n✅ COMPLETATO!")
    print(f"   Video: {output}")
    print(f"   Caratteristiche:")
    print(f"     - 100% musicalmente derivato")
    print(f"     - Zero decorazioni")
    print(f"     - Contesto: dinamica, intervalli, ritmo, contorno")
    print(f"     - Deterministico (seed=42)")


if __name__ == "__main__":
    main()
