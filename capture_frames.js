#!/usr/bin/env node

/**
 * ZORN PENTATONIC FRAME CAPTURE
 *
 * Uses Puppeteer to automatically capture frames from the Paper.js browser renderer
 */

const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
const http = require('http');
const express = require('express');

const FPS = 30;
const OUTPUT_DIR = './frames';
const PORT = 8888;

async function startServer() {
  const app = express();
  app.use(express.static(__dirname));

  return new Promise((resolve) => {
    const server = app.listen(PORT, () => {
      console.log(`✓ Server started on http://localhost:${PORT}`);
      resolve(server);
    });
  });
}

async function captureFrames() {
  console.log('\n🎨 Zorn Pentatonic Frame Capture\n');

  // Start local server
  const server = await startServer();

  // Ensure output directory
  await fs.ensureDir(OUTPUT_DIR);

  console.log(`\n📹 Launching browser...\n`);

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  // Navigate to renderer
  await page.goto(`http://localhost:${PORT}/zorn_pentatonic_paperjs.html`);

  // Wait for Paper.js to initialize
  await page.waitForFunction(() => typeof paper !== 'undefined');

  console.log('✓ Paper.js loaded\n');

  // Load notes JSON
  await page.click('#loadBtn');
  await page.waitForTimeout(1000);

  // Get total frame count
  const totalFrames = await page.evaluate((fps) => {
    const lastNote = notes[notes.length - 1];
    const totalDuration = lastNote.start_time + lastNote.duration + 1.0;
    return Math.ceil(totalDuration * fps);
  }, FPS);

  console.log(`📊 Total frames to render: ${totalFrames}\n`);

  // Capture each frame
  for (let frame = 0; frame < totalFrames; frame++) {
    // Set current frame and render
    await page.evaluate((f) => {
      currentFrame = f;
      renderFrame(f);
    }, frame);

    // Wait for render to complete
    await page.waitForTimeout(100);

    // Capture screenshot
    const fileName = `frame_${String(frame).padStart(5, '0')}.png`;
    const filePath = path.join(OUTPUT_DIR, fileName);

    const canvas = await page.$('#paperCanvas');
    await canvas.screenshot({ path: filePath });

    const progress = ((frame + 1) / totalFrames * 100).toFixed(1);
    const time = (frame / FPS).toFixed(2);

    process.stdout.write(`\r   Frame ${frame + 1}/${totalFrames} (${progress}%) @ ${time}s   `);
  }

  console.log('\n\n✓ All frames captured!\n');

  await browser.close();
  server.close();

  console.log(`📹 To create video with FFmpeg:\n`);
  console.log(`   ffmpeg -framerate ${FPS} -i ${OUTPUT_DIR}/frame_%05d.png \\`);
  console.log(`          -i 1207(1)_audio.wav \\`);
  console.log(`          -c:v libx264 -pix_fmt yuv420p -shortest \\`);
  console.log(`          zorn_pentatonic_paperjs.mp4\n`);
}

// Run
captureFrames().catch(err => {
  console.error('\n❌ Error:', err.message);
  process.exit(1);
});
