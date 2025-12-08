"""
AI-ENHANCED ARTWORK PIPELINE
Usa Replicate API per trasformare l'immagine tecnica in opera pittorica

Flusso:
1. Genera immagine base da musica (algoritmo attuale)
2. Passa attraverso Stable Diffusion img2img su Replicate
3. Ottieni opera d'arte con texture pittorica reale
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

class ReplicateArtEnhancer:
    """
    Migliora le immagini generate usando Replicate AI
    """

    def __init__(self, api_token: str = None):
        """
        Args:
            api_token: Token API di Replicate (da https://replicate.com/account)
                      Se None, cerca in env REPLICATE_API_TOKEN
        """
        self.api_token = api_token or os.environ.get('REPLICATE_API_TOKEN')

        if not self.api_token:
            raise ValueError(
                "Serve token API di Replicate!\n"
                "Ottienilo da: https://replicate.com/account\n"
                "Poi: export REPLICATE_API_TOKEN='r8_...'"
            )

        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

    def enhance_with_style(self,
                          input_image: str,
                          style: str = "oil painting",
                          strength: float = 0.7,
                          prompt: str = None,
                          output_path: str = None) -> str:
        """
        Trasforma immagine tecnica in opera pittorica

        Args:
            input_image: Path all'immagine base generata
            style: Stile pittorico ("oil painting", "watercolor", "abstract expressionism", etc.)
            strength: Quanto mantenere l'originale (0.0=totale trasformazione, 1.0=minimale)
            prompt: Prompt personalizzato (se None, usa default basato su style)
            output_path: Dove salvare (default: input_image + '_enhanced.png')

        Returns:
            Path all'immagine migliorata
        """
        if output_path is None:
            base = Path(input_image).stem
            output_path = f"{base}_enhanced.png"

        # Default prompt basato sullo stile
        if prompt is None:
            prompt = self._get_default_prompt(style)

        print(f"\n🎨 Miglioramento AI dell'immagine...")
        print(f"   Input: {input_image}")
        print(f"   Stile: {style}")
        print(f"   Strength: {strength}")
        print(f"   Prompt: {prompt}")

        # Converti immagine in base64 o URL
        image_data = self._encode_image(input_image)

        # Usa Stable Diffusion img2img
        model = "stability-ai/stable-diffusion:img2img"

        payload = {
            "version": "db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
            "input": {
                "image": image_data,
                "prompt": prompt,
                "strength": 1.0 - strength,  # Replicate usa "quanto cambiare"
                "guidance_scale": 7.5,
                "num_inference_steps": 50,
                "negative_prompt": "ugly, blurry, low quality, pixelated, digital art, 3d render, photograph"
            }
        }

        # Avvia predizione
        print("   Avvio predizione...")
        response = requests.post(
            f"{self.base_url}/predictions",
            headers=self.headers,
            json=payload
        )

        if response.status_code != 201:
            raise Exception(f"Errore API: {response.status_code} - {response.text}")

        prediction = response.json()
        prediction_id = prediction['id']

        print(f"   Prediction ID: {prediction_id}")
        print("   Attendere completamento...")

        # Poll fino a completamento
        while True:
            response = requests.get(
                f"{self.base_url}/predictions/{prediction_id}",
                headers=self.headers
            )

            prediction = response.json()
            status = prediction['status']

            if status == 'succeeded':
                output_url = prediction['output'][0] if isinstance(prediction['output'], list) else prediction['output']
                print(f"   ✅ Completato!")

                # Scarica immagine
                self._download_image(output_url, output_path)
                print(f"   💾 Salvato: {output_path}")

                return output_path

            elif status == 'failed':
                raise Exception(f"Predizione fallita: {prediction.get('error')}")

            elif status in ['starting', 'processing']:
                print(f"   Status: {status}...")
                time.sleep(2)

            else:
                print(f"   Status sconosciuto: {status}")
                time.sleep(2)

    def _get_default_prompt(self, style: str) -> str:
        """Genera prompt basato sullo stile richiesto"""

        prompts = {
            "oil painting": (
                "masterpiece oil painting on canvas, thick impasto brushstrokes, "
                "visible texture, rich colors, expressive, painted by master artist, "
                "museum quality, fine art"
            ),
            "watercolor": (
                "delicate watercolor painting, soft washes, flowing colors, "
                "paper texture visible, translucent layers, artistic, elegant"
            ),
            "abstract expressionism": (
                "abstract expressionist painting, bold gestural brushstrokes, "
                "dynamic composition, emotional, energetic, action painting style, "
                "by Jackson Pollock or Willem de Kooning"
            ),
            "impressionism": (
                "impressionist painting, short broken brushstrokes, "
                "emphasis on light and color, vibrant, by Monet or Renoir style"
            ),
            "mixed media": (
                "mixed media artwork, collage elements, textured layers, "
                "acrylic and oil, contemporary art, gallery worthy"
            ),
            "gouache": (
                "gouache painting, matte finish, opaque colors, "
                "flat areas of color, poster paint aesthetic, modern illustration"
            ),
            "acrylic": (
                "acrylic painting on canvas, bold colors, contemporary style, "
                "smooth or textured finish, vibrant, modern art"
            )
        }

        return prompts.get(style.lower(), prompts["oil painting"])

    def _encode_image(self, image_path: str) -> str:
        """Converti immagine in formato per Replicate"""
        import base64

        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        # Converti in data URI
        base64_str = base64.b64encode(image_bytes).decode('utf-8')

        # Determina mime type
        ext = Path(image_path).suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }
        mime = mime_types.get(ext, 'image/png')

        return f"data:{mime};base64,{base64_str}"

    def _download_image(self, url: str, output_path: str):
        """Scarica immagine da URL"""
        response = requests.get(url)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

    def batch_enhance(self,
                     image_paths: list,
                     style: str = "oil painting",
                     strength: float = 0.7) -> list:
        """
        Migliora batch di immagini
        """
        results = []

        print(f"\n{'='*60}")
        print(f"🎨 BATCH ENHANCEMENT - {len(image_paths)} immagini")
        print(f"{'='*60}")

        for i, img_path in enumerate(image_paths, 1):
            print(f"\n[{i}/{len(image_paths)}] Processando: {img_path}")

            try:
                output = self.enhance_with_style(img_path, style, strength)
                results.append(output)
            except Exception as e:
                print(f"   ❌ Errore: {e}")
                results.append(None)

        print(f"\n{'='*60}")
        print(f"✅ Completati: {len([r for r in results if r])}/{len(image_paths)}")
        print(f"{'='*60}")

        return results


# STILI PREDEFINITI PER MUSICA

MUSIC_STYLES = {
    "rock": {
        "style": "abstract expressionism",
        "prompt": "energetic abstract expressionist painting, bold brushstrokes, raw power, vibrant reds and blacks",
        "strength": 0.6
    },

    "blues": {
        "style": "oil painting",
        "prompt": "moody oil painting, deep blues and warm ochres, emotional, soulful, textured",
        "strength": 0.7
    },

    "jazz": {
        "style": "abstract expressionism",
        "prompt": "improvisational abstract art, flowing organic forms, sophisticated color palette, rhythmic",
        "strength": 0.65
    },

    "metal": {
        "style": "mixed media",
        "prompt": "aggressive mixed media artwork, dark intense colors, chaotic energy, heavy textures",
        "strength": 0.5
    },

    "classical": {
        "style": "impressionism",
        "prompt": "elegant impressionist painting, refined brushwork, harmonious colors, classical composition",
        "strength": 0.75
    },

    "ambient": {
        "style": "watercolor",
        "prompt": "ethereal watercolor, soft atmospheric washes, dreamy colors, meditative, flowing",
        "strength": 0.8
    }
}


def main():
    """
    Main per enhancement delle immagini
    """
    if len(sys.argv) < 2:
        print("="*60)
        print("🎨 AI ART ENHANCER (via Replicate)")
        print("="*60)
        print("\nTrasforma immagini tecniche in opere pittoriche!")
        print("\nSETUP:")
        print("1. Ottieni API token da: https://replicate.com/account")
        print("2. export REPLICATE_API_TOKEN='r8_your_token_here'")
        print("\nUSO:")
        print(f"  python {sys.argv[0]} <immagine> [--style <stile>] [--strength <0-1>]")
        print(f"  python {sys.argv[0]} <immagine> --genre <rock|blues|jazz|metal>")
        print("\nSTILI:")
        print("  - oil painting (default)")
        print("  - watercolor")
        print("  - abstract expressionism")
        print("  - impressionism")
        print("  - mixed media")
        print("  - acrylic")
        print("  - gouache")
        print("\nGENERI MUSICALI (preset):")
        print("  - rock, blues, jazz, metal, classical, ambient")
        print("\nESEMPI:")
        print(f"  python {sys.argv[0]} 1207\(1\)_organic_growth.png")
        print(f"  python {sys.argv[0]} artwork.png --style watercolor")
        print(f"  python {sys.argv[0]} riff.png --genre rock")
        print("="*60)
        sys.exit(1)

    input_image = sys.argv[1]

    if not os.path.exists(input_image):
        print(f"❌ File non trovato: {input_image}")
        sys.exit(1)

    # Parse arguments
    style = "oil painting"
    strength = 0.7
    prompt = None

    if '--style' in sys.argv:
        idx = sys.argv.index('--style')
        style = sys.argv[idx + 1]

    if '--strength' in sys.argv:
        idx = sys.argv.index('--strength')
        strength = float(sys.argv[idx + 1])

    if '--prompt' in sys.argv:
        idx = sys.argv.index('--prompt')
        prompt = sys.argv[idx + 1]

    if '--genre' in sys.argv:
        idx = sys.argv.index('--genre')
        genre = sys.argv[idx + 1].lower()

        if genre in MUSIC_STYLES:
            config = MUSIC_STYLES[genre]
            style = config['style']
            prompt = config['prompt']
            strength = config['strength']
            print(f"🎵 Usando preset per genere: {genre}")
        else:
            print(f"⚠️  Genere sconosciuto: {genre}, uso default")

    # Enhance
    try:
        enhancer = ReplicateArtEnhancer()
        output = enhancer.enhance_with_style(
            input_image,
            style=style,
            strength=strength,
            prompt=prompt
        )

        print(f"\n✨ Completato!")
        print(f"   Input:  {input_image}")
        print(f"   Output: {output}")

    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
