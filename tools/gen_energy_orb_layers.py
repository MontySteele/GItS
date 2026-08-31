#!/usr/bin/env python3
"""EB-88: candidate Hydro orb LAYER SETS for Furina's energy counter.

PRODUCTION ONLY. Every set below is a candidate; the pick is [USER]'s at QUEUE
`M19`, and nothing here writes to an `ImageGen/` out-path, so no pick is made
and `art_process` cannot promote one. Outputs land in the gitignored
`art/candidates/furina_energy_orb/` next to a contact sheet.

WHY PROCEDURAL AND NOT HUNTED
-----------------------------
An orb layer is a UI texture -- a glow, a sphere body, a caustic band, a bezel
ring, a specular gloss. The wiki pool has no such register: `art_hunt` on Hydro
returns 128-512px element sigils, which is the same dead `vfx` register the
Kokomi pass documented (kokomi-art-pass-requirements.md sec.2). Fetching one
would be a fake set. So these are generated, deterministically, the same way
`gen_transition_wipe.py` generates the character-select wipes.

WHAT WAS READ, AND WHAT WAS INFERRED
------------------------------------
Read out of the shipped assembly on 2026-08-13 (`ilspycmd -t
MegaCrit.Sts2.Core.Nodes.Combat.NEnergyCounter`), so these are facts:

  * There are TWO stacks, not one. `_Ready` binds `%Layers` AND
    `%RotationLayers`, both as bare `Control`s.
  * `_Process` spins every `%RotationLayers` child:
    `RotationDegrees += delta * num * (i + 1)`, where `num` is 30 deg/s
    normally and 5 deg/s at Energy == 0. Child index sets the speed, so a
    rotation layer must be CENTRED and must read while spinning -- anything
    with a readable "up" will visibly tumble.
  * At Energy == 0 every child of BOTH stacks gets
    `res://materials/ui/energy_orb_dark.tres` as its `Material` and `%Layers`
    is additionally `Modulate`d to `Colors.DarkGray`. Every layer therefore has
    to survive being darkened; a layer that only reads at full saturation is a
    defect that only shows up on an empty turn.
  * `NEnergyCounter.AssetPaths` lists that material and NOTHING else. The layer
    textures belong to the SCENE, not to the class.
  * The child COUNT is not code-enforced: both loops are
    `GetChildren()`/`GetChildCount()`.

  Register correction for QUEUE `M19` / BACKLOG `EB-88` / `EB-40`, which all
  read "`%Layers` is filled with five orb-layer textures UNDER
  `materials/ui/energy_orb_dark.tres`": `energy_orb_dark.tres` is the DARKENING
  material applied at zero energy, not the container the five textures live
  under. The "five" is the base scene's authoring choice; it is a bill, not a
  constraint.

NOT read, because it cannot be: the base scene itself. `SlayTheSpire2.pck` is
`GDPC` pack format 3 with `pack_flags = 2` (PACK_DIR_ENCRYPTED) -- the file
directory is encrypted, verified directly on 2026-08-13, so
`ironclad_energy_counter.tscn` and its five textures cannot be read off disk
without the game's key. Everything below about layer ROLES (which of the five
is glow / body / caustic / bezel / gloss) is therefore an inference from the
class contract, not a copy of the base scene. State it that way to [USER].

SIZE is a production choice, not a read fact: 256x256, power of two, headroom
over the shipped 74px energy icon. The scene scales `Control`s, so the author
at `EB-40` can resize without a re-render.

Usage:
  python tools/gen_energy_orb_layers.py                    # candidates + sheet
  python tools/gen_energy_orb_layers.py --apply set_a_fontaine   # place a set

RULED 2026-08-30 -- R231 answered QUEUE `M19` with **set A, Fontaine Hydro**,
which was the register's own default. `--apply` writes that set's five layers to
`ImageGen/images/furina/ui/energy_orb/` and writes nothing else. The bare run is
unchanged and still places nothing: production and placement are different acts
and this file keeps them apart on purpose.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art" / "candidates" / "furina_energy_orb"
S = 256  # layer edge, px

# Each set is (slug, human name, palette, notes). Palettes are RGB triples:
#   glow / body_outer / body_inner / rim / gloss
SETS = [
    ("set_a_fontaine", "Set A - Fontaine Hydro",
     dict(glow=(64, 148, 214), body_outer=(22, 68, 122), body_inner=(96, 186, 233),
          rim=(176, 222, 244), gloss=(235, 249, 255)),
     "The conservative read: a vitreous deep-blue sphere with a thin bright "
     "bezel. Closest in construction to the base game's own orb, so it is the "
     "set that will look least like a mod."),
    ("set_b_opera", "Set B - Opera Pale",
     dict(glow=(150, 200, 232), body_outer=(74, 106, 150), body_inner=(206, 231, 248),
          rim=(255, 255, 255), gloss=(255, 255, 255)),
     "Furina's own palette rather than the element's: pale ice-blue and white, "
     "a petal-cut rotation ring instead of a machined bezel. Reads theatrical "
     "and reads WEAKEST when darkened at Energy == 0 -- look at the dark strip."),
    ("set_c_tidal", "Set C - Tidal",
     dict(glow=(38, 172, 178), body_outer=(12, 62, 82), body_inner=(64, 208, 200),
          rim=(140, 240, 226), gloss=(224, 255, 250)),
     "Saturated teal with a heavy wave-crest caustic and a doubled rotation "
     "ring. The most legible at a glance and the furthest from the base game's "
     "colour language; it will not sit quietly next to Klee's counter."),
]

# (index, filename slug, container, human role). Container is the SCENE parent
# the layer is meant for -- this is the inference, and it is what [USER] is
# really being asked to look at.
LAYERS = [
    (1, "layer1_backglow", "%Layers", "outer glow, static, sits behind everything"),
    (2, "layer2_body", "%Layers", "the orb body -- the one layer that must carry the shape"),
    (3, "layer3_caustics", "%RotationLayers", "water caustics, slow spin (child 0 = 30 deg/s)"),
    (4, "layer4_ring", "%RotationLayers", "bezel/rim ring, faster spin (child 1 = 60 deg/s)"),
    (5, "layer5_gloss", "%Layers", "specular gloss + inner shadow, static, on top"),
]


def _blank():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def _radial(inner, outer, r0, r1, gamma=1.0):
    """Radial gradient from `inner` at r0 to `outer` (alpha 0) at r1, in px."""
    img = _blank()
    px = img.load()
    c = S / 2
    for y in range(S):
        for x in range(S):
            r = math.hypot(x - c + 0.5, y - c + 0.5)
            if r >= r1:
                continue
            t = 0.0 if r <= r0 else (r - r0) / (r1 - r0)
            t = t ** gamma
            col = tuple(round(inner[i] * (1 - t) + outer[i] * t) for i in range(3))
            px[x, y] = col + (round(255 * (1 - t)),)
    return img


def backglow(pal):
    return _radial(pal["glow"], pal["glow"], S * 0.24, S * 0.50, gamma=1.6)


def body(pal):
    """Sphere: inner colour lifted up-left so the ball reads lit from above."""
    img = _blank()
    px = img.load()
    c = S / 2
    R = S * 0.40
    for y in range(S):
        for x in range(S):
            dx, dy = x - c + 0.5, y - c + 0.5
            r = math.hypot(dx, dy)
            if r > R:
                continue
            # lambert-ish term from a light at up-left
            n = max(0.0, 1.0 - (r / R) ** 2) ** 0.5
            lx, ly = -0.45, -0.55
            lam = max(0.0, (dx / R) * lx + (dy / R) * ly + n * 0.72)
            t = min(1.0, lam * 1.25)
            col = tuple(round(pal["body_outer"][i] * (1 - t) + pal["body_inner"][i] * t)
                        for i in range(3))
            a = 255 if r < R - 1.5 else round(255 * (R - r) / 1.5)
            px[x, y] = col + (max(0, a),)
    return img


def caustics(pal, lobes):
    """Rotationally repeating bright arcs. No readable 'up' -- it must tumble
    cleanly, which is why this is lobed rather than wave-shaped."""
    img = _blank()
    px = img.load()
    c = S / 2
    for y in range(S):
        for x in range(S):
            dx, dy = x - c + 0.5, y - c + 0.5
            r = math.hypot(dx, dy)
            if not (S * 0.17 < r < S * 0.39):
                continue
            th = math.atan2(dy, dx)
            band = 0.5 + 0.5 * math.sin(th * lobes + r * 0.09)
            band = band ** 3
            # fade at both radial edges so the ring has no hard cut
            edge = min((r - S * 0.17), (S * 0.39 - r)) / (S * 0.05)
            a = round(190 * band * min(1.0, edge))
            if a > 0:
                px[x, y] = pal["rim"] + (a,)
    return img.filter(ImageFilter.GaussianBlur(1.2))


def ring(pal, petals):
    """The bezel. `petals` 0 = a plain annulus; >0 cuts a scalloped edge, which
    is what makes the spin visible at all."""
    img = _blank()
    px = img.load()
    c = S / 2
    for y in range(S):
        for x in range(S):
            dx, dy = x - c + 0.5, y - c + 0.5
            r = math.hypot(dx, dy)
            th = math.atan2(dy, dx)
            outer = S * 0.455
            if petals:
                outer -= S * 0.020 * (0.5 + 0.5 * math.cos(th * petals))
            inner = S * 0.405
            if not (inner < r < outer):
                continue
            edge = min(r - inner, outer - r) / 2.2
            px[x, y] = pal["rim"] + (round(255 * min(1.0, edge)),)
    return img.filter(ImageFilter.GaussianBlur(0.7))


def gloss(pal):
    """Specular cap up-left plus a soft inner shadow along the lower rim."""
    img = _blank()
    d = ImageDraw.Draw(img)
    d.ellipse([S * 0.28, S * 0.20, S * 0.50, S * 0.34], fill=pal["gloss"] + (150,))
    d.ellipse([S * 0.33, S * 0.235, S * 0.44, S * 0.295], fill=pal["gloss"] + (215,))
    img = img.filter(ImageFilter.GaussianBlur(3.0))

    shade = _blank()
    px = shade.load()
    c = S / 2
    R = S * 0.40
    for y in range(S):
        for x in range(S):
            dx, dy = x - c + 0.5, y - c + 0.5
            r = math.hypot(dx, dy)
            if not (R * 0.72 < r < R):
                continue
            if dy < 0:
                continue
            t = (r - R * 0.72) / (R * 0.28)
            px[x, y] = (0, 0, 0, round(95 * t * (dy / R)))
    shade = shade.filter(ImageFilter.GaussianBlur(2.4))
    return Image.alpha_composite(shade, img)


def build_set(slug, pal, lobes, petals):
    return {
        "layer1_backglow": backglow(pal),
        "layer2_body": body(pal),
        "layer3_caustics": caustics(pal, lobes),
        "layer4_ring": ring(pal, petals),
        "layer5_gloss": gloss(pal),
    }


def compose(layers):
    out = _blank()
    for _, name, _, _ in LAYERS:
        out = Image.alpha_composite(out, layers[name])
    return out


def darken(img):
    """Approximate the Energy == 0 state: DarkGray modulate on %Layers. The real
    darkening also applies energy_orb_dark.tres, which is inside the encrypted
    pck and cannot be reproduced here -- so this preview is a FLOOR on how dark
    the zero state gets, not a match for it. Say so on the sheet."""
    px = img.load()
    for y in range(S):
        for x in range(S):
            r, g, b, a = px[x, y]
            px[x, y] = (round(r * 0.663), round(g * 0.663), round(b * 0.663), a)
    return img


SHEET = ROOT / "art" / "contact_sheet_eb88_energy_orb.html"


def write_sheet():
    """The artifact QUEUE `M19` reads. Deliberately has NO radio buttons and no
    picks.tsv export: the card sheets pick one candidate per card, but this is a
    pick of one SET of five, there is no plan row to promote into, and
    `art_process` must never be able to land any of it. [USER] records the set
    at `M19` in words."""
    secs = []
    for slug, name, _pal, note in SETS:
        cells = [
            f'<figure><img src="candidates/furina_energy_orb/{slug}/composed.png">'
            f'<figcaption><b>composed</b><br>all five, stacked in order</figcaption></figure>',
            f'<figure><img class="dk" src="candidates/furina_energy_orb/{slug}/composed_energy_zero.png">'
            f'<figcaption><b>Energy == 0</b><br>DarkGray modulate only — the real state also '
            f'applies energy_orb_dark.tres, which is inside the encrypted pck. This is a FLOOR '
            f'on how dark it gets, not a match.</figcaption></figure>',
        ]
        for _i, fn, container, role in LAYERS:
            spin = " spin" if container == "%RotationLayers" else ""
            cells.append(
                f'<figure><img class="lay{spin}" src="candidates/furina_energy_orb/{slug}/{fn}.png">'
                f'<figcaption><b>{fn}</b><br><code>{container}</code><br>{role}</figcaption></figure>')
        secs.append(f'<section><h2>{name}</h2><p class="note">{note}</p>'
                    f'<div class="row">{"".join(cells)}</div></section>')

    return f"""<!doctype html><meta charset="utf-8"><title>EB-88 — Hydro energy-orb layer sets</title>
<style>
 body{{font:14px/1.5 -apple-system,sans-serif;margin:2em;background:#1b1b1f;color:#eee}}
 h1{{font-size:19px;color:#f8c471}} h2{{margin:1.4em 0 .2em;font-size:16px;color:#f8c471}}
 .note{{color:#cfd3d8;max-width:70em;margin:.2em 0 .8em}}
 .row{{display:flex;gap:14px;flex-wrap:wrap;align-items:flex-start}}
 figure{{margin:0;width:200px;text-align:center;color:#aaa}}
 figure img{{width:190px;height:190px;object-fit:contain;border:3px solid #333;border-radius:6px;
   display:block;margin:0 auto 4px;
   background:repeating-conic-gradient(#2a2a30 0% 25%,#232329 0% 50%) 50%/16px 16px}}
 figcaption{{font-size:12px}} code{{color:#8ecdf5}}
 .spin{{border-color:#5a8;animation:sp 6s linear infinite}}
 @keyframes sp{{to{{transform:rotate(360deg)}}}}
 .warn{{border-left:3px solid #e74c3c;padding:.6em 1em;background:#241b1b;max-width:70em}}
</style>
<h1>EB-88 — candidate Hydro orb layer sets for Furina's energy counter</h1>
<div class="warn">
<b>RULED — <code>R231</code>, 2026-08-30: <code>M19</code> is <u>SET A, FONTAINE HYDRO</u></b>, which was
this register's own default. Its five layers are applied to
<code>ImageGen/images/furina/ui/energy_orb/</code> by
<code>gen_energy_orb_layers.py --apply set_a_fontaine</code>; B and C stay on the page as the
record of what the pick was made against. <b>The ART is all that landed.</b>
<code>EB-40</code>'s scene work — <code>NEnergyCounter</code>'s five <code>GetNode</code>s — is a
separate act by a different hand and is UNBLOCKED, not done; until it lands these files change
nothing in-game. The bare run of this script still places nothing, and there is still no
<code>art/plan.tsv</code> row, so <code>art_process</code> cannot promote any of it.
<p><b>Two things on this page are inferences, not reads.</b> (1) The layer ROLES — which of the five
is glow / body / caustic / bezel / gloss — are derived from the <code>NEnergyCounter</code> class
contract, not copied from the base scene: <code>SlayTheSpire2.pck</code> is <code>GDPC</code> pack
format 3 with <code>pack_flags = 2</code> (PACK_DIR_ENCRYPTED), so
<code>ironclad_energy_counter.tscn</code> and its five textures cannot be read off disk.
(2) 256×256 is a production choice with headroom over the shipped 74px energy icon, not a measured
size.</p>
<p><b>Register correction</b> for <code>M19</code> / <code>EB-88</code> / <code>EB-40</code>, all of
which read "<code>%Layers</code> is filled with five orb-layer textures <i>under</i>
<code>materials/ui/energy_orb_dark.tres</code>": read out of the assembly on 2026-08-13,
<code>energy_orb_dark.tres</code> is the <b>darkening material applied at zero energy</b>, not the
container the textures live under. The "five" is the base scene's authoring choice — both loops are
<code>GetChildren()</code>, so the count is not code-enforced.</p>
<p><b>What the class does enforce, and what it means for the art.</b> There are <b>two</b> stacks:
<code>%Layers</code> (static) and <code>%RotationLayers</code>, whose children
<code>_Process</code> spins at <code>delta · num · (i+1)</code> — 30°/s each step normally, 5°/s at
Energy 0. A rotation layer must be <b>centred</b> and must read <b>while tumbling</b>; the two
green-bordered tiles below are animated at roughly that rate so you can see it. And at Energy 0
<i>both</i> stacks are darkened, so a layer that only reads at full saturation is a defect that
appears on empty turns only.</p>
</div>
{"".join(secs)}
"""


SHAPES = {"set_a_fontaine": (6, 0), "set_b_opera": (5, 8), "set_c_tidal": (9, 16)}

# --apply's destination. A DIRECTORY of its own under Furina's ui/ namespace,
# not five loose files beside select_portrait.png, because these five are one
# indivisible set: the scene stacks them and any one of them alone is not an
# orb. The subdirectory is also why art_ledger's STALE-OUTPUT sweep stays quiet
# -- it globs each expected surface's own directory and does not recurse -- and
# that silence is correct rather than lucky: no C# asks for these paths yet, so
# there is no expected surface to claim them until EB-40 authors the scene.
APPLY_DIR = ROOT / "ImageGen" / "images" / "furina" / "ui" / "energy_orb"

# The five filenames this script owns at the out-path. Spelled out rather than
# derived from LAYERS so art_lint's L11 rot check -- which greps this file for
# each declared GENERATOR_OWNED basename -- can actually find them.
APPLIED_FILES = (
    "layer1_backglow.png",
    "layer2_body.png",
    "layer3_caustics.png",
    "layer4_ring.png",
    "layer5_gloss.png",
)


def apply_set(slug):
    """Write ONE set's five layers to the shipping tree. M19's execution.

    Separate from the candidate run and explicitly argued: everything else here
    is production, and production must never place. This places, so it takes an
    explicit set slug and refuses anything else -- there is no default and no
    bare-invocation path into it, which is the same lesson art_process's
    `--assets` records (a gate is not a batch, and a bare run that promotes
    every rank 1 is how unruled art reaches the tree).

    ART ONLY. The five PNGs are the whole of what this writes. Wiring them into
    a scene is `EB-40`, which has to author `NEnergyCounter`'s five `GetNode`s
    and is a separate act by a different hand; nothing here touches C# or a
    .tscn, and until that work lands these files change nothing in-game.
    """
    match = [s for s in SETS if s[0] == slug]
    if not match:
        raise SystemExit(
            f"--apply: unknown set '{slug}'. Known: "
            + ", ".join(s[0] for s in SETS))
    _slug, name, pal, _note = match[0]
    lobes, petals = SHAPES[slug]
    layers = build_set(slug, pal, lobes, petals)
    APPLY_DIR.mkdir(parents=True, exist_ok=True)
    for _, layer, _, _ in LAYERS:
        dest = APPLY_DIR / f"{layer}.png"
        layers[layer].save(dest)
        print(f"applied: {dest.relative_to(ROOT).as_posix()}")
    print(f"{len(LAYERS)} layers of '{name}' placed under "
          f"{APPLY_DIR.relative_to(ROOT).as_posix()}")


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "--apply":
        if len(argv) != 2:
            raise SystemExit("usage: gen_energy_orb_layers.py --apply <set-slug>")
        apply_set(argv[1])
        return
    if argv:
        raise SystemExit(
            "usage: gen_energy_orb_layers.py [--apply <set-slug>]")
    OUT.mkdir(parents=True, exist_ok=True)
    shapes = SHAPES
    for slug, _name, pal, _note in SETS:
        d = OUT / slug
        d.mkdir(exist_ok=True)
        lobes, petals = shapes[slug]
        layers = build_set(slug, pal, lobes, petals)
        for _, name, _, _ in LAYERS:
            layers[name].save(d / f"{name}.png")
        comp = compose(layers)
        comp.save(d / "composed.png")
        darken(comp.copy()).save(d / "composed_energy_zero.png")
        print(f"  {slug}: 5 layers + composed + composed_energy_zero")
    SHEET.write_text(write_sheet(), encoding="utf-8")
    print(f"\n{len(SETS)} candidate sets -> {OUT}")
    print(f"contact sheet -> {SHEET}")


if __name__ == "__main__":
    main()
