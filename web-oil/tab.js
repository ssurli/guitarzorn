// SPDX-License-Identifier: EUPL-1.2
// Copyright (c) 2026 Stefano Surlinelli — https://github.com/ssurli/guitarzorn
/* Guitarzorn — dalla tablatura agli eventi
   Legge una tablatura a sei righe in testo (accordatura standard, cantino in alto).
   La tablatura non scrive il ritmo: qui LA POSIZIONE ORIZZONTALE È IL TEMPO, tante
   colonne per battito quante ne indichi (le stanghette | non contano).
   Simboli: 5h7 hammer-on · 7p5 pull-off · 5/7 e 7\5 slide · 7b9 bend · 7~ vibrato
            t12 tapping · <12> armonico · x nota stoppata (ignorata)
   Note nella stessa colonna: due = bicordo, tre o più (o una quinta sui bassi) = power chord. */
(function () {
'use strict';
const OPEN = [64, 59, 55, 50, 45, 40];            // e B G D A E, dall'alto in basso
const isTabLine = l => /^\s*[A-Za-z]?\s*\|?[-0-9hpb\/\\~tx<>()|.\s]*-[-0-9hpb\/\\~tx<>()|.\s]*$/.test(l) && (l.match(/-/g) || []).length >= 3;

function parseBlock(lines, colsPerBeat, beat0) {
  // toglie l'etichetta della corda e allinea le righe
  const rows = lines.map(l => { const m = l.match(/^\s*[A-Za-z]?\s*\|/); return m ? l.slice(m[0].length) : l.replace(/^\s*[A-Za-z]\s?/, ''); });
  const width = Math.max(...rows.map(r => r.length));
  // colonna → tempo: le stanghette non occupano tempo (se una colonna è stanghetta sulla prima riga)
  const timeOf = []; let t = 0;
  for (let c = 0; c <= width; c++) { timeOf[c] = t; if (rows[0][c] !== '|') t++; }
  const notes = [];
  rows.forEach((row, sIdx) => {
    let i = 0, last = null, link = null, tap = false;
    while (i < row.length) {
      const ch = row[i];
      if (ch === 't' || ch === 'T') { tap = true; i++; continue; }
      let harm = false, j = i;
      if (ch === '<') { harm = true; j = i + 1; }
      if (/[0-9]/.test(row[j] || '')) {
        let k = j; while (/[0-9]/.test(row[k] || '') && k - j < 2) k++;
        const fret = parseInt(row.slice(j, k), 10);
        const n = { col: timeOf[i], midi: OPEN[sIdx] + fret, string: sIdx, link, tap, harm, vib: false };
        if (harm && row[k] === '>') k++;
        notes.push(n); last = n; link = null; tap = false; i = k;
        const nx = row[i];
        if (nx && 'hpb/\\'.includes(nx) && /[0-9<]/.test(row[i + 1] || '')) { link = nx; i++; }
        continue;
      }
      if (ch === '~' && last) last.vib = true;
      i++;
    }
  });
  // slide e bend: la nota d'arrivo non si ripizzica, diventa la meta del gesto
  const out = [];
  notes.sort((a, b) => a.string - b.string || a.col - b.col);
  for (let i = 0; i < notes.length; i++) {
    const n = notes[i], nx = notes[i + 1];
    let tech = n.tap ? 'tapping' : n.harm ? 'armonico' : n.link === 'h' ? 'hammer_on' : n.link === 'p' ? 'pull_off' : 'normale', to = null, endCol = null, vib = n.vib;
    if (nx && nx.string === n.string && nx.link && '/\\b'.includes(nx.link)) {
      tech = nx.link === 'b' ? 'bend' : 'slide'; to = nx.midi; endCol = nx.col; vib = vib || nx.vib; i++;
    }
    out.push({ col: n.col, midi: n.midi, tech, to, endCol, vib });
  }
  // stessa colonna = suonate insieme
  const byCol = new Map();
  out.forEach(n => { if (!byCol.has(n.col)) byCol.set(n.col, []); byCol.get(n.col).push(n); });
  const cols = [...byCol.keys()].sort((a, b) => a - b), events = [];
  cols.forEach((c, idx) => {
    const group = byCol.get(c).sort((a, b) => a.midi - b.midi), first = group[0];
    const nextCol = idx + 1 < cols.length ? cols[idx + 1] : null;
    let lenCols = nextCol !== null ? nextCol - c : colsPerBeat * 2;
    if (first.endCol !== null && nextCol === null) lenCols = Math.max(lenCols, first.endCol - c + colsPerBeat);
    const midis = group.map(n => n.midi);
    let tech = first.tech;
    if (midis.length >= 3 || (midis.length === 2 && midis[1] - midis[0] === 7 && midis[0] < 55)) tech = 'powerchord';
    else if (midis.length === 2) tech = 'double_stop';
    events.push({ t: beat0 + c / colsPerBeat, d: Math.min(lenCols / colsPerBeat, 4) * 0.92, midis, tech, to: first.to, vib: group.some(n => n.vib) });
  });
  return { events, beats: timeOf[width] / colsPerBeat };
}

/** testo → { events:[{t, d, midis, tech, to, vib}], beats, righe }; t e d in battiti */
function parseTab(text, colsPerBeat) {
  colsPerBeat = colsPerBeat || 4;
  const lines = text.replace(/\r/g, '').split('\n'), blocks = []; let cur = [];
  lines.forEach(l => { if (isTabLine(l)) cur.push(l); else { if (cur.length) blocks.push(cur); cur = []; } });
  if (cur.length) blocks.push(cur);
  const good = blocks.filter(b => b.length === 6);
  let beat0 = 0, events = [];
  good.forEach(b => { const r = parseBlock(b, colsPerBeat, beat0); events = events.concat(r.events); beat0 += Math.ceil(r.beats); });
  return { events, beats: beat0, blocchi: good.length, scartati: blocks.length - good.length };
}

// ---- esempi: studi originali in La minore pentatonica, uno per famiglia di tecniche ----
const ESEMPI = [
  { id: 'legato', titolo: 'Studio 1 · Legato (hammer-on e pull-off)', bpm: 96, tab: [
    'e|----------------------------------|',
    'B|----------------------------------|',
    'G|------------5h7p5-------5h7-------|',
    'D|------5h7-----------7p5-----------|',
    'A|5h7---------------------------7~~~|',
    'E|----------------------------------|'] },
  { id: 'slide', titolo: 'Studio 2 · Slide', bpm: 100, tab: [
    'e|------------------8\\5-------------|',
    'B|------------5/8---------8\\5-------|',
    'G|------5/7---------------------7~~~|',
    'D|5/7-------------------------------|',
    'A|----------------------------------|',
    'E|----------------------------------|'] },
  { id: 'bend', titolo: 'Studio 3 · Bend e vibrato', bpm: 84, tab: [
    'e|------------------5---------------|',
    'B|------------8b10------8~~~--------|',
    'G|7b9---7b9-------------------7b9~~~|',
    'D|----------------------------------|',
    'A|----------------------------------|',
    'E|----------------------------------|'] },
  { id: 'bicordi', titolo: 'Studio 4 · Bicordi', bpm: 120, tab: [
    'e|5---5-5---5-5---5-5-------5~~~----|',
    'B|5---5-5---5-5---5-5---5---5~~~----|',
    'G|----------------------5-----------|',
    'D|----------------------------------|',
    'A|----------------------------------|',
    'E|----------------------------------|'] },
  { id: 'power', titolo: 'Studio 5 · Power chord', bpm: 110, tab: [
    'e|----------------------------------|',
    'B|----------------------------------|',
    'G|----------------------------------|',
    'D|------------------------7~~~------|',
    'A|7---7---10----7---5-----7~~~------|',
    'E|5---5---8-----5---3-----5~~~------|'] },
  { id: 'tapping', titolo: 'Studio 6 · Tapping e armonici', bpm: 100, tab: [
    'e|t12p5h8---t12p5h8---------<12>----|',
    'B|----------------------<12>--------|',
    'G|------------------<12>------------|',
    'D|----------------------------------|',
    'A|----------------------------------|',
    'E|----------------------------------|'] },
].map(e => Object.assign(e, { tab: e.tab.join('\n') }));

window.GuitarzornTab = { parseTab, ESEMPI, OPEN };
})();
