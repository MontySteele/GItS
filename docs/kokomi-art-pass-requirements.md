# Kokomi Art Pass Requirements

**Date:** 2026-07-25
**Status:** hunt complete, inventory verified, shortlists not yet built
**Canonical content:** `docs/kokomi-cards.yaml`, `docs/inazuma-companions.yaml`
**Bill owner:** `tools/art_coverage.py` — if this doc and the tool disagree, the tool is right (the lesson of the Furina bill correction).

## 1. The bill

| Surface | Required portraits |
|---|---:|
| Kokomi personal sheet | 58 |
| Companions (Inazuma) | 15 |
| **Total card-sized outputs** | **73** |

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
| `splash` — large figure illustrations | ~11 | Wish, Full Wish, Multi Wish, Card, Portrait, Profile, Introduction Card, Introduction Banner, Character Card Showcase, in-game Game render, namecard background |
| `sticker` — Paimon's Paintings emoji | 11 | 340×340, transparent, **no burnt-in text**, unmistakably her |
| `tcg` | 1 art / 3 files | Character Card + Platinum + Golden (frame variants of one illustration) |
| `item` / `vfx` — talents, props, Vision | ~10 | Talent Kurage's Oath / Nereid's Ascension / Princess of Watatsumi, Bake-Kurage Summon, Ceremonial Garment Buff Icon, Vision, Item, Item The Deep, Sango Pearl (+Wild), ability preview gifs |
| environment — Watatsumi | ~4 | Island, Island Concept Art, Sangonomiya Shrine, Watatsumi Altar |
| **Viable distinct sources** | **~37** | against **58** personal faces |

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

### Consequence for the plan

~37 viable sources against 58 faces means **crop reuse is mandatory**, exactly
as the Furina hybrid §2 split anticipated — but the ratio (1.6 faces per
source) is far healthier than the ruling's premise implied (4.75). Concretely:

- **Basics and Rares get unique, uncropped-family picks** (13 cards: 5 basic +
  8 rare). This is the strict half of hybrid §2 and there is enough splash and
  talent art to honour it.
- **Commons and Uncommons draw from the crop-reuse pool** (45 cards), where one
  large source yields several distinct crops.
- **The `Sangonomiya Kokomi Card.png` caveat:** 1080×1920 and excellent, but it
  carries the GENSHIN IMPACT wordmark top-centre and a miHoYo logo
  bottom-right. At the 500×380 card aspect a `cover` crop takes a horizontal
  band, so a **mid-body focus excludes both** — but `focus: top` would pull the
  wordmark straight in. Any row using it must not use a top anchor.

**Nothing above is a request to revisit the ruling.** Widening the pool is
still the right call and this pass follows it. The correction is only to the
arithmetic the ruling was justified with, because that arithmetic is about to
decide how aggressively crops get reused.

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

1. ~~Hunt the real inventory~~ — **done**, this document.
2. ~~Ban what fails on sight~~ — **done**, `art_lint.BANNED_SOURCE_FAMILIES`.
3. Build `art/plan.tsv` shortlists — 3 ranked candidates per face, 73 faces.
   Companions first (mechanical), then Kokomi by lane.
4. `python tools/art_fetch.py` → `art/raw/` + `art/SOURCES.tsv`.
5. `python tools/art_contact_sheet.py` → the artifact the taste pass reads.
6. **[USER] taste pass** — the picks are not mine to make. Klee's took three
   red-pen rounds (`docs/klee-art-redpen-round2.md`, `round3.md`) and Furina's
   rejected 13 of batch 1.
7. `python tools/art_process.py` → `ImageGen/images/cards/kokomi/`, then
   `art_lint` and `art_coverage --strict` green.

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
