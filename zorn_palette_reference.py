"""
Zorn Palette – Documento di Riferimento Storico e Teorico
=========================================================
Generato per il progetto guitarzorn: musica → pittura astratta.

INDICE
------
1. Anders Zorn – biografia e contesto
2. I quattro pigmenti: storia, proprietà fisiche, RGB/hex
3. Teoria del colore: perché funziona
4. Logica di mescolanza: toni caldi/freddi, luci, ombre
5. Parallelo filosofico: limitazione come vincolo creativo
6. Il nero come sostituto del blu freddo
7. Approssimazioni RGB/hex per artisti digitali
8. Qualità "olio": spessore, velatura, glazing
9. Mapping A min pentatonica ↔ Palette Zorn
10. Costanti Python pronte per l'uso
"""

# ===========================================================================
# 1. ANDERS ZORN – BIOGRAFIA E CONTESTO
# ===========================================================================
"""
Anders Zorn (18 febbraio 1860 – 22 agosto 1920) era un pittore svedese
rinomato per ritrattistica, paesaggio e acquaforte. Nacque a Mora, in
Dalarna, figlio illegittimo di un birraio bavarese; questa origine modesta
plasmò la sua etica del lavoro essenziale.

Cronologia rilevante:
  1887 – Inizia a dipingere ad olio (tardivamente rispetto ai coetanei).
         Adotta deliberatamente pigmenti "arcaici" quando il mercato era
         invaso da sintetici sgargianti (cadmi, cobalti).
  1890s – Ritrattista internazionale: dipinge tre presidenti USA
         (Cleveland, Harrison, Theodore Roosevelt), Rodin, il re di Svezia.
  ~1900 – La palette limitata è ormai il suo marchio consolidato.

Influenza diretta:
  Edward Simmons (pittore americano) suggerì a Zorn di iniziare con
  Ochre + White + Black. Zorn aggiunse il Vermilion e lo usò come
  colore dominante per il resto della carriera.

Fonte documentaria:
  – Rosemary Hoffman, "Northern Light: Nordic Art at the Turn of the Century":
    "Zorn era noto per eseguire dipinti usando una sobria scala cromatica
     limitata a bianco, ocra, vermiglione e nero avorio."
  – Hans Henrik Brummer (catalogo Zorn, 1986):
    "Fondamentalmente il suo registro era limitato a nero, bianco, terre
     gialle e vermiglione; altri pigmenti potevano essere usati solo per
     accenti locali se necessari."
  – Birge Harrison, "Landscape Painting" (1854–1929):
    "Zorn usa solo due colori — vermiglione e ocra gialla; i suoi altri
     due pigmenti, nero e bianco, essendo la negazione del colore. Con
     questa palette semplice fino alla povertà riesce a dipingere
     un'immensa varietà di soggetti."
"""

# ===========================================================================
# 2. I QUATTRO PIGMENTI
# ===========================================================================
"""
YELLOW OCHRE (Giallo Ocra)
--------------------------
Nome storico: Terra di Siena cruda / Ocra gialla naturale
Origine:      Ossido di ferro idrato (Fe₂O₃·H₂O), minerale estratto
              in Francia, Italia, Cipro fin dall'antichità (caverne di
              Lascaux, ~17 000 a.C.).
Pigment code: PY43 (Pigment Yellow 43)
Proprietà:
  – Semitrasparente in strato sottile, opaco in strato spesso
  – Essiccazione media nell'olio
  – Non tossico, stabilissimo (non sbiadisce, non scurisce)
  – Potere tintoriale moderato: non sovrasta gli altri pigmenti
  – Grana fine, si mescola uniformemente
Tonalità:     Giallo terra caldo, leggermente arancione, mai vivace

VERMILION (Vermiglione)
-----------------------
Nome storico: Cinabro sintetico (HgS), usato da Romani e Cinesi
Origine:      Solfuro di mercurio sintetico (sec. VIII-IX d.C.)
              Sostituto moderno: Cadmio Rosso Chiaro (PO20/PR108)
              oppure Rosso Cadmio Medio
Pigment code: PR106 (Pigment Red 106, vermiglione autentico)
Proprietà originali:
  – Alta opacità, colore intenso rosso-arancio saturo
  – Lenta essiccazione nell'olio
  – TOSSICO (mercurio) → oggi sostituito quasi universalmente
  – Tono leggermente più arancione del cadmio rosso
  – Colore più caldo e brillante della palette
Sostituto moderno: Cadmium Red Light – tono simile, più sicuro ma
                   ancora classificato tossico (Cd). Alternativa
                   non tossica: Naphtol Red Medium.

IVORY BLACK (Nero Avorio)
-------------------------
Nome storico: Nero d'avorio originale (carbone da avorio bruciato)
              Oggi quasi sempre: Bone Black (carbone da ossa) o
              Lamp Black (PBk6)
Pigment code: PBk9 (Pigment Black 9, bone/ivory black)
Proprietà:
  – Nero relativamente FREDDO con sottotono bluastro-viola
     (questa è la chiave della tecnica Zorn! → vedi §6)
  – Alta opacità, forte potere tintoriale
  – Essiccazione LENTA nell'olio (ritarda l'asciugatura delle miscele)
  – Grana più grossolana del Mars Black
  – Semi-opaco in strato sottile → può creare velature scure trasparenti
  – NON usare Mars Black (PBk11): è più neutro/caldo, perde il
    sottotono freddo fondamentale alla tecnica Zorn

LEAD WHITE / TITANIUM WHITE (Bianco di Piombo / Bianco Titanio)
----------------------------------------------------------------
Nome storico: Bianco di piombo (carbonato basico di piombo, 2PbCO₃·Pb(OH)₂)
              usato dal Rinascimento fino al '900
Pigment code originale: PW1 (Pigment White 1, lead white)
Sostituto moderno:      PW6 (Titanium White)
Proprietà bianco di piombo:
  – Tonalità leggermente CALDA (crema), non fredda
  – Essiccazione rapida, rinforza il film d'olio
  – TOSSICO (piombo)
  – Texture burrosa, ottima per impasto
  – Leggermente semitrasparente in strato sottile
Proprietà titanio bianco:
  – Tonalità fredda, brillante (più "plastica")
  – Altissima opacità, potere tintoriale molto alto
     (attenzione: spolpa rapidamente i colori in miscela)
  – Modifica le proporzioni di miscela rispetto al piombo
"""

# ===========================================================================
# 3. TEORIA DEL COLORE: PERCHÉ FUNZIONA
# ===========================================================================
"""
La palette Zorn funziona perché i 4 pigmenti costituiscono una versione
ridotta del triangolo dei primari:

  CALDO ←──────────────────→ FREDDO
   Vermilion (rosso caldo)    Black (nero freddo, ≈ blu scuro)
         ↘                  ↙
            Ochre (giallo terra)
                  ↕
              White (luce)

Ivory Black come "primario freddo sostituto":
  Nero Avorio ≈ blu molto scuro e desaturato. Mescolato con Ochre
  produce verdi terrossi. Mescolato con Vermilion produce marroni
  e viola scuri. Questo "finge" la presenza di blu e verde.

Gamut della palette Zorn:
  – Ottima copertura dei toni carnagione (warm highlights → warm shadows)
  – Buona rappresentazione di: terra, legno, cielo grigio, acqua notturna
  – Limitata per: cieli azzurri intensi, prati verdi brillanti,
    fiori viola saturi → non era un problema per i soggetti di Zorn
    (ritratti in interni, nudi, paesaggi nordici nebbiosi)

Coerenza cromatica:
  Poiché ogni colore della palette condivide pigmenti con gli altri,
  qualsiasi miscela suona "in armonia". È quasi impossibile creare
  una stonatura — esattamente come in musica con la scala pentatonica.

Analogia musicale diretta (da più fonti):
  "A limited palette is much like a key in music, and can be used as
   a framework within which to create harmonies and a colorist
   interpretation of your subject." (Fine Art Tutorials)
"""

# ===========================================================================
# 4. LOGICA DI MESCOLANZA
# ===========================================================================
"""
TONI CALDI (highlights, luce solare):
  Ochre + White              → giallo crema caldo (luce su pelle chiara)
  Ochre + Vermilion          → arancio terracotta (luce su pelle scura)
  Vermilion + White          → rosa salmone (guance, labbra illuminate)

TONI MEDI (mid-tones, penombra):
  Ochre + Vermilion + poco White  → incarnato naturale
  Ochre + poco Black              → verde oliva (penombra fredda)
  Ochre + Vermilion + poco Black  → marrone rossiccio (capelli)

TONI FREDDI (shadows, ombre):
  Black + Ochre              → verde scuro (ombre sullo sfondo)
  Black + Vermilion          → marrone scuro / viola porpora (ombre profonde)
  Black + White              → grigio freddo (≈ cielo coperto, riflessi)
  Black + White + poco Ochre → grigio caldo (ombre in luce)

LUCI ESTREME:
  White dominante + tocco Ochre   → bianco caldo (massima luce)
  White + tocco Vermilion         → rosa pallidissimo

OMBRE PROFONDE:
  Black dominante + poco Vermilion → nero vinaceo (massima ombra, caldo)
  Black puro (raro) → solo per accenti neri neutri

PROPORZIONI INDICATIVE per incarnato base:
  Highlight:  White 60% + Ochre 30% + Vermilion 10%
  Mid-tone:   Ochre 40% + Vermilion 30% + White 20% + Black 10%
  Shadow:     Ochre 30% + Black 40% + Vermilion 20% + White 10%
  Deep shadow: Black 60% + Vermilion 25% + Ochre 15%
"""

# ===========================================================================
# 5. PARALLELO FILOSOFICO: LIMITAZIONE COME VINCOLO CREATIVO
# ===========================================================================
"""
La palette Zorn è un vincolo auto-imposto che libera anziché restringere.

Paralleli storici dello stesso principio:
  MUSICA:   Scala pentatonica (5 note) → blues, rock, folk di tutto il
            mondo. Impossibile suonare "note sbagliate" all'interno della
            scala. La limitazione crea coerenza e permette l'improvvisazione
            libera.
  POESIA:   Sonetto (14 versi, schema fisso) → obbligo formale che
            concentra l'espressione.
  CINEMA:   Dogma 95 (Trier, Vinterberg) → regole rigide come generatori
            di autenticità.
  ARCHIT.:  Casa Farnsworth (Mies) → riduzione fino all'essenziale.

Birge Harrison: "Con questa palette semplice fino alla povertà riesce
a dipingere un'immensa varietà di soggetti." La "povertà" è la forza.

Per il progetto guitarzorn:
  – Pentatonica A minore (5 note) ≡ Palette Zorn (4+1 pigmenti)
  – Entrambi producono coerenza armonica automatica
  – In entrambi la "nota/colore sbagliato" è strutturalmente impossibile
  – La limitazione forza creatività nella variazione di parametri
    secondari: dinamica/spessore, articolazione/texture, ritmo/composizione
"""

# ===========================================================================
# 6. IL NERO COME SOSTITUTO DEL BLU FREDDO
# ===========================================================================
"""
Questo è il principio più contro-intuitivo e più importante della tecnica.

Ivory Black (PBk9) NON è un nero neutro. È un nero con sottotono FREDDO,
tendente al blu-viola quando diluito o miscelato con bianco.

Test pratico:
  Ivory Black + Titanium White → grigio freddo con tinta lievemente viola-blu
  Mars Black  + Titanium White → grigio più neutro/caldo

Zorn sfruttava questo per:
  1. Creare ombre fredde senza usare blu (che avrebbe sporcato la palette)
  2. Dipingere cieli coperti e acqua con soli grigio-blu da Black+White
  3. Creare complementarietà termica: Vermilion (caldo) vs Black (freddo)
     → lo stesso contrasto di Rosso vs Blu nella teoria classica,
     ma dentro una gamma ridotta e coerente

Il pianista blues usa il blues note (♭5) che "suona storta" ma dentro
la pentatonica suona giusta. Il nero di Zorn è la sua blues note:
tecnicamente assenza di colore, praticamente un colore completo.

Per la traduzione digitale:
  – Non usare Black puro (0,0,0) per le ombre → troppo neutro
  – Usare Ivory Black (#1C1C1C) che ha la stessa subtonalità fredda
  – In RGB: black con R < G ≈ B crea il sottotono freddo giusto
    Ivory Black digitale: R=28, G=28, B=28 → ma con velature
    su sfondo bianco appare più freddo del Mars Black digitale
"""

# ===========================================================================
# 7. APPROSSIMAZIONI RGB/HEX PER ARTISTI DIGITALI
# ===========================================================================
"""
Nota: i pigmenti fisici variano per marca e formulazione. Queste sono
approssimazioni di riferimento, non valori assoluti.

YELLOW OCHRE:
  Hex:  #C4A46A  (da Parametri grafici.txt del progetto)
  Hex:  #CC7722  (approssimazione comune online)
  RGB:  (196, 164, 106) — versione progetto
  HSL:  ~(37°, 42%, 59%)
  Carattere: giallo-arancio desaturato, caldo, terroso

VERMILION:
  Hex:  #E34234  (da Parametri grafici.txt del progetto)
  Hex:  #E3371E  (approssimazione storica comune)
  Hex:  #CC4422  (variante più arancione)
  RGB:  (227, 66, 52) — versione progetto
  HSL:  ~(4°, 76%, 55%)
  Carattere: rosso-arancio brillante e saturo

IVORY BLACK:
  Hex:  #1C1C1C  (da Parametri grafici.txt del progetto)
  Hex:  #231F20  (più preciso al pigmento fisico)
  RGB:  (28, 28, 28) — versione progetto
  HSL:  ~(0°, 0%, 11%)
  Carattere: quasi nero con lievissimo sottotono neutro
  Nota: il sottotono freddo si manifesta meglio in velatura su bianco

TITANIUM WHITE:
  Hex:  #F2F2F2  (da Parametri grafici.txt del progetto)
  Hex:  #FDFCFA  (più vicino al bianco di piombo caldo)
  RGB:  (242, 242, 242) — versione progetto
  HSL:  ~(0°, 0%, 95%)
  Carattere: bianco quasi puro, lievissimo grigio

MISCELE PRE-CALCOLATE (utili come riferimento):
  Ochre+White (50/50):        #DBC58C  (luce calda, tono pelle chiara)
  Ochre+Vermilion (50/50):    #DB854B  (arancio terracotta)
  Vermilion+White (50/50):    #F19194  (rosa salmone)
  Black+White (50/50):        #8F8F8F  (grigio medio neutro)
  Black+Ochre (50/50):        #67604A  (verde oliva scuro)
  Ochre+Black (70/30):        #9C8A5C  (mix G della pentatonica)
"""

# ===========================================================================
# 8. QUALITÀ "OLIO": SPESSORE, VELATURA, GLAZING
# ===========================================================================
"""
La tecnica ad olio associata alla palette Zorn ha caratteristiche specifiche
che la simulazione digitale deve replicare:

IMPASTO (pasta spessa):
  – Colore puro o quasi puro, steso con pennellata singola e decisa
  – Visibile texture della pennellata (bristle marks)
  – Usato per i toni chiari (highlights) con White dominante
  – Simula in digitale: alpha alta (0.9-1.0), tratto singolo spesso

VELATURA (glazing):
  – Strato di colore trasparente su colore già secco
  – Cambia la tonalità senza coprire il sottostante
  – Zorn usava velatture di Vermilion per riscaldare le ombre
  – Simula in digitale: alpha bassa (0.2-0.4), blend mode multiply

SFUMATO BAGNATO SU BAGNATO (wet-on-wet):
  – Il colore fresco si mescola con quello sottostante
  – Crea transizioni morbide e colori ibridi non pre-miscelati
  – Caratteristico delle pennellate di Zorn sui bordi
  – Simula in digitale: campionamento del pixel sottostante e mix
    prima di depositare il nuovo colore (già implementato in v3)

GESTO PITTORICO:
  – Zorn lavorava rapidamente con pennellate larghe e sicure
  – Pochi ritocchi: "alla prima" (dipingere alla prima stesura)
  – Le correzioni si fanno con pennellate sovrapposte, non cancellando
  – In digitale: la fisica IK dei bristle (v3) replica questo gesto

GROUND (preparazione):
  – Zorn usava spesso un ground colorato (non bianco puro)
  – Un ground ocra crea un mezzo-tono di base che unifica tutto
  – Le zone non coperte partecipano alla composizione cromatica
  – In digitale: sfondo ocra anziché bianco (già nel progetto)
"""

# ===========================================================================
# 9. MAPPING A MIN PENTATONICA ↔ PALETTE ZORN
# ===========================================================================
"""
MAPPING ORIGINALE (da "Parametri grafici.txt"):
  A (tonica)      → Yellow Ochre    — terra, fondamento, warmth
  C (3a minore)   → Vermilion       — tensione, emozione, blues note
  D (4a giusta)   → Ivory Black     — peso, profondità, struttura
  E (5a giusta)   → Titanium White  — aria, cielo, risoluzione
  G (7a minore)   → Ochre+Black     — ambiguità, passaggio

MAPPING CORRENTE IN V3 (modificato):
  A (tonica)      → Vermilion       — "il colore più saturo e caldo"
  C (3a minore)   → Ochre           — "terra, supporto"
  D (4a giusta)   → Black           — "peso strutturale"
  E (5a giusta)   → White           — "aria, contrasto"
  G (7a minore)   → Gold            — ochre+vermilion blend

ANALISI COMPARATIVA:

Mapping originale (Ochre=A, Vermilion=C):
  PRO:
  – La tonica A come Ochre è semanticamente coerente: ocra = terra =
    fondamento = radice tonale. Il tono più neutro e stabile per la nota
    più stabile.
  – C (3a minore, la "blues note" della pentatonica) come Vermilion:
    la terza minore è la nota più emotiva, il vermiglione il colore più
    emotivo. Connessione semantica molto forte.
  – G (7a minore, nota di passaggio verso A) come Ochre+Black =
    ocra sporcata di nero: la settima vuole risolvere sulla tonica,
    il suo colore è quasi-ocra ma oscurato = quasi-tonica ma in tensione.
  CONTRO:
  – La tonica che "svanisce" nell'ocra può sembrare poco marcata
    visivamente nella composizione finale.

Mapping v3 (Vermilion=A):
  PRO:
  – A come Vermilion: la tonica è il colore più dominante → ogni ritorno
    alla tonica è un "fuoco" visivo. Funziona per composizione.
  – Gold (Ochre+Vermilion) per G7 è elegante: il Gold tira verso A
    (che è Vermilion), come la settima minore tira verso la tonica.
    Condivide pigmento con A (Vermilion) → risoluzione cromatica.
  CONTRO:
  – C (3a minore) come Ochre perde il collegamento semantico con
    l'emozione blues. L'ocra è troppo "tranquilla" per la terza minore.

RACCOMANDAZIONE:
  Entrambi i mapping sono difendibili. Il mapping originale ha più
  coerenza semantica (nota-emozione ↔ colore-emozione). Il mapping v3
  ha più efficacia compositiva (tonica = colore dominante).

  Soluzione ibrida suggerita:
    A → Vermilion  (tonica come colore più forte, impatto visivo)
    C → Vermilion+Ochre blend scuro (3a minore come tono intermedio
        tra A e D, la "nota in mezzo")
    D → Black      (4a = peso, struttura, basso)
    E → White      (5a = aperto, aria, risoluzione alta)
    G → Ochre      (7a = terra di passaggio, warm e neutro vs Vermilion)

  Oppure, mantenere v3 e documentare la scelta come deliberata:
  la tonica DEVE dominare cromaticamente nella composizione.
"""

# ===========================================================================
# 10. COSTANTI PYTHON PRONTE PER L'USO
# ===========================================================================

# Palette di base (RGB tuple)
ZORN_PALETTE: dict[str, tuple[int, int, int]] = {
    'ochre':     (196, 164, 106),   # Yellow Ochre     #C4A46A  PY43
    'vermilion': (227,  66,  52),   # Vermilion         #E34234  PR106 → PO20
    'black':     ( 28,  28,  28),   # Ivory Black       #1C1C1C  PBk9
    'white':     (242, 242, 242),   # Titanium White    #F2F2F2  PW6
}

# Hex equivalenti (per reference e documentazione)
ZORN_HEX: dict[str, str] = {
    'ochre':     '#C4A46A',
    'vermilion': '#E34234',
    'black':     '#1C1C1C',
    'white':     '#F2F2F2',
}

# Proprietà storiche (pigment code, tossicità, sostituto moderno)
ZORN_PIGMENT_INFO: dict[str, dict] = {
    'ochre': {
        'nome_storico': 'Yellow Ochre / Terra di Siena cruda',
        'pigment_code': 'PY43',
        'formula':      'Fe₂O₃·H₂O',
        'tossicita':    'Non tossico',
        'sostituto':    None,
        'trasparenza':  'semitrasparente–opaco',
        'temperatura':  'caldo',
        'sottotono':    'arancio terroso',
    },
    'vermilion': {
        'nome_storico': 'Vermilion / Cinabro sintetico',
        'pigment_code': 'PR106',
        'formula':      'HgS',
        'tossicita':    'TOSSICO (mercurio)',
        'sostituto':    'Cadmium Red Light (PR108) o Naphtol Red',
        'trasparenza':  'opaco',
        'temperatura':  'caldo',
        'sottotono':    'arancio-rosso brillante',
    },
    'black': {
        'nome_storico': 'Ivory Black / Bone Black',
        'pigment_code': 'PBk9',
        'formula':      'C (carbone da avorio/osso)',
        'tossicita':    'Non tossico',
        'sostituto':    'NON sostituire con Mars Black (perde sottotono freddo)',
        'trasparenza':  'semitrasparente–opaco',
        'temperatura':  'freddo',
        'sottotono':    'bluastro-viola (critico per la tecnica)',
    },
    'white': {
        'nome_storico': 'Lead White (originale) / Titanium White (moderno)',
        'pigment_code': 'PW1 (originale) / PW6 (moderno)',
        'formula':      '2PbCO₃·Pb(OH)₂ / TiO₂',
        'tossicita':    'TOSSICO originale (piombo) / Non tossico moderno',
        'sostituto':    'Titanium White (più freddo, potere tintoriale maggiore)',
        'trasparenza':  'opaco',
        'temperatura':  'caldo (piombo) / freddo (titanio)',
        'sottotono':    'crema (piombo) / bianco puro (titanio)',
    },
}

# Mapping pentatonica A minore → colore (versione progetto v3)
A_MINOR_PENTATONIC_MAP_V3: dict[str, str] = {
    'A': 'vermilion',  # tonica — rosso dominante, impatto visivo massimo
    'C': 'ochre',      # 3a minore — terra calda
    'D': 'black',      # 4a giusta — peso strutturale, basso
    'E': 'white',      # 5a giusta — aria, apertura
    'G': 'gold',       # 7a minore — blend ochre+vermilion, tensione→tonica
}

# Mapping originale da "Parametri grafici.txt" (riferimento alternativo)
A_MINOR_PENTATONIC_MAP_ORIGINAL: dict[str, str] = {
    'A': 'ochre',      # tonica — terra, fondamento
    'C': 'vermilion',  # 3a minore — emozione, blues note
    'D': 'black',      # 4a giusta — peso
    'E': 'white',      # 5a giusta — luce
    'G': 'ochre+black',# 7a minore — quasi-tonica in tensione
}

# Miscele pre-calcolate (RGB) per i toni più comuni
ZORN_PREMIXED: dict[str, tuple[int, int, int]] = {
    'gold':           (220, 140,  73),   # ochre+vermilion → G settima (v3)
    'light_skin':     (219, 197, 140),   # ochre+white 50/50
    'mid_skin':       (204, 116,  78),   # ochre+vermilion 50/50
    'pink_light':     (234, 154, 147),   # vermilion+white 50/50
    'warm_gray':      (135, 134, 124),   # black+white+ochre
    'cool_gray':      (135, 135, 135),   # black+white
    'olive_shadow':   (103,  96,  74),   # black+ochre 50/50
    'deep_shadow':    ( 91,  38,  35),   # black+vermilion 60/40
}


def zorn_mix(c1: tuple[int, int, int],
             c2: tuple[int, int, int],
             t: float) -> tuple[int, int, int]:
    """
    Interpolazione lineare RGB tra due colori Zorn.
    t=0.0 → c1, t=1.0 → c2.
    Equivalente alla mescolanza fisica in quantità proporzionali.
    """
    return tuple(
        max(0, min(255, round(c1[i] * (1.0 - t) + c2[i] * t)))
        for i in range(3)
    )


def get_zorn_color(name: str) -> tuple[int, int, int]:
    """Restituisce RGB del colore Zorn per nome."""
    merged = {**ZORN_PALETTE, **ZORN_PREMIXED}
    return merged.get(name, ZORN_PALETTE['ochre'])


# ---------------------------------------------------------------------------
# FONTI CONSULTATE (ricerca web 12 marzo 2026)
# ---------------------------------------------------------------------------
SOURCES = [
    "https://www.jacksonsart.com/blog/2021/02/02/colour-mixing-exploring-the-zorn-palette/",
    "https://www.naturalpigments.com/artist-materials/zorn-palette-four-colors",
    "https://finearttutorials.com/guide/zorn-palette/",
    "https://drawpaintacademy.com/zorn-palette/",
    "https://artincontext.org/zorn-palette/",
    "https://www.whataportrait.com/blog/zorn-palette-exploring-colors-techniques-artistry/",
    "https://artignition.com/zorn-palette/",
    "http://gurneyjourney.blogspot.com/2011/07/zorn-palette.html",
    "https://michaellynnadams.com/zorn-limited-palette/",
    "https://www.naturalpigments.com/new-zorn-palette.html",
]
