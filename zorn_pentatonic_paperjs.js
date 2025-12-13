#!/usr/bin/env node

/**
 * ZORN PENTATONIC PAINTERLY RENDERER - Paper.js Implementation
 *
 * Juritz Transliteration Theory: Music → Painting Practices
 *
 * ENFASI DINAMICA:
 * - Climax → size +50%, splatter +40%
 * - Crescendo/decrescendo → progressive technique intensity
 *
 * INTERVALLI MELODICI:
 * - Unison/step → glazing 60%, wet-on-wet 50%
 * - Large intervals → wider brushstrokes, more gestural
 *
 * RITMO:
 * - Fast notes → dry brush 70%, rapid strokes
 * - Slow notes → craquelure 40%, impasto depth
 *
 * CONTORNO MELODICO:
 * - Ascending → upward stroke direction
 * - Descending → dripping 50%, downward flow
 * - Static → horizontal strokes, stability
 */

import paper from 'paper';
import { Canvas } from 'skia-canvas';
import { createNoise2D } from 'simplex-noise';
import fs from 'fs-extra';
import path from 'path';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

// ============================================================================
// ZORN PALETTE - Limited 4-color palette
// ============================================================================
const ZORN_PALETTE = {
  YELLOW_OCHRE: { r: 227, g: 168, b: 87 },   // Yellow Ochre
  VERMILION: { r: 217, g: 96, b: 59 },       // Vermilion Red
  IVORY_BLACK: { r: 41, g: 36, b: 33 },      // Ivory Black
  TITANIUM_WHITE: { r: 252, g: 250, b: 242 }, // Titanium White (warm)
};

// Canvas background - raw linen texture
const CANVAS_BASE = { r: 242, g: 235, b: 220 };

// ============================================================================
// ZORN PENTATONIC PAINTERLY RENDERER
// ============================================================================
class ZornPentatonicPaperJS {
  constructor(notes, options = {}) {
    this.notes = notes;
    this.fps = options.fps || 30;
    this.width = options.width || 1920;
    this.height = options.height || 1080;
    this.outputDir = options.outputDir || './frames';
    this.seed = options.seed || 42;

    // Perlin noise for organic variation
    this.noise = createNoise2D();
    this.noiseScale = 0.01;

    // Musical analysis
    this.dynamicsAnalysis = null;
    this.contours = [];

    // Setup Paper.js with node-canvas
    this.setupPaper();

    // Analyze musical context
    this.analyzeMusic();

    // Random seed for deterministic output
    this.rng = this.seededRandom(this.seed);
  }

  /**
   * Seeded random number generator for deterministic output
   */
  seededRandom(seed) {
    let state = seed;
    return () => {
      state = (state * 1664525 + 1013904223) % 4294967296;
      return state / 4294967296;
    };
  }

  /**
   * Setup Paper.js with skia-canvas backend
   */
  setupPaper() {
    const canvas = new Canvas(this.width, this.height);
    paper.setup(canvas);

    this.canvas = canvas;
    this.project = paper.project;
    this.view = paper.view;

    // Background layer - canvas texture
    this.applyCanvasTexture();

    console.log(`✓ Paper.js setup: ${this.width}x${this.height} @ ${this.fps}fps`);
  }

  /**
   * Apply raw linen canvas texture with Perlin noise
   */
  applyCanvasTexture() {
    const rect = new paper.Path.Rectangle({
      point: [0, 0],
      size: [this.width, this.height],
      fillColor: this.rgbToColor(CANVAS_BASE)
    });

    // Add subtle texture with multiple noise layers
    const raster = rect.rasterize();
    const ctx = raster.canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, this.width, this.height);
    const data = imageData.data;

    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        const idx = (y * this.width + x) * 4;

        // Multi-octave Perlin noise for organic texture
        const noise1 = this.noise(x * 0.01, y * 0.01) * 0.5;
        const noise2 = this.noise(x * 0.05, y * 0.05) * 0.3;
        const noise3 = this.noise(x * 0.1, y * 0.1) * 0.2;
        const variation = (noise1 + noise2 + noise3) * 15;

        data[idx] = Math.max(0, Math.min(255, data[idx] + variation));
        data[idx + 1] = Math.max(0, Math.min(255, data[idx + 1] + variation));
        data[idx + 2] = Math.max(0, Math.min(255, data[idx + 2] + variation));
      }
    }

    ctx.putImageData(imageData, 0, 0);
    rect.remove();

    console.log('✓ Canvas texture applied (Perlin noise)');
  }

  // ==========================================================================
  // MUSICAL ANALYSIS
  // ==========================================================================

  /**
   * Analyze complete musical context
   */
  analyzeMusic() {
    this.dynamicsAnalysis = this.analyzeDynamics(this.notes);
    this.contours = this.analyzeMelodicContour(this.notes, 3);

    console.log('✓ Musical analysis complete:');
    console.log(`  - Dynamics: avg=${this.dynamicsAnalysis.avg.toFixed(2)}, ` +
                `range=${this.dynamicsAnalysis.range.toFixed(2)}, ` +
                `climax @ note ${this.dynamicsAnalysis.climax_idx}`);
    console.log(`  - Crescendo: ${this.dynamicsAnalysis.has_crescendo}`);
    console.log(`  - Decrescendo: ${this.dynamicsAnalysis.has_decrescendo}`);
  }

  /**
   * ENFASI: Analyze overall dynamics of the riff
   */
  analyzeDynamics(notes) {
    const velocities = notes.map(n => n.velocity_value || 0.5);
    const avg = velocities.reduce((a, b) => a + b, 0) / velocities.length;
    const max = Math.max(...velocities);
    const min = Math.min(...velocities);
    const range = max - min;
    const climax_idx = velocities.indexOf(max);

    return {
      avg,
      max,
      min,
      range,
      climax_idx,
      has_crescendo: this.detectCrescendo(velocities),
      has_decrescendo: this.detectDecrescendo(velocities),
    };
  }

  detectCrescendo(velocities, window = 5) {
    for (let i = 0; i <= velocities.length - window; i++) {
      const slice = velocities.slice(i, i + window);
      const increases = slice.slice(1).filter((v, idx) => v > slice[idx]).length;
      if (increases >= window * 0.7) return true;
    }
    return false;
  }

  detectDecrescendo(velocities, window = 5) {
    for (let i = 0; i <= velocities.length - window; i++) {
      const slice = velocities.slice(i, i + window);
      const decreases = slice.slice(1).filter((v, idx) => v < slice[idx]).length;
      if (decreases >= window * 0.7) return true;
    }
    return false;
  }

  /**
   * Analyze interval between two consecutive notes
   */
  analyzeInterval(note1, note2) {
    const pitch1 = note1.pitch || 60;
    const pitch2 = note2.pitch || 60;
    const semitones = Math.abs(pitch2 - pitch1);

    let type;
    if (semitones === 0) type = 'unison';
    else if (semitones <= 2) type = 'step';
    else if (semitones <= 4) type = 'small';
    else if (semitones <= 7) type = 'medium';
    else type = 'large';

    const direction = pitch2 > pitch1 ? 'ascending' : (pitch2 < pitch1 ? 'descending' : 'static');

    return { semitones, type, direction };
  }

  /**
   * Analyze rhythm/duration type
   */
  analyzeRhythm(note) {
    const duration = note.duration || 0.5;

    let type;
    if (duration < 0.15) type = 'very_fast';
    else if (duration < 0.3) type = 'fast';
    else if (duration < 0.6) type = 'medium';
    else if (duration < 1.0) type = 'slow';
    else type = 'very_slow';

    return { duration, type };
  }

  /**
   * Analyze melodic contour with sliding window
   */
  analyzeMelodicContour(notes, window = 3) {
    const contours = [];

    for (let i = 0; i < notes.length; i++) {
      const start = Math.max(0, i - Math.floor(window / 2));
      const end = Math.min(notes.length, start + window);
      const windowNotes = notes.slice(start, end);
      const pitches = windowNotes.map(n => n.pitch || 60);

      // Linear regression to detect trend
      const trend = this.linearTrend(pitches);

      let contour;
      if (trend > 0.5) contour = 'ascending';
      else if (trend < -0.5) contour = 'descending';
      else contour = 'static';

      contours.push(contour);
    }

    return contours;
  }

  linearTrend(values) {
    const n = values.length;
    const x = Array.from({ length: n }, (_, i) => i);
    const avgX = x.reduce((a, b) => a + b, 0) / n;
    const avgY = values.reduce((a, b) => a + b, 0) / n;

    const numerator = x.reduce((sum, xi, i) => sum + (xi - avgX) * (values[i] - avgY), 0);
    const denominator = x.reduce((sum, xi) => sum + Math.pow(xi - avgX, 2), 0);

    return denominator === 0 ? 0 : numerator / denominator;
  }

  // ==========================================================================
  // COLOR UTILITIES
  // ==========================================================================

  rgbToColor(rgb, alpha = 1.0) {
    return new paper.Color(rgb.r / 255, rgb.g / 255, rgb.b / 255, alpha);
  }

  /**
   * Select Zorn palette color based on pitch
   */
  getPaletteColor(pitch) {
    const normalized = (pitch % 12) / 12;

    if (normalized < 0.25) return ZORN_PALETTE.YELLOW_OCHRE;
    else if (normalized < 0.5) return ZORN_PALETTE.VERMILION;
    else if (normalized < 0.75) return ZORN_PALETTE.IVORY_BLACK;
    else return ZORN_PALETTE.TITANIUM_WHITE;
  }

  /**
   * Mix two Zorn colors
   */
  mixColors(color1, color2, ratio = 0.5) {
    return {
      r: Math.round(color1.r * (1 - ratio) + color2.r * ratio),
      g: Math.round(color1.g * (1 - ratio) + color2.g * ratio),
      b: Math.round(color1.b * (1 - ratio) + color2.b * ratio),
    };
  }

  /**
   * Add variation to color with Perlin noise
   */
  varyColor(color, x, y, intensity = 0.1) {
    const noise = this.noise(x * this.noiseScale, y * this.noiseScale);
    const variation = noise * intensity * 255;

    return {
      r: Math.max(0, Math.min(255, color.r + variation)),
      g: Math.max(0, Math.min(255, color.g + variation)),
      b: Math.max(0, Math.min(255, color.b + variation)),
    };
  }

  // ==========================================================================
  // PAINTERLY TECHNIQUES WITH PAPER.JS
  // ==========================================================================

  /**
   * BRUSHSTROKE - Organic stroke with pressure variation
   * Paper.js advantage: fluid curveTo(), Perlin noise jitter
   */
  drawBrushstroke(x, y, angle, length, width, color, alpha = 0.8, blendMode = 'normal') {
    const numBristles = Math.floor(30 + this.rng() * 20); // 30-50 bristles

    for (let i = 0; i < numBristles; i++) {
      const offsetAngle = angle + (this.rng() - 0.5) * 0.3;

      // Perlin noise for ORGANIC jitter (not digital random.gauss)
      const noiseX = this.noise(x * 0.1, i * 0.1) * width * 0.3;
      const noiseY = this.noise(y * 0.1, i * 0.1) * width * 0.3;

      const startX = x + noiseX;
      const startY = y + noiseY;
      const endX = startX + Math.cos(offsetAngle) * length;
      const endY = startY + Math.sin(offsetAngle) * length;

      // Pressure variation along stroke
      const pressure = 0.3 + this.rng() * 0.7;
      const bristleWidth = width * 0.1 * pressure;

      // Fluid Bezier curve with curveTo (Paper.js native)
      const path = new paper.Path();
      path.strokeColor = this.rgbToColor(this.varyColor(color, startX, startY, 0.05), alpha);
      path.strokeWidth = bristleWidth;
      path.strokeCap = 'round';
      path.blendMode = blendMode;

      const midX = (startX + endX) / 2 + (this.rng() - 0.5) * width * 0.2;
      const midY = (startY + endY) / 2 + (this.rng() - 0.5) * width * 0.2;

      path.add(new paper.Point(startX, startY));
      path.curveTo(
        new paper.Point(midX, midY),
        new paper.Point(endX, endY)
      );
    }
  }

  /**
   * IMPASTO - Thick paint with 12 layers for depth
   * Paper.js advantage: multiply blending for realistic depth
   */
  drawImpasto(x, y, radius, color, alpha = 0.9) {
    const numLayers = 12;

    for (let layer = 0; layer < numLayers; layer++) {
      const layerRadius = radius * (1 - layer * 0.05);
      const layerAlpha = alpha * (0.7 + layer * 0.025);

      // Irregular polygon for paint texture
      const points = [];
      const numPoints = 8;
      for (let i = 0; i < numPoints; i++) {
        const angle = (i / numPoints) * Math.PI * 2;
        const variation = this.rng() * 0.3 + 0.85;
        const px = x + Math.cos(angle) * layerRadius * variation;
        const py = y + Math.sin(angle) * layerRadius * variation;
        points.push(new paper.Point(px, py));
      }

      const polygon = new paper.Path(points);
      polygon.closed = true;
      polygon.fillColor = this.rgbToColor(
        this.varyColor(color, x, y + layer * 2, 0.08),
        layerAlpha
      );
      polygon.blendMode = 'multiply'; // REAL BLENDING - not possible in matplotlib!
    }
  }

  /**
   * WET-ON-WET (Alla Prima) - Colors mixing while wet
   * Paper.js advantage: overlay blending for realistic color mixing
   */
  drawWetOnWet(x, y, radius, color1, color2, alpha = 0.7) {
    const numBlobs = Math.floor(8 + this.rng() * 4); // 8-12 blobs

    for (let i = 0; i < numBlobs; i++) {
      const ratio = i / numBlobs;
      const mixedColor = this.mixColors(color1, color2, ratio);

      const offsetX = x + (this.rng() - 0.5) * radius;
      const offsetY = y + (this.rng() - 0.5) * radius;
      const blobRadius = radius * (0.3 + this.rng() * 0.4);

      const circle = new paper.Path.Circle({
        center: [offsetX, offsetY],
        radius: blobRadius,
        fillColor: this.rgbToColor(mixedColor, alpha),
        blendMode: 'overlay' // Realistic wet-on-wet mixing
      });
    }
  }

  /**
   * GLAZING - Transparent layers for optical depth
   * Paper.js advantage: multiply blending creates realistic glazing effect
   */
  drawGlazing(x, y, radius, color, alpha = 0.3) {
    const numLayers = Math.floor(3 + this.rng() * 3); // 3-6 layers

    for (let i = 0; i < numLayers; i++) {
      const layerRadius = radius * (1 + i * 0.1);
      const offsetX = x + (this.rng() - 0.5) * radius * 0.3;
      const offsetY = y + (this.rng() - 0.5) * radius * 0.3;

      const circle = new paper.Path.Circle({
        center: [offsetX, offsetY],
        radius: layerRadius,
        fillColor: this.rgbToColor(this.varyColor(color, offsetX, offsetY, 0.05), alpha),
        blendMode: 'multiply' // Essential for optical glazing depth
      });
    }
  }

  /**
   * DRY BRUSH - Rapid interrupted strokes
   * Paper.js advantage: precise control over stroke gaps
   */
  drawDryBrush(x, y, angle, length, width, color, alpha = 0.6) {
    const numSegments = Math.floor(5 + this.rng() * 5); // 5-10 interrupted segments

    for (let i = 0; i < numSegments; i++) {
      const segmentRatio = this.rng();
      const segmentLength = length * (0.1 + this.rng() * 0.2);

      const startX = x + Math.cos(angle) * length * segmentRatio;
      const startY = y + Math.sin(angle) * length * segmentRatio;

      const path = new paper.Path();
      path.strokeColor = this.rgbToColor(this.varyColor(color, startX, startY, 0.1), alpha);
      path.strokeWidth = width * (0.5 + this.rng() * 0.5);
      path.strokeCap = 'round';

      path.add(new paper.Point(startX, startY));
      path.add(new paper.Point(
        startX + Math.cos(angle) * segmentLength,
        startY + Math.sin(angle) * segmentLength
      ));
    }
  }

  /**
   * DRIPPING - Vertical paint flow for descending passages
   * Paper.js advantage: smooth curves for natural drip paths
   */
  drawDripping(x, y, length, width, color, alpha = 0.5) {
    const numDrips = Math.floor(2 + this.rng() * 3); // 2-5 drips

    for (let i = 0; i < numDrips; i++) {
      const startX = x + (this.rng() - 0.5) * width;
      const dripLength = length * (0.5 + this.rng() * 0.5);

      const path = new paper.Path();
      path.strokeColor = this.rgbToColor(this.varyColor(color, startX, y, 0.05), alpha);
      path.strokeWidth = width * 0.1 * (0.5 + this.rng() * 0.5);
      path.strokeCap = 'round';
      path.blendMode = 'multiply';

      // Natural drip curve with gravity effect
      const controlY = y + dripLength * 0.3;
      const endY = y + dripLength;

      path.add(new paper.Point(startX, y));
      path.curveTo(
        new paper.Point(startX + (this.rng() - 0.5) * 5, controlY),
        new paper.Point(startX + (this.rng() - 0.5) * 10, endY)
      );
    }
  }

  /**
   * SPLATTER - Energetic paint marks for dynamic peaks
   */
  drawSplatter(x, y, radius, color, alpha = 0.6) {
    const numSplatters = Math.floor(5 + this.rng() * 10); // 5-15 marks

    for (let i = 0; i < numSplatters; i++) {
      const distance = this.rng() * radius;
      const angle = this.rng() * Math.PI * 2;
      const splatX = x + Math.cos(angle) * distance;
      const splatY = y + Math.sin(angle) * distance;
      const splatRadius = radius * 0.05 * (0.3 + this.rng() * 0.7);

      const circle = new paper.Path.Circle({
        center: [splatX, splatY],
        radius: splatRadius,
        fillColor: this.rgbToColor(this.varyColor(color, splatX, splatY, 0.1), alpha),
        blendMode: 'normal'
      });
    }
  }

  /**
   * CRAQUELURE - Surface cracks for slow sustained notes
   */
  drawCraquelure(x, y, radius, alpha = 0.4) {
    const numCracks = Math.floor(3 + this.rng() * 4); // 3-7 cracks

    for (let i = 0; i < numCracks; i++) {
      const angle = this.rng() * Math.PI * 2;
      const length = radius * (0.5 + this.rng() * 0.5);

      const path = new paper.Path();
      path.strokeColor = this.rgbToColor(ZORN_PALETTE.IVORY_BLACK, alpha);
      path.strokeWidth = 0.5 + this.rng() * 0.5;

      const startX = x + Math.cos(angle) * radius * 0.3;
      const startY = y + Math.sin(angle) * radius * 0.3;
      const endX = startX + Math.cos(angle) * length;
      const endY = startY + Math.sin(angle) * length;

      // Jagged crack with multiple segments
      const segments = 4;
      path.add(new paper.Point(startX, startY));

      for (let j = 1; j <= segments; j++) {
        const t = j / segments;
        const segX = startX + (endX - startX) * t + (this.rng() - 0.5) * 5;
        const segY = startY + (endY - startY) * t + (this.rng() - 0.5) * 5;
        path.add(new paper.Point(segX, segY));
      }
    }
  }

  // ==========================================================================
  // CONTEXT-AWARE NOTE RENDERING
  // ==========================================================================

  /**
   * Render single note with full musical context awareness
   */
  renderNote(note, noteIndex, growthFactor = 1.0) {
    // Note position - map pitch to Y, time to X
    const x = 100 + (note.start_time / 20) * (this.width - 200);
    const y = this.height / 2 + (60 - note.pitch) * 8;

    // Base color from Zorn palette
    const baseColor = this.getPaletteColor(note.pitch);

    // Base size from velocity
    let baseSize = 20 + (note.velocity_value || 0.5) * 60;

    // ENFASI DINAMICA - Climax detection
    const climaxDistance = Math.abs(noteIndex - this.dynamicsAnalysis.climax_idx) / this.notes.length;
    const climaxFactor = 1.0 - climaxDistance;
    baseSize *= (1.0 + climaxFactor * 0.5); // +50% at climax

    // Apply growth factor for progressive animation
    const size = baseSize * growthFactor;

    // Musical context
    const rhythmInfo = this.analyzeRhythm(note);
    const contour = this.contours[noteIndex];

    // Interval analysis (if not first note)
    let intervalInfo = null;
    if (noteIndex > 0) {
      intervalInfo = this.analyzeInterval(this.notes[noteIndex - 1], note);
    }

    // TECHNIQUE SELECTION BASED ON MUSICAL CONTEXT

    // Base impasto for all notes
    this.drawImpasto(x, y, size * 0.6, baseColor, 0.8);

    // GLAZING: Small intervals → dense stratified texture
    if (intervalInfo && ['unison', 'step'].includes(intervalInfo.type)) {
      const glazingProb = 0.6;
      if (this.rng() < glazingProb * growthFactor) {
        this.drawGlazing(x, y, size * 0.8, baseColor, 0.3);
      }
    }

    // WET-ON-WET: Small intervals + medium dynamics
    if (intervalInfo && ['unison', 'step', 'small'].includes(intervalInfo.type)) {
      const wetProb = 0.5;
      if (this.rng() < wetProb * growthFactor) {
        const secondaryColor = this.getPaletteColor(note.pitch + 3);
        this.drawWetOnWet(x, y, size * 0.7, baseColor, secondaryColor, 0.6);
      }
    }

    // DRY BRUSH: Fast notes → rapid interrupted strokes
    if (['very_fast', 'fast'].includes(rhythmInfo.type)) {
      const dryBrushProb = 0.7;
      if (this.rng() < dryBrushProb * growthFactor) {
        const angle = contour === 'ascending' ? -Math.PI / 4 :
                     contour === 'descending' ? Math.PI / 4 : 0;
        this.drawDryBrush(x, y, angle, size * 1.2, size * 0.4, baseColor, 0.6);
      }
    }

    // BRUSHSTROKE: Directional based on contour
    const strokeAngle = contour === 'ascending' ? -Math.PI / 3 :
                       contour === 'descending' ? Math.PI / 3 : 0;
    this.drawBrushstroke(x, y, strokeAngle, size * 1.5, size * 0.3, baseColor, 0.7, 'multiply');

    // DRIPPING: Descending + high dynamics
    if (contour === 'descending') {
      const drippingProb = 0.5;
      if (this.rng() < drippingProb * growthFactor) {
        this.drawDripping(x, y, size * 1.5, size * 0.6, baseColor, 0.4);
      }
    }

    // SPLATTER: Dynamic peaks (near climax)
    if (climaxFactor > 0.7) {
      const splatterProb = 0.4;
      if (this.rng() < splatterProb * growthFactor) {
        this.drawSplatter(x, y, size * 1.3, baseColor, 0.5);
      }
    }

    // CRAQUELURE: Slow sustained notes
    if (['slow', 'very_slow'].includes(rhythmInfo.type)) {
      const craquelureProb = 0.4;
      if (this.rng() < craquelureProb * growthFactor) {
        this.drawCraquelure(x, y, size * 0.8, 0.3);
      }
    }
  }

  // ==========================================================================
  // PROGRESSIVE ANIMATION & FRAME EXPORT
  // ==========================================================================

  /**
   * Render frame at specific time
   */
  renderFrame(frameNumber) {
    const currentTime = frameNumber / this.fps;

    // Clear and reapply canvas texture
    paper.project.activeLayer.removeChildren();
    this.applyCanvasTexture();

    // Render notes progressively with growth animation
    for (let i = 0; i < this.notes.length; i++) {
      const note = this.notes[i];
      const noteStart = note.start_time;
      const noteDuration = note.duration;

      if (noteStart <= currentTime) {
        // Growth duration: 60% of note duration
        const growthDuration = noteDuration * 0.6;
        const timeSinceStart = currentTime - noteStart;
        const growthFactor = Math.min(timeSinceStart / growthDuration, 1.0);

        this.renderNote(note, i, growthFactor);
      }
    }

    paper.view.update();
  }

  /**
   * Export frame to PNG
   */
  async exportFrame(frameNumber) {
    this.renderFrame(frameNumber);

    const fileName = `frame_${String(frameNumber).padStart(5, '0')}.png`;
    const filePath = path.join(this.outputDir, fileName);

    // skia-canvas uses async toBuffer
    const buffer = await this.canvas.toBuffer('png');
    await fs.writeFile(filePath, buffer);

    return filePath;
  }

  /**
   * Render all frames for video
   */
  async renderAllFrames() {
    // Ensure output directory exists
    await fs.ensureDir(this.outputDir);

    // Calculate total frames from last note end time
    const lastNote = this.notes[this.notes.length - 1];
    const totalDuration = lastNote.start_time + lastNote.duration + 1.0; // +1s buffer
    const totalFrames = Math.ceil(totalDuration * this.fps);

    console.log(`\n🎨 Rendering ${totalFrames} frames @ ${this.fps}fps (${totalDuration.toFixed(1)}s)`);
    console.log(`   Output: ${this.outputDir}/\n`);

    for (let frame = 0; frame < totalFrames; frame++) {
      const progress = ((frame + 1) / totalFrames * 100).toFixed(1);
      process.stdout.write(`\r   Frame ${frame + 1}/${totalFrames} (${progress}%)   `);

      await this.exportFrame(frame);
    }

    console.log('\n\n✓ All frames rendered successfully!');
    console.log(`\n📹 To create video with FFmpeg:`);
    console.log(`   ffmpeg -framerate ${this.fps} -i ${this.outputDir}/frame_%05d.png \\`);
    console.log(`          -i 1207(1)_audio.wav \\`);
    console.log(`          -c:v libx264 -pix_fmt yuv420p -shortest \\`);
    console.log(`          zorn_pentatonic_paperjs.mp4`);
  }

  /**
   * Render single test frame
   */
  async renderTestFrame() {
    console.log('🎨 Rendering test frame...');

    await fs.ensureDir(this.outputDir);

    // Render frame at 50% through the piece
    const lastNote = this.notes[this.notes.length - 1];
    const totalDuration = lastNote.start_time + lastNote.duration;
    const testTime = totalDuration * 0.5;
    const testFrame = Math.floor(testTime * this.fps);

    const filePath = await this.exportFrame(testFrame);

    console.log(`✓ Test frame rendered: ${filePath}`);
    console.log(`   Frame ${testFrame} @ ${testTime.toFixed(2)}s`);
  }
}

// ============================================================================
// CLI INTERFACE
// ============================================================================

async function main() {
  const argv = yargs(hideBin(process.argv))
    .usage('Usage: $0 <notes.json> [options]')
    .option('test', {
      type: 'boolean',
      description: 'Render single test frame instead of full video',
      default: false
    })
    .option('fps', {
      type: 'number',
      description: 'Frames per second',
      default: 30
    })
    .option('width', {
      type: 'number',
      description: 'Canvas width',
      default: 1920
    })
    .option('height', {
      type: 'number',
      description: 'Canvas height',
      default: 1080
    })
    .option('output', {
      type: 'string',
      description: 'Output directory for frames',
      default: './frames'
    })
    .option('seed', {
      type: 'number',
      description: 'Random seed for deterministic output',
      default: 42
    })
    .demandCommand(1, 'Please provide notes JSON file')
    .help()
    .argv;

  const notesFile = argv._[0];

  // Load notes JSON
  console.log(`\n📖 Loading notes: ${notesFile}`);
  const notes = await fs.readJSON(notesFile);
  console.log(`✓ Loaded ${notes.length} notes`);

  // Create renderer
  const renderer = new ZornPentatonicPaperJS(notes, {
    fps: argv.fps,
    width: argv.width,
    height: argv.height,
    outputDir: argv.output,
    seed: argv.seed
  });

  // Render test or full video
  if (argv.test) {
    await renderer.renderTestFrame();
  } else {
    await renderer.renderAllFrames();
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(err => {
    console.error('\n❌ Error:', err.message);
    process.exit(1);
  });
}

export default ZornPentatonicPaperJS;
