"""
Hybrid SD Processor: Apply Stable Diffusion artistic effect via Replicate API
Automates the image-to-image transformation for oil painting style
"""

import os
import sys


def apply_sd_artistic_effect(input_image_path, output_path,
                             strength=0.65, style='balanced',
                             api_token=None):
    """
    Apply Stable Diffusion artistic effect via Replicate

    Parameters:
    -----------
    input_image_path: str - path to input image (raw artwork)
    output_path: str - path to save output
    strength: float (0.0-1.0) - how much AI modifies image (0.65 recommended)
    style: str - prompt style preset
        - 'balanced': soft oil painting (recommended)
        - 'painterly': thick brushstrokes
        - 'dreamlike': soft blended (ChatGPT-like)
    api_token: str - Replicate API token (or set REPLICATE_API_TOKEN env var)

    Returns:
    --------
    str - path to output image
    """

    # Check for replicate package
    try:
        import replicate
    except ImportError:
        print("❌ Error: 'replicate' package not found.")
        print("Install with: pip install replicate")
        sys.exit(1)

    # Check API token
    if api_token:
        os.environ['REPLICATE_API_TOKEN'] = api_token

    if not os.environ.get('REPLICATE_API_TOKEN'):
        print("❌ Error: REPLICATE_API_TOKEN not set")
        print("Set it with: export REPLICATE_API_TOKEN='your-token'")
        print("Get token at: https://replicate.com/account/api-tokens")
        sys.exit(1)

    # Prompt templates
    prompts = {
        'balanced': """oil painting on canvas, soft blended brushstrokes,
                      impressionist style, Zorn palette with ochre yellow,
                      vermilion red, ivory black and titanium white,
                      thick impasto texture, painterly, abstract expressionist,
                      materic surface, natural lighting, high quality canvas texture,
                      artistic, no sharp edges, dreamlike quality, professional art""",

        'painterly': """thick oil paint on linen canvas, alla prima technique,
                       Zorn limited palette, visible brush marks, impasto texture,
                       impressionist masterpiece, museum quality, warm ochre tones
                       with vermilion accents, chiaroscuro lighting, painterly abstraction""",

        'dreamlike': """soft dreamlike oil painting, blended brushstrokes fading into background,
                       muted Zorn palette, subtle color transitions, atmospheric, ethereal quality,
                       delicate impasto, impressionist mood, warm ambient light, artistic blur,
                       no sharp edges, organic color blending, smooth texture"""
    }

    negative_prompt = """digital art, vector, sharp edges, geometric,
                        photograph, 3d render, cartoon, anime, modern, clean,
                        computer graphics, illustration"""

    print(f"\n🎨 Applying Stable Diffusion artistic effect...")
    print(f"   Input: {input_image_path}")
    print(f"   Style: {style}")
    print(f"   Strength: {strength}")
    print("-" * 60)

    # Open and validate input
    if not os.path.exists(input_image_path):
        print(f"❌ Error: Input file not found: {input_image_path}")
        sys.exit(1)

    # Run Stable Diffusion via Replicate
    print("   ├─ Uploading to Replicate...")

    with open(input_image_path, "rb") as image_file:
        try:
            print("   ├─ Running Stable Diffusion SDXL...")
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "image": image_file,
                    "prompt": prompts.get(style, prompts['balanced']),
                    "negative_prompt": negative_prompt,
                    "strength": strength,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 50,
                }
            )

            # Download result
            print("   ├─ Downloading result...")
            import urllib.request
            urllib.request.urlretrieve(output[0], output_path)

            print(f"   └─ Saved to {output_path}")
            print("-" * 60)
            print(f"✅ Artistic effect applied successfully!")
            print(f"📁 Output: {output_path}")

            return output_path

        except Exception as e:
            print(f"❌ Error running Stable Diffusion: {e}")
            sys.exit(1)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Apply Stable Diffusion artistic effect to guitar riff artwork'
    )

    parser.add_argument('input', help='Input image path (raw artwork)')
    parser.add_argument('output', nargs='?', default='sd_output.png',
                       help='Output image path (default: sd_output.png)')
    parser.add_argument('--style', '-s', default='dreamlike',
                       choices=['balanced', 'painterly', 'dreamlike'],
                       help='Prompt style preset (default: dreamlike)')
    parser.add_argument('--strength', '-t', type=float, default=0.65,
                       help='Transformation strength 0.0-1.0 (default: 0.65)')
    parser.add_argument('--token', help='Replicate API token (or use env var)')

    args = parser.parse_args()

    # Validate strength
    if not 0.0 <= args.strength <= 1.0:
        print("❌ Error: strength must be between 0.0 and 1.0")
        sys.exit(1)

    apply_sd_artistic_effect(
        args.input,
        args.output,
        strength=args.strength,
        style=args.style,
        api_token=args.token
    )


if __name__ == "__main__":
    main()
