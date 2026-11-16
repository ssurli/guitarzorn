// SPDX-License-Identifier: EUPL-1.2
// Copyright (c) 2026 Stefano Surlinelli — https://github.com/ssurli/guitarzorn
/* Guitarzorn — LA CODIFICA
   Una sola tabella per tutto: demo, tablatura, strumento passano da qui.
     nota      → pigmento            (pentatonica di La ↔ tavolozza di Zorn)
     ottava    → luminosità          (stessa tinta, più chiara in alto, più scura in basso)
     tecnica   → tipo di pennellata  (come si muove il pennello, non quale simbolo disegna)
     dinamica  → saturazione e spessore
   Fonte: "Parametri grafici.txt". Dove quel testo non decide, la scelta è segnata con (*). */
(function () {
'use strict';
// pigmenti come miscela [ocra, vermiglione, nero avorio, bianco di titanio]
const norm = p => { const s = p[0] + p[1] + p[2] + p[3] || 1; return p.map(v => v / s); };
const mix = (a, b, t) => norm(a.map((v, i) => v * (1 - t) + b[i] * t));
const NERO = [0, 0, 1, 0], BIANCO = [0, 0, 0, 1];

const NOTE = {
  9:  { nome: 'A',  ruolo: 'tonica',         colore: 'Giallo ocra',            pig: norm([0.84, 0.09, 0.07, 0]) },   // (*) appena scurita: deve leggersi sul fondo ocra
  0:  { nome: 'C',  ruolo: 'terza minore',   colore: 'Rosso vermiglione',      pig: norm([0.12, 0.88, 0, 0]) },
  2:  { nome: 'D',  ruolo: 'quarta',         colore: 'Nero avorio',            pig: norm([0.14, 0.06, 0.80, 0]) },
  4:  { nome: 'E',  ruolo: 'quinta',         colore: 'Bianco di titanio',      pig: norm([0.10, 0, 0, 0.90]) },
  7:  { nome: 'G',  ruolo: 'settima minore', colore: 'Ocra + nero',            pig: norm([0.60, 0.10, 0.30, 0]) },
  // note esterne alla scala = sfumature
  10: { nome: 'Bb', ruolo: 'esterna', colore: 'Rosso scuro', pig: norm([0.05, 0.70, 0.25, 0]) },
  5:  { nome: 'F',  ruolo: 'esterna', colore: 'Grigio',      pig: norm([0.05, 0, 0.45, 0.50]) },
};
// (*) le altre note esterne: sfumatura a metà tra le due note di scala vicine
[[11, 'B', 9, 0], [1, 'C#', 0, 2], [3, 'Eb', 2, 4], [6, 'F#', 4, 7], [8, 'G#', 7, 9]].forEach(([pc, nome, a, b]) => {
  NOTE[pc] = { nome, ruolo: 'esterna', colore: 'Sfumatura ' + NOTE[a].nome + '–' + NOTE[b].nome, pig: mix(NOTE[a].pig, NOTE[b].pig, 0.5) };
});

// ottava di riferimento: da A3 (57) a G#4 (68)
const OTTAVA = { piuChiaraPerOttava: 0.22, piuScuraPerOttava: 0.14 };
function pigmentFor(midi) {
  const base = NOTE[((midi % 12) + 12) % 12].pig, o = Math.floor((midi - 57) / 12);
  if (o > 0) return mix(base, BIANCO, Math.min(0.6, OTTAVA.piuChiaraPerOttava * o));
  if (o < 0) return mix(base, NERO, Math.min(0.5, OTTAVA.piuScuraPerOttava * -o));
  return base;
}
const noteName = midi => NOTE[((midi % 12) + 12) % 12].nome;

/* tecnica → pennellata. `gesto` sono i parametri del pennello:
   dir       'seguente' (verso la nota che segue) · 'libera' · 'su' · 'giu' · 'verso' (su se l'arrivo è più acuto)
   curva     di quanto piega per pixel (negativo = verso l'alto)
   velocita  px al secondo · larghezza, spessore, carica: moltiplicatori
   secco     quanto lavora a pennello asciutto · raccolta: quanto colore prende dalla tela
   tremolo   ampiezza e passo dell'ondulazione · unita: parte dove finiva il tocco precedente
   chiaro    quota di bianco aggiunta al pigmento · bordo: 0 = squadrato, 1 = sfumato            */
const TECNICHE = {
  normale:      { simbolo: '5',     nome: 'Nota singola',    forma: 'Pennellata singola: corta se la nota è breve, lunga e sfumata se è tenuta',
                  gesto: { dir: 'seguente' } },
  staccato:     { simbolo: '',      nome: 'Staccato',        forma: 'Puntini netti, isolati',
                  gesto: { dir: 'libera', larghezza: 1.15, spessore: 1.3, velocita: 200 } },
  legato:       { simbolo: '',      nome: 'Legato',          forma: 'Pennellata sfumata, continua',
                  gesto: { dir: 'seguente', raccolta: 0.09, opacita: 0.6, secco: 1.2, spessore: 0.8 } },
  hammer_on:    { simbolo: '5h7',   nome: 'Hammer-on',       forma: 'Due macchie ravvicinate con sfumatura di unione',
                  gesto: { dir: 'seguente', unita: true, raccolta: 0.14, larghezza: 0.9, spessore: 1.5, velocita: 210, forza: 0.7 } },
  pull_off:     { simbolo: '7p5',   nome: 'Pull-off',        forma: 'Due macchie ravvicinate con sfumatura di unione',
                  gesto: { dir: 'seguente', unita: true, raccolta: 0.14, larghezza: 0.85, spessore: 1.2, velocita: 210, forza: 0.6 } },
  slide:        { simbolo: '5/7',   nome: 'Slide',           forma: 'Pennellata diagonale continua che scivola',
                  gesto: { dir: 'verso', angolo: 1.05, curva: 0, velocita: 480, secco: 2.0, larghezza: 0.95, carica: 0.55 } },
  bend:         { simbolo: '7b9',   nome: 'Bend',            forma: 'Pennellata curva che si piega verso l’alto',
                  gesto: { dir: 'fissa', angolo: 0.25, curva: -0.0085, velocita: 300, spessore: 1.35 } },
  vibrato:      { simbolo: '7~',    nome: 'Vibrato',         forma: 'Pennellata tremolante, ondulata',
                  gesto: { dir: 'libera', apertura: 0.2, tremolo: 5, passo: 62, velocita: 300 } },
  double_stop:  { simbolo: 'due corde', nome: 'Bicordo',     forma: 'Macchie sovrapposte: due pennellate insieme, la seconda si sporca della prima',
                  gesto: { dir: 'fissa', angolo: -0.15, apertura: 0.3, spessore: 1.25, velocita: 230, raccoltaSeconda: 0.1 } },
  powerchord:   { simbolo: 'tre corde', nome: 'Power chord', forma: 'Pennellata squadrata, blocco netto, colori delle note fusi',
                  gesto: { dir: 'fissa', angolo: 0, apertura: 0.12, larghezza: 2.0, spessore: 1.4, velocita: 240, secco: 1.0, bordo: 0.3, fuso: true } },
  tapping:      { simbolo: 't12',   nome: 'Tapping',         forma: 'Piccole gocce di luce, più brillanti della nota',
                  gesto: { dir: 'libera', apertura: 3, larghezza: 0.6, spessore: 2.0, velocita: 160, chiaro: 0.28, lunghezzaMax: 26 } },
  armonico:     { simbolo: '<12>',  nome: 'Armonico naturale', forma: 'Alone leggero, molto chiaro, appena percettibile',
                  gesto: { dir: 'libera', larghezza: 1.3, spessore: 0.5, opacita: 0.45, chiaro: 0.6, velocita: 220 } },
  armonico_artificiale: { simbolo: '', nome: 'Armonico artificiale', forma: 'Scintille affilate: tratti corti, direzionali, quasi graffi',
                  gesto: { dir: 'libera', apertura: 2, larghezza: 0.4, spessore: 1.4, velocita: 520, secco: 2.2, chiaro: 0.4, lunghezzaMax: 60 } },
  leva:         { simbolo: '',      nome: 'Leva del tremolo', forma: 'Pennellata che cade verso il basso e si scurisce',
                  gesto: { dir: 'fissa', angolo: 0.8, curva: 0.004, velocita: 320, secco: 2.0, carica: 0.5, scuro: 0.25 } },
  // bicordo finale tenuto (nel riff di Johnny B. Goode)
  double_stop_final: { simbolo: '', nome: 'Bicordo tenuto', forma: 'Due pennellate lunghe e tremolanti',
                  gesto: { dir: 'fissa', angolo: -0.1, apertura: 0.15, tremolo: 4.5, passo: 78, larghezza: 1.25, spessore: 1.5, velocita: 250, carica: 1.6, lunghezzaMax: 700, raccoltaSeconda: 0.1 } },
};

// dinamica → saturazione (opacità) e spessore della pasta; forza 1 = forte
const DINAMICA = { p: 0.55, mp: 0.75, mf: 1.0, f: 1.25, ff: 1.55 };
const opacitaPer = forza => Math.max(0.42, Math.min(0.9, 0.38 + 0.36 * forza));

window.GuitarzornCodifica = { NOTE, OTTAVA, TECNICHE, DINAMICA, pigmentFor, noteName, opacitaPer, mix, NERO, BIANCO };
})();
