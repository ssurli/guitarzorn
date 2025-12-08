"""
ZORN PENTATONIC PAINTERLY RENDERER
====================================

Mantiene il parallelismo concettuale:
- PENTATONICA (5 note) ↔ ZORN PALETTE (4-5 colori)
- Entrambi = semplificazione essenziale

Ma aggiunge texture pittoriche REALI:
- Pennellate simulate
- Impasto (texture materica)
- Canvas texture
- Bordi organici
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, PathPatch
from matplotlib.path import Path
import numpy as np
import random
from scipy.ndimage import gaussian_filter
from typing import List, Dict, Tuple
import json
import sys


class ZornPentatonicPainterly:
    """
    Renderer che mantiene palette Zorn (4 colori)
    ma con aspetto PITTORICO professionale
    """

    def __init__(self):
        # PALETTE ZORN RIGOROSA (4 colori base)
        self.zorn_colors = {
            'ochre': np.array([196, 164, 106]) / 255.0,      # Giallo Ocra
            'vermilion': np.array([227, 66, 52]) / 255.0,     # Rosso Vermiglione
            'black': np.array([28, 28, 28]) / 255.0,          # Nero Avorio
            'white': np.array([242, 242, 242]) / 255.0,       # Bianco Titanio
        }

        # PENTATONICA A MINOR → MIXING ZORN
        # Usiamo i 4 colori base + interpolazioni
        self.pentatonic_mapping = {
            'A': self.zorn_colors['ochre'],                                    # Tonica → Ocra puro
            'C': self._mix_colors('vermilion', 'ochre', 0.7),                  # Terza min → Vermilion + Ocra
            'D': self._mix_colors('black', 'ochre', 0.6),                      # Quarta → Nero + Ocra
            'E': self._mix_colors('white', 'ochre', 0.7),                      # Quinta → Bianco + Ocra
            'G': self._mix_colors('ochre', 'black', 0.6),                      # Settima min → Ocra + Nero
        }

        # Canvas setup
        self.width = 2000
        self.height = 1200
        self.fig, self.ax = plt.subplots(figsize=(20, 12), dpi=150)

        # Sfondo ocra (tipico Zorn)
        bg_color = self.zorn_colors['ochre'] * 1.1  # Leggermente più chiaro
        bg_color = np.clip(bg_color, 0, 1)
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.axis('off')

        random.seed(42)
        np.random.seed(42)

        # Texture canvas
        self.canvas_texture = self._create_canvas_texture()

    def _mix_colors(self, color1_name: str, color2_name: str, ratio: float) -> np.ndarray:
        """
        Mixing lineare di due colori Zorn
        ratio: 0.0 = tutto color1, 1.0 = tutto color2
        """
        c1 = self.zorn_colors[color1_name]
        c2 = self.zorn_colors[color2_name]
        mixed = c1 * (1 - ratio) + c2 * ratio
        return np.clip(mixed, 0, 1)

    def _create_canvas_texture(self) -> np.ndarray:
        """Texture lino/canvas realistica"""
        texture = np.random.randn(self.height//4, self.width//4) * 0.015
        texture = gaussian_filter(texture, sigma=1.2)
        return texture

    def get_note_color(self, note_name: str, velocity: float, octave: int = 4) -> Tuple[np.ndarray, float]:
        """
        Restituisce colore per nota pentatonica + alpha

        Args:
            note_name: A, C, D, E, G
            velocity: 0.0-1.0 (p=0.2, mp=0.4, mf=0.6, f=0.9)
            octave: Modula luminosità

        Returns:
            (color, alpha)
        """
        # Colore base dalla pentatonica
        if note_name not in self.pentatonic_mapping:
            # Fallback ad A se nota non pentatonica
            note_name = 'A'

        base_color = self.pentatonic_mapping[note_name].copy()

        # OCTAVE → Luminosità (ottave basse = scuro, alte = chiaro)
        if octave < 4:
            # Ottave basse: mix con nero
            base_color = base_color * 0.7 + self.zorn_colors['black'] * 0.3
        elif octave > 4:
            # Ottave alte: mix con bianco
            base_color = base_color * 0.8 + self.zorn_colors['white'] * 0.2

        # VELOCITY → Saturazione
        if velocity < 0.5:
            # Piano: desatura verso grigio neutro
            gray = np.array([0.4, 0.4, 0.4])
            saturation_factor = velocity / 0.5
            base_color = base_color * saturation_factor + gray * (1 - saturation_factor)

        # VELOCITY → Opacità
        alpha = 0.6 + velocity * 0.35  # Piano=0.6, Forte=0.95

        return np.clip(base_color, 0, 1), alpha

    def draw_brushstroke(self, x: float, y: float, angle: float, length: float,
                        width: float, color: np.ndarray, alpha: float = 0.7):
        """
        Pennellata realistica con setole multiple MIGLIORATA
        """
        # MIGLIORAMENTO: Più setole (10-15 invece di 3)
        num_bristles = max(10, int(width * 3))

        for i in range(num_bristles):
            # Offset casuale per ogni setola (più variazione)
            offset_x = random.gauss(0, width * 0.4)
            offset_y = random.gauss(0, width * 0.4)

            # Lunghezza variabile (più varietà)
            bristle_length = length * random.uniform(0.7, 1.2)

            # Calcola endpoint
            end_x = x + offset_x + np.cos(angle) * bristle_length
            end_y = y + offset_y + np.sin(angle) * bristle_length

            # MIGLIORAMENTO: Variazione colore più ricca
            color_var = color + np.random.randn(3) * 0.04
            color_var = np.clip(color_var, 0, 1)

            # MIGLIORAMENTO: Linewidth variabile per texture
            line_var = width * random.uniform(0.3, 0.6)

            # Disegna setola
            self.ax.plot([x + offset_x, end_x], [y + offset_y, end_y],
                        color=color_var, linewidth=line_var,
                        alpha=alpha*random.uniform(0.6, 1.0),
                        solid_capstyle='round')

    def draw_impasto(self, x: float, y: float, radius: float,
                     color: np.ndarray, alpha: float = 0.8):
        """
        Impasto: texture materica con layer sovrapposti MIGLIORATA
        """
        # MIGLIORAMENTO: 6 layer invece di 3 per più profondità
        for layer in range(6):
            offset = layer * 1.5
            layer_alpha = alpha * (1.0 - layer * 0.12)
            layer_radius = radius * (1.0 - layer * 0.08)

            # MIGLIORAMENTO: Variazione colore più ricca per ogni layer
            if layer > 0:
                # Layer superiori: mix di chiaro/scuro per texture ottica
                variation = random.uniform(-0.03, 0.08)
                layer_color = color * (1.0 + variation)
                layer_color = np.clip(layer_color, 0, 1)
            else:
                layer_color = color

            # MIGLIORAMENTO: Forma più irregolare (8-15 punti)
            num_points = random.randint(8, 15)
            angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)

            points = []
            for angle in angles:
                # MIGLIORAMENTO: Più irregolarità nei bordi
                r = layer_radius * random.uniform(0.6, 1.4)
                px = x + offset + r * np.cos(angle)
                py = y + offset + r * np.sin(angle)
                points.append([px, py])

            polygon = Polygon(points, facecolor=layer_color,
                            edgecolor=None, alpha=layer_alpha)
            self.ax.add_patch(polygon)

    def draw_glazing(self, x: float, y: float, radius: float,
                     color: np.ndarray, alpha: float = 0.25):
        """
        NUOVA TECNICA: Glazing - layer trasparenti sovrapposti
        Crea profondità ottica come nelle tecniche classiche
        """
        # 3-4 layer trasparenti con offset leggero
        num_glazes = random.randint(3, 4)

        for i in range(num_glazes):
            offset_x = random.gauss(0, 3)
            offset_y = random.gauss(0, 3)

            # Variazione colore sottile
            glaze_color = color + np.random.randn(3) * 0.02
            glaze_color = np.clip(glaze_color, 0, 1)

            # Cerchio trasparente
            circle = Circle((x + offset_x, y + offset_y),
                          radius * random.uniform(0.8, 1.2),
                          facecolor=glaze_color,
                          edgecolor=None,
                          alpha=alpha * random.uniform(0.7, 1.0))
            self.ax.add_patch(circle)

    def draw_dry_brush(self, x: float, y: float, angle: float, length: float,
                      color: np.ndarray):
        """
        NUOVA TECNICA: Dry Brush - pennellate secche con gaps
        Simula pennello con poca pittura
        """
        # 5-8 tratti corti e interrotti
        num_strokes = random.randint(5, 8)

        for i in range(num_strokes):
            # Position lungo la direzione del brush
            t = i / num_strokes
            start_x = x + np.cos(angle) * length * t
            start_y = y + np.sin(angle) * length * t

            # Lunghezza corta e interrotta
            stroke_len = length * random.uniform(0.05, 0.15)
            end_x = start_x + np.cos(angle) * stroke_len
            end_y = start_y + np.sin(angle) * stroke_len

            # Offset laterale per texture
            offset = random.gauss(0, 3)
            start_x += np.cos(angle + np.pi/2) * offset
            start_y += np.sin(angle + np.pi/2) * offset
            end_x += np.cos(angle + np.pi/2) * offset
            end_y += np.sin(angle + np.pi/2) * offset

            # Colore con variazione
            stroke_color = color + np.random.randn(3) * 0.03
            stroke_color = np.clip(stroke_color, 0, 1)

            # Disegna stroke interrotto
            self.ax.plot([start_x, end_x], [start_y, end_y],
                        color=stroke_color,
                        linewidth=random.uniform(1, 3),
                        alpha=random.uniform(0.4, 0.7),
                        solid_capstyle='round')

    def draw_dripping(self, x: float, y: float, color: np.ndarray, intensity: float = 1.0):
        """
        NUOVA TECNICA: Dripping Pollock-style
        Gocciolature verticali/diagonali dalla nota
        """
        num_drips = int(random.randint(2, 5) * intensity)

        for _ in range(num_drips):
            # Direzione principalmente verso il basso ma con variazione
            angle = np.pi/2 + random.gauss(0, 0.3)  # ~90° con variazione

            # Lunghezza variabile
            drip_length = random.uniform(20, 80) * intensity

            # Punto di partenza con offset
            start_x = x + random.gauss(0, 10)
            start_y = y + random.gauss(0, 10)

            # Disegna gocciolatura come serie di piccoli segmenti
            segments = random.randint(5, 10)
            current_x, current_y = start_x, start_y

            for seg in range(segments):
                seg_len = drip_length / segments
                # Aggiungi sinuosità alla goccia
                angle_var = angle + random.gauss(0, 0.1)
                end_x = current_x + np.cos(angle_var) * seg_len
                end_y = current_y + np.sin(angle_var) * seg_len

                # Colore con variazione
                drip_color = color + np.random.randn(3) * 0.02
                drip_color = np.clip(drip_color, 0, 1)

                # Spessore che si assottiglia
                thickness = (1.5 - seg/segments) * random.uniform(0.5, 1.5)

                self.ax.plot([current_x, end_x], [current_y, end_y],
                           color=drip_color, linewidth=thickness,
                           alpha=random.uniform(0.3, 0.6),
                           solid_capstyle='round')

                current_x, current_y = end_x, end_y

    def draw_splatter(self, x: float, y: float, color: np.ndarray, intensity: float = 1.0):
        """
        NUOVA TECNICA: Splatter marks (schizzi)
        Piccole macchie casuali intorno alla nota
        """
        num_splatters = int(random.randint(8, 15) * intensity)

        for _ in range(num_splatters):
            # Posizione casuale attorno al punto
            angle = random.uniform(0, 2*np.pi)
            distance = random.uniform(10, 50) * intensity
            sx = x + np.cos(angle) * distance
            sy = y + np.sin(angle) * distance

            # Dimensione piccola
            size = random.uniform(1, 4)

            # Colore con variazione
            splat_color = color + np.random.randn(3) * 0.05
            splat_color = np.clip(splat_color, 0, 1)

            # Disegna come piccolo cerchio irregolare
            circle = Circle((sx, sy), size,
                          facecolor=splat_color,
                          edgecolor=None,
                          alpha=random.uniform(0.3, 0.7))
            self.ax.add_patch(circle)

    def draw_craquelure(self, x: float, y: float, radius: float, color: np.ndarray):
        """
        NUOVA TECNICA: Craquelure (crepe della pittura secca)
        Rete di piccole crepe per effetto invecchiamento
        """
        num_cracks = random.randint(5, 10)

        # Colore scuro per le crepe
        crack_color = self.zorn_colors['black'] * 0.5

        for _ in range(num_cracks):
            # Punto di partenza casuale nel raggio
            start_angle = random.uniform(0, 2*np.pi)
            start_dist = random.uniform(0, radius * 0.8)
            start_x = x + np.cos(start_angle) * start_dist
            start_y = y + np.sin(start_angle) * start_dist

            # Lunghezza della crepa
            crack_len = random.uniform(radius * 0.2, radius * 0.6)
            crack_angle = random.uniform(0, 2*np.pi)

            # Disegna crepa come linea spezzata
            segments = 3
            current_x, current_y = start_x, start_y

            for seg in range(segments):
                seg_len = crack_len / segments
                angle_var = crack_angle + random.gauss(0, 0.3)
                end_x = current_x + np.cos(angle_var) * seg_len
                end_y = current_y + np.sin(angle_var) * seg_len

                self.ax.plot([current_x, end_x], [current_y, end_y],
                           color=crack_color, linewidth=0.3,
                           alpha=random.uniform(0.2, 0.4))

                current_x, current_y = end_x, end_y

    def apply_canvas_texture(self):
        """
        Applica texture canvas effettiva all'immagine
        """
        # Crea pattern di texture più visibile
        for _ in range(50):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)

            # Piccole linee per simulare trama del canvas
            angle = random.choice([0, np.pi/2])  # Orizzontale o verticale
            length = random.uniform(5, 15)

            end_x = x + np.cos(angle) * length
            end_y = y + np.sin(angle) * length

            # Colore neutro (variazione dello sfondo)
            canvas_color = self.zorn_colors['ochre'] * random.uniform(0.95, 1.05)
            canvas_color = np.clip(canvas_color, 0, 1)

            self.ax.plot([x, end_x], [y, end_y],
                        color=canvas_color, linewidth=0.5,
                        alpha=random.uniform(0.1, 0.2))

    def draw_melodic_path(self, notes: List[Dict], alpha: float = 0.15):
        """
        Disegna percorso melodico come guida visiva
        """
        if len(notes) < 2:
            return

        positions = [(n['x_pos'], n['y_pos']) for n in notes]

        # Curva smooth con Bézier
        path_data = []
        path_data.append((Path.MOVETO, positions[0]))

        for i in range(1, len(positions)):
            # Control point per curva morbida
            prev = positions[i-1]
            curr = positions[i]
            ctrl_x = (prev[0] + curr[0]) / 2
            ctrl_y = (prev[1] + curr[1]) / 2

            path_data.append((Path.CURVE3, (ctrl_x, ctrl_y)))
            path_data.append((Path.CURVE3, curr))

        codes, verts = zip(*path_data)
        path = Path(verts, codes)

        # Disegna path sottile
        patch = PathPatch(path, facecolor='none',
                         edgecolor=self.zorn_colors['black'],
                         linewidth=1.5, alpha=alpha)
        self.ax.add_patch(patch)

    def render_note(self, note: Dict):
        """
        Renderizza singola nota con tecnica pittorica
        """
        x = note['x_pos']
        y = note['y_pos']
        note_name = note['note']
        velocity = note.get('velocity_value', 0.7)
        duration = note['duration']
        technique = note.get('technique', 'normal')

        # Ottava dal pitch MIDI
        octave = note['pitch'] // 12

        # Colore e alpha
        color, alpha = self.get_note_color(note_name, velocity, octave)

        # Dimensione base da velocity e durata
        base_size = 30 + velocity * 40 + duration * 20

        # TECNICA → FORMA PITTORICA
        if technique == 'staccato':
            # Punto singolo netto
            self.draw_impasto(x, y, base_size * 0.6, color, alpha * 1.1)

        elif technique == 'legato':
            # Pennellata lunga e fluida
            angle = random.uniform(0, 2 * np.pi)
            self.draw_brushstroke(x, y, angle, base_size * 1.5,
                                base_size * 0.3, color, alpha)

        elif technique == 'slide':
            # Pennellata diagonale
            angle = np.pi / 4  # 45 gradi
            self.draw_brushstroke(x, y, angle, base_size * 2,
                                base_size * 0.4, color, alpha)

        elif technique == 'bend':
            # Curva pittorica
            # Disegna curva con punti
            t = np.linspace(0, 1, 20)
            curve_x = x + t * base_size
            curve_y = y + np.sin(t * np.pi) * base_size * 0.5

            for i in range(len(t)-1):
                self.ax.plot([curve_x[i], curve_x[i+1]],
                           [curve_y[i], curve_y[i+1]],
                           color=color, linewidth=base_size*0.2,
                           alpha=alpha, solid_capstyle='round')

        elif technique == 'vibrato':
            # Forma ondulata
            num_waves = 5
            for i in range(num_waves):
                offset_y = np.sin(i / num_waves * 2 * np.pi) * base_size * 0.3
                self.draw_impasto(x + i * 10, y + offset_y,
                                base_size * 0.5, color, alpha * 0.7)

        else:
            # Forma standard: impasto + pennellata + NUOVE TECNICHE
            self.draw_impasto(x, y, base_size * 0.7, color, alpha)

            # Pennellata decorativa
            angle = random.uniform(0, 2 * np.pi)
            self.draw_brushstroke(x, y, angle, base_size * 0.8,
                                base_size * 0.2, color, alpha * 0.6)

            # MIGLIORAMENTO: Aggiungi glazing per profondità (30% probabilità)
            if random.random() < 0.3:
                self.draw_glazing(x, y, base_size * 0.9, color, alpha * 0.2)

            # MIGLIORAMENTO: Aggiungi dry brush per texture (20% probabilità)
            if random.random() < 0.2:
                angle_dry = random.uniform(0, 2 * np.pi)
                self.draw_dry_brush(x, y, angle_dry, base_size * 0.6, color)

            # NUOVA TECNICA: Dripping Pollock-style (15% probabilità)
            if random.random() < 0.15:
                self.draw_dripping(x, y, color, intensity=velocity)

            # NUOVA TECNICA: Splatter marks (25% probabilità)
            if random.random() < 0.25:
                self.draw_splatter(x, y, color, intensity=velocity * 0.8)

            # NUOVA TECNICA: Craquelure per invecchiamento (10% probabilità)
            if random.random() < 0.1:
                self.draw_craquelure(x, y, base_size * 0.8, color)

    def render_artwork(self, notes: List[Dict], output_path: str):
        """
        Renderizza opera completa
        """
        print(f"🎨 Rendering con palette Zorn (parallelismo pentatonica)...")
        print(f"   {len(notes)} note da renderizzare")

        # 0. NUOVA TECNICA: Applica texture canvas
        print("   Applicando canvas texture...")
        self.apply_canvas_texture()

        # 1. Disegna percorso melodico
        self.draw_melodic_path(notes, alpha=0.12)

        # 2. MIGLIORAMENTO: Background texture elements (50 invece di 30!)
        print("   Disegnando background ricco...")
        for _ in range(50):
            x = random.uniform(100, self.width - 100)
            y = random.uniform(100, self.height - 100)
            radius = random.uniform(30, 100)

            # Usa colori Zorn per background
            bg_color_choice = random.choice(['ochre', 'white', 'black', 'vermilion'])
            bg_color = self.zorn_colors[bg_color_choice]

            # MIGLIORAMENTO: Varietà di tecniche per background + NUOVE TECNICHE
            technique = random.choice(['impasto', 'glazing', 'brushstroke', 'splatter', 'dripping'])

            if technique == 'impasto':
                self.draw_impasto(x, y, radius, bg_color, alpha=0.12)
            elif technique == 'glazing':
                self.draw_glazing(x, y, radius, bg_color, alpha=0.15)
            elif technique == 'brushstroke':
                angle = random.uniform(0, 2 * np.pi)
                self.draw_brushstroke(x, y, angle, radius * 1.5,
                                    radius * 0.3, bg_color, alpha=0.1)
            elif technique == 'splatter':
                # NUOVA: Splatter nel background
                self.draw_splatter(x, y, bg_color, intensity=0.5)
            else:  # dripping
                # NUOVA: Dripping nel background
                self.draw_dripping(x, y, bg_color, intensity=0.4)

        # 3. Renderizza note
        for note in notes:
            self.render_note(note)

        # 4. Salva
        print(f"💾 Salvando: {output_path}")
        self.fig.savefig(output_path,
                        facecolor=self.fig.get_facecolor(),
                        dpi=150,
                        bbox_inches='tight')
        print(f"✅ Completato!")

        plt.close()


def load_notes_from_json(json_path: str) -> List[Dict]:
    """Carica note da file JSON"""
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Se è già una lista, usala direttamente
    if isinstance(data, list):
        return data
    # Altrimenti cerca 'notes' nel dict
    return data.get('notes', [])


def main():
    if len(sys.argv) < 2:
        print("Uso: python zorn_pentatonic_painterly.py <notes.json> [output.png]")
        print("\nEsempio:")
        print("  python zorn_pentatonic_painterly.py 1207(1)_notes.json zorn_pentatonic_art.png")
        sys.exit(1)

    input_json = sys.argv[1]
    output_png = sys.argv[2] if len(sys.argv) > 2 else 'zorn_pentatonic_art.png'

    # Carica note
    print(f"📖 Caricando note da: {input_json}")
    notes = load_notes_from_json(input_json)

    if not notes:
        print("❌ Nessuna nota trovata nel JSON!")
        sys.exit(1)

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

        # Normalizza velocity
        if 'velocity' in note:
            vel_map = {'p': 0.2, 'mp': 0.4, 'mf': 0.6, 'f': 0.9, 'ff': 1.0}
            note['velocity_value'] = vel_map.get(note['velocity'], 0.7)
        else:
            note['velocity_value'] = 0.7

    # Renderizza
    renderer = ZornPentatonicPainterly()
    renderer.render_artwork(notes, output_png)


if __name__ == "__main__":
    main()
