#!/bin/bash
# Complete Hybrid Pipeline: Guitar Riff → Raw Artwork → Stable Diffusion → Final Oil Painting

set -e

# Default parameters
SEED=${1:-42}
STYLE=${2:-dreamlike}
STRENGTH=${3:-0.65}
OUTPUT_NAME=${4:-final_artwork}

echo ""
echo "============================================================"
echo "🎸 COMPLETE HYBRID PIPELINE: CODE + STABLE DIFFUSION"
echo "============================================================"
echo ""
echo "Parameters:"
echo "  Seed: $SEED"
echo "  Style: $STYLE"
echo "  Strength: $STRENGTH"
echo "  Output: ${OUTPUT_NAME}_sd.png"
echo ""
echo "============================================================"

# Step 1: Generate base artwork with Python code
echo ""
echo "[STEP 1/2] Generating base artwork from guitar riff..."
echo "------------------------------------------------------------"

python zorn_riff_art_enhanced.py --seed "$SEED" --output base_for_sd

RAW_FILE="base_for_sd_raw.png"

if [ ! -f "$RAW_FILE" ]; then
    echo "❌ Error: Raw file not found: $RAW_FILE"
    exit 1
fi

echo "✅ Base artwork generated: $RAW_FILE"

# Step 2: Apply Stable Diffusion artistic effect
echo ""
echo "[STEP 2/2] Applying Stable Diffusion artistic effect..."
echo "------------------------------------------------------------"

# Check if replicate is installed
if ! python -c "import replicate" 2>/dev/null; then
    echo "❌ Error: 'replicate' package not installed"
    echo "Install with: pip install replicate"
    exit 1
fi

# Check API token
if [ -z "$REPLICATE_API_TOKEN" ]; then
    echo "❌ Error: REPLICATE_API_TOKEN not set"
    echo "Set it with: export REPLICATE_API_TOKEN='your-token'"
    echo "Get token at: https://replicate.com/account/api-tokens"
    exit 1
fi

python hybrid_sd_processor.py \
    "$RAW_FILE" \
    "${OUTPUT_NAME}_sd.png" \
    --style "$STYLE" \
    --strength "$STRENGTH"

echo ""
echo "============================================================"
echo "✅ PIPELINE COMPLETE!"
echo "============================================================"
echo ""
echo "📁 Files generated:"
echo "  - $RAW_FILE (base artwork)"
echo "  - ${OUTPUT_NAME}_sd.png (final with SD effect)"
echo ""
echo "🎨 The final image has AI-enhanced oil painting effect"
echo "   matching the quality of ChatGPT/Midjourney output!"
echo ""
echo "============================================================"
