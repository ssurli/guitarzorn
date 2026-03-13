"""
guitarzorn v5 — Guitar Evolution
=================================
Approach 2B: "The Riff Paints Its Own Instrument"

The 12-note Johnny B. Goode riff paints the guitar that produced it.
Each pentatonic note is assigned to a guitar anatomy zone:
  A (vermilion) → body          — tonic, dominant resonant mass
  C (ochre)     → neck          — minor 3rd, pathway of movement
  D (black)     → headstock     — perfect 4th, structural weight
  E (white)     → strings       — perfect 5th, vibrating source
  G (gold)      → sound hole    — minor 7th, tension-release opening

Musical parameters drive stroke placement:
  Duration  → number of strokes in the zone
  Velocity  → stroke size and opacity
  Technique → stroke shape (via v3 _build_traces dispatch)
  String    → sub-zone vertical position
  Fret      → luminosity variation of zone color

The v3 bristle IK-chain physics engine provides the stroke primitive.
Zone masks constrain strokes to anatomically correct regions.
The painting builds the guitar form through accumulation of musical gestures.
"""

import importlib.util
import math
import os
import random
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ── load v3 bristle engine ─────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "v3", os.path.join(_here, "zorn_riff_art_v3.py"))
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)

ZORN           = _v3.ZORN
zorn_blend     = _v3.zorn_blend
get_note_color = _v3.get_note_color
ZornBase       = _v3.ZornRiffBristlePainting

# ── Musical note → guitar anatomy zone ────────────────────────────────────────
NOTE_ZONE: Dict[str, str] = {
    'A': 'body',       # tonic      → largest zone, dominant vermilion
    'C': 'neck',       # minor 3rd  → fretboard, ochre pathway
    'D': 'headstock',  # 4th        → structural dark machinery
    'E': 'strings',    # 5th (bright) → vibrating source, white light
    'G': 'soundhole',  # minor 7th  → tension-release, gold ring
}

ZONE_COLOR: Dict[str, Tuple[int, int, int]] = {
    'body':      ZORN['vermilion'],
    'neck':      ZORN['ochre'],
    'headstock': ZORN['black'],
    'strings':   ZORN['white'],
    'soundhole': ZORN['gold'],
}

# painting order: back-to-front
ZONE_PRIORITY = ['body', 'neck', 'headstock', 'soundhole', 'strings']


class ZornGuitarEvolution(ZornBase):
    """
    v5: Zone-directed evolutionary guitar painting.

    The guitar is painted by the riff itself: each note deposits bristle
    strokes into the guitar anatomy zone that corresponds to its pitch class.
    The technique-specific stroke vocabulary from v3 drives the shape of marks
    within each zone, so the painting carries the full articulation vocabulary
    of the original performance.
    """

    def __init__(self, width: int = 1600, height: int = 1000,
                 seed: int = 42, n_repeat: int = 10):
        super().__init__(width, height, seed)
        self.n_repeat = n_repeat   # base painting passes per note event

        # Dark canvas — guitar on a near-black ground
        bg = zorn_blend(ZORN['black'], ZORN['ochre'], 0.10) + (255,)
        self.canvas = Image.new('RGBA', (width, height), bg)
        self.arr    = np.array(self.canvas)

        print("Building guitar zones...")
        self.zone_masks, self.guitar_info = self._build_guitar_zones()

        # Cache sampled pixel positions per zone for fast random sampling
        self.zone_pts: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
        for zname, mask in self.zone_masks.items():
            ys, xs = np.where(mask)
            if len(xs) > 0:
                self.zone_pts[zname] = (xs, ys)

        print("Building target image...")
        self.target = self._build_target_image()

    # ── Guitar geometry ──────────────────────────────────────────────────────

    def _build_guitar_zones(self) -> Tuple[Dict[str, np.ndarray], Dict]:
        """
        Procedurally generate guitar silhouette and zone masks.

        Layout (horizontal, headstock LEFT, body RIGHT):

          x:  50 .......... 235 ........... 890 ................ 1560
              [HEADSTOCK]  [NUT]  [NECK/FRETBOARD]  [BODY]
          y:                  460 .......... 540   (neck center band)
                            275 ................ 725 (body extent)
        """
        W, H = self.W, self.H

        # ── 1. BODY ─────────────────────────────────────────────────────────
        body_img = Image.new('L', (W, H), 0)
        db = ImageDraw.Draw(body_img)
        # Upper bout (toward neck side, slightly smaller)
        db.ellipse([870, 290, 1300, 660], fill=255)
        # Lower bout (toward tail, larger)
        db.ellipse([1010, 310, 1530, 710], fill=255)
        # Connecting fill bridges the waist gap
        db.rectangle([960, 375, 1450, 625], fill=255)
        # Rounded tail
        db.ellipse([1400, 400, 1565, 600], fill=255)
        body_arr = np.array(body_img) > 128

        # ── 2. NECK ─────────────────────────────────────────────────────────
        neck_img = Image.new('L', (W, H), 0)
        dn = ImageDraw.Draw(neck_img)
        # Neck tapers slightly from body join (wider) to nut (narrower)
        neck_pts = [
            (235, 455), (890, 462),   # top edge: nut→body
            (890, 538), (235, 545),   # bottom edge: body→nut
        ]
        dn.polygon(neck_pts, fill=255)
        neck_arr = np.array(neck_img) > 128

        # ── 3. HEADSTOCK ────────────────────────────────────────────────────
        head_img = Image.new('L', (W, H), 0)
        dh = ImageDraw.Draw(head_img)
        # Main headstock body
        dh.rectangle([50, 405, 235, 595], fill=255)
        # Slight flare at the far end (tuning peg head)
        dh.rectangle([50, 395, 120, 605], fill=255)
        # Rounded top/bottom
        dh.ellipse([50, 393, 130, 420], fill=255)
        dh.ellipse([50, 580, 130, 607], fill=255)
        head_arr = np.array(head_img) > 128

        # ── 4. SOUND HOLE + BINDING ─────────────────────────────────────────
        # Center of sound hole on body
        sh_cx, sh_cy = 1195, 500
        sh_outer_r   = 93   # outer ring of rosette/binding
        sh_inner_r   = 73   # inner edge of ring (opening)

        sh_img = Image.new('L', (W, H), 0)
        ds = ImageDraw.Draw(sh_img)
        # Rosette ring (gold): outer circle minus inner circle
        ds.ellipse([sh_cx - sh_outer_r, sh_cy - sh_outer_r,
                    sh_cx + sh_outer_r, sh_cy + sh_outer_r], fill=255)
        ds.ellipse([sh_cx - sh_inner_r, sh_cy - sh_inner_r,
                    sh_cx + sh_inner_r, sh_cy + sh_inner_r], fill=0)

        # Body binding: thin border around body exterior
        body_pil     = Image.fromarray((body_arr * 255).astype(np.uint8), 'L')
        body_dilated = body_pil.filter(ImageFilter.MaxFilter(21))
        body_eroded  = body_pil.filter(ImageFilter.MinFilter(21))
        binding_arr  = ((np.array(body_dilated) > 128) &
                        ~(np.array(body_eroded) > 128))

        # Neck binding: thin border around neck exterior
        neck_pil     = Image.fromarray((neck_arr * 255).astype(np.uint8), 'L')
        neck_dilated = neck_pil.filter(ImageFilter.MaxFilter(13))
        neck_eroded  = neck_pil.filter(ImageFilter.MinFilter(13))
        neck_binding = ((np.array(neck_dilated) > 128) &
                        ~(np.array(neck_eroded) > 128))

        sh_arr = (np.array(sh_img) > 128) | binding_arr | neck_binding

        # ── 5. STRINGS ──────────────────────────────────────────────────────
        # Six strings: from nut (x=235) across neck and body to bridge (x=1230)
        # String 1 (high E) at top, string 6 (low E) at bottom
        string_ys = [469, 479, 489, 511, 521, 531]
        str_arr = np.zeros((H, W), dtype=bool)
        for sy in string_ys:
            str_arr[sy - 2:sy + 3, 235:1235] = True

        # ── Make zones mutually exclusive ────────────────────────────────────
        # Iterate in REVERSE painting order so highest z-order zones (strings)
        # claim their pixels first before lower zones can take them.
        # Painting order (back→front): body neck headstock soundhole strings
        # Assignment order (high→low priority): strings soundhole headstock neck body
        zone_raw = {
            'body':      body_arr,
            'neck':      neck_arr,
            'headstock': head_arr,
            'soundhole': sh_arr,
            'strings':   str_arr,
        }
        assigned = np.zeros((H, W), dtype=bool)
        final_masks: Dict[str, np.ndarray] = {}
        for zname in reversed(ZONE_PRIORITY):   # strings first → highest priority
            m = zone_raw[zname] & ~assigned
            final_masks[zname] = m
            assigned |= m

        # Remove the physical sound hole opening from body (shows dark ground)
        hole_img = Image.new('L', (W, H), 0)
        ImageDraw.Draw(hole_img).ellipse(
            [sh_cx - sh_inner_r + 2, sh_cy - sh_inner_r + 2,
             sh_cx + sh_inner_r - 2, sh_cy + sh_inner_r - 2], fill=255)
        hole_arr = np.array(hole_img) > 128
        final_masks['body'] = final_masks['body'] & ~hole_arr

        guitar_info = {
            'body_cx': 1210, 'body_cy': 500,
            'neck_x0': 235,  'neck_x1': 890, 'neck_cy': 500,
            'head_x0': 50,   'head_x1': 235, 'head_cy': 500,
            'sh_cx': sh_cx,  'sh_cy': sh_cy,
            'sh_outer_r': sh_outer_r, 'sh_inner_r': sh_inner_r,
            'string_ys': string_ys,
            'string_x0': 235, 'string_x1': 1235,
        }
        return final_masks, guitar_info

    def _build_target_image(self) -> np.ndarray:
        """Build solid-color zone target image for visual reference."""
        target = np.zeros((self.H, self.W, 4), dtype=np.uint8)
        bg = zorn_blend(ZORN['black'], ZORN['ochre'], 0.10)
        target[:, :, :3] = bg
        target[:, :,  3] = 255
        for zname, mask in self.zone_masks.items():
            if not np.any(mask):
                continue
            col = ZONE_COLOR[zname]
            target[mask, 0] = col[0]
            target[mask, 1] = col[1]
            target[mask, 2] = col[2]
        return target

    def save_target(self, out: str = 'guitar_target_v5.png'):
        """Save the procedural guitar target for inspection."""
        Image.fromarray(self.target[:, :, :3]).save(out)
        print(f"  Target saved: {out}")

    # ── Ground layer ─────────────────────────────────────────────────────────

    def _ground_layer(self):
        """
        Dark ground with subtle guitar-body toning.
        Warm ochre glazes hint at the body shape before active painting begins.
        """
        arr   = np.array(self.canvas)
        noise = np.random.normal(0, 5, arr.shape[:2] + (3,)).astype(int)
        arr[:, :, :3] = np.clip(arr[:, :, :3].astype(int) + noise, 0, 255)
        self.canvas.paste(
            Image.fromarray(arr[:, :, :3].astype(np.uint8)).convert('RGBA'))
        self.arr[:] = np.array(self.canvas)

        # Warm ochre underpainting on body zone (luminous ground under vermilion)
        body_pts = self.zone_pts.get('body')
        if body_pts is not None and len(body_pts[0]) > 0:
            warm = zorn_blend(ZORN['ochre'], ZORN['black'], 0.20)
            for _ in range(14):
                pos = self._sample_zone('body')
                self._paint_one(pos, random.uniform(16, 32),
                                random.randint(90, 140), warm, 'mf',
                                ang=random.gauss(0, 0.30), alpha_scale=0.28)

        # Cool dark wash on headstock zone
        head_pts = self.zone_pts.get('headstock')
        if head_pts is not None and len(head_pts[0]) > 0:
            cool = zorn_blend(ZORN['black'], ZORN['ochre'], 0.08)
            for _ in range(6):
                pos = self._sample_zone('headstock')
                self._paint_one(pos, random.uniform(12, 22),
                                random.randint(70, 110), cool, 'mp',
                                ang=random.gauss(0, 0.25), alpha_scale=0.35)

    # ── Sampling helpers ─────────────────────────────────────────────────────

    def _sample_zone(self, zone_name: str) -> np.ndarray:
        """Return a random pixel coordinate within a zone."""
        xs, ys = self.zone_pts[zone_name]
        idx = random.randint(0, len(xs) - 1)
        return np.array([float(xs[idx]), float(ys[idx])])

    # ── Per-note zone painting ────────────────────────────────────────────────

    def _paint_zone_note(self, note: Dict, notes: List[Dict],
                         note_idx: int, zone_name: str):
        """
        Deposit bristle strokes from one riff event into its guitar zone.

        Stroke count scales with note duration.
        Position is sampled from the zone mask, with string/fret sub-positioning.
        Technique-specific trace parameters from _build_traces drive shape.
        """
        if zone_name not in self.zone_pts:
            return

        base_sz = self._vel_to_size(note['velocity'])
        traces  = self._build_traces(note, notes, note_idx)
        color   = get_note_color(note['note'], note['velocity'])

        # Duration-proportional repeat: longer notes paint more
        n_reps  = max(2, int(self.n_repeat * note['duration'] / 0.5))

        # String-derived Y sub-positioning within zone
        # String 1 (high E) = top of frame, string 6 (low E) = bottom
        gi      = self.guitar_info
        str_num = note.get('string', 3)
        str_ys  = gi['string_ys']
        # Map string 1–6 to a Y offset within the zone bandwidth
        y_sub   = (str_ys[min(str_num - 1, 5)] - gi['neck_cy'])
        y_sub  *= 0.5  # soften the sub-positioning for natural spread

        for _ in range(n_reps):
            for n_steps, ang, sm, asc, av, (dx, dy) in traces:
                # Sample base position from zone mask
                pos    = self._sample_zone(zone_name)

                # Sub-position bias: strings info → vertical offset
                sub_off = np.array([0.0, y_sub * random.uniform(0.3, 0.9)])

                jitter = np.array([random.gauss(0, 30.0),
                                   random.gauss(0, 22.0)])
                start  = np.clip(
                    pos + sub_off + np.array([dx, dy]) + jitter,
                    [0.0, 0.0], [float(self.W), float(self.H)])

                size   = base_sz * sm * random.uniform(0.80, 1.25)
                n_st   = max(25, int(n_steps * random.uniform(0.70, 1.30)))

                self._paint_one(
                    start, size, n_st, color, note['velocity'],
                    ang=ang + random.gauss(0, 0.12),
                    alpha_scale=asc,
                    ang_vel=av)

    # ── Entry point ───────────────────────────────────────────────────────────

    def create(self, out: str = 'johnny_b_goode_zorn_v5.png',
               save_target: bool = False):
        """Paint the guitar using the riff events and save the result."""
        notes = self.parse_riff()

        if save_target:
            self.save_target()

        print("Ground layer (dark imprimitura + warm body glaze)...")
        self._ground_layer()

        # Organize notes by zone
        notes_by_zone: Dict[str, List[Tuple[int, Dict]]] = {
            z: [] for z in ZONE_PRIORITY}
        for idx, note in enumerate(notes):
            zone = NOTE_ZONE.get(note['note'], 'body')
            notes_by_zone[zone].append((idx, note))

        # Paint zone by zone, body first → strings last
        print("Painting zones (body → neck → headstock → soundhole → strings)...")
        for zone_name in ZONE_PRIORITY:
            zone_events = notes_by_zone[zone_name]
            if not zone_events or zone_name not in self.zone_pts:
                print(f"  {zone_name:10s}: skipped (no events or empty mask)")
                continue

            total_dur  = sum(n['duration'] for _, n in zone_events)
            n_trace_est = sum(
                len(self._build_traces(n, notes, i)) *
                max(2, int(self.n_repeat * n['duration'] / 0.5))
                for i, n in zone_events)

            print(f"  {zone_name:10s}: {len(zone_events)} note(s), "
                  f"dur={total_dur:.2f}b, ~{n_trace_est} strokes")

            for note_idx, note in zone_events:
                self._paint_zone_note(note, notes, note_idx, zone_name)

        self.canvas.convert('RGB').save(out, dpi=(150, 150))
        print(f"\nArtwork v5 saved: {out}")


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(
        description='guitarzorn v5 — the riff of Johnny B. Goode '
                    'paints the guitar it was played on')
    p.add_argument('--seed',   type=int, default=42,
                   help='random seed (default: 42)')
    p.add_argument('--repeat', type=int, default=10,
                   help='painting passes per note event (default: 10)')
    p.add_argument('--out',    default='johnny_b_goode_zorn_v5.png',
                   help='output filename')
    p.add_argument('--target', action='store_true',
                   help='also save the procedural guitar target image')
    args = p.parse_args()

    ZornGuitarEvolution(
        seed=args.seed,
        n_repeat=args.repeat,
    ).create(out=args.out, save_target=args.target)
