"""
AUDIO-TO-VISUAL PIPELINE
Sistema completo per convertire una performance musicale dal vivo in opera d'arte

FLUSSO:
1. Video/Audio input → Estrazione audio
2. Analisi audio → Pitch, Onset, Loudness, Duration
3. Feature musicali → Parametri visivi
4. Generazione artwork (Organic Growth / Tension Field)
"""

import numpy as np
import librosa
import soundfile as sf
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class AudioAnalyzer:
    """
    Analizza un file audio e estrae feature musicali
    """
    def __init__(self, audio_file: str, sr: int = 22050):
        """
        Args:
            audio_file: Path al file audio (wav, mp3, etc.)
            sr: Sample rate (default 22050 Hz)
        """
        print(f"🎵 Caricamento audio: {audio_file}")
        self.y, self.sr = librosa.load(audio_file, sr=sr)
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        print(f"   Durata: {self.duration:.2f}s, Sample rate: {self.sr}Hz")

    def extract_notes(self,
                     hop_length: int = 512,
                     fmin: float = 80.0,  # E2 (chitarra 6a corda)
                     fmax: float = 880.0,  # A5 (chitarra 1a corda alta)
                     ) -> List[Dict]:
        """
        Estrae le note dal segnale audio

        Returns:
            Lista di dict con: pitch, start_time, duration, velocity, confidence
        """
        print("🎼 Estrazione note...")

        # 1. ONSET DETECTION - quando iniziano le note
        onset_frames = librosa.onset.onset_detect(
            y=self.y,
            sr=self.sr,
            hop_length=hop_length,
            backtrack=True
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sr, hop_length=hop_length)
        print(f"   Trovati {len(onset_times)} onset (attacchi di nota)")

        # 2. PITCH DETECTION - altezza delle note
        pitches, magnitudes = librosa.piptrack(
            y=self.y,
            sr=self.sr,
            hop_length=hop_length,
            fmin=fmin,
            fmax=fmax,
            threshold=0.1
        )

        # 3. RMS ENERGY - intensità (velocity)
        rms = librosa.feature.rms(y=self.y, hop_length=hop_length)[0]

        # 4. Estrai le note
        notes = []
        for i, onset_time in enumerate(onset_times):
            onset_frame = onset_frames[i]

            # Estrai pitch al momento dell'onset
            pitch_slice = pitches[:, onset_frame]
            magnitude_slice = magnitudes[:, onset_frame]

            # Prendi il pitch con maggiore magnitudine
            if magnitude_slice.max() > 0:
                max_idx = magnitude_slice.argmax()
                pitch_hz = pitch_slice[max_idx]

                if pitch_hz > 0:  # Valido
                    # Converti Hz a MIDI
                    midi_pitch = librosa.hz_to_midi(pitch_hz)

                    # Calcola durata (distanza dal prossimo onset o fine audio)
                    if i < len(onset_times) - 1:
                        duration = onset_times[i + 1] - onset_time
                    else:
                        duration = self.duration - onset_time

                    # Calcola velocity (energia RMS normalizzata)
                    rms_value = rms[onset_frame]
                    velocity_normalized = np.clip(rms_value / rms.max(), 0, 1)

                    # Mappa a velocity simbolica
                    if velocity_normalized < 0.3:
                        velocity = 'p'
                    elif velocity_normalized < 0.5:
                        velocity = 'mp'
                    elif velocity_normalized < 0.7:
                        velocity = 'mf'
                    else:
                        velocity = 'f'

                    # Nome della nota
                    note_name = librosa.midi_to_note(int(midi_pitch), unicode=False)
                    note_letter = note_name[:-1] if len(note_name) > 1 else note_name

                    notes.append({
                        'note': note_letter,
                        'pitch': int(midi_pitch),
                        'pitch_hz': pitch_hz,
                        'start_time': onset_time,
                        'duration': duration,
                        'velocity': velocity,
                        'velocity_value': velocity_normalized,
                        'confidence': magnitude_slice.max(),
                        'index': len(notes)
                    })

        print(f"   ✅ Estratte {len(notes)} note valide")
        return notes

    def detect_techniques(self, notes: List[Dict]) -> List[Dict]:
        """
        Cerca di inferire tecniche chitarristiche dalle caratteristiche audio

        Tecniche rilevabili:
        - Vibrato: oscillazione del pitch
        - Slide: pitch che cambia gradualmente
        - Bend: pitch che sale rapidamente
        - Staccato: durata molto breve
        - Legato: note connesse senza silenzio
        """
        print("🎸 Rilevamento tecniche...")

        hop_length = 512

        # Calcola il pitch continuo per tutta la traccia
        f0, voiced_flag, voiced_probs = librosa.pyin(
            self.y,
            fmin=80,
            fmax=880,
            sr=self.sr,
            hop_length=hop_length
        )

        for note in notes:
            # Default
            note['technique'] = 'regular'

            # Frame range per questa nota
            start_frame = librosa.time_to_frames(note['start_time'], sr=self.sr, hop_length=hop_length)
            end_frame = librosa.time_to_frames(
                note['start_time'] + note['duration'],
                sr=self.sr,
                hop_length=hop_length
            )

            # Estrai pitch per questa nota
            note_f0 = f0[start_frame:end_frame]
            note_f0 = note_f0[~np.isnan(note_f0)]  # Rimuovi NaN

            if len(note_f0) < 2:
                continue

            # VIBRATO: oscillazione del pitch
            f0_diff = np.diff(note_f0)
            if len(f0_diff) > 5:
                # Conta quanti cambi di direzione (su/giù)
                sign_changes = np.sum(np.diff(np.sign(f0_diff)) != 0)
                if sign_changes > 3:  # Multiple oscillazioni
                    note['technique'] = 'vibrato'
                    continue

            # BEND: pitch che sale rapidamente
            if len(note_f0) > 1:
                pitch_change = note_f0[-1] - note_f0[0]
                if pitch_change > 30:  # Sale di più di un semitono
                    note['technique'] = 'bend'
                    continue

            # SLIDE: pitch che cambia gradualmente
            if len(note_f0) > 5:
                pitch_slope = np.polyfit(range(len(note_f0)), note_f0, 1)[0]
                if abs(pitch_slope) > 5:  # Cambio graduale significativo
                    note['technique'] = 'slide'
                    continue

            # STACCATO: nota molto breve
            if note['duration'] < 0.15:
                note['technique'] = 'staccato'
                continue

            # LEGATO: nota lunga e fluida
            if note['duration'] > 0.4:
                note['technique'] = 'legato'

        # Conta tecniche trovate
        techniques_count = {}
        for note in notes:
            tech = note['technique']
            techniques_count[tech] = techniques_count.get(tech, 0) + 1

        print(f"   Tecniche rilevate: {techniques_count}")

        return notes

    def calculate_harmonic_tension(self, notes: List[Dict], key: str = 'A') -> List[Dict]:
        """
        Calcola la tensione armonica di ogni nota rispetto a una tonalità

        Args:
            notes: Lista di note
            key: Tonalità di riferimento (default 'A' per A minor pentatonic)
        """
        # Mappa tensione per pentatonica minore di A
        tension_map = {
            'A': 0.0,   # Tonica
            'C': 0.5,   # Terza minore
            'D': 0.6,   # Quarta
            'E': 0.2,   # Quinta
            'G': 0.8,   # Settima minore
            # Note cromatiche (non in scala)
            'B': 0.7,
            'F': 0.9,
        }

        for note in notes:
            note_name = note['note']
            # Rimuovi # e b per semplicità
            base_note = note_name.replace('#', '').replace('b', '')
            note['tension'] = tension_map.get(base_note, 0.5)  # Default media

        return notes


def extract_audio_from_video(video_file: str, output_audio: str = "temp_audio.wav") -> str:
    """
    Estrae l'audio da un file video

    Args:
        video_file: Path al file video (.mp4, .mov, etc.)
        output_audio: Path per salvare l'audio estratto

    Returns:
        Path al file audio estratto
    """
    print(f"🎬 Estrazione audio da video: {video_file}")

    try:
        # Prova con moviepy
        from moviepy.editor import VideoFileClip

        video = VideoFileClip(video_file)
        video.audio.write_audiofile(output_audio, verbose=False, logger=None)
        video.close()

        print(f"   ✅ Audio estratto: {output_audio}")
        return output_audio

    except ImportError:
        # Fallback: usa ffmpeg direttamente
        import subprocess

        cmd = [
            'ffmpeg', '-i', video_file,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # WAV format
            '-ar', '22050',  # Sample rate
            '-ac', '1',  # Mono
            '-y',  # Overwrite
            output_audio
        ]

        subprocess.run(cmd, capture_output=True, check=True)
        print(f"   ✅ Audio estratto con ffmpeg: {output_audio}")
        return output_audio


if __name__ == "__main__":
    # Test con un file audio di esempio
    import sys

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        print("Usage: python audio_analyzer.py <audio_or_video_file>")
        print("\nEsempio:")
        print("  python audio_analyzer.py 1207(1).mp4")
        print("  python audio_analyzer.py riff.wav")
        sys.exit(1)

    # Se è un video, estrai audio
    if input_file.endswith(('.mp4', '.mov', '.avi', '.MP4', '.MOV')):
        audio_file = extract_audio_from_video(input_file)
    else:
        audio_file = input_file

    # Analizza
    analyzer = AudioAnalyzer(audio_file)
    notes = analyzer.extract_notes()
    notes = analyzer.detect_techniques(notes)
    notes = analyzer.calculate_harmonic_tension(notes)

    # Stampa risultati
    print("\n" + "="*60)
    print("📊 RISULTATI ANALISI")
    print("="*60)
    print(f"Totale note: {len(notes)}")
    print(f"\nPrime 10 note:")
    for i, note in enumerate(notes[:10]):
        print(f"{i+1}. {note['note']} (MIDI {note['pitch']}) "
              f"@ {note['start_time']:.2f}s, "
              f"dur={note['duration']:.2f}s, "
              f"vel={note['velocity']}, "
              f"tech={note['technique']}, "
              f"tension={note['tension']:.1f}")

    # Salva i dati estratti
    import json
    output_json = "extracted_notes.json"

    # Converti numpy types a Python natives per JSON
    notes_serializable = []
    for note in notes:
        note_copy = {}
        for key, value in note.items():
            if isinstance(value, (np.integer, np.floating)):
                note_copy[key] = float(value)
            else:
                note_copy[key] = value
        notes_serializable.append(note_copy)

    with open(output_json, 'w') as f:
        json.dump(notes_serializable, f, indent=2)

    print(f"\n✅ Dati salvati in: {output_json}")
    print("\nOra puoi usare questi dati per generare l'artwork!")
