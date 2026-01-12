"""
Hybrid Transliteration Pipeline Demo
Demonstrates the strategy suggested by ChatGPT:
1. Clean musical rendering (your existing code)
2. Material degradation layer (procedural effects)
3. Comparison output
"""

import sys
import os
from pathlib import Path

# Import your existing renderer
# Note: importing from file with space in name
import importlib.util
spec = importlib.util.spec_from_file_location("zorn_riff_art", "zorn_riff_art (1).py")
zorn_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zorn_module)
ZornGuitarRiffArt = zorn_module.ZornGuitarRiffArt

# Import material effects
from material_effects import MaterialEffects


def generate_clean_version(output_dir: str = "output") -> str:
    """
    STEP 1: Generate clean 'spartito visivo'
    This is your existing renderer - musical truth
    """
    print("\n🎵 STEP 1: Generating clean musical rendering...")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)
    clean_path = os.path.join(output_dir, "johnny_clean.png")

    artist = ZornGuitarRiffArt()
    artist.create_artwork(filename=clean_path)

    print(f"✅ Clean version saved: {clean_path}")
    return clean_path


def apply_material_layer(clean_path: str, preset: str = "balanced") -> str:
    """
    STEP 2: Apply material degradation
    This is the "resistenza del medium" - physical truth
    """
    print("\n🎨 STEP 2: Applying material degradation layer...")
    print("=" * 60)

    material_path = clean_path.replace("_clean.png", "_material.png")

    effects = MaterialEffects(seed=42)

    # Presets based on different painting styles
    presets = {
        "subtle": {
            "canvas_texture": 0.08,
            "paint_irregularity": 0.20,
            "brush_drag": 0.15,
            "edge_roughness": 0.20,
            "color_bleeding": 0.08
        },
        "balanced": {
            "canvas_texture": 0.18,
            "paint_irregularity": 0.35,
            "brush_drag": 0.25,
            "edge_roughness": 0.35,
            "color_bleeding": 0.12
        },
        "heavy": {
            "canvas_texture": 0.30,
            "paint_irregularity": 0.50,
            "brush_drag": 0.40,
            "edge_roughness": 0.50,
            "color_bleeding": 0.20
        }
    }

    params = presets.get(preset, presets["balanced"])

    print(f"Using preset: {preset.upper()}")
    print(f"  Canvas texture: {params['canvas_texture']:.2f}")
    print(f"  Paint irregularity: {params['paint_irregularity']:.2f}")
    print(f"  Brush drag: {params['brush_drag']:.2f}")
    print(f"  Edge roughness: {params['edge_roughness']:.2f}")
    print(f"  Color bleeding: {params['color_bleeding']:.2f}")

    effects.apply_full_material_pipeline(
        clean_path,
        material_path,
        **params
    )

    print(f"✅ Material version saved: {material_path}")
    return material_path


def create_comparison(clean_path: str, material_path: str) -> str:
    """
    STEP 3: Create side-by-side comparison
    """
    print("\n📊 STEP 3: Creating comparison image...")
    print("=" * 60)

    from PIL import Image

    clean_img = Image.open(clean_path)
    material_img = Image.open(material_path)

    # Create side-by-side comparison
    width, height = clean_img.size
    comparison = Image.new('RGB', (width * 2 + 20, height), color=(240, 240, 240))

    comparison.paste(clean_img, (0, 0))
    comparison.paste(material_img, (width + 20, 0))

    comparison_path = clean_path.replace("_clean.png", "_comparison.png")
    comparison.save(comparison_path, dpi=(150, 150))

    print(f"✅ Comparison saved: {comparison_path}")
    return comparison_path


def main():
    """
    Complete hybrid pipeline demonstration
    """
    print("\n" + "=" * 60)
    print("🎸 ZORN HYBRID TRANSLITERATION PIPELINE")
    print("=" * 60)
    print("\nStrategy: 'Musica decide cosa. Materia decide come male viene.'")
    print("\n1. Musical renderer generates semantic truth")
    print("2. Material effects add physical resistance")
    print("3. Result: Juritzsian hybrid of concept + matter")

    # Parse command line arguments
    preset = "balanced"
    if len(sys.argv) > 1:
        preset = sys.argv[1]
        if preset not in ["subtle", "balanced", "heavy"]:
            print(f"\n⚠️  Unknown preset '{preset}', using 'balanced'")
            preset = "balanced"

    print(f"\nUsing material preset: {preset.upper()}")

    # Run pipeline
    output_dir = "output"
    clean_path = generate_clean_version(output_dir)
    material_path = apply_material_layer(clean_path, preset)
    comparison_path = create_comparison(clean_path, material_path)

    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  Clean (spartito):  {clean_path}")
    print(f"  Material (fisico): {material_path}")
    print(f"  Comparison:        {comparison_path}")
    print("\nTo try different presets:")
    print("  python demo_hybrid_pipeline.py subtle")
    print("  python demo_hybrid_pipeline.py balanced")
    print("  python demo_hybrid_pipeline.py heavy")


if __name__ == "__main__":
    main()
