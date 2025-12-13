/**
 * ZORN PENTATONIC PAINTERLY RENDERER - Browser Paper.js Implementation
 *
 * Juritz Transliteration Theory: Music → Painting Practices
 */

// ============================================================================
// ZORN PALETTE
// ============================================================================
const ZORN_PALETTE = {
  YELLOW_OCHRE: [227, 168, 87],   // Yellow Ochre
  VERMILION: [217, 96, 59],       // Vermilion Red
  IVORY_BLACK: [41, 36, 33],      // Ivory Black
  TITANIUM_WHITE: [252, 250, 242] // Titanium White (warm)
};

const CANVAS_BASE = [242, 235, 220]; // Raw linen

// ============================================================================
// GLOBAL STATE
// ============================================================================
let notes = [];
let dynamicsAnalysis = null;
let contours = [];
let currentFrame = 0;
let isPlaying = false;
let animationInterval = null;
let fps = 30;
let seed = 42;
let rngState = seed;

// ============================================================================
// SEEDED RANDOM
// ============================================================================
function seededRandom() {
  rngState = (rngState * 1664525 + 1013904223) % 4294967296;
  return rngState / 4294967296;
}

function resetRNG() {
  rngState = seed;
}

// ============================================================================
// PERLIN NOISE (Simplified 2D)
// ============================================================================
const permutation = [];
for (let i = 0; i < 256; i++) permutation[i] = i;
permutation.sort(() => Math.random() - 0.5);
const p = [...permutation, ...permutation];

function fade(t) {
  return t * t * t * (t * (t * 6 - 15) + 10);
}

function lerp(t, a, b) {
  return a + t * (b - a);
}

function grad(hash, x, y) {
  const h = hash & 15;
  const u = h < 8 ? x : y;
  const v = h < 4 ? y : x;
  return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
}

function noise2D(x, y) {
  const X = Math.floor(x) & 255;
  const Y = Math.floor(y) & 255;

  x -= Math.floor(x);
  y -= Math.floor(y);

  const u = fade(x);
  const v = fade(y);

  const a = p[X] + Y;
  const aa = p[a];
  const ab = p[a + 1];
  const b = p[X + 1] + Y;
  const ba = p[b];
  const bb = p[b + 1];

  return lerp(v,
    lerp(u, grad(p[aa], x, y), grad(p[ba], x - 1, y)),
    lerp(u, grad(p[ab], x, y - 1), grad(p[bb], x - 1, y - 1))
  );
}

// ============================================================================
// LOAD NOTES JSON
// ============================================================================
async function loadNotesJSON() {
  const infoEl = document.getElementById('info');
  try {
    infoEl.textContent = 'Loading 1207(1)_notes.json...';

    const response = await fetch('1207(1)_notes.json');
    notes = await response.json();

    infoEl.textContent = `✓ Loaded ${notes.length} notes. Analyzing musical context...`;

    // Analyze musical context
    dynamicsAnalysis = analyzeDynamics(notes);
    contours = analyzeMelodicContour(notes, 3);

    infoEl.innerHTML = `
      <div class="progress">✓ Ready! ${notes.length} notes loaded</div>
      <div>Dynamics: avg=${dynamicsAnalysis.avg.toFixed(2)}, climax @ note ${dynamicsAnalysis.climax_idx}</div>
      <div>Crescendo: ${dynamicsAnalysis.has_crescendo} | Decrescendo: ${dynamicsAnalysis.has_decrescendo}</div>
    `;

    document.getElementById('playBtn').disabled = false;
    document.getElementById('resetBtn').disabled = false;

    // Initial render (frame 0 - canvas texture only)
    resetAnimation();

  } catch (err) {
    infoEl.textContent = `❌ Error loading notes: ${err.message}`;
    console.error(err);
  }
}

// ============================================================================
// MUSICAL ANALYSIS
// ============================================================================
function analyzeDynamics(notes) {
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
    has_crescendo: detectCrescendo(velocities),
    has_decrescendo: detectDecrescendo(velocities)
  };
}

function detectCrescendo(velocities, window = 5) {
  for (let i = 0; i <= velocities.length - window; i++) {
    const slice = velocities.slice(i, i + window);
    const increases = slice.slice(1).filter((v, idx) => v > slice[idx]).length;
    if (increases >= window * 0.7) return true;
  }
  return false;
}

function detectDecrescendo(velocities, window = 5) {
  for (let i = 0; i <= velocities.length - window; i++) {
    const slice = velocities.slice(i, i + window);
    const decreases = slice.slice(1).filter((v, idx) => v < slice[idx]).length;
    if (decreases >= window * 0.7) return true;
  }
  return false;
}

function analyzeInterval(note1, note2) {
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

function analyzeRhythm(note) {
  const duration = note.duration || 0.5;

  let type;
  if (duration < 0.15) type = 'very_fast';
  else if (duration < 0.3) type = 'fast';
  else if (duration < 0.6) type = 'medium';
  else if (duration < 1.0) type = 'slow';
  else type = 'very_slow';

  return { duration, type };
}

function analyzeMelodicContour(notes, window = 3) {
  const contours = [];

  for (let i = 0; i < notes.length; i++) {
    const start = Math.max(0, i - Math.floor(window / 2));
    const end = Math.min(notes.length, start + window);
    const windowNotes = notes.slice(start, end);
    const pitches = windowNotes.map(n => n.pitch || 60);

    const trend = linearTrend(pitches);

    let contour;
    if (trend > 0.5) contour = 'ascending';
    else if (trend < -0.5) contour = 'descending';
    else contour = 'static';

    contours.push(contour);
  }

  return contours;
}

function linearTrend(values) {
  const n = values.length;
  const x = Array.from({ length: n }, (_, i) => i);
  const avgX = x.reduce((a, b) => a + b, 0) / n;
  const avgY = values.reduce((a, b) => a + b, 0) / n;

  const numerator = x.reduce((sum, xi, i) => sum + (xi - avgX) * (values[i] - avgY), 0);
  const denominator = x.reduce((sum, xi) => sum + Math.pow(xi - avgX, 2), 0);

  return denominator === 0 ? 0 : numerator / denominator;
}

// ============================================================================
// COLOR UTILITIES
// ============================================================================
function rgbToColor(rgb, alpha = 1.0) {
  return new paper.Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha);
}

function getPaletteColor(pitch) {
  const normalized = (pitch % 12) / 12;

  if (normalized < 0.25) return ZORN_PALETTE.YELLOW_OCHRE;
  else if (normalized < 0.5) return ZORN_PALETTE.VERMILION;
  else if (normalized < 0.75) return ZORN_PALETTE.IVORY_BLACK;
  else return ZORN_PALETTE.TITANIUM_WHITE;
}

function mixColors(color1, color2, ratio = 0.5) {
  return [
    Math.round(color1[0] * (1 - ratio) + color2[0] * ratio),
    Math.round(color1[1] * (1 - ratio) + color2[1] * ratio),
    Math.round(color1[2] * (1 - ratio) + color2[2] * ratio)
  ];
}

function varyColor(color, x, y, intensity = 0.1) {
  const noiseVal = noise2D(x * 0.01, y * 0.01);
  const variation = noiseVal * intensity * 255;

  return [
    Math.max(0, Math.min(255, color[0] + variation)),
    Math.max(0, Math.min(255, color[1] + variation)),
    Math.max(0, Math.min(255, color[2] + variation))
  ];
}

// ============================================================================
// CANVAS TEXTURE
// ============================================================================
function applyCanvasTexture() {
  const canvas = document.getElementById('paperCanvas');
  const ctx = canvas.getContext('2d', { willReadFrequently: true });

  // Fill with base color
  ctx.fillStyle = `rgb(${CANVAS_BASE[0]}, ${CANVAS_BASE[1]}, ${CANVAS_BASE[2]})`;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Add Perlin noise texture
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;

  for (let y = 0; y < canvas.height; y += 2) { // Sample every 2px for performance
    for (let x = 0; x < canvas.width; x += 2) {
      const noise1 = noise2D(x * 0.01, y * 0.01) * 0.5;
      const noise2 = noise2D(x * 0.05, y * 0.05) * 0.3;
      const noise3 = noise2D(x * 0.1, y * 0.1) * 0.2;
      const variation = (noise1 + noise2 + noise3) * 15;

      for (let dy = 0; dy < 2; dy++) {
        for (let dx = 0; dx < 2; dx++) {
          const idx = ((y + dy) * canvas.width + (x + dx)) * 4;
          if (idx < data.length) {
            data[idx] = Math.max(0, Math.min(255, data[idx] + variation));
            data[idx + 1] = Math.max(0, Math.min(255, data[idx + 1] + variation));
            data[idx + 2] = Math.max(0, Math.min(255, data[idx + 2] + variation));
          }
        }
      }
    }
  }

  ctx.putImageData(imageData, 0, 0);
}

// ============================================================================
// PAINTERLY TECHNIQUES (Paper.js)
// ============================================================================
function drawBrushstroke(x, y, angle, length, width, color, alpha = 0.9, blendMode = 'normal') {
  const numBristles = Math.floor(50 + seededRandom() * 30); // 50-80 (era 30-50)

  for (let i = 0; i < numBristles; i++) {
    const offsetAngle = angle + (seededRandom() - 0.5) * 0.4;
    const noiseX = noise2D(x * 0.1, i * 0.1) * width * 0.4;
    const noiseY = noise2D(y * 0.1, i * 0.1) * width * 0.4;

    const startX = x + noiseX;
    const startY = y + noiseY;
    const endX = startX + Math.cos(offsetAngle) * length;
    const endY = startY + Math.sin(offsetAngle) * length;

    const pressure = 0.4 + seededRandom() * 0.8; // Più pressione
    const bristleWidth = width * 0.15 * pressure; // Più larghe

    const path = new paper.Path();
    path.strokeColor = rgbToColor(varyColor(color, startX, startY, 0.08), alpha);
    path.strokeWidth = bristleWidth;
    path.strokeCap = 'round';
    path.blendMode = blendMode;

    const midX = (startX + endX) / 2 + (seededRandom() - 0.5) * width * 0.3;
    const midY = (startY + endY) / 2 + (seededRandom() - 0.5) * width * 0.3;

    path.add(new paper.Point(startX, startY));
    path.curveTo(
      new paper.Point(midX, midY),
      new paper.Point(endX, endY)
    );
  }
}

function drawImpasto(x, y, radius, color, alpha = 0.95) {
  const numLayers = 18; // Era 12, ora più profondità

  for (let layer = 0; layer < numLayers; layer++) {
    const layerRadius = radius * (1 - layer * 0.04);
    const layerAlpha = alpha * (0.75 + layer * 0.015);

    const points = [];
    const numPoints = 10; // Era 8
    for (let i = 0; i < numPoints; i++) {
      const angle = (i / numPoints) * Math.PI * 2;
      const variation = seededRandom() * 0.4 + 0.8;
      const px = x + Math.cos(angle) * layerRadius * variation;
      const py = y + Math.sin(angle) * layerRadius * variation;
      points.push(new paper.Point(px, py));
    }

    const polygon = new paper.Path(points);
    polygon.closed = true;
    polygon.fillColor = rgbToColor(varyColor(color, x, y + layer * 2, 0.12), layerAlpha); // Più variazione
    polygon.blendMode = 'multiply';
  }
}

function drawWetOnWet(x, y, radius, color1, color2, alpha = 0.8) {
  const numBlobs = Math.floor(12 + seededRandom() * 6); // 12-18 (era 8-12)

  for (let i = 0; i < numBlobs; i++) {
    const ratio = i / numBlobs;
    const mixedColor = mixColors(color1, color2, ratio);

    const offsetX = x + (seededRandom() - 0.5) * radius * 1.2;
    const offsetY = y + (seededRandom() - 0.5) * radius * 1.2;
    const blobRadius = radius * (0.4 + seededRandom() * 0.5); // Più grandi

    const circle = new paper.Path.Circle({
      center: [offsetX, offsetY],
      radius: blobRadius,
      fillColor: rgbToColor(mixedColor, alpha),
      blendMode: 'overlay'
    });
  }
}

function drawGlazing(x, y, radius, color, alpha = 0.3) {
  const numLayers = Math.floor(3 + seededRandom() * 3);

  for (let i = 0; i < numLayers; i++) {
    const layerRadius = radius * (1 + i * 0.1);
    const offsetX = x + (seededRandom() - 0.5) * radius * 0.3;
    const offsetY = y + (seededRandom() - 0.5) * radius * 0.3;

    const circle = new paper.Path.Circle({
      center: [offsetX, offsetY],
      radius: layerRadius,
      fillColor: rgbToColor(varyColor(color, offsetX, offsetY, 0.05), alpha),
      blendMode: 'multiply'
    });
  }
}

function drawDryBrush(x, y, angle, length, width, color, alpha = 0.6) {
  const numSegments = Math.floor(5 + seededRandom() * 5);

  for (let i = 0; i < numSegments; i++) {
    const segmentRatio = seededRandom();
    const segmentLength = length * (0.1 + seededRandom() * 0.2);

    const startX = x + Math.cos(angle) * length * segmentRatio;
    const startY = y + Math.sin(angle) * length * segmentRatio;

    const path = new paper.Path();
    path.strokeColor = rgbToColor(varyColor(color, startX, startY, 0.1), alpha);
    path.strokeWidth = width * (0.5 + seededRandom() * 0.5);
    path.strokeCap = 'round';

    path.add(new paper.Point(startX, startY));
    path.add(new paper.Point(
      startX + Math.cos(angle) * segmentLength,
      startY + Math.sin(angle) * segmentLength
    ));
  }
}

function drawDripping(x, y, length, width, color, alpha = 0.5) {
  const numDrips = Math.floor(2 + seededRandom() * 3);

  for (let i = 0; i < numDrips; i++) {
    const startX = x + (seededRandom() - 0.5) * width;
    const dripLength = length * (0.5 + seededRandom() * 0.5);

    const path = new paper.Path();
    path.strokeColor = rgbToColor(varyColor(color, startX, y, 0.05), alpha);
    path.strokeWidth = width * 0.1 * (0.5 + seededRandom() * 0.5);
    path.strokeCap = 'round';
    path.blendMode = 'multiply';

    const controlY = y + dripLength * 0.3;
    const endY = y + dripLength;

    path.add(new paper.Point(startX, y));
    path.curveTo(
      new paper.Point(startX + (seededRandom() - 0.5) * 5, controlY),
      new paper.Point(startX + (seededRandom() - 0.5) * 10, endY)
    );
  }
}

function drawSplatter(x, y, radius, color, alpha = 0.6) {
  const numSplatters = Math.floor(5 + seededRandom() * 10);

  for (let i = 0; i < numSplatters; i++) {
    const distance = seededRandom() * radius;
    const angle = seededRandom() * Math.PI * 2;
    const splatX = x + Math.cos(angle) * distance;
    const splatY = y + Math.sin(angle) * distance;
    const splatRadius = radius * 0.05 * (0.3 + seededRandom() * 0.7);

    const circle = new paper.Path.Circle({
      center: [splatX, splatY],
      radius: splatRadius,
      fillColor: rgbToColor(varyColor(color, splatX, splatY, 0.1), alpha),
      blendMode: 'normal'
    });
  }
}

function drawCraquelure(x, y, radius, alpha = 0.4) {
  const numCracks = Math.floor(3 + seededRandom() * 4);

  for (let i = 0; i < numCracks; i++) {
    const angle = seededRandom() * Math.PI * 2;
    const length = radius * (0.5 + seededRandom() * 0.5);

    const path = new paper.Path();
    path.strokeColor = rgbToColor(ZORN_PALETTE.IVORY_BLACK, alpha);
    path.strokeWidth = 0.5 + seededRandom() * 0.5;

    const startX = x + Math.cos(angle) * radius * 0.3;
    const startY = y + Math.sin(angle) * radius * 0.3;
    const endX = startX + Math.cos(angle) * length;
    const endY = startY + Math.sin(angle) * length;

    const segments = 4;
    path.add(new paper.Point(startX, startY));

    for (let j = 1; j <= segments; j++) {
      const t = j / segments;
      const segX = startX + (endX - startX) * t + (seededRandom() - 0.5) * 5;
      const segY = startY + (endY - startY) * t + (seededRandom() - 0.5) * 5;
      path.add(new paper.Point(segX, segY));
    }
  }
}

// ============================================================================
// OIL PAINTING SIMULATION - Bristle-based brush (inspired by Javier Gracia Carpio)
// ============================================================================

/**
 * Bristle - Simulates a single brush hair with chain physics
 */
class Bristle {
  constructor(nElements, thickness) {
    this.nPositions = nElements + 1;
    this.positions = [];
    this.lengths = [];
    this.thicknesses = [];

    const thicknessDecrement = thickness / nElements;

    for (let i = 0; i < this.nPositions; i++) {
      this.positions[i] = { x: 0, y: 0 };
      this.lengths[i] = this.nPositions - i;
      this.thicknesses[i] = thickness - (i - 1) * thicknessDecrement;
    }
  }

  setPosition(newPosition) {
    for (let i = 0; i < this.nPositions; i++) {
      this.positions[i].x = newPosition.x;
      this.positions[i].y = newPosition.y;
    }
  }

  updatePosition(newPosition) {
    this.positions[0].x = newPosition.x;
    this.positions[0].y = newPosition.y;

    for (let i = 1; i < this.nPositions; i++) {
      const pos = this.positions[i];
      const prevPos = this.positions[i - 1];
      const length = this.lengths[i];
      const ang = Math.atan2(prevPos.y - pos.y, prevPos.x - pos.x);
      pos.x = prevPos.x - length * Math.cos(ang);
      pos.y = prevPos.y - length * Math.sin(ang);
    }
  }

  paintOnScreen(color) {
    let previousPos = this.positions[0];

    for (let i = 1; i < this.nPositions; i++) {
      const pos = this.positions[i];
      const path = new paper.Path.Line(
        new paper.Point(previousPos.x, previousPos.y),
        new paper.Point(pos.x, pos.y)
      );
      path.strokeColor = color;
      path.strokeWidth = this.thicknesses[i];
      path.strokeCap = 'round';
      previousPos = pos;
    }
  }
}

/**
 * OilBrush - Simulates an oil painting brush with multiple bristles
 */
class OilBrush {
  constructor(size) {
    this.maxBristleLength = 15;
    this.maxBristleThickness = 5;
    this.positionsForAverage = 4;
    this.bristleVerticalNoise = 8;
    this.maxBristleHorizontalNoise = 4;
    this.noiseSpeedFactor = 0.04;

    this.position = { x: 0, y: 0 };
    this.nBristles = Math.round(size * (1.6 + seededRandom() * 0.3));
    this.bristles = [];
    this.bOffsets = [];
    this.bPositions = [];
    this.positionsHistory = [];
    this.averagePosition = { x: 0, y: 0 };
    this.noiseSeed = seededRandom() * 1000;
    this.updatesCounter = 0;
    this.bristleHorizontalNoise = Math.min(0.3 * size, this.maxBristleHorizontalNoise);

    const bristleLength = Math.min(size, this.maxBristleLength);
    const nElements = Math.round(Math.sqrt(2 * bristleLength));
    const bristleThickness = Math.min(0.8 * bristleLength, this.maxBristleThickness);

    for (let bristle = 0; bristle < this.nBristles; bristle++) {
      this.bristles[bristle] = new Bristle(nElements, bristleThickness);
      this.bOffsets[bristle] = {
        x: size * (seededRandom() - 0.5),
        y: this.bristleVerticalNoise * (seededRandom() - 0.5)
      };
      this.bPositions[bristle] = { x: 0, y: 0 };
    }
  }

  init(newPosition) {
    this.position.x = newPosition.x;
    this.position.y = newPosition.y;
    this.positionsHistory = [];
    this.averagePosition.x = this.position.x;
    this.averagePosition.y = this.position.y;
    this.updatesCounter = 0;
  }

  update(newPosition, updateBristleElements) {
    this.position.x = newPosition.x;
    this.position.y = newPosition.y;

    const historySize = this.positionsHistory.length;

    if (historySize < this.positionsForAverage) {
      this.positionsHistory[historySize] = { x: newPosition.x, y: newPosition.y };
    } else {
      const pos = this.positionsHistory[this.updatesCounter % this.positionsForAverage];
      pos.x = newPosition.x;
      pos.y = newPosition.y;
    }

    const currentHistorySize = Math.min(historySize + 1, this.positionsForAverage);
    let xNewAverage = 0;
    let yNewAverage = 0;

    for (let i = 0; i < currentHistorySize; i++) {
      const pos = this.positionsHistory[i];
      xNewAverage += pos.x;
      yNewAverage += pos.y;
    }

    xNewAverage /= currentHistorySize;
    yNewAverage /= currentHistorySize;

    const directionAngle = Math.PI / 2 + Math.atan2(
      yNewAverage - this.averagePosition.y,
      xNewAverage - this.averagePosition.x
    );

    this.averagePosition.x = xNewAverage;
    this.averagePosition.y = yNewAverage;

    this.updateBristlePositions(directionAngle);

    if (updateBristleElements) {
      if (currentHistorySize === this.positionsForAverage) {
        for (let bristle = 0; bristle < this.nBristles; bristle++) {
          this.bristles[bristle].updatePosition(this.bPositions[bristle]);
        }
      } else if (currentHistorySize === this.positionsForAverage - 1) {
        for (let bristle = 0; bristle < this.nBristles; bristle++) {
          this.bristles[bristle].setPosition(this.bPositions[bristle]);
        }
      }
    }

    this.updatesCounter++;
  }

  updateBristlePositions(directionAngle) {
    if (this.positionsHistory.length >= this.positionsForAverage - 1) {
      const cos = Math.cos(directionAngle);
      const sin = Math.sin(directionAngle);
      const noisePos = this.noiseSeed + this.noiseSpeedFactor * this.updatesCounter;

      for (let bristle = 0; bristle < this.nBristles; bristle++) {
        const offset = this.bOffsets[bristle];
        const x = offset.x + this.bristleHorizontalNoise * (noise2D(noisePos + 0.1 * bristle, 0) - 0.5);
        const y = offset.y;

        const pos = this.bPositions[bristle];
        pos.x = this.position.x + (x * cos - y * sin);
        pos.y = this.position.y + (x * sin + y * cos);
      }
    }
  }

  paintOnScreen(colors) {
    if (this.positionsHistory.length === this.positionsForAverage) {
      for (let bristle = 0; bristle < this.nBristles; bristle++) {
        this.bristles[bristle].paintOnScreen(colors[bristle]);
      }
    }
  }

  getNBristles() {
    return this.nBristles;
  }

  getBristlesPositions() {
    if (this.positionsHistory.length === this.positionsForAverage) {
      return this.bPositions;
    }
    return undefined;
  }
}

/**
 * Enhanced oil painting brushstroke using bristle simulation
 * Optimized for real-time performance
 */
function drawOilBrushstroke(x, y, angle, length, width, color, alpha = 0.9) {
  // Reduced complexity for performance: smaller brush, fewer steps
  const brushSize = Math.min(width, 8); // Max 8 instead of unlimited
  const brush = new OilBrush(brushSize);
  const nSteps = Math.max(3, Math.ceil(length / 6)); // Fewer steps

  // Initialize brush at starting position
  brush.init({ x, y });

  // Generate bristle colors with variation
  const noiseSeed = seededRandom() * 1000;
  const bristleColors = [];

  for (let bristle = 0; bristle < brush.getNBristles(); bristle++) {
    const deltaColor = 12 * (noise2D(noiseSeed + 0.4 * bristle, 0) - 0.5);
    const variedColor = [
      Math.max(0, Math.min(255, color[0] + deltaColor)),
      Math.max(0, Math.min(255, color[1] + deltaColor)),
      Math.max(0, Math.min(255, color[2] + deltaColor))
    ];
    bristleColors[bristle] = rgbToColor(variedColor, alpha);
  }

  // Paint the stroke step by step
  for (let step = 0; step < nSteps; step++) {
    const t = step / nSteps;
    const offsetAngle = angle + (seededRandom() - 0.5) * 0.3;
    const currentX = x + Math.cos(offsetAngle) * length * t;
    const currentY = y + Math.sin(offsetAngle) * length * t;

    brush.update({ x: currentX, y: currentY }, true);
    brush.paintOnScreen(bristleColors);
  }
}

// ============================================================================
// GUITAR TECHNIQUE VISUAL NOTATION (based on graphic algorithm)
// ============================================================================

/**
 * LEGATO - Blob sfumato/elongato
 */
function drawLegato(x, y, size, color, direction = 'horizontal') {
  const angle = direction === 'horizontal' ? 0 : Math.PI / 2;
  const length = size * 1.8;
  const width = size * 0.6;

  // Create elongated blob with soft edges
  for (let i = 0; i < 15; i++) {
    const offset = (i / 15 - 0.5) * length;
    const localWidth = width * (1 - Math.abs(offset / length) * 0.5);

    const circle = new paper.Path.Circle({
      center: [x + Math.cos(angle) * offset, y + Math.sin(angle) * offset],
      radius: localWidth,
      fillColor: rgbToColor(color, 0.15 - i * 0.008),
      blendMode: 'multiply'
    });
  }
}

/**
 * STACCATO - Punti/dots multipli
 */
function drawStaccato(x, y, size, color) {
  const numDots = 3 + Math.floor(seededRandom() * 3); // 3-5 dots

  for (let i = 0; i < numDots; i++) {
    const angle = (i / numDots) * Math.PI * 2;
    const distance = size * 0.4;
    const dotX = x + Math.cos(angle) * distance;
    const dotY = y + Math.sin(angle) * distance;
    const dotRadius = size * 0.15;

    const dot = new paper.Path.Circle({
      center: [dotX, dotY],
      radius: dotRadius,
      fillColor: rgbToColor(color, 0.9),
      blendMode: 'normal'
    });
  }

  // Center dot
  const centerDot = new paper.Path.Circle({
    center: [x, y],
    radius: size * 0.2,
    fillColor: rgbToColor(color, 1.0),
    blendMode: 'normal'
  });
}

/**
 * BEND - Curva rossa/colorata
 */
function drawBendTechnique(x, y, size, color) {
  const startY = y + size * 0.5;
  const endY = y - size * 0.5;
  const controlX = x + size * 0.6;

  const path = new paper.Path();
  path.strokeColor = rgbToColor(color, 0.9);
  path.strokeWidth = size * 0.12;
  path.strokeCap = 'round';

  path.add(new paper.Point(x, startY));
  path.curveTo(
    new paper.Point(controlX, (startY + endY) / 2),
    new paper.Point(x, endY)
  );

  // Add arrow at top
  const arrowSize = size * 0.15;
  const arrow = new paper.Path([
    new paper.Point(x - arrowSize, endY + arrowSize),
    new paper.Point(x, endY),
    new paper.Point(x + arrowSize, endY + arrowSize)
  ]);
  arrow.strokeColor = rgbToColor(color, 0.9);
  arrow.strokeWidth = size * 0.08;
  arrow.strokeCap = 'round';
}

/**
 * SLIDE - Linea diagonale
 */
function drawSlideTechnique(x, y, size, color, direction = 'up') {
  const angle = direction === 'up' ? -Math.PI / 4 : Math.PI / 4;
  const length = size * 1.5;

  const startX = x - Math.cos(angle) * length / 2;
  const startY = y - Math.sin(angle) * length / 2;
  const endX = x + Math.cos(angle) * length / 2;
  const endY = y + Math.sin(angle) * length / 2;

  const path = new paper.Path.Line(
    new paper.Point(startX, startY),
    new paper.Point(endX, endY)
  );
  path.strokeColor = rgbToColor(color, 0.85);
  path.strokeWidth = size * 0.15;
  path.strokeCap = 'round';

  // Add motion lines
  for (let i = 0; i < 3; i++) {
    const offset = (i - 1) * size * 0.3;
    const motionPath = new paper.Path.Line(
      new paper.Point(startX + offset, startY),
      new paper.Point(endX + offset, endY)
    );
    motionPath.strokeColor = rgbToColor(color, 0.3 - i * 0.1);
    motionPath.strokeWidth = size * 0.08;
    motionPath.strokeCap = 'round';
  }
}

/**
 * VIBRATO - Forma ondulata
 */
function drawVibratoTechnique(x, y, size, color) {
  const numWaves = 4;
  const amplitude = size * 0.3;

  const path = new paper.Path();
  path.strokeColor = rgbToColor(color, 0.85);
  path.strokeWidth = size * 0.12;
  path.strokeCap = 'round';

  for (let i = 0; i <= numWaves * 2; i++) {
    const t = i / (numWaves * 2);
    const px = x - size + t * size * 2;
    const py = y + Math.sin(i * Math.PI) * amplitude;

    if (i === 0) {
      path.add(new paper.Point(px, py));
    } else {
      path.lineTo(new paper.Point(px, py));
    }
  }

  // Add subtle fill
  const fillPath = path.clone();
  fillPath.closePath();
  fillPath.fillColor = rgbToColor(color, 0.2);
  fillPath.strokeColor = null;
  fillPath.blendMode = 'multiply';
}

// ============================================================================
// NOTE RENDERING
// ============================================================================
function renderNote(note, noteIndex, growthFactor = 1.0) {
  const canvas = document.getElementById('paperCanvas');

  // Calculate total duration dynamically
  const lastNote = notes[notes.length - 1];
  const totalDuration = lastNote.start_time + lastNote.duration;

  // Map time to X (full canvas width)
  const x = 50 + (note.start_time / totalDuration) * (canvas.width - 100);

  // Map pitch to Y (full canvas height) - increased scale
  const pitchRange = 48; // 4 octaves
  const y = canvas.height / 2 + (60 - note.pitch) * 20; // 20px per semitone (era 8)

  // Base color from Zorn palette
  const baseColor = getPaletteColor(note.pitch);

  // Base size from velocity - MOLTO PIÙ GRANDE
  let baseSize = 80 + (note.velocity_value || 0.5) * 150; // Era 30 + 80

  // ENFASI DINAMICA - Climax detection
  const climaxDistance = Math.abs(noteIndex - dynamicsAnalysis.climax_idx) / notes.length;
  const climaxFactor = 1.0 - climaxDistance;
  baseSize *= (1.0 + climaxFactor * 0.7); // +70% at climax

  // Apply growth factor
  const size = baseSize * growthFactor;

  // Musical context
  const rhythmInfo = analyzeRhythm(note);
  const contour = contours[noteIndex];

  let intervalInfo = null;
  if (noteIndex > 0) {
    intervalInfo = analyzeInterval(notes[noteIndex - 1], note);
  }

  // GUITAR TECHNIQUE-BASED VISUAL NOTATION
  const technique = note.technique || 'regular';

  // Primary shape based on guitar technique
  switch(technique) {
    case 'legato':
      drawLegato(x, y, size, baseColor, contour === 'ascending' ? 'horizontal' : 'horizontal');
      break;

    case 'staccato':
      drawStaccato(x, y, size, baseColor);
      break;

    case 'bend':
      drawBendTechnique(x, y, size, baseColor);
      drawImpasto(x, y, size * 0.5, baseColor, 0.7); // Base form
      break;

    case 'slide':
      const slideDir = contour === 'ascending' ? 'up' : 'down';
      drawSlideTechnique(x, y, size, baseColor, slideDir);
      break;

    case 'vibrato':
      drawVibratoTechnique(x, y, size, baseColor);
      drawImpasto(x, y, size * 0.5, baseColor, 0.7); // Base form
      break;

    case 'regular':
    default:
      // Regular technique - use full painterly rendering
      drawImpasto(x, y, size * 0.6, baseColor, 0.8);

      // GLAZING: Small intervals
      if (intervalInfo && ['unison', 'step'].includes(intervalInfo.type)) {
        if (seededRandom() < 0.6 * growthFactor) {
          drawGlazing(x, y, size * 0.8, baseColor, 0.3);
        }
      }
      break;
  }

  // WET-ON-WET: Small intervals with color mixing from adjacent notes
  if (intervalInfo && ['unison', 'step', 'small'].includes(intervalInfo.type)) {
    if (seededRandom() < 0.5 * growthFactor) {
      // Mix with previous note's color for realistic wet-on-wet
      let secondaryColor;
      if (noteIndex > 0) {
        const prevNote = notes[noteIndex - 1];
        const prevColor = getPaletteColor(prevNote.pitch);
        // Blend 30% previous note color with 70% new color
        secondaryColor = mixColors(prevColor, baseColor, 0.3);
      } else {
        secondaryColor = getPaletteColor(note.pitch + 3);
      }
      drawWetOnWet(x, y, size * 0.7, baseColor, secondaryColor, 0.6);
    }
  }

  // DRY BRUSH: Fast notes
  if (['very_fast', 'fast'].includes(rhythmInfo.type)) {
    if (seededRandom() < 0.7 * growthFactor) {
      const angle = contour === 'ascending' ? -Math.PI / 4 :
                   contour === 'descending' ? Math.PI / 4 : 0;
      drawDryBrush(x, y, angle, size * 1.2, size * 0.4, baseColor, 0.6);
    }
  }

  // BRUSHSTROKE: Directional (using simple version until oil brush is tested)
  const strokeAngle = contour === 'ascending' ? -Math.PI / 3 :
                     contour === 'descending' ? Math.PI / 3 : 0;
  // TODO: Re-enable oil brushstroke once tested in test_oil_brush.html
  // drawOilBrushstroke(x, y, strokeAngle, size * 1.5, size * 0.3, baseColor, 0.7);
  drawBrushstroke(x, y, strokeAngle, size * 1.5, size * 0.3, baseColor, 0.7, 'multiply');

  // DRIPPING: Descending
  if (contour === 'descending') {
    if (seededRandom() < 0.5 * growthFactor) {
      drawDripping(x, y, size * 1.5, size * 0.6, baseColor, 0.4);
    }
  }

  // SPLATTER: Climax
  if (climaxFactor > 0.7) {
    if (seededRandom() < 0.4 * growthFactor) {
      drawSplatter(x, y, size * 1.3, baseColor, 0.5);
    }
  }

  // CRAQUELURE: Slow notes
  if (['slow', 'very_slow'].includes(rhythmInfo.type)) {
    if (seededRandom() < 0.4 * growthFactor) {
      drawCraquelure(x, y, size * 0.8, 0.3);
    }
  }
}

// ============================================================================
// FRAME RENDERING
// ============================================================================
function renderFrame(frameNumber) {
  paper.project.clear();
  resetRNG();

  // Apply canvas texture first
  applyCanvasTexture();

  fps = parseInt(document.getElementById('fpsSelect').value);
  const currentTime = frameNumber / fps;

  // Render notes progressively
  for (let i = 0; i < notes.length; i++) {
    const note = notes[i];
    const noteStart = note.start_time;
    const noteDuration = note.duration;

    if (noteStart <= currentTime) {
      const growthDuration = noteDuration * 0.6;
      const timeSinceStart = currentTime - noteStart;
      const growthFactor = Math.min(timeSinceStart / growthDuration, 1.0);

      renderNote(note, i, growthFactor);
    }
  }

  paper.view.update();
}

// ============================================================================
// ANIMATION CONTROLS
// ============================================================================
function playAnimation() {
  if (notes.length === 0) return;

  isPlaying = true;
  document.getElementById('playBtn').disabled = true;
  document.getElementById('pauseBtn').disabled = false;

  // Start audio playback
  const audio = document.getElementById('audioPlayer');

  console.log('🔊 Attempting to play audio...');
  console.log('   Audio element:', audio);
  console.log('   Audio ready state:', audio.readyState);
  console.log('   Audio current time:', audio.currentTime);

  audio.currentTime = currentFrame / fps;

  // Stop animation when audio ends
  audio.onended = () => {
    console.log('🎵 Audio ended, stopping animation');
    pauseAnimation();
  };

  const playPromise = audio.play();
  if (playPromise !== undefined) {
    playPromise
      .then(() => {
        console.log('✅ Audio playing successfully!');
      })
      .catch(err => {
        console.error('❌ Audio playback failed:', err.name, err.message);
        alert('Audio bloccato dal browser! Clicca OK e premi Play di nuovo.');
      });
  }

  fps = parseInt(document.getElementById('fpsSelect').value);
  const lastNote = notes[notes.length - 1];
  const totalDuration = lastNote.start_time + lastNote.duration + 1.0;
  const totalFrames = Math.ceil(totalDuration * fps);

  animationInterval = setInterval(() => {
    if (currentFrame >= totalFrames) {
      pauseAnimation();
      return;
    }

    renderFrame(currentFrame);

    const progress = ((currentFrame + 1) / totalFrames * 100).toFixed(1);
    const time = (currentFrame / fps).toFixed(2);
    document.getElementById('info').innerHTML = `
      <div class="progress">▶ Playing: Frame ${currentFrame + 1}/${totalFrames} (${progress}%)</div>
      <div>Time: ${time}s / ${totalDuration.toFixed(1)}s | 🔊 Audio</div>
    `;

    currentFrame++;
  }, 1000 / fps);
}

function pauseAnimation() {
  isPlaying = false;
  if (animationInterval) {
    clearInterval(animationInterval);
    animationInterval = null;
  }

  // Pause audio
  const audio = document.getElementById('audioPlayer');
  audio.pause();

  document.getElementById('playBtn').disabled = false;
  document.getElementById('pauseBtn').disabled = true;

  document.getElementById('info').innerHTML = `
    <div class="progress">⏸ Paused at frame ${currentFrame}</div>
    <div>Time: ${(currentFrame / fps).toFixed(2)}s</div>
  `;
}

function resetAnimation() {
  pauseAnimation();
  currentFrame = 0;

  // Reset audio to beginning
  const audio = document.getElementById('audioPlayer');
  audio.currentTime = 0;

  renderFrame(0);

  document.getElementById('info').innerHTML = `
    <div class="progress">↺ Reset to frame 0</div>
    <div>Canvas texture only (notes will appear as they play)</div>
  `;
}

function downloadFrame() {
  const canvas = document.getElementById('paperCanvas');
  const dataURL = canvas.toDataURL('image/png');

  const link = document.createElement('a');
  link.download = `zorn_frame_${String(currentFrame).padStart(5, '0')}.png`;
  link.href = dataURL;
  link.click();

  document.getElementById('info').innerHTML = `
    <div class="progress">💾 Downloaded frame ${currentFrame}</div>
  `;
}

// ============================================================================
// INITIALIZE
// ============================================================================
window.addEventListener('load', () => {
  paper.setup(document.getElementById('paperCanvas'));
  console.log('✓ Paper.js initialized');
  console.log('✓ Zorn Pentatonic Painterly Renderer ready');
  console.log('  Load notes JSON to begin');
});
