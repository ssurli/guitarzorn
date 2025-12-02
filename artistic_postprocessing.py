"""
Artistic Post-Processing Filters
Transform digital artwork into realistic oil painting style
100% procedural - no AI required
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
from scipy.ndimage import gaussian_filter, median_filter
import random


class ArtisticPostProcessor:
    """Apply painterly effects to digital artwork"""

    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)

    def load_image(self, path):
        """Load image as PIL Image and numpy array"""
        img = Image.open(path).convert('RGB')
        return img, np.array(img)

    def save_image(self, img_array, path, quality=95):
        """Save numpy array as image"""
        img = Image.fromarray(np.uint8(np.clip(img_array, 0, 255)))
        img.save(path, quality=quality)
        return img

    def apply_oil_painting_effect(self, img_array, radius=4, intensity=50):
        """
        Simulate oil painting with bilateral-like filtering
        radius: brush stroke size (3-7 recommended)
        intensity: color quantization (30-70 recommended)
        """
        from scipy.ndimage import uniform_filter

        # Convert to float
        img_float = img_array.astype(float)

        # Apply median filter for oil painting effect
        result = np.zeros_like(img_float)

        for channel in range(3):
            # Median filter creates the "posterization" effect
            filtered = median_filter(img_float[:, :, channel], size=radius)
            result[:, :, channel] = filtered

        # Slight blur to blend
        for channel in range(3):
            result[:, :, channel] = gaussian_filter(result[:, :, channel], sigma=0.8)

        return result

    def add_canvas_texture(self, img_array, strength=0.3, scale=2):
        """
        Add canvas/linen texture overlay
        strength: texture visibility (0.1-0.5)
        scale: texture grain size (1-4)
        """
        h, w = img_array.shape[:2]

        # Generate procedural canvas texture (woven pattern)
        x = np.arange(w)
        y = np.arange(h)
        xx, yy = np.meshgrid(x, y)

        # Woven texture pattern
        texture = (
            np.sin(xx / scale) * 0.3 +
            np.sin(yy / scale) * 0.3 +
            np.sin((xx + yy) / (scale * 1.5)) * 0.2
        )

        # Add fine grain noise
        noise = np.random.randn(h, w) * 0.2
        texture += noise

        # Normalize to [0, 1]
        texture = (texture - texture.min()) / (texture.max() - texture.min())
        texture = gaussian_filter(texture, sigma=0.5)

        # Apply texture as subtle overlay
        result = img_array.copy().astype(float)
        for channel in range(3):
            # Multiplicative blending for natural look
            texture_effect = 1 + (texture - 0.5) * strength
            result[:, :, channel] *= texture_effect

        return np.clip(result, 0, 255)

    def add_brush_strokes_texture(self, img_array, strength=0.4):
        """
        Simulate visible brush stroke texture
        Uses directional blur to create stroke directionality
        """
        h, w = img_array.shape[:2]
        result = img_array.copy().astype(float)

        # Create random stroke direction texture using simpler approach
        # Generate coarse random field
        coarse_h, coarse_w = h // 20 + 1, w // 20 + 1
        angle_map = np.random.rand(coarse_h, coarse_w) * 360
        angle_map = np.kron(angle_map, np.ones((20, 20)))[:h, :w]

        # Apply directional texture variation
        stroke_texture = np.zeros((h, w))

        for i in range(0, h - 5, 5):
            for j in range(0, w - 5, 5):
                # Safe indexing
                i_idx = min(i, h - 1)
                j_idx = min(j, w - 1)

                angle = angle_map[i_idx, j_idx]
                length = random.uniform(3, 8)

                # Create mini stroke
                dx = int(length * np.cos(np.radians(angle)))
                dy = int(length * np.sin(np.radians(angle)))

                # Safe slice
                i_end = min(i + 5, h)
                j_end = min(j + 5, w)
                stroke_texture[i:i_end, j:j_end] += random.uniform(0.5, 1.5)

        # Smooth and normalize
        stroke_texture = gaussian_filter(stroke_texture, sigma=2)
        if stroke_texture.max() > stroke_texture.min():
            stroke_texture = (stroke_texture - stroke_texture.min()) / (stroke_texture.max() - stroke_texture.min())

        # Apply to image
        for channel in range(3):
            texture_effect = 1 + (stroke_texture - 0.5) * strength
            result[:, :, channel] *= texture_effect

        return np.clip(result, 0, 255)

    def apply_impasto_effect(self, img_array, strength=0.6):
        """
        Simulate thick paint (impasto) by enhancing local contrast
        Creates the illusion of paint thickness and relief
        """
        from scipy.ndimage import sobel

        # Calculate edge magnitude (where paint would be thicker)
        gray = np.mean(img_array, axis=2)

        edge_x = sobel(gray, axis=1)
        edge_y = sobel(gray, axis=0)
        edge_magnitude = np.sqrt(edge_x**2 + edge_y**2)

        # Normalize
        edge_magnitude = edge_magnitude / edge_magnitude.max()

        # Create impasto mask (paint is thicker on edges)
        impasto_mask = gaussian_filter(edge_magnitude, sigma=2)

        # Apply highlight on "thick" areas
        result = img_array.copy().astype(float)

        for channel in range(3):
            # Brighten edges slightly (catching light on thick paint)
            highlight = impasto_mask * strength * 30
            result[:, :, channel] += highlight

            # Add subtle shadow around peaks
            shadow_mask = gaussian_filter(impasto_mask, sigma=4)
            result[:, :, channel] -= shadow_mask * strength * 10

        return np.clip(result, 0, 255)

    def soft_blend_edges(self, img_array, blur_sigma=1.5):
        """
        Soften edges for more organic, less digital look
        """
        result = img_array.copy().astype(float)

        for channel in range(3):
            result[:, :, channel] = gaussian_filter(result[:, :, channel], sigma=blur_sigma)

        return result

    def add_color_variations(self, img_array, variation=0.15):
        """
        Add subtle color variations to simulate paint mixing inconsistencies
        """
        h, w = img_array.shape[:2]
        result = img_array.copy().astype(float)

        for channel in range(3):
            # Generate smooth noise pattern
            noise = np.random.randn(h // 10, w // 10) * variation
            noise = np.kron(noise, np.ones((10, 10)))[:h, :w]
            noise = gaussian_filter(noise, sigma=3)

            # Apply multiplicative variation
            result[:, :, channel] *= (1 + noise)

        return np.clip(result, 0, 255)

    def enhance_saturation(self, img, saturation_boost=1.3):
        """Boost saturation for more vibrant oil painting look"""
        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(saturation_boost)

    def apply_full_pipeline(self, input_path, output_path,
                           oil_radius=4,
                           canvas_strength=0.3,
                           brush_strength=0.4,
                           impasto_strength=0.6,
                           blur_sigma=1.2,
                           color_variation=0.12,
                           saturation_boost=1.2):
        """
        Apply complete artistic transformation pipeline

        Parameters:
        -----------
        input_path: str - input image path
        output_path: str - output image path
        oil_radius: int (3-7) - oil painting brush size
        canvas_strength: float (0.1-0.5) - canvas texture visibility
        brush_strength: float (0.2-0.6) - brush stroke texture
        impasto_strength: float (0.4-0.8) - thick paint effect
        blur_sigma: float (0.5-2.0) - edge softening
        color_variation: float (0.05-0.2) - color inconsistency
        saturation_boost: float (1.0-1.5) - color vibrancy
        """
        print(f"🎨 Applying artistic post-processing to {input_path}")
        print("=" * 60)

        # Load image
        print("   ├─ Loading image...")
        img, img_array = self.load_image(input_path)

        # 1. Oil painting effect
        print(f"   ├─ Applying oil painting effect (radius={oil_radius})...")
        img_array = self.apply_oil_painting_effect(img_array, radius=oil_radius)

        # 2. Canvas texture
        print(f"   ├─ Adding canvas texture (strength={canvas_strength})...")
        img_array = self.add_canvas_texture(img_array, strength=canvas_strength)

        # 3. Brush strokes
        print(f"   ├─ Adding brush stroke texture (strength={brush_strength})...")
        img_array = self.add_brush_strokes_texture(img_array, strength=brush_strength)

        # 4. Impasto (thick paint)
        print(f"   ├─ Applying impasto effect (strength={impasto_strength})...")
        img_array = self.apply_impasto_effect(img_array, strength=impasto_strength)

        # 5. Soft blend edges
        print(f"   ├─ Softening edges (blur={blur_sigma})...")
        img_array = self.soft_blend_edges(img_array, blur_sigma=blur_sigma)

        # 6. Color variations
        print(f"   ├─ Adding color variations (variation={color_variation})...")
        img_array = self.add_color_variations(img_array, variation=color_variation)

        # 7. Save intermediate
        print("   ├─ Converting to PIL Image...")
        img = self.save_image(img_array, output_path.replace('.png', '_temp.png'))

        # 8. Saturation boost
        print(f"   ├─ Enhancing saturation (boost={saturation_boost})...")
        img = self.enhance_saturation(img, saturation_boost=saturation_boost)

        # 9. Final save
        print(f"   └─ Saving to {output_path}...")
        img.save(output_path, quality=95)

        print("✅ Artistic post-processing complete!")
        print("=" * 60)

        return img


def quick_artistic_transform(input_path, output_path, preset='balanced'):
    """
    Quick transform with presets

    Presets:
    - 'subtle': Light artistic effect
    - 'balanced': Moderate effect (recommended)
    - 'strong': Heavy painterly effect
    - 'impasto': Very thick paint look
    """
    presets = {
        'subtle': {
            'oil_radius': 3,
            'canvas_strength': 0.2,
            'brush_strength': 0.3,
            'impasto_strength': 0.4,
            'blur_sigma': 0.8,
            'color_variation': 0.08,
            'saturation_boost': 1.1
        },
        'balanced': {
            'oil_radius': 4,
            'canvas_strength': 0.3,
            'brush_strength': 0.4,
            'impasto_strength': 0.6,
            'blur_sigma': 1.2,
            'color_variation': 0.12,
            'saturation_boost': 1.2
        },
        'strong': {
            'oil_radius': 5,
            'canvas_strength': 0.4,
            'brush_strength': 0.5,
            'impasto_strength': 0.7,
            'blur_sigma': 1.5,
            'color_variation': 0.15,
            'saturation_boost': 1.3
        },
        'impasto': {
            'oil_radius': 6,
            'canvas_strength': 0.35,
            'brush_strength': 0.5,
            'impasto_strength': 0.8,
            'blur_sigma': 1.0,
            'color_variation': 0.18,
            'saturation_boost': 1.25
        }
    }

    params = presets.get(preset, presets['balanced'])

    processor = ArtisticPostProcessor()
    return processor.apply_full_pipeline(input_path, output_path, **params)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python artistic_postprocessing.py input.png output.png [preset]")
        print("\nPresets: subtle, balanced, strong, impasto")
        print("Default: balanced")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    preset = sys.argv[3] if len(sys.argv) > 3 else 'balanced'

    print(f"\n🎨 Artistic Post-Processing")
    print(f"Preset: {preset}")
    print("=" * 60)

    quick_artistic_transform(input_path, output_path, preset=preset)
