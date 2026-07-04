"""
guitarzorn — partitura canonica: intro di Johnny B. Goode (Chuck Berry)
========================================================================
Versione in LA (l'originale è in Si bemolle), 4 battute, shuffle.
Lo swing è "cotto" nei tempi: le coppie di crome swing sono 2/3 + 1/3
di beat, così pittura e audio condividono la stessa griglia temporale.

Struttura riconoscibile dell'intro:
  Battuta 1 — figura d'apertura: slide E4→G4, sol ribattuto, BEND G4→A4
              (il bend "piangente"), poi il dondolo G-E in legato swing.
  Battuta 2 — discesa Chuck Berry: A4 G4 E4 D4, hammer C4→C#4 (il passo
              b3→3 marchio di fabbrica), arrivo su A3 con vibrato.
  Battute 3-4 — il "campanello": double-stop A4+E4 (fondamentale+quinta)
              ribattuti in shuffle staccato, alternanza forte/medio, poi
              l'accordo finale lungo con vibrato.

Ogni evento è codificato con MIDI diretto (niente corda/tasto: elimina
alla radice il bug di tuning della v7 segnalato dall'Agente 2).

Schema evento:
  midi      int              nota singola (oppure usare 'dyad')
  dyad      [int, int]       double-stop (grave, acuto) — pittura bicolore
  t         float            inizio in beat (swing già applicato)
  d         float            durata in beat
  vel       'p'..'ff'        dinamica
  tech      str              tecnica → forma pittorica
  slide_to  int (opz.)       MIDI d'arrivo dello slide
  bend      int (opz.)       semitoni di bend
  hammer_to int (opz.)       MIDI d'arrivo dell'hammer-on
"""

TEMPO_BPM = 168          # lo shuffle di Chuck Berry corre
BEATS_TOTAL = 14.5       # 3.5 battute + coda dell'accordo finale
SWING = (2 / 3, 1 / 3)   # coppia di crome swing (già cotta nei tempi sotto)

JOHNNY_B_GOODE_INTRO = [
    # ── Battuta 1: figura d'apertura ──────────────────────────────────────
    dict(midi=64, t=0.000, d=0.667, vel='f',  tech='slide', slide_to=67),
    dict(midi=67, t=0.667, d=0.333, vel='mf', tech='staccato'),
    dict(midi=67, t=1.000, d=1.000, vel='ff', tech='bend', bend=2),
    dict(midi=67, t=2.000, d=0.667, vel='f',  tech='legato'),
    dict(midi=64, t=2.667, d=0.333, vel='mf', tech='legato'),
    dict(midi=67, t=3.000, d=0.667, vel='f',  tech='legato'),
    dict(midi=64, t=3.667, d=0.333, vel='mf', tech='legato'),
    # ── Battuta 2: discesa Chuck Berry ────────────────────────────────────
    dict(midi=69, t=4.000, d=0.667, vel='f',  tech='staccato'),
    dict(midi=67, t=4.667, d=0.333, vel='f',  tech='legato'),
    dict(midi=64, t=5.000, d=0.667, vel='mf', tech='legato'),
    dict(midi=62, t=5.667, d=0.333, vel='mf', tech='legato'),
    dict(midi=60, t=6.000, d=0.333, vel='f',  tech='hammer_on', hammer_to=61),
    dict(midi=61, t=6.333, d=0.334, vel='f',  tech='legato'),
    dict(midi=57, t=6.667, d=1.333, vel='f',  tech='vibrato'),
    # ── Battute 3-4: il "campanello" (double-stop A4+E4, shuffle) ────────
    dict(dyad=[64, 69], t= 8.000, d=0.30, vel='f',  tech='double_stop'),
    dict(dyad=[64, 69], t= 8.667, d=0.30, vel='mf', tech='double_stop'),
    dict(dyad=[64, 69], t= 9.000, d=0.30, vel='f',  tech='double_stop'),
    dict(dyad=[64, 69], t= 9.667, d=0.30, vel='mf', tech='double_stop'),
    dict(dyad=[64, 69], t=10.000, d=0.30, vel='f',  tech='double_stop'),
    dict(dyad=[64, 69], t=10.667, d=0.30, vel='mf', tech='double_stop'),
    dict(dyad=[64, 69], t=11.000, d=0.30, vel='f',  tech='double_stop'),
    dict(dyad=[64, 69], t=11.667, d=0.30, vel='mf', tech='double_stop'),
    # accordo finale: lungo, fortissimo, con vibrato
    dict(dyad=[64, 69], t=12.000, d=2.000, vel='ff', tech='double_stop_final'),
]

# Nota → classe di pitch per il colore Zorn (mapping v2, Agente 2)
PITCH_CLASS_NAMES = {0: 'C', 2: 'D', 4: 'E', 5: 'F', 7: 'G', 9: 'A', 10: 'Bb', 11: 'B'}


def pitch_class(midi: int) -> str:
    """Nome della classe di pitch (per il mapping colore)."""
    pc = midi % 12
    if pc in PITCH_CLASS_NAMES:
        return PITCH_CLASS_NAMES[pc]
    # cromatismi (es. C#4 dell'hammer): risolvi al semitono inferiore
    return PITCH_CLASS_NAMES.get((pc - 1) % 12, 'A')


def octave(midi: int) -> int:
    return midi // 12 - 1


if __name__ == '__main__':
    for e in JOHNNY_B_GOODE_INTRO:
        notes = e.get('dyad') or [e['midi']]
        names = '+'.join(f"{pitch_class(m)}{octave(m)}" for m in notes)
        print(f"t={e['t']:6.3f}  d={e['d']:5.3f}  {e['vel']:2s}  "
              f"{e['tech']:16s}  {names}")
