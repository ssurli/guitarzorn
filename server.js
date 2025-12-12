#!/usr/bin/env node

/**
 * Simple HTTP server for Zorn Pentatonic Paper.js renderer
 */

const express = require('express');
const path = require('path');

const PORT = process.env.PORT || 8888;

const app = express();

// Serve static files
app.use(express.static(__dirname));

// Start server
app.listen(PORT, () => {
  console.log('\n🎨 Zorn Pentatonic Paper.js Renderer Server\n');
  console.log(`✓ Server running at http://localhost:${PORT}`);
  console.log(`\n📖 Open in browser:`);
  console.log(`   http://localhost:${PORT}/zorn_pentatonic_paperjs.html`);
  console.log(`\n🎯 Instructions:`);
  console.log(`   1. Click "Load 1207(1)_notes.json"`);
  console.log(`   2. Click "▶ Play Animation"`);
  console.log(`   3. Use "💾 Save Current Frame" to export frames\n`);
  console.log(`Press Ctrl+C to stop server\n`);
});
