/**
 * enhance.js — Tinder portfolio photo enhancer via Nanobanana
 * (Nanobanana = Gemini 2.5 Flash Image, community codename)
 *
 * Usage:
 *   GEMINI_API_KEY=your_key npm run enhance
 *
 * Place your 5 input photos in input/ as input1.jpg … input5.jpg
 * Enhanced outputs are written to photos/ and wired into index.html.
 */

import { GoogleGenAI } from "@google/genai";
import fs from "fs";
import path from "path";

const NANOBANANA_MODEL = "gemini-2.5-flash-preview-05-20"; // Nanobanana

// One enhancement prompt per photo slot — tuned for Tinder
const PHOTO_PROMPTS = [
  // photo1: main profile shot — clean, confident look
  "Enhance this portrait photo for a dating profile. " +
    "Keep the person exactly as they are. " +
    "Improve lighting to be soft and flattering, " +
    "boost skin tones naturally, sharpen facial details, " +
    "and gently brighten the background. " +
    "Output a polished, high-quality portrait in 4:5 aspect ratio.",

  // photo2: social / city shot
  "Enhance this outdoor/social photo for a dating profile. " +
    "Keep the person exactly as they are. " +
    "Improve contrast and vibrancy, make colours pop, " +
    "and ensure the subject stands out clearly against the background. " +
    "Output in 4:5 aspect ratio.",

  // photo3: adventure / water shot 1
  "Enhance this adventure/water photo for a dating profile. " +
    "Keep the person exactly as they are. " +
    "Boost the blue-green tones of the water, " +
    "improve brightness and clarity, " +
    "and make the scene look vivid and exciting. " +
    "Output in 4:5 aspect ratio.",

  // photo4: adventure / water shot 2 — moody side angle
  "Enhance this moody adventure photo for a dating profile. " +
    "Keep the person exactly as they are. " +
    "Deepen shadows slightly for a cinematic look, " +
    "enhance the rocky/water textures, " +
    "and ensure the face is well lit despite the side angle. " +
    "Output in 4:5 aspect ratio.",

  // photo5: beach / full body
  "Enhance this beach full-body photo for a dating profile. " +
    "Keep the person exactly as they are. " +
    "Make the sea colour deep and turquoise, " +
    "boost the sky-blue tones, " +
    "improve skin tone warmth naturally, " +
    "and add a slight summer warmth grade. " +
    "Output in 4:5 aspect ratio.",
];

async function enhancePhoto(ai, inputPath, outputPath, prompt, index) {
  console.log(`\n[${index + 1}/5] Processing: ${path.basename(inputPath)}`);

  const imageData = fs.readFileSync(inputPath);
  const base64Image = imageData.toString("base64");
  const mimeType = inputPath.endsWith(".png") ? "image/png" : "image/jpeg";

  const response = await ai.models.generateContent({
    model: NANOBANANA_MODEL,
    contents: [
      {
        role: "user",
        parts: [
          { text: prompt },
          { inlineData: { mimeType, data: base64Image } },
        ],
      },
    ],
    config: {
      responseModalities: ["IMAGE", "TEXT"],
    },
  });

  // Extract the generated image from the response
  for (const part of response.candidates[0].content.parts) {
    if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync(outputPath, buffer);
      console.log(`  ✓ Saved → ${outputPath}`);
      return;
    }
  }

  // Fallback: if no image generated, copy original
  console.log(`  ⚠ No image returned — copying original as fallback.`);
  fs.copyFileSync(inputPath, outputPath);
}

async function main() {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    console.error(
      "Error: set the GEMINI_API_KEY environment variable.\n" +
        "  export GEMINI_API_KEY=your_key_here\n" +
        "  npm run enhance"
    );
    process.exit(1);
  }

  const ai = new GoogleGenAI({ apiKey });

  const inputDir = path.join("input");
  const outputDir = path.join("photos");

  if (!fs.existsSync(inputDir)) {
    fs.mkdirSync(inputDir, { recursive: true });
    console.log(
      "Created input/ directory.\n" +
        "Place your 5 photos there as input1.jpg … input5.jpg, then re-run."
    );
    process.exit(0);
  }

  fs.mkdirSync(outputDir, { recursive: true });

  for (let i = 0; i < 5; i++) {
    // Accept .jpg or .png
    const exts = ["jpg", "jpeg", "png"];
    let inputPath = null;
    for (const ext of exts) {
      const candidate = path.join(inputDir, `input${i + 1}.${ext}`);
      if (fs.existsSync(candidate)) { inputPath = candidate; break; }
    }

    if (!inputPath) {
      console.warn(`  ⚠ input/input${i + 1}.jpg not found — skipping.`);
      continue;
    }

    const outputPath = path.join(outputDir, `photo${i + 1}.jpg`);
    await enhancePhoto(ai, inputPath, outputPath, PHOTO_PROMPTS[i], i);
  }

  console.log("\nAll done! Open portfolio/index.html in your browser.\n");
}

main().catch((err) => {
  console.error("Fatal error:", err.message);
  process.exit(1);
});
