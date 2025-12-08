"""
LIVE PERFORMANCE TO ARTWORK
Sistema completo: Video → Audio Analysis → Visual Art

Unisce:
- audio_analyzer.py (estrazione note dal vivo)
- approach_4_organic_growth.py (visualizzazione organica)
- approach_5_tension_field.py (visualizzazione tensione armonica)
"""

import json
import sys
import os
from audio_analyzer import AudioAnalyzer, extract_audio_from_video

# Import degli approcci visivi
from approach_4_organic_growth import OrganicGrowthArt
from approach_5_tension_field import TensionFieldArt

class LivePerformanceToArt:
    """
    Converte una performance dal vivo in opera d'arte
    """

    def __init__(self, input_file: str):
        """
        Args:
            input_file: Path a file video (.mp4, .mov) o audio (.wav, .mp3)
        """
        self.input_file = input_file
        self.notes = None
        self.audio_file = None

    def analyze(self):
        """
        Analizza il file e estrae le note
        """
        print("\n" + "="*60)
        print("🎸 LIVE PERFORMANCE TO ART")
        print("="*60)

        # Se è video, estrai audio
        if self.input_file.endswith(('.mp4', '.mov', '.avi', '.MP4', '.MOV', '.webm')):
            self.audio_file = extract_audio_from_video(self.input_file, "temp_extracted_audio.wav")
        else:
            self.audio_file = self.input_file

        # Analizza audio
        analyzer = AudioAnalyzer(self.audio_file)
        self.notes = analyzer.extract_notes()
        self.notes = analyzer.detect_techniques(self.notes)
        self.notes = analyzer.calculate_harmonic_tension(self.notes)

        # Statistiche
        print("\n📊 ANALISI COMPLETATA")
        print(f"   Note totali: {len(self.notes)}")
        print(f"   Durata: {analyzer.duration:.2f}s")

        # Tecniche rilevate
        techniques = {}
        for note in self.notes:
            tech = note['technique']
            techniques[tech] = techniques.get(tech, 0) + 1
        print(f"   Tecniche: {techniques}")

        return self.notes

    def generate_organic_growth(self, output_file: str = "live_organic_growth.png"):
        """
        Genera artwork con approccio Organic Growth
        """
        if self.notes is None:
            raise ValueError("Devi prima chiamare analyze()")

        print("\n🌱 Generazione Organic Growth...")

        # Crea l'artwork modificando l'approccio per usare le note reali
        artist = OrganicGrowthArtLive(self.notes)
        artist.create_artwork(output_file)

        print(f"✅ Salvato: {output_file}")
        return output_file

    def generate_tension_field(self, output_file: str = "live_tension_field.png"):
        """
        Genera artwork con approccio Tension Field
        """
        if self.notes is None:
            raise ValueError("Devi prima chiamare analyze()")

        print("\n⚖️ Generazione Tension Field...")

        # Crea l'artwork modificando l'approccio per usare le note reali
        artist = TensionFieldArtLive(self.notes)
        artist.create_artwork(output_file)

        print(f"✅ Salvato: {output_file}")
        return output_file


class OrganicGrowthArtLive(OrganicGrowthArt):
    """
    Versione di Organic Growth che usa note estratte dal vivo
    """

    def __init__(self, live_notes):
        super().__init__()
        self.live_notes = live_notes

    def parse_johnny_b_goode_riff(self):
        """
        Override: usa le note dal vivo invece del riff pre-codificato
        """
        return self.live_notes


class TensionFieldArtLive(TensionFieldArt):
    """
    Versione di Tension Field che usa note estratte dal vivo
    """

    def __init__(self, live_notes):
        super().__init__()
        self.live_notes = live_notes

    def parse_johnny_b_goode_riff(self):
        """
        Override: usa le note dal vivo invece del riff pre-codificato
        """
        return self.live_notes


def main():
    """
    Main: analizza e genera artwork
    """
    if len(sys.argv) < 2:
        print("="*60)
        print("🎸 LIVE PERFORMANCE TO ART")
        print("="*60)
        print("\nConverte un video/audio di te che suoni in un'opera d'arte!")
        print("\nUSO:")
        print(f"  python {sys.argv[0]} <video_o_audio_file> [--organic] [--tension] [--both]")
        print("\nESEMPI:")
        print(f"  python {sys.argv[0]} 1207(1).mp4")
        print(f"  python {sys.argv[0]} riff.wav --both")
        print(f"  python {sys.argv[0]} performance.mp4 --organic")
        print("\nOPZIONI:")
        print("  --organic : Genera solo Organic Growth (default)")
        print("  --tension : Genera solo Tension Field")
        print("  --both    : Genera entrambi")
        print("="*60)
        sys.exit(1)

    input_file = sys.argv[1]

    # Verifica che il file esista
    if not os.path.exists(input_file):
        print(f"❌ Errore: File non trovato: {input_file}")
        sys.exit(1)

    # Opzioni
    generate_organic = '--organic' in sys.argv or '--both' in sys.argv or len(sys.argv) == 2
    generate_tension = '--tension' in sys.argv or '--both' in sys.argv

    # Analizza e genera
    converter = LivePerformanceToArt(input_file)
    converter.analyze()

    # Salva dati estratti
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Converti note per JSON (rimuovi numpy types)
    import numpy as np
    notes_json = []
    for note in converter.notes:
        note_copy = {}
        for key, value in note.items():
            if isinstance(value, (np.integer, np.floating)):
                note_copy[key] = float(value)
            else:
                note_copy[key] = value
        notes_json.append(note_copy)

    json_file = f"{base_name}_notes.json"
    with open(json_file, 'w') as f:
        json.dump(notes_json, f, indent=2)
    print(f"\n💾 Note salvate in: {json_file}")

    # Genera artwork
    print("\n" + "="*60)
    print("🎨 GENERAZIONE ARTWORK")
    print("="*60)

    if generate_organic:
        converter.generate_organic_growth(f"{base_name}_organic_growth.png")

    if generate_tension:
        converter.generate_tension_field(f"{base_name}_tension_field.png")

    print("\n" + "="*60)
    print("✨ COMPLETATO!")
    print("="*60)

    if converter.audio_file and converter.audio_file.startswith("temp_"):
        print(f"\nPuoi eliminare il file temporaneo: {converter.audio_file}")


if __name__ == "__main__":
    main()
