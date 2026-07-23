# Klee Art Asset Manifest (measured from Downfall's completed reference character)

Every dimension below is scraped from Hexaghost (complete) / Champ (Spine humanoid) — these are the actual pipeline inputs, not guesses. The ImageGen pipeline handles framing/compositing from these raw inputs.

## The bill, by category

| Category | Dims | Slice count | Full count | Notes |
|---|---|---|---|---|
| Card portraits | 500×380 | 31 | 75 | ImageGen input; art only, frame is composited |
| Companion portraits | 500×380 | 7 | 16 | Same pipeline |
| Power icons | 256×256 | ~8 | ~24 | 6 elemental auras + Bomb + Spark cover the slice; aura icons are shared mod-wide (pay once, every character reuses) |
| Relic icons | 256×256 | 1 | ~10 | Pounding Surprise only for slice |
| Character select portrait | 132×195 | 1 (+locked variant) | 2 | |
| Character icon | 88×88 | 1 (+outline) | 2 | |
| Energy icon | 74×74 + 22×22 | 2 | 2 | |
| Map marker | 49×64 | 1 | 1 | |
| Selection screen art | 1920×1200 | 1 | 1 | The big splash |
| Victory transition | 2560×1200 | 0 (defer) | 1 | |
| Co-op minigame poses | 422×1200 ×4 | 0 (defer) | 4 | Rock/paper/scissors/point poses — yes, really; C4 concern |
| Combat model layers | ~256–1024 per layer | 3–5 layers | 3–5 | ONE artwork, cut into layers — see recipe |

**Slice total: ~55 images, most of them small icons. Full character: ~135.**

## The combat model layer cut — AS SHIPPED (animation sprint 1, Track B, 2026-07-23)

Source artwork: `ImageGen/images/model/character_klee_full_wish.png` (1069x1245,
the wish splash — same source the static `combat_model.png` was scaled from).
The plan's nominal cut was body/head/backpack/Dodoco; in THIS pose a head cut
runs through hair overlaps and buys visible seams for a weak effect, while the
splash's big free-floating elements separate almost surgically. Shipped cut
(5 layers, z back-to-front):

| Layer | Master (full res) | Shipped (combat scale) | Motion role |
|---|---|---|---|
| smoke | 698x884 | 154x202 | slow x-drift (blast cloud) |
| floaters | 1058x1124 | 240x256 | ambient bob (bell-bombs, flowers, trails) |
| dumpty | 407x479 | 98x110 | the held Jumpy Dumpty: bob + micro-rotate |
| body | 528x847 | 124x195 | Klee herself: sway; hurt-flash target |
| dodoco | 153x187 | 41x49 | independent bob + wiggle ("she's alive") |

Method (all scripted, no hand editor work): alpha connected components gave
the floaters for free; the one merged blob (Klee+dumpty+smoke+dodoco) was
hard-partitioned by hand-digitized fence polylines + flood fill, leftover
outline pixels assigned by priority dilation (dodoco > dumpty > body > smoke).
Hard partition means the at-rest recomposition is pixel-exact by construction.
Lower layers are inpainted (edge-extension onion peel) behind movers: smoke
32px behind dumpty/body/dodoco, body 20px behind dodoco — sized so worst-case
relative idle motion (~27 source px) never reveals a hole.

Masters: `ImageGen/images/model/layers/klee_layer_*.png` (+ `layers.json`
offsets). Shipped: `layers/combat/klee_combat_*.png` (+ `layers_combat.json`),
pre-scaled to the same 240x280 box the static model used — house rule: ship
pre-sized art, no runtime minification. Both tiers F in `art/SOURCES.tsv`
(derived from the already-ledgered wish splash). Layer PNGs are gitignored
with the rest of ImageGen/images; `tools/cut_klee_combat_layers.py` (the
committed cut — fences, partition, inpaint, export) regenerates all of them
from the wish splash, and its printed offsets must match the sprite positions
in `klee-mod/pck-src/klee/model/combat.tscn`.

## The combat model: no Spine required (Hexaghost proves it)
Hexaghost's in-combat "model" is a Godot scene: TextureRect layers (a 512px core + five 256px orb layers) driven by an **AnimationPlayer + AnimationTree**, with GPUParticles2D for smoke/hurt effects. Champ, by contrast, uses a Spine rig (54KB .spskel + one 512×1024 atlas). We take the Hexaghost road:
1. Pick ONE full-body Klee artwork.
2. Cut 3–5 layers in any editor: back hair/cape → body → head → arms → front accessories (Dodoco is its own layer, obviously — it should bob independently).
3. Godot scene mirroring `hexaghost2.tscn` structure: idle = 2–3px sinusoidal bob with per-layer phase offsets (this alone reads as "alive"), attack = quick forward lunge tween + slight squash, hurt = shake + a spark GPUParticles burst. The character class's `AttackAnimDelay`/`CastAnimDelay` floats sync damage timing — trivial.
An afternoon of work for a result that reads far better than static, and infinitely cheaper than rigging.

## Three-tier art policy (art is never a blocker)
1. **Tier P (programmatic):** generated frames + card name text — the C2 default; the build never waits on art.
2. **Tier F (found/fan art):** private builds only, per principles §9. Never in anything distributed, including Workshop "unlisted."
3. **Tier O (original/commissioned):** the only tier that ships publicly.
Track per-asset tier in a manifest column; "promote to Tier O" becomes a simple filter query when/if a public release happens.

## Sourcing notes for Tier F (private)
- Genshin's own **Genius Invokation TCG art** is dimensionally and compositionally near-perfect for card portraits — action cards literally depict skills/bursts in card-art framing.
- In-game **skill/element icons** map directly onto power icons (aura icons especially: instantly readable to any Genshin player).
- Curation beats volume: the slice needs ~40 curated pieces, not a scraped archive — manual saving is both sufficient and avoids automated-scraping ToS issues on art sites.
- Keep a `SOURCES.txt` (url per asset) even for private use: if the project ever goes public, it's the checklist of what needs replacing, and if any fanartist's work inspired a commissioned piece, it's the courtesy-credit list.
