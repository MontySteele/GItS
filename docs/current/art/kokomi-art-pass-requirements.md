# Kokomi Art Pass Requirements

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

**Date:** 2026-07-25
**Status:** card shortlists built and provisionally applied (77 faces, awaiting
the [USER] taste pass); **character-shell track DONE** — see §5a
**Canonical content:** `docs/kokomi-cards.yaml`, `docs/inazuma-companions.yaml`
**Bill owner:** `tools/art_coverage.py` — if this doc and the tool disagree, the tool is right (the lesson of the Furina bill correction).

## 1. The bill

| Surface | Required portraits |
|---|---:|
| Kokomi personal sheet | 62 |
| Companions (Inazuma) | 15 |
| **Total card-sized outputs** | **77** |

*(Stale since later the same day — recap note 2026-07-26: the shell track
shipped (§5a, commit `68fb11b`) and all 73 faces carry applied provisional
rank-1 picks (`6f1b969`); "zero exist" described the pre-pass world. The
[USER] taste pass is what remains — `docs/current/playtest/open-playtest-items.md` §6.1.)*

*(Bill correction 2026-07-26, post-merge sweep: **58 → 62**. The Neap Tide
amendment added four faces this table did not follow — R73's
`before_sun_and_moon` and the three F4 Sly-lane bridge rows (`ebb_tide`,
`salt_line`, `undertow`). All four are now planned, rendered and ledgered, and
`art_coverage.py` reports 267/267 with an empty MISSING bill. Note what the
delay cost nothing and what it nearly cost: the game renders the BETA
placeholder for an unplanned face and NOTHING fails, so a sheet that grows
between art passes is invisible until someone runs the tool. This is the same
sheet-moved-projection-did-not shape as the five defects in the Neap Tide
addendum, with the art bill as the projection.)*

Zero currently exist. She ships playable on Klee's assets via
`build_pck.ps1`'s `Copy-KokomiFallback`, so **the game looks finished and this
bill is invisible everywhere except the coverage tool.** That is the whole
reason the tool was taught the roster before this pass started.

Policy is unchanged and binding: **Tier F (found/official) is private-playtest
only**; a public build needs Tier O. See `teyvat-spire-design-principles.md` §9.

## 2. THE SCARCITY RULING WAS MADE ON AN INCOMPLETE INVENTORY

The standing ruling (2026-07-25, [USER]) reads: *"Kokomi has only ~8 usable
large illos for 38 personal faces (Furina had ~25 for 76). Ruled **widen the
source pool** — TCG/event splashes/manga/promo on top of the Furina hybrid §2
split, accepting a mixed visual register and a longer SOURCES ledger."*

**The direction was right. The count was not, in both directions.** A real
hunt (`tools/art_hunt.py`, 2026-07-25) found more than 8 — and then eyes-on
inspection disqualified two whole families the raw counts had included.

### What actually exists

| Register | Count | Notes |
|---|---:|---|
| `splash` — large figure illustrations | 10 | Portrait 4900×5700, Introduction Card 2250², Profile 2400×1320, Wish 2048×1024, Full Wish 1568², Card 1080×1920, Game 964×1736, Showcase 700×2646, Namecard BG 840×400, Multi Wish 320×1024 |
| `sticker` | 15 | 11 Paimon's Paintings emoji (300–340², transparent, **no text**), 3 Expressions (420²), Side by Side (263×315) |
| `tcg` | 3 | Character Card + Platinum + Golden, 420×720 each |
| `item` | 5 | Sango Pearl Wild 797², Vision 400², Sango Pearl 256², The Deep 256², Item 256² |
| `vfx` | **0 usable** | see below — every one is a sigil |
| **Viable distinct sources** | **33** | against **62** personal faces (58 when this was counted; +4 in the Neap Tide amendment) |

### `vfx` IS A DEAD REGISTER FOR HER — the single most important finding

Every piece of her kit art is a sigil or a clip thumbnail:

| Source | Size |
|---|---|
| Talent Nereid's Ascension / Kurage's Oath / Princess of Watatsumi | 128×128 |
| Ceremonial Garment Buff Icon | 100×100 |
| Nereid's Ascension / Kurage's Oath / Garment Water / Garment Attack previews | 480×270 |

Not one reaches a 500×380 card, and `vfx` is **not** undersize-exempt — only
`item` and `sticker` are, and rightly: a sigil is not an illustration.

This matters more than the raw count suggests. Her kit art is the obvious
*content* match for her attack and ability cards — the Garment previews
literally depict the Ceremonial Garment — and **none of it can be used on any
card face.** The first draft of the plan leaned on it for twelve rank-1 picks
and `art_process` rejected all twelve on L8. They now sit at rank 3 in every
shortlist, so the taste pass can still choose one deliberately; they must
never be the default.

Bake-Kurage Summon (420×720) is the exception and is *not* a sigil — it is a
full-size render of the jellyfish, and it is the only kit art that works.

### What was disqualified, and why it matters

Two families were counted as inventory by a title-only read and then rejected
on sight. Both are now enumerated bans in `tools/art_lint.py`:

- **`Sangonomiya Kokomi Character Details 1–7`** — a direct read-across from
  the already-banned `Furina Character Details` family, then confirmed by eye.
  Details 1 is her key illustration under a burnt-in name wordmark, a stat
  block and three paragraphs of kit text; Details 5 is solid body text with a
  chibi inset. *The illustration under Details 1 is genuinely good* — its
  tagline is even "Pearl of Wisdom", which is what [USER] independently named
  her starter relic. If it is ever wanted it should be a deliberate manual crop
  with eyes on it, not a shortlist row that slips through on a title match.

- **`Icon Emoji Sangonomiya Kokomi Xiaohongshu 02–16`** (16 files) — 120×120
  chat emoji with **Chinese caption text burnt across the art**. Two
  disqualifiers at once: burnt-in text, and a 4× upscale to reach 500×380.
  This one needed an explicit ban rather than relying on L8, because the
  `sticker` register is `UNDERSIZE_EXEMPT` — **L8 would have waved all sixteen
  through.**

Naming them here rather than silently dropping them: a later pass that
re-runs the hunt will see 27 emoji and 7 Character Details and reasonably
wonder why the plan ignores them.

### Consequence for the plan: the unit is SLOTS, not sources

33 sources against 62 faces means crop reuse is mandatory, as hybrid §2
anticipated. But the real currency turned out to be **(source, anchor)
slots**: a large source backs several distinct faces, a small transparent icon
backs exactly one.

| Family | Sources | Slots |
|---|---:|---:|
| large splash (multi-anchor) | 10 | 38 |
| tcg (multi-anchor) | 3 | 12 |
| item (single) | 5 | 5 |
| sticker (single) | 15 | 15 |
| **total** | **33** | **70** for 62 faces |

**Headroom, as of the 2026-07-26 gap fill: 8 slots.** The four Neap Tide faces
were each given a source that NO card row held at rank 1 — Bake-Kurage Summon,
Namecard Background The Deep, Expression 2, Profile — which was the last of the
unclaimed-*source* slack, not of the slot slack. The distinction matters for
whoever adds the next card: there are still spare anchors on the large splash
and tcg families, so the next face is a re-crop of an already-used source, and
it will need an L12 check rather than a hunt.

**Anchors are computed, not chosen.** A `cover` focus is a *centre*, and the
crop is clamped inside the image, so any anchor nearer an edge than half the
crop renders identical pixels. On Portrait (4900×5700) the valid centre range
is only [0.33, 0.67]; on Introduction Card (2250²) it is [0.38, 0.62]. The
generator derives each source's range from its geometry and spreads slots
inside it.

**`Sangonomiya Kokomi Card.png` caveat:** 1080×1920 and her best art, but it
carries the GENSHIN IMPACT wordmark top-centre and a miHoYo logo bottom-right.
A 500×380 `cover` crop takes a horizontal band, so anchors inside [0.24, 0.74]
exclude both. A top anchor pulls the wordmark straight in.

**Nothing above is a request to revisit the ruling.** Widening the pool is
still the right call and this pass follows it. The correction is only to the
arithmetic the ruling was justified with, because that arithmetic decides how
aggressively crops get reused.

## 2a. The lint could not see the thing that was actually wrong

Worth recording, because it cost two rebuilds and it generalises.

`art_lint` L1 compares `(title, frame)` and L7 compares `(mode, focus)` — both
compare **what the plan says**. Both crop modes clamp, so two rows that differ
on paper can render the same picture:

- the first draft used `cover_autocrop` margins as if they were anchors
  (`cover@0.22` vs `cover@0.58`) → **11 pixel-identical groups across ~28
  cards, lint fully green**;
- the second draft switched to real `cover` anchors but picked values outside
  the valid centre range → **3 more identical pairs, lint still green**.

Both were found by hashing `art/candidates/*/r1.png`, not by any rule. That
sweep is now **L12** in `art_lint`, and it immediately turned up three
*pre-existing* identical pairs nobody had noticed:

| Pair | Status |
|---|---|
| `blazing_delight` == `true_spark_knight` | shipped Klee art, allowlisted, **wants a re-pick** |
| `catalytic_conversion` == `spark_collection` | already in `PENDING_RED_PEN` for a related L1 |
| `crowd_work` == `standing_ovation` | shipped Furina art, allowlisted, **wants a re-pick** |

They are allowlisted as *known defects*, not exemptions — the gate now holds
the line while they wait for a ruling.

## 3. Companions (Inazuma) — not scarce at all

Fifteen faces across seven characters (Gorou 3, Sayu 3, Shinobu 3, Sara 2,
Thoma 2, Itto 1, Raiden 1). Every one of the seven has the full standard set:
Wish, Full Wish, Multi Wish, Portrait, Introduction Card, three Expressions,
and most have a TCG Character Card.

This is the same abundance the Fontaine companions had, so it takes the same
treatment: `tcg` cover at `y0.16` where a Character Card exists,
`cover_autocrop` off the Wish splash otherwise. Low risk, high confidence,
and it can be shortlisted mechanically.

## 4. Register assignment by lane

Her sheet divides cleanly, which helps a thin splash pool go further:

| Lane | Cards | Natural register |
|---|---:|---|
| Commander (orders, banners, mustering) | 10 | `item` (props, standards, notices), `splash` for the rares |
| Priest (rituals, offerings, prayers) | 15 | `item` (Sango Pearl, offerings, shrine), environment |
| Assist (tricks, quiet moments, misdirection) | 11 | `sticker` — the 11 Paimon's Paintings emoji land almost entirely here |
| Generic / attacks | 22 | `splash`, `tcg`, `vfx` (talent previews) |

The assist lane is the happy accident of this pass: *A Moment Alone*,
*Daydream of a Quiet Life*, *A Whispered Word* and *Quiet Harbor* are exactly
what a chibi reaction sticker is for, and the sticker pool is the one part of
the inventory that is not scarce relative to its lane.

## 5. Order of work

1. Hunt the real inventory — **done**, this document.
2. Ban what fails on sight — **done**, `art_lint.BANNED_SOURCE_FAMILIES`.
3. Build `art/plan.tsv` shortlists — 3 ranked candidates per face, 73 faces.
   Companions first (mechanical), then Kokomi by lane.
4. `python tools/art_fetch.py` → `art/raw/` + `art/SOURCES.tsv`.
5. `python tools/art_contact_sheet.py` → the artifact the taste pass reads.
6. **[USER] taste pass** — the picks are not mine to make. Klee's took three
   red-pen rounds (`docs/archive/klee-art-redpen-round2.md`, `round3.md`) and Furina's
   rejected 13 of batch 1.
7. `python tools/art_process.py` → `ImageGen/images/cards/kokomi/`, then
   `art_lint` and `art_coverage --strict` green.

## 5a. Character-shell track — DONE 2026-07-25

The eight non-card surfaces that make her a character rather than a card set.
She was wearing Klee's for all eight (`Copy-KokomiFallback`), which is
deliberately invisible: the build is green, the mod loads, and the select
screen just shows the wrong girl.

| Surface | Size | Producer |
|---|---|---|
| `ui/select_portrait.png` | 132×195 | `gen_kokomi_stills.py` |
| `ui/select_portrait_locked.png` | 132×195 | derived from the portrait |
| `ui/char_icon.png` | 88×88 | `gen_kokomi_stills.py` |
| `ui/map_marker.png` | 49×64 | `gen_kokomi_stills.py` |
| `ui/selection_splash.png` | 1920×1200 | `gen_kokomi_stills.py` |
| `model/combat_model.png` | 240×280 | `gen_kokomi_stills.py` |
| `ui/select_bg.png` | 1920×1080 | `art_process` (the only plan row) |
| `ui/transition_wipe.png` | 960×540 | `gen_transition_wipe.py`, procedural |

All eight are registered in `art_lint.GENERATOR_OWNED` except `select_bg`, so
no plan row can ever claim a path a generator writes (L11).

**Three things this track had to solve that Furina's did not.**

1. **Her governing render is flattened onto white.** Furina's arrived as a
   transparent cutout. Kokomi's best full-body art — Portrait, 4900×5700 — is
   on a white plate, and fed to B4's framing code it yields a full-frame alpha
   bbox: every rule degrades to frame-centring, which is *the exact bug B4 was
   called to fix*, reintroduced by the source rather than by the code. So the
   cut is a precondition. Keying by colour is wrong (she wears white stockings
   and a white kimono panel and a global white test punches holes through
   her), so `cutout_from_plate` keys by **connectivity**: only near-white
   reachable from the border is background.

2. **Her silhouette is not just her.** The Portrait sweeps a large fin to her
   right and floats a fish beside her raised hand, which drags the alpha bbox
   midpoint **275 px right of her actual head** — enough to land her face
   visibly left of frame in a 132×195 portrait. `head_crop` gained
   `centre_on="head"`, which takes the **median** alpha column of the top
   band. Median rather than the band's min/max midpoint because median is
   mass-weighted and ignores a small bright fish: across band sizes of
   12/18/25/35% the median moves 2165→2221 while the min/max midpoint swings
   2191→2667→2608→2215.

3. **The splash is 1920×1200 but only 1080 rows are ever seen.**
   `char_select_bg_kokomi.tscn` draws it in a 1920×1080 `TextureRect` with
   `stretch_mode = 6` (KEEP_ASPECT_COVERED), so the top and bottom 60 rows are
   cropped. Framing against the full 1200 put her head under the top cut and
   took her feet off entirely — **correct in the file, wrong in the game**,
   which is the only kind of art defect that survives review. The generator now
   measures against the visible band, and derives the band from the scene's
   geometry rather than typing it in.

**The framing math moved to `tools/char_stills.py`** rather than being copied.
B4's centring rule was a [USER] verdict, and a verdict that exists in two files
drifts on the next edit. Furina's six surfaces are pinned byte-for-byte by
`tier0/tests/test_char_stills.py`, which re-runs her generator and compares
hashes — the extraction is proven not to have moved one of her pixels.

**Two defects found along the way, both outside this track:**

- `build_pck.ps1` shipped the generators' cached working renders, because it
  copied every `*.png` under `model/`. Kokomi's cutout is 8.6 MB against a
  whole pck of 8.3 MB. Excluded by suffix now, so the next character's cutout
  is covered before anyone notices it exists.
- `validate.ps1` failed on a **passing** lint. Under PS 5.1 with
  `ErrorActionPreference = 'Stop'`, any native stderr raises
  `NativeCommandError` even at exit 0; `lint_constant_parity` had grown an
  import of `tier05.relics`, which emits three house-rule `UserWarning`s.
  Latent on `main` since `e263577` and blocking every deploy.

## 6. Open questions for the taste pass

1. **Crop reuse budget.** 45 cards over ~24 reusable sources is ~2 crops per
   source. Furina's hybrid §2 capped this implicitly; is there a number you
   want stated, or is it eyes-on per card?
2. **Environment art as card faces.** Watatsumi Island / Shrine / Altar are
   on-theme for the priest lane but contain no character. Furina's pass
   rejected an empty-corridor screenshot as "a random hallway". Is a *shrine*
   different from a *hallway*, or is the same ban in force?
3. **Character Details 1.** Banned as a family, but the illustration under the
   text is her best key art. Do you want a manual crop of it for a Rare?
