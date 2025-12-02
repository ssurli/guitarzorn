"""
Examples: Generate variations of guitar riff abstract art
Run different configurations to explore the creative space
"""

from zorn_riff_art_enhanced import EnhancedZornGuitarRiffArt
import matplotlib.pyplot as plt


def example_1_basic():
    """Example 1: Basic generation with default parameters"""
    print("\n🎨 Example 1: Basic generation")
    print("=" * 60)

    artist = EnhancedZornGuitarRiffArt(seed=42)
    artist.create_artwork('example_1_basic.png')


def example_2_variation_seeds():
    """Example 2: Multiple variations with different seeds"""
    print("\n🎨 Example 2: Seed variations (5 versions)")
    print("=" * 60)

    seeds = [42, 123, 456, 789, 1001]

    for i, seed in enumerate(seeds, 1):
        print(f"   Generating variation {i}/5 (seed={seed})...")
        artist = EnhancedZornGuitarRiffArt(seed=seed)
        artist.create_artwork(f'example_2_seed_{seed}.png')

    print("✅ Generated 5 variations with different seeds")


def example_3_high_resolution():
    """Example 3: High resolution for printing"""
    print("\n🎨 Example 3: High resolution (300 DPI)")
    print("=" * 60)

    artist = EnhancedZornGuitarRiffArt(
        width=3000,
        height=2000,
        dpi=300,
        seed=42
    )
    artist.create_artwork('example_3_high_res.png')
    print("   Suitable for large format printing")


def example_4_panoramic():
    """Example 4: Panoramic format"""
    print("\n🎨 Example 4: Panoramic format")
    print("=" * 60)

    artist = EnhancedZornGuitarRiffArt(
        width=2400,
        height=800,
        dpi=150,
        seed=42
    )
    artist.create_artwork('example_4_panoramic.png')


def example_5_minimalist():
    """Example 5: Minimalist version (less background)"""
    print("\n🎨 Example 5: Minimalist style")
    print("=" * 60)

    artist = EnhancedZornGuitarRiffArt(seed=42)

    # Override to reduce background elements
    original_method = artist.add_background_texture

    def minimalist_background():
        """Reduced background elements for cleaner look"""
        import random
        num_elements = 5  # Reduced from 15

        for _ in range(num_elements):
            x = random.uniform(artist.margin, artist.width - artist.margin)
            y = random.uniform(artist.margin, artist.height - artist.margin)

            shape_type = random.choice(['circle', 'triangle', 'square', 'arc'])
            color_name = random.choice(['ochre', 'vermilion', 'black', 'white'])
            color = artist.colors[color_name]
            size = random.uniform(20, 60)

            artist.draw_abstract_shape((x, y), color, shape_type, size)

        # No background splatters for minimalist look

    artist.add_background_texture = minimalist_background
    artist.create_artwork('example_5_minimalist.png')


def example_6_explosive():
    """Example 6: Explosive/energetic version (more splatter)"""
    print("\n🎨 Example 6: Explosive/energetic style")
    print("=" * 60)

    artist = EnhancedZornGuitarRiffArt(seed=42)

    # Override for more intense background
    original_method = artist.add_background_texture

    def explosive_background():
        """More aggressive splatter and elements"""
        import random

        # More background shapes
        num_elements = 25

        for _ in range(num_elements):
            x = random.uniform(artist.margin, artist.width - artist.margin)
            y = random.uniform(artist.margin, artist.height - artist.margin)

            shape_type = random.choice(['circle', 'triangle', 'square', 'arc'])
            color_name = random.choice(['ochre', 'vermilion', 'black', 'white'])
            color = artist.colors[color_name]
            size = random.uniform(20, 80)

            artist.draw_abstract_shape((x, y), color, shape_type, size)

        # Intense splatters
        for _ in range(20):
            x = random.uniform(artist.margin, artist.width - artist.margin)
            y = random.uniform(artist.margin, artist.height - artist.margin)
            color_name = random.choice(['ochre', 'vermilion', 'black'])
            color = artist.colors[color_name]

            artist.draw_splatter_effect((x, y), color, intensity=70, num_splatters=50)

    artist.add_background_texture = explosive_background
    artist.create_artwork('example_6_explosive.png')


def example_7_square_canvas():
    """Example 7: Square canvas format"""
    print("\n🎨 Example 7: Square canvas")
    print("=" * 60)

    artist = EnhancedZornGuitarRiffArt(
        width=1200,
        height=1200,
        dpi=150,
        seed=42
    )
    artist.create_artwork('example_7_square.png')


def example_8_series():
    """Example 8: Series of 3 with consistent style"""
    print("\n🎨 Example 8: Triptych series")
    print("=" * 60)

    seeds = [100, 200, 300]
    titles = ['Panel_1_Left', 'Panel_2_Center', 'Panel_3_Right']

    for seed, title in zip(seeds, titles):
        print(f"   Generating {title}...")
        artist = EnhancedZornGuitarRiffArt(
            width=800,
            height=1200,
            dpi=150,
            seed=seed
        )
        artist.create_artwork(f'example_8_{title}.png')

    print("✅ Triptych complete - display side by side")


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("🎨 GUITAR RIFF ABSTRACT ART - Examples Collection")
    print("=" * 60)

    examples = [
        ("Basic Generation", example_1_basic),
        ("Seed Variations", example_2_variation_seeds),
        ("High Resolution", example_3_high_resolution),
        ("Panoramic Format", example_4_panoramic),
        ("Minimalist Style", example_5_minimalist),
        ("Explosive Style", example_6_explosive),
        ("Square Canvas", example_7_square_canvas),
        ("Triptych Series", example_8_series),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n" + "=" * 60)
    choice = input("\nSelect example (1-8) or 'all' to run all: ").strip().lower()

    if choice == 'all':
        for name, func in examples:
            func()
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        _, func = examples[int(choice) - 1]
        func()
    else:
        print("❌ Invalid choice")
        return

    print("\n" + "=" * 60)
    print("✅ Examples complete!")
    print("=" * 60)


def quick_batch(num_variations=5):
    """Quick batch generation with random seeds"""
    print(f"\n🎨 Quick Batch: Generating {num_variations} random variations")
    print("=" * 60)

    import random
    random.seed()  # Use system time

    for i in range(num_variations):
        seed = random.randint(1, 10000)
        print(f"   [{i+1}/{num_variations}] Generating with seed {seed}...")

        artist = EnhancedZornGuitarRiffArt(seed=seed)
        artist.create_artwork(f'batch_variation_{i+1:03d}_seed{seed}.png')

    print(f"✅ Generated {num_variations} variations")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'batch':
            num = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            quick_batch(num)
        elif sys.argv[1].startswith('ex'):
            example_num = sys.argv[1].replace('ex', '')
            if example_num.isdigit():
                example_map = {
                    '1': example_1_basic,
                    '2': example_2_variation_seeds,
                    '3': example_3_high_resolution,
                    '4': example_4_panoramic,
                    '5': example_5_minimalist,
                    '6': example_6_explosive,
                    '7': example_7_square_canvas,
                    '8': example_8_series,
                }
                func = example_map.get(example_num)
                if func:
                    func()
                else:
                    print(f"❌ Example {example_num} not found")
        else:
            print("Usage:")
            print("  python examples_variations.py              # Interactive menu")
            print("  python examples_variations.py ex1          # Run example 1")
            print("  python examples_variations.py ex2          # Run example 2")
            print("  python examples_variations.py batch 10     # Generate 10 random variations")
    else:
        run_all_examples()
