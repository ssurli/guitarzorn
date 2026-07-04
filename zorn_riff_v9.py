"""
guitarzorn v9 — La Passeggiata Melodica
========================================
Stesso motore fisico della v8 (Kubelka-Munk a 4 pigmenti, aratura della
pasta, tela nel lighting) e stessi canali semantici del mapping v2
(pitch class→colore, velocity→materia, ottava→luminosità, durata→lunghezza,
tecnica→gesto). Cambia il MAPPING SPAZIALE:

  la melodia non scorre su una timeline — DISEGNA UN CAMMINO.

  • Ogni nota parte dove finisce la precedente (linea di Klee/Kandinsky:
    "una passeggiata di un punto").
  • L'intervallo melodico verso la nota successiva è la SVOLTA del
    cammino: salita = il gesto gira verso l'alto, discesa verso il basso,
    salto grande = svolta ampia (±6°/semitono, clamp ±48°).
  • Le pause fanno avanzare il cammino senza dipingere: il silenzio
    è tela nuda lungo il percorso.
  • Il cambio di battuta è una svolta di fraseggio (±28° alternati):
    il cammino "gira l'angolo" dove la musica respira.
  • La RIPETIZIONE non avanza: si accumula. I double-stop ribattuti del
    "campanello" si impilano in una rosetta a girasole (angolo aureo,
    r∝√k) costruendo impasto — la ripetizione diventa materia, come
    un looper che sovraincide.
  • Uno sterzo dolce e deterministico riporta il cammino verso il
    centro quando si avvicina ai bordi: la composizione resta in tela.

Tutto è deterministico: la casualità (seed fisso) esiste solo nella
fisica della mano (tremolio, setole, jitter di ripetizione).
"""

import math
import random

import numpy as np

from zorn_riff_v8 import (OilCanvas, blur, mixc, note_conc,
                          OCHRE, VERM, BLACK, WHITE,
                          VEL_WIDTH, VEL_THICK, VEL_OPAC, K_TECH)
from score import JOHNNY_B_GOODE_INTRO, pitch_class


def _wrap(a: float) -> float:
    """Angolo in (-pi, pi]."""
    while a > math.pi:
        a -= 2 * math.pi
    while a <= -math.pi:
        a += 2 * math.pi
    return a


class ZornMelodicWalk:
    W, H = 1920, 1080
    MARGIN = 150

    L_BEAT = 200                    # px di cammino per beat
    SEMI_TURN = math.radians(6.0)   # svolta per semitono d'intervallo
    MAX_TURN = math.radians(48.0)   # clamp della svolta melodica
    PHRASE_TURN = math.radians(28.0)  # svolta di fraseggio al cambio battuta
    DYAD_SEP = 2.4                  # px di separazione per semitono del dyad

    _N_REP = 2                      # pennellate per nota (mano che ritorna)
    _J_POS = 3.5
    _J_ANG = 0.04

    def __init__(self, seed: int = 42):
        random.seed(seed)
        bg = mixc(mixc(OCHRE, WHITE, 0.35), VERM, 0.012)
        self.cv = OilCanvas(self.W, self.H, bg, seed)

        # stato della passeggiata
        self.x = self.W * 0.15
        self.y = self.H * 0.70
        self.theta = math.radians(-16.0)   # partenza: verso destra, un filo su

    # ── dinamiche condivise col v8 ──────────────────────────────────────────
    @staticmethod
    def _dry(t: float) -> float:
        return 0.28 if (t % 1.0) < 0.05 else 0.52

    @staticmethod
    def _shuffle_w(t: float) -> float:
        return 1.15 if (t % 1.0) < 0.5 else 0.85

    # ── sterzo dolce verso il centro (deterministico) ───────────────────────
    def _steer(self):
        m = 170
        near = min(self.x - m, self.W - m - self.x,
                   self.y - m, self.H - m - self.y)
        if near < 150:
            target = math.atan2(self.H * 0.50 - self.y, self.W * 0.54 - self.x)
            d = _wrap(target - self.theta)
            k = min(1.0, (150 - near) / 150)
            self.theta = _wrap(self.theta + max(-0.55, min(0.55, d)) * 0.8 * k)
        # mai camminare all'indietro: il tempo va avanti
        if abs(self.theta) > math.radians(115):
            self.theta = math.copysign(math.radians(115), self.theta)

    def _advance(self, dist: float, ang: float = None):
        a = self.theta if ang is None else ang
        self.x += dist * math.cos(a)
        self.y += dist * math.sin(a)
        self.x = max(self.MARGIN, min(self.W - self.MARGIN, self.x))
        self.y = max(self.MARGIN, min(self.H - self.MARGIN, self.y))

    # ── il gesto di una nota (con ripetizioni "mano che ritorna") ──────────
    def _mark(self, x, y, ang, length, width, conc, opacity, thickness,
              curvature=0.0, waviness=0.0, wave_freq=4.0,
              dryness=0.4, smear=0.10, taper_end=0.55):
        for _ in range(self._N_REP):
            self.cv.stroke(
                x + random.gauss(0, self._J_POS),
                y + random.gauss(0, self._J_POS),
                ang + random.gauss(0, self._J_ANG),
                length, width, conc,
                opacity=opacity, thickness=thickness,
                curvature=curvature, waviness=waviness, wave_freq=wave_freq,
                dryness=dryness, smear=smear, taper_end=taper_end)

    # ── ground: riusa lo stile v8 ───────────────────────────────────────────
    def ground(self):
        base_cols = [
            mixc(OCHRE, WHITE, 0.16), OCHRE, OCHRE,
            mixc(OCHRE, BLACK, 0.022), mixc(OCHRE, VERM, 0.030),
        ]
        y = -20.0
        while y < self.H + 20:
            x = random.uniform(-300, -80)
            while x < self.W + 50:
                L = random.uniform(350, 700)
                self.cv.stroke(
                    x=x, y=y + random.gauss(0, 6),
                    angle=random.gauss(0.0, 0.04),
                    length=L, width=random.uniform(40, 70),
                    conc=random.choice(base_cols),
                    opacity=random.uniform(0.55, 0.78),
                    thickness=random.uniform(0.12, 0.28),
                    curvature=random.gauss(0, 0.04),
                    dryness=random.uniform(0.55, 0.78),
                    smear=random.uniform(0.20, 0.38),
                    taper_end=random.uniform(0.50, 0.80))
                x += L * random.uniform(0.65, 0.90)
            y += random.uniform(30, 46)
        for col, count in [(mixc(OCHRE, WHITE, 0.30), 8),
                           (mixc(OCHRE, VERM, 0.035), 6)]:
            for _ in range(count):
                self.cv.stroke(
                    x=random.uniform(0, self.W), y=random.uniform(0, self.H),
                    angle=random.gauss(0.0, 0.08),
                    length=random.uniform(120, 280),
                    width=random.uniform(18, 38), conc=col,
                    opacity=random.uniform(0.22, 0.44),
                    thickness=random.uniform(0.08, 0.18),
                    curvature=random.gauss(0, 0.10),
                    dryness=random.uniform(0.60, 0.85),
                    smear=random.uniform(0.25, 0.45),
                    taper_end=random.uniform(0.6, 0.92))

    # ── la passeggiata ──────────────────────────────────────────────────────
    def walk(self):
        evs = JOHNNY_B_GOODE_INTRO
        prev_end = 0.0
        prev_bar = 0
        prev_pitches = None
        cluster_k = 0
        cluster_anchor = None
        phrase_sign = 1.0

        for i, e in enumerate(evs):
            notes = sorted(e.get('dyad') or [e['midi']])
            tech = e['tech']
            vel = e['vel']
            t, d = e['t'], e['d']

            # pausa → il cammino avanza in silenzio (tela nuda)
            gap = t - prev_end
            if gap > 0.05:
                self._advance(gap * self.L_BEAT * 0.5)
                self._steer()

            # cambio battuta → svolta di fraseggio (alternata)
            bar = int(t // 4)
            if bar > prev_bar:
                self.theta = _wrap(self.theta + phrase_sign * self.PHRASE_TURN)
                phrase_sign = -phrase_sign
                prev_bar = bar

            # ripetizione (stesso contenuto) → rosetta, non avanzare
            pitches = tuple(notes)
            repeating = (pitches == prev_pitches
                         and tech.startswith('double_stop'))
            if repeating:
                cluster_k += 1
            else:
                cluster_k = 0
                cluster_anchor = (self.x, self.y)

            # parametri materia (mapping v2)
            width0 = VEL_WIDTH[vel] * self._shuffle_w(t) * 1.15
            thick = VEL_THICK[vel]
            opac = VEL_OPAC[vel]
            dry = self._dry(t)
            L = d * self.L_BEAT * K_TECH.get(tech, 0.8)

            # rosetta a girasole per le ripetizioni: r∝√k, angolo aureo
            if repeating and cluster_anchor is not None:
                ga = cluster_k * 2.39996
                r = width0 * 0.88 * math.sqrt(cluster_k)
                bx = cluster_anchor[0] + r * math.cos(ga)
                by = cluster_anchor[1] + r * math.sin(ga)
                ang = self.theta + math.sin(cluster_k * 2.4) * 0.30
                thick *= (1.0 + 0.06 * cluster_k)      # l'impasto si accumula
            else:
                bx, by = self.x, self.y
                ang = self.theta

            names = '+'.join(pitch_class(m) for m in notes)
            print(f"  [{i+1:2d}/{len(evs)}] t={t:6.3f} {names:5s} {tech:18s} "
                  f"P=({bx:6.0f},{by:6.0f}) θ={math.degrees(ang):6.1f}°"
                  f"{'  ⟲' + str(cluster_k) if repeating else ''}")

            # ── il gesto, per ogni voce del dyad ────────────────────────────
            n_lo, n_hi = notes[0], notes[-1]
            for vi, midi in enumerate(notes):
                conc = note_conc(midi)
                # voci del dyad separate perpendicolarmente al cammino
                if len(notes) > 1:
                    off = (midi - (n_lo + n_hi) / 2) * self.DYAD_SEP
                    ox = bx + math.sin(ang) * off      # voce acuta sopra
                    oy = by - math.cos(ang) * off
                else:
                    ox, oy = bx, by
                smear = 0.5 if (len(notes) > 1 and vi == 1) else 0.10

                if tech == 'staccato':
                    self._mark(ox, oy, ang, max(26, L), width0, conc,
                               opac, thick * 1.05, dryness=0.42,
                               smear=smear, taper_end=0.35)
                elif tech == 'legato':
                    self._mark(ox, oy, ang, L, width0, conc,
                               opac, thick, dryness=dry,
                               smear=smear, taper_end=0.70)
                elif tech == 'slide':
                    # lo slide accelera: tratto pieno, coda lunga
                    self._mark(ox, oy, ang, L, width0 * 0.9, conc,
                               opac, thick, dryness=0.50,
                               smear=smear, taper_end=0.82)
                elif tech == 'bend':
                    semis = e.get('bend', 2)
                    self._mark(ox, oy, ang, L, width0 * 0.82, conc,
                               opac, thick * 1.15,
                               curvature=-0.65 * semis,
                               dryness=0.30, smear=smear, taper_end=0.55)
                elif tech == 'vibrato':
                    self._mark(ox, oy, ang, L, width0 * 0.85, conc,
                               opac, thick,
                               waviness=9.0, wave_freq=5.0,
                               dryness=dry, smear=smear, taper_end=0.55)
                elif tech == 'hammer_on':
                    # dab + frustata verso la nota martellata
                    self._mark(ox, oy, ang, max(22, L * 0.5), width0, conc,
                               opac, thick * 1.1, dryness=0.30,
                               smear=smear, taper_end=0.4)
                    to = e.get('hammer_to', midi + 1)
                    a2 = _wrap(ang - (to - midi) * self.SEMI_TURN * 2)
                    self._mark(ox + 10 * math.cos(ang), oy + 10 * math.sin(ang),
                               a2, L * 0.7, width0 * 0.55,
                               note_conc(to), opac * 0.9, thick * 0.8,
                               dryness=0.45, smear=smear, taper_end=0.8)
                elif tech.startswith('double_stop'):
                    if tech == 'double_stop_final':
                        self._mark(ox, oy, ang, L, width0 * 1.1, conc,
                                   opac, thick * 1.30,
                                   waviness=7.0, wave_freq=4.0,
                                   dryness=0.22, smear=smear, taper_end=0.6)
                    else:
                        self._mark(ox, oy, ang, max(24, L), width0, conc,
                                   opac, thick, dryness=0.40,
                                   smear=smear, taper_end=0.45)
                else:
                    self._mark(ox, oy, ang, L, width0, conc, opac, thick,
                               dryness=dry, smear=smear)

            # ── avanzamento + svolta melodica ───────────────────────────────
            if not repeating:
                curv = -0.65 * e.get('bend', 0) if tech == 'bend' else 0.0
                self._advance(L * 0.92, ang + curv * 0.5)
                self._advance(8)                      # respiro tra i gesti
            elif tech == 'double_stop_final':
                self._advance(L * 0.9)

            # svolta = intervallo verso la prossima nota
            if i + 1 < len(evs):
                nxt = sorted(evs[i + 1].get('dyad') or [evs[i + 1]['midi']])
                iv = nxt[-1] - notes[-1]
                turn = max(-self.MAX_TURN,
                           min(self.MAX_TURN, iv * self.SEMI_TURN))
                self.theta = _wrap(self.theta - turn)   # salita = verso l'alto
            self._steer()

            prev_end = t + d
            prev_pitches = pitches

    def create(self, out: str = 'johnny_b_goode_zorn_v9.png'):
        print("Ground (campo ocra, concentrazioni KM)...")
        self.ground()
        self.cv.conc = np.clip(blur(self.cv.conc, 14.0), 0, 1)
        print("La passeggiata melodica...")
        self.walk()
        print("Relief lighting (KM → RGB, tela nel rilievo)...")
        img = self.cv.render()
        img.save(out, dpi=(150, 150))
        print(f"\nArtwork v9 salvato: {out}")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(
        description='guitarzorn v9 — la melodia disegna un cammino')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--out', default='johnny_b_goode_zorn_v9.png')
    args = p.parse_args()
    ZornMelodicWalk(seed=args.seed).create(out=args.out)
