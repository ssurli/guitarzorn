"""
Material Effects Module for Zorn Guitar Riff Art
Simulates physical painting properties without AI image generation
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from scipy.ndimage import gaussian_filter
from typing import Tuple


class MaterialEffects:
    """
    Applies physical painting simulation to rendered artwork
    Based on traditional oil/gouache painting techniques
    """

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def apply_canvas_texture(self, image: Image.Image, intensity: float = 0.15) -> Image.Image:
        """
        Simulates canvas weave texture using Perlin-like noise

        Args:
            image: Input PIL Image
            intensity: Texture strength (0.0-1.0)

        Returns:
            Image with canvas texture overlay
        """
        w, h = image.size

        # Generate coherent noise for canvas texture
        noise = self._generate_canvas_noise(w, h)

        # Convert to texture map
        texture = (noise * 255 * intensity).astype(np.uint8)
        texture_img = Image.fromarray(texture, mode='L')

        # Blend with original using Screen mode approximation
        img_array = np.array(image).astype(float)
        texture_array = np.array(texture_img.convert('RGB')).astype(float)

        # Screen blend: 1 - (1-A)*(1-B)
        result = 255 - (255 - img_array) * (255 - texture_array * 0.3) / 255

        return Image.fromarray(result.astype(np.uint8))

    def _generate_canvas_noise(self, width: int, height: int) -> np.ndarray:
        """
        Generate multi-octave Perlin-like noise for canvas texture
        """
        # Start with high-frequency noise
        noise = self.rng.uniform(-1, 1, (height // 4, width // 4))

        # Smooth it to create coherent texture
        noise = gaussian_filter(noise, sigma=1.5)

        # Resize to full resolution
        from scipy.ndimage import zoom
        noise = zoom(noise, 4, order=1)

        # Crop to exact size
        noise = noise[:height, :width]

        # Add directional anisotropy (warp/weft of canvas)
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        warp = 0.3 * np.sin(x * 0.05)
        weft = 0.2 * np.sin(y * 0.08)

        noise = noise + warp[:height, :width] + weft

        # Normalize to [0, 1]
        noise = (noise - noise.min()) / (noise.max() - noise.min())

        return noise

    def apply_paint_irregularity(self, image: Image.Image, amount: float = 0.4) -> Image.Image:
        """
        Simulates uneven paint application and pigment density

        Args:
            image: Input PIL Image
            amount: Irregularity strength (0.0-1.0)

        Returns:
            Image with paint irregularities
        """
        img_array = np.array(image).astype(float)
        h, w = img_array.shape[:2]

        # Generate low-frequency noise for pigment density variation
        density_map = self.rng.uniform(0.85, 1.15, (h // 8, w // 8))
        density_map = gaussian_filter(density_map, sigma=2.0)

        from scipy.ndimage import zoom
        density_map = zoom(density_map, 8, order=1)[:h, :w]

        # Apply density variation to each channel
        for c in range(3):
            img_array[:, :, c] *= (1 - amount + amount * density_map)

        img_array = np.clip(img_array, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8))

    def apply_brush_drag(self, image: Image.Image, direction: str = 'horizontal',
                        strength: float = 0.5) -> Image.Image:
        """
        Simulates brush drag marks and directional strokes

        Args:
            image: Input PIL Image
            direction: 'horizontal', 'vertical', or 'both'
            strength: Drag effect strength (0.0-1.0)

        Returns:
            Image with brush drag effect
        """
        img_array = np.array(image).astype(float)

        if direction in ['horizontal', 'both']:
            # Horizontal motion blur (brush drag)
            kernel_size = int(3 + strength * 5)
            kernel = np.zeros((1, kernel_size))
            kernel[0, :] = 1.0 / kernel_size

            for c in range(3):
                img_array[:, :, c] = gaussian_filter(
                    img_array[:, :, c],
                    sigma=(0, strength * 1.5)
                )

        if direction in ['vertical', 'both']:
            for c in range(3):
                img_array[:, :, c] = gaussian_filter(
                    img_array[:, :, c],
                    sigma=(strength * 1.2, 0)
                )

        img_array = np.clip(img_array, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8))

    def apply_edge_roughness(self, image: Image.Image, roughness: float = 0.3) -> Image.Image:
        """
        Makes edges imperfect and organic (opposite of vector sharpness)

        Args:
            image: Input PIL Image
            roughness: Amount of edge roughness (0.0-1.0)

        Returns:
            Image with roughened edges
        """
        # Slight blur to soften edges
        blur_radius = 0.3 + roughness * 0.7
        blurred = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Add subtle noise to edges
        img_array = np.array(blurred).astype(float)
        edge_noise = self.rng.uniform(-roughness * 5, roughness * 5, img_array.shape)
        img_array += edge_noise
        img_array = np.clip(img_array, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8))

    def apply_color_bleeding(self, image: Image.Image, amount: float = 0.2) -> Image.Image:
        """
        Simulates subtle color bleeding between adjacent painted areas

        Args:
            image: Input PIL Image
            amount: Bleeding strength (0.0-1.0)

        Returns:
            Image with color bleeding effect
        """
        # Very subtle gaussian blur to mix adjacent colors
        blurred = image.filter(ImageFilter.GaussianBlur(radius=amount * 2.0))

        # Blend with original
        img_array = np.array(image).astype(float)
        blur_array = np.array(blurred).astype(float)

        result = img_array * (1 - amount * 0.5) + blur_array * (amount * 0.5)
        result = np.clip(result, 0, 255)

        return Image.fromarray(result.astype(np.uint8))

    def apply_full_material_pipeline(self, image_path: str, output_path: str = None,
                                    canvas_texture: float = 0.15,
                                    paint_irregularity: float = 0.4,
                                    brush_drag: float = 0.3,
                                    edge_roughness: float = 0.3,
                                    color_bleeding: float = 0.15) -> str:
        """
        Apply complete material degradation pipeline

        Args:
            image_path: Path to input PNG from matplotlib
            output_path: Output path (defaults to *_material.png)
            canvas_texture: Canvas weave strength
            paint_irregularity: Uneven pigment density
            brush_drag: Directional brush marks
            edge_roughness: Softens sharp vector edges
            color_bleeding: Adjacent color mixing

        Returns:
            Path to output image
        """
        if output_path is None:
            output_path = image_path.replace('.png', '_material.png')

        # Load image
        image = Image.open(image_path).convert('RGB')

        # Apply effects in order (most subtle to most visible)
        print("Applying canvas texture...")
        image = self.apply_canvas_texture(image, canvas_texture)

        print("Applying paint irregularity...")
        image = self.apply_paint_irregularity(image, paint_irregularity)

        print("Applying brush drag...")
        image = self.apply_brush_drag(image, direction='horizontal', strength=brush_drag)

        print("Applying edge roughness...")
        image = self.apply_edge_roughness(image, edge_roughness)

        print("Applying color bleeding...")
        image = self.apply_color_bleeding(image, color_bleeding)

        # Save with original DPI
        image.save(output_path, dpi=(150, 150))
        print(f"Material version saved to: {output_path}")

        return output_path


def apply_anisotropic_jitter(x: float, y: float,
                            direction: Tuple[float, float],
                            canvas_roughness: float = 1.0,
                            hand_tremor: float = 0.5,
                            seed: int = None) -> Tuple[float, float]:
    """
    Anisotropic coordinate jitter guided by stroke direction
    Replaces the simple uniform jitter in ZornGuitarRiffArt

    This is what ChatGPT was trying to suggest, but done correctly.

    Args:
        x, y: Base coordinates
        direction: (dx, dy) stroke direction vector
        canvas_roughness: Simulates irregular canvas surface (0.0-2.0)
        hand_tremor: Human hand instability (0.0-2.0)
        seed: Optional random seed

    Returns:
        (x_jittered, y_jittered)
    """
    if seed is not None:
        rng = np.random.RandomState(seed)
    else:
        rng = np.random

    # Normalize direction
    magnitude = np.sqrt(direction[0]**2 + direction[1]**2)
    if magnitude > 0:
        norm_dir = (direction[0] / magnitude, direction[1] / magnitude)
    else:
        norm_dir = (1, 0)  # Default horizontal

    # Perpendicular direction (for anisotropic displacement)
    perp_dir = (-norm_dir[1], norm_dir[0])

    # Canvas roughness: low-frequency noise (Perlin-like, but simplified)
    # Use position-dependent noise instead of pure random
    canvas_noise_x = np.sin(x * 0.03 + y * 0.02) * canvas_roughness
    canvas_noise_y = np.cos(x * 0.02 + y * 0.04) * canvas_roughness

    # Hand tremor: high-frequency random displacement
    tremor_x = rng.normal(0, hand_tremor * 0.3)
    tremor_y = rng.normal(0, hand_tremor * 0.3)

    # Combine: more displacement perpendicular to stroke direction
    total_displacement_x = (
        canvas_noise_x +
        tremor_x +
        perp_dir[0] * rng.normal(0, 0.5) * canvas_roughness  # Anisotropic component
    )

    total_displacement_y = (
        canvas_noise_y +
        tremor_y +
        perp_dir[1] * rng.normal(0, 0.5) * canvas_roughness  # Anisotropic component
    )

    return (x + total_displacement_x, y + total_displacement_y)


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python material_effects.py <input_image.png> [output_image.png]")
        print("\nExample:")
        print("  python material_effects.py johnny_b_goode_zorn_riff.png")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    effects = MaterialEffects(seed=42)
    result_path = effects.apply_full_material_pipeline(
        input_path,
        output_path,
        canvas_texture=0.18,
        paint_irregularity=0.35,
        brush_drag=0.25,
        edge_roughness=0.35,
        color_bleeding=0.12
    )

    print(f"\n✅ Material effects applied successfully!")
    print(f"Original: {input_path}")
    print(f"Material: {result_path}")
