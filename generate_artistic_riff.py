#!/usr/bin/env python3
"""
Complete pipeline: Generate riff artwork + Apply artistic post-processing
Creates realistic oil painting style from guitar riff
"""

from zorn_riff_art_enhanced import EnhancedZornGuitarRiffArt
from artistic_postprocessing import quick_artistic_transform, ArtisticPostProcessor
import argparse


def generate_artistic_riff(output_name='artistic_riff',
                           seed=42,
                           width=1600,
                           height=1000,
                           dpi=150,
                           preset='balanced'):
    """
    Complete pipeline: generate + artistic post-processing

    Parameters:
    -----------
    output_name: str - base name for output files
    seed: int - random seed for repeatability
    width, height: int - canvas dimensions
    dpi: int - resolution
    preset: str - artistic effect preset (subtle/balanced/strong/impasto)
    """

    print("\n" + "=" * 60)
    print("🎸 GUITAR RIFF → OIL PAINTING")
    print("=" * 60)

    # Step 1: Generate base artwork
    print("\n[STEP 1/2] Generating abstract riff artwork...")
    print("-" * 60)

    artist = EnhancedZornGuitarRiffArt(
        width=width,
        height=height,
        dpi=dpi,
        seed=seed
    )

    raw_output = f'{output_name}_raw.png'
    artist.create_artwork(raw_output)

    # Step 2: Apply artistic post-processing
    print("\n[STEP 2/2] Applying oil painting effects...")
    print("-" * 60)

    final_output = f'{output_name}_artistic.png'
    quick_artistic_transform(raw_output, final_output, preset=preset)

    print("\n" + "=" * 60)
    print("✅ COMPLETE!")
    print("=" * 60)
    print(f"📁 Raw output:      {raw_output}")
    print(f"🎨 Artistic output: {final_output}")
    print(f"   Seed: {seed} | Preset: {preset}")
    print("=" * 60 + "\n")

    return raw_output, final_output


def batch_generate_artistic(num_variations=5, preset='balanced'):
    """Generate multiple artistic variations"""
    import random

    print(f"\n🎨 Batch Generation: {num_variations} artistic variations")
    print("=" * 60)

    outputs = []

    for i in range(num_variations):
        seed = random.randint(1, 10000)
        print(f"\n[{i+1}/{num_variations}] Generating variation with seed {seed}...")

        raw, artistic = generate_artistic_riff(
            output_name=f'artistic_batch_{i+1:02d}',
            seed=seed,
            preset=preset
        )

        outputs.append((raw, artistic))

    print("\n" + "=" * 60)
    print(f"✅ Generated {num_variations} artistic variations")
    print("=" * 60)

    return outputs


def compare_presets(seed=42):
    """Generate the same riff with all presets for comparison"""
    presets = ['subtle', 'balanced', 'strong', 'impasto']

    print("\n🎨 Generating comparison across all presets...")
    print("=" * 60)

    # Generate base once
    artist = EnhancedZornGuitarRiffArt(seed=seed)
    base_output = 'comparison_base.png'
    artist.create_artwork(base_output)

    # Apply each preset
    processor = ArtisticPostProcessor()

    for preset in presets:
        print(f"\nApplying preset: {preset}")
        output = f'comparison_{preset}.png'
        quick_artistic_transform(base_output, output, preset=preset)

    print("\n✅ Comparison complete! Compare these files:")
    for preset in presets:
        print(f"   - comparison_{preset}.png")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate artistic oil painting style guitar riff artwork'
    )

    parser.add_argument('--output', '-o', default='artistic_riff',
                       help='Base name for output files')
    parser.add_argument('--seed', '-s', type=int, default=42,
                       help='Random seed (for repeatability)')
    parser.add_argument('--width', '-w', type=int, default=1600,
                       help='Canvas width in pixels')
    parser.add_argument('--height', '-H', type=int, default=1000,
                       help='Canvas height in pixels')
    parser.add_argument('--dpi', '-d', type=int, default=150,
                       help='Resolution in DPI')
    parser.add_argument('--preset', '-p', default='balanced',
                       choices=['subtle', 'balanced', 'strong', 'impasto', 'ultra', 'dreamlike'],
                       help='Artistic effect preset')
    parser.add_argument('--batch', '-b', type=int, metavar='N',
                       help='Generate N random variations')
    parser.add_argument('--compare', action='store_true',
                       help='Generate comparison of all presets')

    args = parser.parse_args()

    if args.compare:
        compare_presets(seed=args.seed)
    elif args.batch:
        batch_generate_artistic(num_variations=args.batch, preset=args.preset)
    else:
        generate_artistic_riff(
            output_name=args.output,
            seed=args.seed,
            width=args.width,
            height=args.height,
            dpi=args.dpi,
            preset=args.preset
        )
